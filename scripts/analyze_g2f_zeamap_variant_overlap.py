#!/usr/bin/env python3
"""Analyze coordinate/allele overlap between G2F VCF and ZEAMAP variants."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--g2f-vcf", default="data/external/g2f/genotypic_2014_2023/inbreds_G2F_2014-2023_437k.vcf")
    parser.add_argument("--zeamap-variants", default="data/deep_model/v0_1/variant_metadata.tsv")
    parser.add_argument("--out-dir", default="data/deep_model/external_pretrain_v0")
    return parser.parse_args()


def norm_chrom(value: object) -> str:
    text = str(value).strip()
    if text.lower().startswith("chr"):
        text = text[3:]
    return text


def load_zeamap(path: Path) -> tuple[dict[tuple[str, int], list[dict[str, object]]], int]:
    df = pd.read_csv(path, sep="\t", usecols=["variant_index", "chrom", "pos", "variant_id", "ref", "alt"])
    df["chrom_norm"] = df["chrom"].map(norm_chrom)
    by_coord: dict[tuple[str, int], list[dict[str, object]]] = {}
    for row in df.itertuples(index=False):
        key = (str(row.chrom_norm), int(row.pos))
        by_coord.setdefault(key, []).append(
            {
                "variant_index": int(row.variant_index),
                "variant_id": str(row.variant_id),
                "chrom": str(row.chrom_norm),
                "pos": int(row.pos),
                "ref": str(row.ref).upper(),
                "alt": str(row.alt).upper(),
            }
        )
    return by_coord, len(df)


def classify_alleles(z_ref: str, z_alt: str, g_ref: str, g_alt: str) -> str:
    if z_ref == g_ref and z_alt == g_alt:
        return "same_ref_alt"
    if z_ref == g_alt and z_alt == g_ref:
        return "swapped_ref_alt"
    if {z_ref, z_alt} == {g_ref, g_alt}:
        return "same_unordered"
    return "allele_mismatch"


def main() -> None:
    args = parse_args()
    g2f_vcf = Path(args.g2f_vcf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    zeamap_by_coord, n_zeamap = load_zeamap(Path(args.zeamap_variants))
    stats = Counter()
    chrom_stats = Counter()
    sample_names: list[str] = []
    matches: list[dict[str, object]] = []
    mismatch_examples: list[dict[str, object]] = []

    with g2f_vcf.open("rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("##"):
                continue
            if line.startswith("#CHROM"):
                fields = line.rstrip("\n").split("\t")
                sample_names = fields[9:]
                stats["g2f_samples"] = len(sample_names)
                continue
            if not line or line.startswith("#"):
                continue
            stats["g2f_variants"] += 1
            fields = line.rstrip("\n").split("\t", 9)
            if len(fields) < 9:
                stats["malformed_variant_lines"] += 1
                continue
            chrom = norm_chrom(fields[0])
            pos = int(fields[1])
            g_ref = fields[3].upper()
            alts = [x.upper() for x in fields[4].split(",")]
            if len(g_ref) != 1 or any(len(x) != 1 for x in alts):
                stats["g2f_non_snv_or_multibase"] += 1
            if len(alts) != 1:
                stats["g2f_multiallelic"] += 1
            key = (chrom, pos)
            chrom_stats[chrom] += 1
            z_variants = zeamap_by_coord.get(key)
            if not z_variants:
                continue
            stats["coord_overlap_g2f_rows"] += 1
            for z in z_variants:
                cls = classify_alleles(str(z["ref"]), str(z["alt"]), g_ref, alts[0])
                stats[f"allele_{cls}"] += 1
                row = {
                    "g2f_chrom": chrom,
                    "g2f_pos": pos,
                    "g2f_ref": g_ref,
                    "g2f_alt": alts[0],
                    "zeamap_variant_index": z["variant_index"],
                    "zeamap_variant_id": z["variant_id"],
                    "zeamap_ref": z["ref"],
                    "zeamap_alt": z["alt"],
                    "match_class": cls,
                }
                if cls in {"same_ref_alt", "swapped_ref_alt"}:
                    matches.append(row)
                elif len(mismatch_examples) < 100:
                    mismatch_examples.append(row)

    match_df = pd.DataFrame(matches)
    mismatch_df = pd.DataFrame(mismatch_examples)
    match_path = out_dir / "g2f_zeamap_variant_matches.tsv"
    mismatch_path = out_dir / "g2f_zeamap_allele_mismatch_examples.tsv"
    match_df.to_csv(match_path, sep="\t", index=False)
    mismatch_df.to_csv(mismatch_path, sep="\t", index=False)

    unique_zeamap_matched = int(match_df["zeamap_variant_index"].nunique()) if not match_df.empty else 0
    summary = {
        "g2f_vcf": str(g2f_vcf),
        "zeamap_variants": str(args.zeamap_variants),
        "n_zeamap_variants": n_zeamap,
        "n_g2f_samples": int(stats["g2f_samples"]),
        "n_g2f_variants": int(stats["g2f_variants"]),
        "n_g2f_coord_overlap_rows": int(stats["coord_overlap_g2f_rows"]),
        "n_exact_ref_alt_matches": int(stats["allele_same_ref_alt"]),
        "n_swapped_ref_alt_matches": int(stats["allele_swapped_ref_alt"]),
        "n_usable_same_or_swapped_matches": len(matches),
        "n_unique_zeamap_variants_matched": unique_zeamap_matched,
        "zeamap_match_fraction": unique_zeamap_matched / n_zeamap if n_zeamap else 0.0,
        "n_allele_mismatch": int(stats["allele_allele_mismatch"]),
        "n_g2f_non_snv_or_multibase": int(stats["g2f_non_snv_or_multibase"]),
        "n_g2f_multiallelic": int(stats["g2f_multiallelic"]),
        "chrom_variant_counts": dict(sorted(chrom_stats.items(), key=lambda x: x[0])),
        "match_table": str(match_path),
        "mismatch_examples": str(mismatch_path),
    }
    (out_dir / "g2f_zeamap_overlap_summary.json").write_text(
        json.dumps(summary, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
