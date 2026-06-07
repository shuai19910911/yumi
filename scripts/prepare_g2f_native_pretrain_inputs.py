#!/usr/bin/env python3
"""Build a genotype-only pretraining tensor from the native G2F VCF.

This intentionally keeps G2F in its own B73 v5 marker space. Direct marker
alignment to ZEAMAP AGPv4 is not usable, so transfer should be done by loading
shape-compatible encoder weights rather than by intersecting SNP columns.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--vcf", default="data/external/g2f/genotypic_2014_2023/inbreds_G2F_2014-2023_437k.vcf")
    parser.add_argument("--out-dir", default="data/deep_model/external_pretrain_v0/g2f_native_b73v5")
    parser.add_argument("--split-seed", type=int, default=20260605)
    parser.add_argument("--train-frac", type=float, default=0.80)
    parser.add_argument("--val-frac", type=float, default=0.10)
    parser.add_argument("--chunk-variants", type=int, default=512)
    parser.add_argument("--max-variants", type=int, default=0, help="Optional small-run limit for testing.")
    return parser.parse_args()


def parse_header_and_count(vcf: Path) -> tuple[list[str], int]:
    samples: list[str] = []
    n_variants = 0
    with vcf.open("rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#CHROM"):
                samples = line.rstrip("\n").split("\t")[9:]
                continue
            if not line.startswith("#"):
                n_variants += 1
    if not samples:
        raise ValueError(f"VCF header with samples was not found: {vcf}")
    return samples, n_variants


def encode_gt(value: str) -> int:
    gt = value.split(":", 1)[0]
    if gt in {"0/0", "0|0"}:
        return 0
    if gt in {"0/1", "1/0", "0|1", "1|0"}:
        return 1
    if gt in {"1/1", "1|1"}:
        return 2
    return 3


def write_splits(samples: list[str], out_dir: Path, seed: int, train_frac: float, val_frac: float) -> None:
    rng = np.random.default_rng(seed)
    order = np.arange(len(samples))
    rng.shuffle(order)
    n_train = int(round(len(samples) * train_frac))
    n_val = int(round(len(samples) * val_frac))
    split = np.full(len(samples), "test", dtype=object)
    split[order[:n_train]] = "train"
    split[order[n_train : n_train + n_val]] = "val"
    pd.DataFrame(
        {
            "accession_id_norm": samples,
            "split": split,
            "seed": int(seed),
        }
    ).to_csv(out_dir / "splits.tsv", sep="\t", index=False)


def flush_chunk(
    matrix: np.memmap,
    chunk: list[list[int]],
    start_variant: int,
) -> int:
    if not chunk:
        return start_variant
    block = np.asarray(chunk, dtype=np.int8)
    end_variant = start_variant + block.shape[0]
    matrix[:, start_variant:end_variant] = block.T
    return end_variant


def main() -> None:
    args = parse_args()
    vcf = Path(args.vcf)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    samples, n_variants_full = parse_header_and_count(vcf)
    n_variants = min(n_variants_full, int(args.max_variants)) if int(args.max_variants) > 0 else n_variants_full
    n_samples = len(samples)
    tmp_matrix = out_dir / "genotype_samples_by_variants.int8.npy.tmp"
    final_matrix = out_dir / "genotype_samples_by_variants.int8.npy"
    matrix = np.lib.format.open_memmap(
        tmp_matrix,
        mode="w+",
        dtype=np.int8,
        shape=(n_samples, n_variants),
    )

    variant_rows: list[dict[str, object]] = []
    chunk: list[list[int]] = []
    variant_index = 0
    written_until = 0
    genotype_counts = np.zeros(4, dtype=np.int64)
    multiallelic_variants = 0

    with vcf.open("rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            if variant_index >= n_variants:
                break
            fields = line.rstrip("\n").split("\t")
            if len(fields) < 10:
                raise ValueError(f"Malformed VCF line at variant {variant_index + 1}")
            alt = fields[4]
            if "," in alt:
                multiallelic_variants += 1
            encoded = [encode_gt(x) for x in fields[9:]]
            if len(encoded) != n_samples:
                raise ValueError(
                    f"Variant {variant_index} has {len(encoded)} sample calls, expected {n_samples}"
                )
            counts = np.bincount(np.asarray(encoded, dtype=np.int8), minlength=4)
            genotype_counts += counts[:4]
            chunk.append(encoded)
            variant_rows.append(
                {
                    "variant_index": variant_index,
                    "chrom": fields[0],
                    "pos": int(fields[1]),
                    "variant_id": fields[2],
                    "ref": fields[3],
                    "alt": alt,
                    "source": "G2F_2014_2023_native_B73v5",
                }
            )
            variant_index += 1
            if len(chunk) >= int(args.chunk_variants):
                written_until = flush_chunk(matrix, chunk, written_until)
                chunk = []
                matrix.flush()
                if written_until % 51200 == 0:
                    print(json.dumps({"written_variants": written_until, "total_variants": n_variants}), flush=True)

    written_until = flush_chunk(matrix, chunk, written_until)
    matrix.flush()
    if written_until != n_variants:
        raise ValueError(f"Wrote {written_until} variants, expected {n_variants}")
    tmp_matrix.replace(final_matrix)

    pd.DataFrame({"accession_id_norm": samples}).to_csv(out_dir / "accessions.tsv", sep="\t", index=False)
    pd.DataFrame(variant_rows).to_csv(out_dir / "variant_metadata.tsv", sep="\t", index=False)
    np.save(out_dir / "phenotype_targets.float32.npy", np.zeros((n_samples, 1), dtype=np.float32))
    np.save(out_dir / "phenotype_observed_mask.bool.npy", np.zeros((n_samples, 1), dtype=bool))
    np.save(out_dir / "population_covariates.float32.npy", np.zeros((n_samples, 1), dtype=np.float32))
    write_splits(samples, out_dir, int(args.split_seed), float(args.train_frac), float(args.val_frac))

    manifest = {
        "dataset": "G2F 2014-2023 native genotype pretraining package",
        "vcf": str(vcf),
        "genome_build": "B73 v5 / G2F PHG marker space",
        "n_samples": n_samples,
        "n_variants": n_variants,
        "n_variants_full_vcf": n_variants_full,
        "max_variants_limit": int(args.max_variants),
        "matrix": str(final_matrix),
        "genotype_encoding": {
            "0": "homozygous reference",
            "1": "heterozygous",
            "2": "homozygous alternate",
            "3": "missing, multiallelic non-0/1 allele, or unsupported genotype",
        },
        "genotype_call_counts": {
            "0": int(genotype_counts[0]),
            "1": int(genotype_counts[1]),
            "2": int(genotype_counts[2]),
            "3": int(genotype_counts[3]),
        },
        "n_multiallelic_variant_rows": int(multiallelic_variants),
        "split_seed": int(args.split_seed),
        "note": "Do not directly align this tensor to ZEAMAP AGPv4 SNP columns; transfer only shape-compatible model weights.",
    }
    (out_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(manifest, indent=2, ensure_ascii=False), flush=True)


if __name__ == "__main__":
    main()
