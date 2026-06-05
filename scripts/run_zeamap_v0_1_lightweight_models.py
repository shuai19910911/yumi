#!/usr/bin/env python3
"""Compare lightweight models on ZEAMAP v0.1 robust traits."""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.exceptions import ConvergenceWarning
from sklearn.linear_model import ElasticNetCV, RidgeCV
from sklearn.neural_network import MLPRegressor
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from run_zeamap_v0_1_baseline import RESULTS, V01, build_population_features, make_splits, metric_row


REPORT = Path("docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seeds", default="20260605,20260606,20260607,20260608,20260609")
    parser.add_argument("--min-train-n", type=int, default=30)
    parser.add_argument("--min-eval-n", type=int, default=10)
    return parser.parse_args()


def parse_seeds(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def fit_predict(model_name: str, x_train: np.ndarray, y_train: np.ndarray, x_test: np.ndarray, seed: int) -> np.ndarray:
    if model_name == "ridge":
        model = make_pipeline(StandardScaler(), RidgeCV(alphas=np.logspace(-2, 4, 9), cv=None))
    elif model_name == "elasticnet":
        model = make_pipeline(
            StandardScaler(),
            ElasticNetCV(
                l1_ratio=[0.1, 0.3, 0.5, 0.7, 0.9],
                alphas=np.logspace(-3, 2, 8),
                cv=3,
                max_iter=5000,
                random_state=seed,
            ),
        )
    elif model_name == "small_mlp":
        model = make_pipeline(
            StandardScaler(),
            MLPRegressor(
                hidden_layer_sizes=(32,),
                activation="relu",
                alpha=0.05,
                learning_rate_init=0.001,
                max_iter=600,
                early_stopping=True,
                validation_fraction=0.15,
                n_iter_no_change=30,
                random_state=seed,
            ),
        )
    else:
        raise ValueError(model_name)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", ConvergenceWarning)
        model.fit(x_train, y_train)
    return model.predict(x_test)


def run_seed(
    seed: int,
    phenotype: pd.DataFrame,
    population: pd.DataFrame,
    robust_traits: list[str],
    pop_features: pd.DataFrame,
    geno_pop_features: pd.DataFrame,
    min_train_n: int,
    min_eval_n: int,
) -> pd.DataFrame:
    split = make_splits(population, seed)
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno = phenotype[["accession_id_norm"] + robust_traits].copy()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)
    rows = []

    feature_sets = {
        "population_ridge": ("ridge", pop_features),
        "genotype_population_ridge": ("ridge", geno_pop_features),
        "genotype_population_elasticnet": ("elasticnet", geno_pop_features),
        "genotype_population_small_mlp": ("small_mlp", geno_pop_features),
    }

    for trait in robust_traits:
        y = pd.to_numeric(pheno[trait], errors="coerce")
        train_n = int(y[(pheno["split"] == "train")].notna().sum())
        test_n = int(y[(pheno["split"] == "test")].notna().sum())
        if train_n < min_train_n or test_n < min_eval_n or y.var(skipna=True) <= 0:
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

        for output_model, (fit_model, features) in feature_sets.items():
            merged = work.merge(features, on="accession_id_norm", how="left")
            feature_cols = [c for c in merged.columns if c not in {"accession_id_norm", "split", "y"}]
            train_m = merged[(merged["split"] == "train") & merged["y"].notna()].copy()
            test_m = merged[(merged["split"] == "test") & merged["y"].notna()].copy()
            if len(test_m) < min_eval_n:
                continue
            x_train = train_m[feature_cols].to_numpy(dtype=float)
            x_test = test_m[feature_cols].to_numpy(dtype=float)
            y_true = test_m["y"].to_numpy(dtype=float)
            pred_scaled = fit_predict(fit_model, x_train, y_train, x_test, seed)
            pred = pred_scaled * y_std + y_mean
            row = {
                "seed": seed,
                "trait": trait,
                "model": output_model,
                "split": "test",
                "train_non_missing": train_n,
                "test_non_missing": test_n,
            }
            row.update(metric_row(y_true, pred))
            rows.append(row)
    return pd.DataFrame(rows)


