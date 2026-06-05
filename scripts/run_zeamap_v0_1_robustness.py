#!/usr/bin/env python3
"""Run multi-seed robustness checks for ZEAMAP v0.1 selected traits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from run_zeamap_v0_1_baseline import (
    RESULTS,
    V01,
    build_population_features,
    fit_predict_ridge,
    make_splits,
    metric_row,
)


REPORT = Path("docs/2026-06-05-zeamap-v0-1-robustness-report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", type=str, default="20260605,20260606,20260607,20260608,20260609")
    parser.add_argument("--min-train-n", type=int, default=30)
    parser.add_argument("--min-eval-n", type=int, default=10)
    return parser.parse_args()


def parse_seeds(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def run_one_seed(
    seed: int,
    phenotype: pd.DataFrame,
    population: pd.DataFrame,
    selected_traits: list[str],
    feature_sets: dict[str, pd.DataFrame],
    min_train_n: int,
    min_eval_n: int,
) -> pd.DataFrame:
    split = make_splits(population, seed)
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno = phenotype[["accession_id_norm"] + selected_traits].copy()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)
    rows = []

    for trait in selected_traits:
        y = pd.to_numeric(pheno[trait], errors="coerce")
        train_n = int(y[(pheno["split"] == "train")].notna().sum())
        val_n = int(y[(pheno["split"] == "val")].notna().sum())
        test_n = int(y[(pheno["split"] == "test")].notna().sum())
        if train_n < min_train_n or val_n < min_eval_n or test_n < min_eval_n or y.var(skipna=True) <= 0:
            continue

        work = pheno[["accession_id_norm", "split"]].copy()
        work["y"] = y
        train_df = work[(work["split"] == "train") & work["y"].notna()].copy()
        y_train_raw = train_df["y"].to_numpy(dtype=float)
        y_mean = float(y_train_raw.mean())
        y_std = float(y_train_raw.std())
        if y_std <= 0:
            continue
        y_train = (y_train_raw - y_mean) / y_std

        for model_name, features in feature_sets.items():
            merged = work.merge(features, on="accession_id_norm", how="left")
            feature_cols = [c for c in merged.columns if c not in {"accession_id_norm", "split", "y"}]
            train_m = merged[(merged["split"] == "train") & merged["y"].notna()].copy()
            x_train = train_m[feature_cols].to_numpy(dtype=float)
            eval_m = merged[(merged["split"] == "test") & merged["y"].notna()].copy()
            if len(eval_m) < min_eval_n:
                continue
            x_eval = eval_m[feature_cols].to_numpy(dtype=float)
            y_true = eval_m["y"].to_numpy(dtype=float)
            if model_name == "mean_baseline":
                pred = np.full(len(y_true), y_mean)
            else:
                pred_scaled = fit_predict_ridge(x_train, y_train, x_eval)
                pred = pred_scaled * y_std + y_mean
            row = {
                "seed": seed,
                "trait": trait,
                "model": model_name,
                "split": "test",
                "train_non_missing": train_n,
                "val_non_missing": val_n,
                "test_non_missing": test_n,
            }
            row.update(metric_row(y_true, pred))
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(metrics: pd.DataFrame, selected: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    if "priority_tier" not in selected.columns:
        gp_pearson = "pearson__genotype_pca_population_ridge"
        gp_r2 = "r2__genotype_pca_population_ridge"
        selected = selected.copy()
        selected["priority_tier"] = np.select(
            [
                (selected[gp_pearson] >= 0.70) & (selected[gp_r2] >= 0.45),
                (selected[gp_pearson] >= 0.50) & (selected[gp_r2] >= 0.20),
            ],
            ["high", "medium"],
            default="watch",
        )
    model_summary = (
        metrics.groupby("model", dropna=False)
        .agg(
            seeds=("seed", "nunique"),
            traits_evaluated=("trait", "nunique"),
            median_r2=("r2", "median"),
            mean_r2=("r2", "mean"),
            median_pearson=("pearson", "median"),
            mean_pearson=("pearson", "mean"),
            positive_r2_fraction=("r2", lambda x: float((x > 0).mean())),
            pearson_gt_0_3_fraction=("pearson", lambda x: float((x > 0.3).mean())),
        )
        .reset_index()
        .sort_values(["median_pearson", "median_r2"], ascending=False)
    )

    target = metrics[metrics["model"] == "genotype_pca_population_ridge"].copy()
    trait_summary = (
        target.groupby("trait", dropna=False)
        .agg(
            seeds_evaluated=("seed", "nunique"),
            mean_pearson=("pearson", "mean"),
            median_pearson=("pearson", "median"),
            sd_pearson=("pearson", "std"),
            min_pearson=("pearson", "min"),
            mean_r2=("r2", "mean"),
            median_r2=("r2", "median"),
            sd_r2=("r2", "std"),
            min_r2=("r2", "min"),
            positive_r2_seeds=("r2", lambda x: int((x > 0).sum())),
            pearson_gt_0_3_seeds=("pearson", lambda x: int((x > 0.3).sum())),
        )
        .reset_index()
    )
    trait_summary = trait_summary.merge(
        selected[["trait", "trait_family", "priority_tier"]], on="trait", how="left"
    )
    trait_summary["robust_selected"] = (
        (trait_summary["seeds_evaluated"] >= 5)
        & (trait_summary["median_pearson"] >= 0.3)
        & (trait_summary["median_r2"] > 0)
        & (trait_summary["positive_r2_seeds"] >= 4)
        & (trait_summary["pearson_gt_0_3_seeds"] >= 4)
    )
    trait_summary = trait_summary.sort_values(["robust_selected", "median_pearson", "median_r2"], ascending=False)

    robust = trait_summary[trait_summary["robust_selected"]].copy()
    return model_summary, trait_summary, robust


def write_report(seeds: list[int], model_summary: pd.DataFrame, trait_summary: pd.DataFrame, robust: pd.DataFrame) -> None:
    family_summary = (
        robust.groupby("trait_family", dropna=False)
        .agg(
            robust_traits=("trait", "count"),
            median_pearson=("median_pearson", "median"),
            median_r2=("median_r2", "median"),
        )
        .reset_index()
        .sort_values(["robust_traits", "median_pearson"], ascending=False)
    )
    top10 = robust[
        [
            "trait",
            "trait_family",
            "priority_tier",
            "median_pearson",
            "min_pearson",
            "median_r2",
            "min_r2",
            "positive_r2_seeds",
            "pearson_gt_0_3_seeds",
        ]
    ].head(10)
    report = f"""# ZEAMAP v0.1 multi-seed robustness report

