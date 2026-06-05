#!/usr/bin/env python3
"""Build methylation region summary features and test them on robust traits."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_zeamap_v0_1_baseline import RESULTS, V01, fit_predict_ridge, make_splits, metric_row
from run_zeamap_v0_1_baseline import build_population_features


LOCAL_ROOT = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP")
METH_ROOT = LOCAL_ROOT / "epigenome/dna_methylation/01_regions"
REPORT = Path("docs/2026-06-05-zeamap-v0-1-methylation-subset-report.md")
FEATURE_PATH = V01 / "methylation_region_summary.tsv"

CONTEXT_DIRS = {
    "mCG": METH_ROOT / "AMP_mCG_bed",
    "mCHG": METH_ROOT / "AMP_mCHG_bed",
    "mCHH": METH_ROOT / "AMP_mCHH_bed",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="20260605,20260606,20260607,20260608,20260609")
    parser.add_argument("--force-rebuild-features", action="store_true")
    parser.add_argument("--min-train-n", type=int, default=25)
    parser.add_argument("--min-eval-n", type=int, default=8)
    return parser.parse_args()


def parse_seeds(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def summarize_bedgraph(path: Path, context: str) -> dict[str, float | int | str]:
    values = []
    lengths = []
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if not line.strip():
                continue
            chrom, start, end, value = line.rstrip("\n").split("\t")[:4]
            start_i = int(start)
            end_i = int(end)
            val = float(value)
            values.append(val)
            lengths.append(max(0, end_i - start_i))
    arr = np.array(values, dtype=float)
    lens = np.array(lengths, dtype=float)
    if len(arr) == 0:
        weighted = np.nan
    else:
        weighted = float(np.average(arr, weights=np.maximum(lens, 1)))
    return {
        "accession_id_norm": path.name.replace(".bedgraph.gz", "").upper(),
        f"{context}_region_count": int(len(arr)),
        f"{context}_mean": float(np.mean(arr)) if len(arr) else np.nan,
        f"{context}_median": float(np.median(arr)) if len(arr) else np.nan,
        f"{context}_weighted_mean": weighted,
        f"{context}_zero_fraction": float((arr <= 0.001).mean()) if len(arr) else np.nan,
        f"{context}_high_fraction": float((arr >= 0.8).mean()) if len(arr) else np.nan,
        f"{context}_total_bp": float(lens.sum()) if len(arr) else 0.0,
    }


def build_methylation_features(force: bool = False) -> pd.DataFrame:
    if FEATURE_PATH.exists() and not force:
        return pd.read_csv(FEATURE_PATH, sep="\t")
    frames = []
    for context, directory in CONTEXT_DIRS.items():
        rows = [summarize_bedgraph(path, context) for path in sorted(directory.glob("*.bedgraph.gz"))]
        frames.append(pd.DataFrame(rows))
    merged = frames[0]
    for frame in frames[1:]:
        merged = merged.merge(frame, on="accession_id_norm", how="outer")
    merged.to_csv(FEATURE_PATH, sep="\t", index=False)
    return merged


def run_seed(
    seed: int,
    phenotype: pd.DataFrame,
    population: pd.DataFrame,
    robust_traits: list[str],
    base_features: pd.DataFrame,
    methyl_features: pd.DataFrame,
    methyl_ids: set[str],
    min_train_n: int,
    min_eval_n: int,
) -> pd.DataFrame:
    population_sub = population[population["accession_id_norm"].isin(methyl_ids)].copy()
    split = make_splits(population_sub, seed)
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno = phenotype[phenotype["accession_id_norm"].isin(methyl_ids)][["accession_id_norm"] + robust_traits].copy()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)
    feature_sets = {
        "genotype_population_ridge": base_features[base_features["accession_id_norm"].isin(methyl_ids)],
        "genotype_population_methylation_ridge": base_features.merge(methyl_features, on="accession_id_norm", how="inner"),
    }
    rows = []
    for trait in robust_traits:
        y = pd.to_numeric(pheno[trait], errors="coerce")
        train_n = int(y[(pheno["split"] == "train")].notna().sum())
        test_n = int(y[(pheno["split"] == "test")].notna().sum())
        if train_n < min_train_n or test_n < min_eval_n or y.var(skipna=True) <= 0:
            continue
        work = pheno[["accession_id_norm", "split"]].copy()
        work["y"] = y
        train_df = work[(work["split"] == "train") & work["y"].notna()]
        y_train_raw = train_df["y"].to_numpy(dtype=float)
        y_mean = float(y_train_raw.mean())
        y_std = float(y_train_raw.std())
        if y_std <= 0:
            continue
        y_train = (y_train_raw - y_mean) / y_std
        for model_name, features in feature_sets.items():
            merged = work.merge(features, on="accession_id_norm", how="inner")
            feature_cols = [c for c in merged.columns if c not in {"accession_id_norm", "split", "y"}]
            train_m = merged[(merged["split"] == "train") & merged["y"].notna()]
            test_m = merged[(merged["split"] == "test") & merged["y"].notna()]
            if len(train_m) < min_train_n or len(test_m) < min_eval_n:
                continue
            x_train = train_m[feature_cols].to_numpy(dtype=float)
            x_test = test_m[feature_cols].to_numpy(dtype=float)
            y_true = test_m["y"].to_numpy(dtype=float)
            pred_scaled = fit_predict_ridge(x_train, y_train, x_test)
            pred = pred_scaled * y_std + y_mean
            row = {
                "seed": seed,
                "trait": trait,
                "model": model_name,
                "split": "test",
                "train_non_missing": train_n,
                "test_non_missing": test_n,
            }
            row.update(metric_row(y_true, pred))
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    model_summary = (
        metrics.groupby("model")
        .agg(
            seeds=("seed", "nunique"),
            traits_evaluated=("trait", "nunique"),
            median_r2=("r2", "median"),
            mean_r2=("r2", "mean"),
            median_pearson=("pearson", "median"),
            mean_pearson=("pearson", "mean"),
            positive_r2_fraction=("r2", lambda x: float((x > 0).mean())),
        )
        .reset_index()
        .sort_values(["median_pearson", "median_r2"], ascending=False)
    )
    wide = metrics.pivot_table(index=["trait", "seed"], columns="model", values=["pearson", "r2"], aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    wide["pearson_gain_methylation"] = (
        wide["pearson__genotype_population_methylation_ridge"] - wide["pearson__genotype_population_ridge"]
    )
    wide["r2_gain_methylation"] = wide["r2__genotype_population_methylation_ridge"] - wide["r2__genotype_population_ridge"]
    trait_summary = (
        wide.groupby("trait")
        .agg(
            median_pearson_gain=("pearson_gain_methylation", "median"),
            mean_pearson_gain=("pearson_gain_methylation", "mean"),
            median_r2_gain=("r2_gain_methylation", "median"),
            mean_r2_gain=("r2_gain_methylation", "mean"),
            methylation_better_pearson_seeds=("pearson_gain_methylation", lambda x: int((x > 0).sum())),
            methylation_better_r2_seeds=("r2_gain_methylation", lambda x: int((x > 0).sum())),
        )
        .reset_index()
        .sort_values(["median_pearson_gain", "median_r2_gain"], ascending=False)
    )
    return model_summary, trait_summary


def write_report(
    seeds: list[int],
    methyl_features: pd.DataFrame,
    methyl_ids: set[str],
    metrics: pd.DataFrame,
    model_summary: pd.DataFrame,
    trait_summary: pd.DataFrame,
) -> None:
    top_gain = trait_summary.head(10)
    report = f"""# ZEAMAP v0.1 methylation subset experiment

