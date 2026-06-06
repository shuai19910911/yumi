#!/usr/bin/env python3
"""Inspect externally downloaded maize genotype files before ingestion.

This script is intentionally conservative. It does not transform data. It only
walks a download directory, records file sizes, detects likely genotype formats,
and extracts lightweight metadata such as VCF sample counts.
"""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path


GENOTYPE_SUFFIXES = (
    ".vcf",
    ".vcf.gz",
    ".hmp",
    ".hmp.txt",
    ".hmp.txt.gz",
    ".hapmap",
    ".hapmap.gz",
    ".txt",
    ".txt.gz",
    ".tsv",
    ".tsv.gz",
    ".csv",
    ".csv.gz",
    ".zip",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", default="data/external")
    parser.add_argument("--out-tsv", default="data/external/external_genotype_inventory.tsv")
    parser.add_argument("--out-json", default="data/external/external_genotype_inventory.json")
    parser.add_argument("--max-header-lines", type=int, default=2000)
    return parser.parse_args()


def open_text(path: Path):
    if path.suffix == ".gz":
        return gzip.open(path, "rt", encoding="utf-8", errors="replace")
    return path.open("rt", encoding="utf-8", errors="replace")


def detect_format(path: Path) -> str:
    name = path.name.lower()
    if name.endswith(".vcf") or name.endswith(".vcf.gz"):
        return "vcf"
    if ".hmp" in name or "hapmap" in name:
        return "hapmap"
    if name.endswith(".zip"):
        return "archive_zip"
    if name.endswith(".csv") or name.endswith(".csv.gz"):
        return "csv_or_genotype_table"
    if name.endswith(".tsv") or name.endswith(".tsv.gz"):
        return "tsv_or_genotype_table"
    if name.endswith(".txt") or name.endswith(".txt.gz"):
        return "txt_or_genotype_table"
    return "unknown"


def inspect_vcf(path: Path, max_header_lines: int) -> dict[str, object]:
    meta_lines = 0
    chrom_header = ""
    n_samples = None
    first_variant = ""
    with open_text(path) as handle:
        for i, line in enumerate(handle):
            if i >= max_header_lines and not chrom_header:
                break
            line = line.rstrip("\n")
            if line.startswith("##"):
                meta_lines += 1
                continue
            if line.startswith("#CHROM"):
                chrom_header = line
                fields = line.split("\t")
                n_samples = max(0, len(fields) - 9)
                continue
            if not line.startswith("#"):
                first_variant = line[:300]
                break
    return {
        "vcf_meta_lines": meta_lines,
        "vcf_has_chrom_header": bool(chrom_header),
        "vcf_n_samples": n_samples,
        "first_variant_preview": first_variant,
    }


def inspect_text_table(path: Path, max_header_lines: int) -> dict[str, object]:
    first_nonempty = ""
    delimiter = "unknown"
    n_columns = None
    with open_text(path) as handle:
        for i, line in enumerate(handle):
            if i >= max_header_lines:
                break
            line = line.rstrip("\n")
            if not line:
                continue
            first_nonempty = line[:300]
            if "\t" in line:
                delimiter = "tab"
                n_columns = len(line.split("\t"))
            elif "," in line:
                delimiter = "comma"
                n_columns = len(line.split(","))
            else:
                delimiter = "space_or_other"
                n_columns = len(line.split())
            break
    return {
        "table_delimiter_guess": delimiter,
        "table_n_columns_guess": n_columns,
        "first_line_preview": first_nonempty,
    }


def inspect_file(path: Path, root: Path, max_header_lines: int) -> dict[str, object]:
    fmt = detect_format(path)
    auxiliary = looks_like_auxiliary(path)
    item: dict[str, object] = {
        "path": str(path),
        "relative_path": str(path.relative_to(root)),
        "size_bytes": path.stat().st_size,
        "format_guess": fmt,
        "auxiliary_file": auxiliary,
        "usable_for_pretraining": (not auxiliary)
        and fmt in {"vcf", "hapmap", "csv_or_genotype_table", "tsv_or_genotype_table", "txt_or_genotype_table"},
    }
    try:
        if fmt == "vcf":
            item.update(inspect_vcf(path, max_header_lines))
        elif fmt in {"hapmap", "csv_or_genotype_table", "tsv_or_genotype_table", "txt_or_genotype_table"}:
            item.update(inspect_text_table(path, max_header_lines))
    except Exception as exc:  # noqa: BLE001 - inventory should continue across damaged files.
        item["inspect_error"] = repr(exc)
    return item


def is_candidate(path: Path) -> bool:
    name = path.name.lower()
    if name.startswith("external_genotype_inventory"):
        return False
    if name == "resource_manifest.tsv" or name.endswith(".blocked.html"):
        return False
    return any(name.endswith(suffix) for suffix in GENOTYPE_SUFFIXES)


def looks_like_auxiliary(path: Path) -> bool:
    text = str(path).lower()
    auxiliary_terms = (
        "liftover",
        "lift_over",
        "chain",
        "b73v4_to_b73v5",
        "b73v5_to_b73v4",
        "readme",
        "metadata",
        "manifest",
        "key_inbreds",
    )
    return any(term in text for term in auxiliary_terms)


def main() -> None:
    args = parse_args()
    root = Path(args.root)
    root.mkdir(parents=True, exist_ok=True)
    files = [p for p in root.rglob("*") if p.is_file() and is_candidate(p)]
    inventory = [inspect_file(p, root, args.max_header_lines) for p in sorted(files)]

    out_tsv = Path(args.out_tsv)
    out_json = Path(args.out_json)
    out_tsv.parent.mkdir(parents=True, exist_ok=True)
    out_json.parent.mkdir(parents=True, exist_ok=True)

    keys = sorted({k for item in inventory for k in item})
    with out_tsv.open("w", encoding="utf-8") as handle:
        handle.write("\t".join(keys) + "\n")
        for item in inventory:
            handle.write("\t".join(str(item.get(k, "")) for k in keys) + "\n")
    out_json.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    summary = {
        "root": str(root),
        "n_candidate_files": len(inventory),
        "total_candidate_size_bytes": sum(int(x["size_bytes"]) for x in inventory),
        "formats": {},
        "out_tsv": str(out_tsv),
        "out_json": str(out_json),
    }
    for item in inventory:
        fmt = str(item["format_guess"])
        summary["formats"][fmt] = summary["formats"].get(fmt, 0) + 1
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
