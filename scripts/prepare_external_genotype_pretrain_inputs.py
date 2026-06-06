#!/usr/bin/env python3
"""Prepare external maize genotype files for masked-genotype pretraining.

Current scope:
- read the inventory produced by inspect_external_genotype_downloads.py;
- fail clearly if no usable external genotype files are present;
- write a pretraining plan JSON that downstream conversion code can consume.

The actual VCF/HapMap-to-window-tensor converter will be implemented after the
G2F/Panzea files are downloaded and inspected, because their exact formats and
coordinate builds determine the safest parser.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", default="data/external/external_genotype_inventory.tsv")
    parser.add_argument("--zeamap-variants", default="data/deep_model/v0_1/variant_metadata.tsv")
    parser.add_argument("--out-dir", default="data/deep_model/external_pretrain_v0")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    inventory_path = Path(args.inventory)
    zeamap_variants_path = Path(args.zeamap_variants)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not inventory_path.exists():
        raise SystemExit(
            f"Inventory not found: {inventory_path}. Run scripts/inspect_external_genotype_downloads.py first."
        )
    if not zeamap_variants_path.exists():
        raise SystemExit(f"ZEAMAP variant metadata not found: {zeamap_variants_path}")

    inventory = pd.read_csv(inventory_path, sep="\t")
    usable = inventory[inventory["usable_for_pretraining"].astype(str).str.lower() == "true"].copy()
    zeamap_variants = pd.read_csv(zeamap_variants_path, sep="\t", usecols=["chrom", "pos", "variant_id", "ref", "alt"])

    plan = {
        "status": "blocked_until_external_genotypes_available" if usable.empty else "ready_for_parser_implementation",
        "inventory": str(inventory_path),
        "n_inventory_files": int(len(inventory)),
        "n_usable_files": int(len(usable)),
        "usable_files": usable["path"].astype(str).tolist(),
        "zeamap_variant_reference": str(zeamap_variants_path),
        "n_zeamap_variants": int(len(zeamap_variants)),
        "required_next_parser_steps": [
            "confirm genome coordinate build for each external genotype file",
            "parse sample/accession identifiers",
            "parse variant chrom/pos/ref/alt and genotype calls",
            "intersect or liftover variants to ZEAMAP/B73 coordinate space",
            "encode genotype calls as 0/1/2/3 int8 windows",
            "write external genotype tensor and manifest for pretraining",
        ],
    }

    (out_dir / "external_pretrain_plan.json").write_text(json.dumps(plan, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(plan, indent=2, ensure_ascii=False))

    if usable.empty:
        raise SystemExit("No usable external genotype files found yet. Download G2F/Panzea genotype files first.")


if __name__ == "__main__":
    main()