日期：2026-06-05

## Setup

- Methylation source: DNA methylation `01_regions` bedgraph files
- Contexts: mCG, mCHG, mCHH
- Features per accession: region count, mean, median, length-weighted mean, zero fraction, high fraction, total bp
- Methylation-covered accessions in feature table: {len(methyl_features)}
- Methylation-covered v0.1 accessions used: {len(methyl_ids)}
- Traits: 66 robust selected traits
- Seeds: {", ".join(map(str, seeds))}

## Model Summary

```text
{model_summary.to_string(index=False)}
```

## Top 10 Trait Gains From Methylation Summary

```text
{top_gain.to_string(index=False)}
```

## Interpretation

- This is a coarse accession-level methylation summary test, not a gene/promoter methylation model.
- If global methylation summaries do not improve over genotype+population, the next useful methylation step should be gene/promoter/cis-window aggregation, not larger models.

## Outputs

- `data/processed/v0_1/methylation_region_summary.tsv`
- `results/v0_1_baseline/methylation_subset_metrics.tsv`
- `results/v0_1_baseline/methylation_subset_model_summary.tsv`
- `results/v0_1_baseline/methylation_subset_trait_summary.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    methyl = build_methylation_features(args.force_rebuild_features)
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    pca = pd.read_csv(V01 / "genotype_pca.tsv", sep="\t")
    pop = build_population_features(population)
    base = pca.merge(pop, on="accession_id_norm", how="left")
    robust = pd.read_csv(RESULTS / "robust_selected_traits.tsv", sep="\t")
    robust_traits = robust["trait"].astype(str).tolist()
    mask = pd.read_csv(V01 / "modality_mask.tsv", sep="\t")
    methyl_ids = set(mask.loc[mask["has_any_methylation"].astype(bool), "accession_id_norm"].astype(str))
    methyl_ids &= set(methyl["accession_id_norm"].astype(str))
    methyl = methyl[methyl["accession_id_norm"].isin(methyl_ids)].copy()
    feature_cols = [c for c in methyl.columns if c != "accession_id_norm"]
    methyl[feature_cols] = methyl[feature_cols].fillna(methyl[feature_cols].median())

    metrics = pd.concat(
        [
            run_seed(seed, phenotype, population, robust_traits, base, methyl, methyl_ids, args.min_train_n, args.min_eval_n)
            for seed in seeds
        ],
        ignore_index=True,
    )
    model_summary, trait_summary = summarize(metrics)
    metrics.to_csv(RESULTS / "methylation_subset_metrics.tsv", sep="\t", index=False)
    model_summary.to_csv(RESULTS / "methylation_subset_model_summary.tsv", sep="\t", index=False)
    trait_summary.to_csv(RESULTS / "methylation_subset_trait_summary.tsv", sep="\t", index=False)
    (RESULTS / "methylation_subset_run_config.json").write_text(
        json.dumps({"seeds": seeds, "min_train_n": args.min_train_n, "min_eval_n": args.min_eval_n}, indent=2),
        encoding="utf-8",
    )
    write_report(seeds, methyl, methyl_ids, metrics, model_summary, trait_summary)


if __name__ == "__main__":
    main()