日期：2026-06-05

## Setup

- Seeds: {", ".join(map(str, seeds))}
- Traits tested: {trait_summary["trait"].nunique()}
- Models: mean, population ridge, genotype PCA ridge, genotype PCA + population ridge
- Genotype PCA is fixed from `data/processed/v0_1/genotype_pca.tsv`; this checks split robustness, not PCA refitting robustness.

## Model Summary

```text
{model_summary.to_string(index=False)}
```

## Robust Trait Rule

For `genotype_pca_population_ridge`:

- evaluated in all 5 seeds
- median Pearson >= 0.3
- median R2 > 0
- positive R2 in at least 4 seeds
- Pearson > 0.3 in at least 4 seeds

## Robust Traits

- robust selected traits: {len(robust)}

```text
{family_summary.to_string(index=False)}
```

## Top 10 Robust Traits

```text
{top10.to_string(index=False)}
```

## Interpretation

- Robust traits are the preferred target set for lightweight MLP, ElasticNet comparison, and later methylation subset experiments.
- Traits that passed single-split selection but failed robustness should remain watch-list traits, not primary model targets.

## Outputs

- `results/v0_1_baseline/robustness_metrics.tsv`
- `results/v0_1_baseline/robustness_model_summary.tsv`
- `results/v0_1_baseline/robustness_trait_summary.tsv`
- `results/v0_1_baseline/robust_selected_traits.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    selected = pd.read_csv(RESULTS / "selected_traits.tsv", sep="\t")
    selected_traits = selected["trait"].astype(str).tolist()

    pop_features = build_population_features(population)
    pca_features = pd.read_csv(V01 / "genotype_pca.tsv", sep="\t")
    mean_feature = pd.DataFrame({"accession_id_norm": pca_features["accession_id_norm"].astype(str), "constant": 1.0})
    geno_pop = pca_features.merge(pop_features, on="accession_id_norm", how="left")
    feature_sets = {
        "mean_baseline": mean_feature,
        "population_ridge": pop_features,
        "genotype_pca_ridge": pca_features,
        "genotype_pca_population_ridge": geno_pop,
    }

    metrics = pd.concat(
        [
            run_one_seed(seed, phenotype, population, selected_traits, feature_sets, args.min_train_n, args.min_eval_n)
            for seed in seeds
        ],
        ignore_index=True,
    )
    model_summary, trait_summary, robust = summarize(metrics, selected)

    RESULTS.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(RESULTS / "robustness_metrics.tsv", sep="\t", index=False)
    model_summary.to_csv(RESULTS / "robustness_model_summary.tsv", sep="\t", index=False)
    trait_summary.to_csv(RESULTS / "robustness_trait_summary.tsv", sep="\t", index=False)
    robust.to_csv(RESULTS / "robust_selected_traits.tsv", sep="\t", index=False)
    (RESULTS / "robustness_run_config.json").write_text(
        json.dumps({"seeds": seeds, "min_train_n": args.min_train_n, "min_eval_n": args.min_eval_n}, indent=2),
        encoding="utf-8",
    )
    write_report(seeds, model_summary, trait_summary, robust)


if __name__ == "__main__":
    main()
