#!/usr/bin/env python3
"""Prepare ZEAMAP v0.1 tensors for deep genotype-to-phenotype models.

This script does not train a model. It only converts the existing processed
dataset into aligned numpy/TSV/JSON files that GPU training scripts can read
without touching the original ZEAMAP files.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_SEEDS = [20260605, 20260606, 20260607, 20260608, 20260609]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--processed-dir", default="data/processed/v0_1")
    parser.add_argument("--results-dir", default="results/v0_1_baseline")
    parser.add_argument("--out-dir", default="data/deep_model/v0_1")
    parser.add_argument("--seeds", default=",".join(str(x) for x in DEFAULT_SEEDS))
    return parser.parse_args()


def parse_seeds(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def make_splits(accessions: pd.Series, seed: int) -> pd.DataFrame:
    """Deterministic accession-level train/val/test split."""
    rng = np.random.default_rng(seed)
    ids = accessions.astype(str).to_numpy()
    order = np.arange(len(ids))
    rng.shuffle(order)
    n = len(ids)
    n_train = int(round(n * 0.70))
    n_val = int(round(n * 0.15))
    split = np.full(n, "test", dtype=object)
    split[order[:n_train]] = "train"
    split[order[n_train : n_train + n_val]] = "val"
    return pd.DataFrame({"accession_id_norm": ids, "split": split, "seed": seed})


def standardize_population(population: pd.DataFrame) -> pd.DataFrame:
    pop = population.copy()
    id_col = "accession_id_norm"
    numeric_cols = [c for c in pop.columns if c != id_col and pd.api.types.is_numeric_dtype(pop[c])]
    out = pop[[id_col] + numeric_cols].copy()
    for col in numeric_cols:
        values = pd.to_numeric(out[col], errors="coerce")
        out[col] = values.fillna(values.median())
    return out


def main() -> None:
    args = parse_args()
    processed = Path(args.processed_dir)
    results = Path(args.results_dir)
    out = Path(args.out_dir)
    out.mkdir(parents=True, exist_ok=True)

    accessions = pd.read_csv(processed / "accessions.tsv", sep="\t")
    accession_ids = accessions["accession_id_norm"].astype(str).tolist()

    phenotype = pd.read_parquet(processed / "phenotype.parquet")
    population = pd.read_parquet(processed / "population.parquet")
    pop_features = standardize_population(population)

    benchmark = pd.read_csv(results / "final_v0_1_trait_benchmark.tsv", sep="\t")
    traits = benchmark["trait"].astype(str).tolist()
    trait_meta = benchmark[
        [
            "trait",
            "trait_family",
            "priority_tier",
            "median_pearson",
            "median_r2",
            "ridge_median_pearson",
            "elasticnet_median_pearson",
            "mlp_median_pearson",
        ]
    ].copy()

    dosage_npz = np.load(processed / "genotype_dosage_int8.npz", allow_pickle=True)
    dosage = dosage_npz["dosage"]
    samples = [str(x) for x in dosage_npz["samples"].tolist()]
    variant_id = [str(x) for x in dosage_npz["variant_id"].tolist()]

    sample_to_idx = {s: i for i, s in enumerate(samples)}
    missing = [x for x in accession_ids if x not in sample_to_idx]
    if missing:
        raise ValueError(f"{len(missing)} accessions are missing from genotype dosage: {missing[:5]}")
    sample_order = np.array([sample_to_idx[x] for x in accession_ids], dtype=np.int64)

    # Stored as variants x samples in v0.1; GPU code expects samples x variants.
    genotype = dosage[:, sample_order].T.astype(np.int8, copy=True)
    np.save(out / "genotype_samples_by_variants.int8.npy", genotype)

    # Values outside 0/1/2 are treated as missing by downstream models.
    genotype_mask = np.isin(genotype, [0, 1, 2])
    np.save(out / "genotype_observed_mask.bool.npy", genotype_mask)

    y_df = phenotype[["accession_id_norm"] + traits].copy()
    y_df = pd.DataFrame({"accession_id_norm": accession_ids}).merge(y_df, on="accession_id_norm", how="left")
    y = y_df[traits].apply(pd.to_numeric, errors="coerce").to_numpy(dtype=np.float32)
    y_mask = np.isfinite(y)
    np.save(out / "phenotype_targets.float32.npy", np.nan_to_num(y, nan=0.0).astype(np.float32))
    np.save(out / "phenotype_observed_mask.bool.npy", y_mask)

    pop_df = pd.DataFrame({"accession_id_norm": accession_ids}).merge(pop_features, on="accession_id_norm", how="left")
    pop_cols = [c for c in pop_df.columns if c != "accession_id_norm"]
    pop_arr = pop_df[pop_cols].to_numpy(dtype=np.float32)
    np.save(out / "population_covariates.float32.npy", pop_arr)

    variant_meta = pd.read_csv(processed / "genotype_variants.tsv", sep="\t")
    variant_meta = variant_meta.copy()
    if "variant_id" not in variant_meta.columns:
        variant_meta.insert(0, "variant_id", variant_id)
    variant_meta.to_csv(out / "variant_metadata.tsv", sep="\t", index=False)

    pd.DataFrame({"accession_id_norm": accession_ids}).to_csv(out / "accessions.tsv", sep="\t", index=False)
    trait_meta.to_csv(out / "traits.tsv", sep="\t", index=False)
    pop_df[["accession_id_norm"] + pop_cols].to_csv(out / "population_covariates.tsv", sep="\t", index=False)

    splits = []
    for seed in parse_seeds(args.seeds):
        splits.append(make_splits(pd.Series(accession_ids), seed))
    split_df = pd.concat(splits, ignore_index=True)
    split_df.to_csv(out / "splits.tsv", sep="\t", index=False)

    manifest = {
        "dataset": "ZEAMAP v0.1 deep model tensor package",
        "n_accessions": len(accession_ids),
        "n_variants": int(genotype.shape[1]),
        "n_traits": len(traits),
        "n_population_covariates": len(pop_cols),
        "genotype_shape_samples_by_variants": list(genotype.shape),
        "phenotype_shape_samples_by_traits": list(y.shape),
        "genotype_value_counts": {str(k): int(v) for k, v in zip(*np.unique(genotype, return_counts=True))},
        "phenotype_observed_fraction": float(y_mask.mean()),
        "seeds": parse_seeds(args.seeds),
        "files": {
            "genotype": "genotype_samples_by_variants.int8.npy",
            "genotype_mask": "genotype_observed_mask.bool.npy",
            "targets": "phenotype_targets.float32.npy",
            "target_mask": "phenotype_observed_mask.bool.npy",
            "population": "population_covariates.float32.npy",
            "accessions": "accessions.tsv",
            "traits": "traits.tsv",
            "splits": "splits.tsv",
            "variants": "variant_metadata.tsv",
        },
    }
    (out / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(manifest, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
