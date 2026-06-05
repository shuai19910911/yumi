#!/usr/bin/env python3
"""Prepare GEMMA BIMBAM inputs for ZEAMAP v0.1 paper-level MLM GWAS."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_zeamap_v0_1_baseline import RESULTS, V01


OUT = V01 / "gemma_gwas_v0_1"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trait-family", default="oil")
    parser.add_argument("--priority-tier", default="high")
    parser.add_argument("--max-traits", type=int, default=10)
    parser.add_argument("--covariates", default="PC1,PC2,PC3,K1,K2,K3")
    return parser.parse_args()


def target_traits(args: argparse.Namespace) -> list[str]:
    final = pd.read_csv(RESULTS / "final_v0_1_trait_benchmark.tsv", sep="\t")
    selected = final[(final["trait_family"] == args.trait_family) & (final["priority_tier"] == args.priority_tier)].copy()
    if selected.empty:
        selected = final[final["trait_family"] == args.trait_family].copy()
    return selected.sort_values(["ridge_median_pearson", "ridge_median_r2"], ascending=False)["trait"].head(args.max_traits).tolist()


def write_bimbam(dosage: np.ndarray, variants: pd.DataFrame, samples: pd.DataFrame, path: Path) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for i, row in variants.iterrows():
            geno = dosage[i, :].astype(np.float32)
            missing = geno < 0
            if missing.any():
                valid = geno[~missing]
                fill = float(valid.mean()) if len(valid) else 0.0
                geno[missing] = fill
            geno_text = "\t".join(f"{x:.4f}" for x in geno)
            handle.write(f"{row.variant_id}\t{row.alt}\t{row.ref}\t{geno_text}\n")


def main() -> None:
    args = parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    traits = target_traits(args)

    npz = np.load(V01 / "genotype_dosage_int8.npz", allow_pickle=False)
    dosage = npz["dosage"]
    samples = pd.read_csv(V01 / "genotype_samples.tsv", sep="\t")
    variants = pd.read_csv(V01 / "genotype_variants.tsv", sep="\t")
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t").set_index("accession_id_norm")
    population = pd.read_csv(V01 / "population.tsv", sep="\t").set_index("accession_id_norm")
    sample_ids = samples["accession_id_norm"].astype(str)

    bimbam = OUT / "zeamap_v0_1_filtered_snps.bimbam.txt"
    if not bimbam.exists():
        write_bimbam(dosage, variants, samples, bimbam)

    annotation = variants[["variant_id", "pos", "chrom"]].copy()
    annotation.to_csv(OUT / "zeamap_v0_1_filtered_snps.annotation.txt", sep="\t", index=False, header=False)
    samples[["accession_id_norm"]].to_csv(OUT / "samples.txt", sep="\t", index=False, header=False)

    cov_cols = [x.strip() for x in args.covariates.split(",") if x.strip()]
    cov = population.reindex(sample_ids)[cov_cols].apply(pd.to_numeric, errors="coerce")
    cov = cov.fillna(cov.median())
    cov.insert(0, "intercept", 1.0)
    cov.to_csv(OUT / "covariates.txt", sep="\t", index=False, header=False)

    pheno_manifest = []
    for trait in traits:
        y = phenotype.reindex(sample_ids)[trait]
        pheno_name = trait.replace("/", "_").replace(":", "_")
        pheno_path = OUT / f"{pheno_name}.phenotype.txt"
        y.to_csv(pheno_path, sep="\t", index=False, header=False, na_rep="NA")
        pheno_manifest.append(
            {
                "trait": trait,
                "phenotype_file": pheno_path.name,
                "non_missing": int(y.notna().sum()),
            }
        )
    pd.DataFrame(pheno_manifest).to_csv(OUT / "phenotype_manifest.tsv", sep="\t", index=False)
    (OUT / "gemma_input_config.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