def summarize(metrics: pd.DataFrame, robust_traits: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
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
    trait_wide = metrics.pivot_table(index=["trait", "seed"], columns="model", values=["pearson", "r2"], aggfunc="first")
    trait_wide.columns = [f"{a}__{b}" for a, b in trait_wide.columns]
    trait_wide = trait_wide.reset_index()
    trait_summary = (
        trait_wide.groupby("trait", dropna=False)
        .agg(
            ridge_median_pearson=("pearson__genotype_population_ridge", "median"),
            elasticnet_median_pearson=("pearson__genotype_population_elasticnet", "median"),
            mlp_median_pearson=("pearson__genotype_population_small_mlp", "median"),
            ridge_median_r2=("r2__genotype_population_ridge", "median"),
            elasticnet_median_r2=("r2__genotype_population_elasticnet", "median"),
            mlp_median_r2=("r2__genotype_population_small_mlp", "median"),
        )
        .reset_index()
    )
    trait_summary = trait_summary.merge(
        robust_traits[["trait", "trait_family", "priority_tier"]], on="trait", how="left"
    )
    trait_summary["best_model_by_pearson"] = trait_summary[
        ["ridge_median_pearson", "elasticnet_median_pearson", "mlp_median_pearson"]
    ].idxmax(axis=1).str.replace("_median_pearson", "", regex=False)
    return model_summary, trait_summary


def write_report(seeds: list[int], model_summary: pd.DataFrame, trait_summary: pd.DataFrame) -> None:
    best_counts = trait_summary["best_model_by_pearson"].value_counts().rename_axis("model").reset_index(name="traits")
    top10 = trait_summary.sort_values("ridge_median_pearson", ascending=False).head(10)
    report = f"""# ZEAMAP v0.1 lightweight model comparison

日期：2026-06-05

## Setup

- Input traits: 66 robust selected traits
- Seeds: {", ".join(map(str, seeds))}
- Models: population ridge, genotype+population ridge, genotype+population ElasticNet, genotype+population small MLP
- Feature input: fixed `genotype_pca.tsv` plus population covariates

## Model Summary

```text
{model_summary.to_string(index=False)}
```

## Best Model Counts

```text
{best_counts.to_string(index=False)}
```

## Top 10 Traits By Ridge Pearson

```text
{top10.to_string(index=False)}
```

## Interpretation

- This comparison tests whether a non-linear small MLP or sparse ElasticNet improves over the ridge baseline.
- If ridge remains competitive, the next stage should prioritize feature engineering or methylation subset features rather than larger models.

## Outputs

- `results/v0_1_baseline/lightweight_model_metrics.tsv`
- `results/v0_1_baseline/lightweight_model_summary.tsv`
- `results/v0_1_baseline/lightweight_trait_summary.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    robust = pd.read_csv(RESULTS / "robust_selected_traits.tsv", sep="\t")
    robust_traits = robust["trait"].astype(str).tolist()
    pop_features = build_population_features(population)
    pca_features = pd.read_csv(V01 / "genotype_pca.tsv", sep="\t")
    geno_pop = pca_features.merge(pop_features, on="accession_id_norm", how="left")

    metrics = pd.concat(
        [
            run_seed(seed, phenotype, population, robust_traits, pop_features, geno_pop, args.min_train_n, args.min_eval_n)
            for seed in seeds
        ],
        ignore_index=True,
    )
    model_summary, trait_summary = summarize(metrics, robust)
    metrics.to_csv(RESULTS / "lightweight_model_metrics.tsv", sep="\t", index=False)
    model_summary.to_csv(RESULTS / "lightweight_model_summary.tsv", sep="\t", index=False)
    trait_summary.to_csv(RESULTS / "lightweight_trait_summary.tsv", sep="\t", index=False)
    (RESULTS / "lightweight_run_config.json").write_text(
        json.dumps({"seeds": seeds, "min_train_n": args.min_train_n, "min_eval_n": args.min_eval_n}, indent=2),
        encoding="utf-8",
    )
    write_report(seeds, model_summary, trait_summary)


if __name__ == "__main__":
    main()
