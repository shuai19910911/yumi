#!/usr/bin/env python3
"""Run ZEAMAP v0.1 accession-level baseline benchmark.

This script is intended to run on a CPU compute node under the yumi mamba
environment.
"""

from __future__ import annotations

import argparse
import json
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import ConstantInputWarning, pearsonr, spearmanr
from sklearn.decomposition import PCA
from sklearn.linear_model import RidgeCV
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


PROJECT_ROOT = Path(".")
V01 = PROJECT_ROOT / "data/processed/v0_1"
RESULTS = PROJECT_ROOT / "results/v0_1_baseline"
REPORT = PROJECT_ROOT / "docs/2026-06-05-zeamap-v0-1-baseline-report.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-pcs", type=int, default=100)
    parser.add_argument("--random-state", type=int, default=20260605)
    parser.add_argument("--min-total-n", type=int, default=80)
    parser.add_argument("--min-train-n", type=int, default=30)
    parser.add_argument("--min-eval-n", type=int, default=10)
    return parser.parse_args()


def read_inputs() -> dict[str, object]:
    samples = pd.read_csv(V01 / "genotype_samples.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    mask = pd.read_csv(V01 / "modality_mask.tsv", sep="\t")
    npz = np.load(V01 / "genotype_dosage_int8.npz", allow_pickle=False)
    dosage = npz["dosage"]
    tsv_samples = samples["accession_id_norm"].astype(str).tolist()
    if dosage.shape[1] != len(tsv_samples):
        raise RuntimeError("Dosage matrix sample dimension does not match genotype_samples.tsv")
    return {
        "samples": samples,
        "population": population,
        "phenotype": phenotype,
        "mask": mask,
        "dosage": dosage,
    }


def make_splits(population: pd.DataFrame, random_state: int) -> pd.DataFrame:
    accessions = population["accession_id_norm"].astype(str).to_numpy()
    strata = population["structure_group"].fillna("UNKNOWN").astype(str)
    use_strata = strata.value_counts().min() >= 3
    stratify = strata if use_strata else None

    train_val, test = train_test_split(
        accessions,
        test_size=0.15,
        random_state=random_state,
        stratify=stratify,
    )
    strata_by_id = pd.Series(strata.values, index=accessions)
    train_val_strata = pd.Series(train_val).map(strata_by_id).fillna("UNKNOWN").astype(str)
    use_train_val_strata = train_val_strata.value_counts().min() >= 2
    stratify_train_val = train_val_strata if use_train_val_strata else None
    train, val = train_test_split(
        train_val,
        test_size=0.15 / 0.85,
        random_state=random_state,
        stratify=stratify_train_val if use_train_val_strata else None,
    )

    split = pd.DataFrame({"accession_id_norm": accessions})
    split["split"] = "unassigned"
    split.loc[split["accession_id_norm"].isin(train), "split"] = "train"
    split.loc[split["accession_id_norm"].isin(val), "split"] = "val"
    split.loc[split["accession_id_norm"].isin(test), "split"] = "test"
    return split


def save_splits(split: pd.DataFrame) -> None:
    split_dir = V01 / "splits"
    split_dir.mkdir(parents=True, exist_ok=True)
    split.to_csv(split_dir / "split_assignments.tsv", sep="\t", index=False)
    for name in ["train", "val", "test"]:
        ids = split.loc[split["split"] == name, "accession_id_norm"].astype(str)
        (split_dir / f"{name}.txt").write_text("\n".join(ids) + "\n", encoding="utf-8")


def build_population_features(population: pd.DataFrame) -> pd.DataFrame:
    base_cols = ["PC1", "PC2", "PC3", "K1", "K2", "K3"]
    numeric = population[["accession_id_norm"] + base_cols].copy()
    for col in base_cols:
        numeric[col] = pd.to_numeric(numeric[col], errors="coerce")
    cat = population[["population_group", "structure_group"]].fillna("UNKNOWN").astype(str)
    try:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
    except TypeError:
        encoder = OneHotEncoder(sparse=False, handle_unknown="ignore")
    encoded = encoder.fit_transform(cat)
    cat_names = [f"popcat__{x}" for x in encoder.get_feature_names_out(cat.columns)]
    cat_df = pd.DataFrame(encoded, columns=cat_names)
    features = pd.concat([numeric.reset_index(drop=True), cat_df], axis=1)
    feature_cols = [c for c in features.columns if c != "accession_id_norm"]
    features[feature_cols] = features[feature_cols].fillna(features[feature_cols].median())
    return features


def build_genotype_pca(dosage: np.ndarray, samples: pd.DataFrame, n_pcs: int, random_state: int) -> tuple[pd.DataFrame, pd.DataFrame]:
    x = dosage.T.astype(np.float32, copy=True)
    missing = x < 0
    if missing.any():
        means = np.nanmean(np.where(missing, np.nan, x), axis=0).astype(np.float32)
        rows, cols = np.where(missing)
        x[rows, cols] = means[cols]
    means = x.mean(axis=0, dtype=np.float64).astype(np.float32)
    stds = x.std(axis=0, dtype=np.float64).astype(np.float32)
    stds[stds == 0] = 1.0
    x -= means
    x /= stds

    max_components = min(n_pcs, x.shape[0] - 1, x.shape[1])
    pca = PCA(n_components=max_components, svd_solver="randomized", random_state=random_state)
    pcs = pca.fit_transform(x)
    cols = [f"geno_pc{i + 1}" for i in range(max_components)]
    pca_df = pd.DataFrame(pcs, columns=cols)
    pca_df.insert(0, "accession_id_norm", samples["accession_id_norm"].astype(str).values)
    variance = pd.DataFrame(
        {
            "component": cols,
            "explained_variance_ratio": pca.explained_variance_ratio_,
            "cumulative_explained_variance_ratio": np.cumsum(pca.explained_variance_ratio_),
        }
    )
    return pca_df, variance


def metric_row(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float | int]:
    valid = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true = y_true[valid]
    y_pred = y_pred[valid]
    out: dict[str, float | int] = {"n_eval": int(len(y_true))}
    y_true_std = float(np.nanstd(y_true))
    y_pred_std = float(np.nanstd(y_pred))
    if len(y_true) < 3 or y_true_std <= 1e-12:
        out.update({"r2": np.nan, "pearson": np.nan, "spearman": np.nan, "mae": np.nan, "rmse": np.nan})
        return out
    out["r2"] = float(r2_score(y_true, y_pred))
    if y_pred_std > 1e-12:
        with warnings.catch_warnings():
            warnings.simplefilter("error", ConstantInputWarning)
            try:
                out["pearson"] = float(pearsonr(y_true, y_pred).statistic)
            except ConstantInputWarning:
                out["pearson"] = np.nan
            try:
                out["spearman"] = float(spearmanr(y_true, y_pred).statistic)
            except ConstantInputWarning:
                out["spearman"] = np.nan
    else:
        out["pearson"] = np.nan
        out["spearman"] = np.nan
    out["mae"] = float(mean_absolute_error(y_true, y_pred))
    out["rmse"] = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    return out


def fit_predict_ridge(x_train: np.ndarray, y_train: np.ndarray, x_eval: np.ndarray) -> np.ndarray:
    alphas = np.logspace(-2, 4, 9)
    model = make_pipeline(StandardScaler(), RidgeCV(alphas=alphas, cv=None))
    model.fit(x_train, y_train)
    return model.predict(x_eval)


def run_trait_models(
    phenotype: pd.DataFrame,
    split: pd.DataFrame,
    feature_sets: dict[str, pd.DataFrame],
    min_total_n: int,
    min_train_n: int,
    min_eval_n: int,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    pheno = phenotype.copy()
    trait_cols = [c for c in pheno.columns if c != "accession_id_norm"]
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)

    trait_qc_rows = []
    metric_rows = []
    for trait in trait_cols:
        y = pd.to_numeric(pheno[trait], errors="coerce")
        total_n = int(y.notna().sum())
        train_n = int(y[(pheno["split"] == "train")].notna().sum())
        val_n = int(y[(pheno["split"] == "val")].notna().sum())
        test_n = int(y[(pheno["split"] == "test")].notna().sum())
        variance = float(y.var(skipna=True)) if total_n > 1 else np.nan
        keep = total_n >= min_total_n and train_n >= min_train_n and val_n >= min_eval_n and test_n >= min_eval_n and np.isfinite(variance) and variance > 0
        trait_qc_rows.append(
            {
                "trait": trait,
                "trait_group": trait.split("__", 1)[0],
                "total_non_missing": total_n,
                "train_non_missing": train_n,
                "val_non_missing": val_n,
                "test_non_missing": test_n,
                "missing_rate": float(1 - total_n / len(pheno)),
                "variance": variance,
                "used_for_baseline": bool(keep),
            }
        )
        if not keep:
            continue

        work = pheno[["accession_id_norm", "split"]].copy()
        work["y"] = y
        train_df = work[(work["split"] == "train") & work["y"].notna()].copy()
        y_train_raw = train_df["y"].to_numpy(dtype=float)
        y_mean = float(y_train_raw.mean())
        y_std = float(y_train_raw.std())
        if y_std == 0:
            continue
        y_train = (y_train_raw - y_mean) / y_std

        for model_name, features in feature_sets.items():
            merged = work.merge(features, on="accession_id_norm", how="left")
            feature_cols = [c for c in merged.columns if c not in {"accession_id_norm", "split", "y"}]
            train_m = merged[(merged["split"] == "train") & merged["y"].notna()].copy()
            x_train = train_m[feature_cols].to_numpy(dtype=float)

            for eval_split in ["val", "test"]:
                eval_m = merged[(merged["split"] == eval_split) & merged["y"].notna()].copy()
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
                    "trait": trait,
                    "trait_group": trait.split("__", 1)[0],
                    "model": model_name,
                    "split": eval_split,
                }
                row.update(metric_row(y_true, pred))
                metric_rows.append(row)

    return pd.DataFrame(trait_qc_rows), pd.DataFrame(metric_rows)


def summarize_metrics(metrics: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    test = metrics[metrics["split"] == "test"].copy()
    summary = (
        test.groupby("model", dropna=False)
        .agg(
            traits_evaluated=("trait", "nunique"),
            median_r2=("r2", "median"),
            mean_r2=("r2", "mean"),
            median_pearson=("pearson", "median"),
            mean_pearson=("pearson", "mean"),
            positive_r2_traits=("r2", lambda x: int((x > 0).sum())),
            pearson_gt_0_2_traits=("pearson", lambda x: int((x > 0.2).sum())),
        )
        .reset_index()
        .sort_values(["median_pearson", "median_r2"], ascending=False)
    )
    wide = test.pivot_table(index=["trait", "trait_group"], columns="model", values=["r2", "pearson"], aggfunc="first")
    wide.columns = [f"{a}__{b}" for a, b in wide.columns]
    wide = wide.reset_index()
    rank_col = "pearson__genotype_pca_population_ridge"
    if rank_col in wide.columns:
        top = wide.sort_values(rank_col, ascending=False)
    else:
        top = wide
    return summary, top


def write_report(args: argparse.Namespace, split: pd.DataFrame, variance: pd.DataFrame, trait_qc: pd.DataFrame, summary: pd.DataFrame) -> None:
    split_counts = split["split"].value_counts().to_dict()
    used_traits = trait_qc[trait_qc["used_for_baseline"]]
    top_var = variance["cumulative_explained_variance_ratio"].iloc[min(len(variance), args.n_pcs) - 1]
    report = f"""# ZEAMAP v0.1 baseline benchmark report

Run date: 2026-06-05

## Inputs

- `data/processed/v0_1/genotype_dosage_int8.npz`
- `data/processed/v0_1/phenotype.tsv`
- `data/processed/v0_1/population.tsv`

## Environment

- mamba environment: `yumi`
- CPU job: Slurm `q07`

## Split

- train: {split_counts.get("train", 0)}
- val: {split_counts.get("val", 0)}
- test: {split_counts.get("test", 0)}

## Genotype PCA

- requested PCs: {args.n_pcs}
- output PCs: {len(variance)}
- cumulative explained variance: {top_var:.6f}

## Trait filtering

- total traits: {len(trait_qc)}
- traits used for baseline: {len(used_traits)}
- minimum total non-missing: {args.min_total_n}
- minimum train non-missing: {args.min_train_n}
- minimum val/test non-missing: {args.min_eval_n}

## Model comparison

```text
{summary.to_string(index=False)}
```

## Outputs

- `data/processed/v0_1/splits/split_assignments.tsv`
- `data/processed/v0_1/genotype_pca.tsv`
- `data/processed/v0_1/genotype_pca_variance.tsv`
- `results/v0_1_baseline/trait_qc.tsv`
- `results/v0_1_baseline/trait_metrics.tsv`
- `results/v0_1_baseline/model_comparison.tsv`
- `results/v0_1_baseline/top_predictable_traits.tsv`

## Notes

- All results use accession-level splits.
- `mean_baseline` predicts the training mean for each trait.
- Ridge models standardize features inside the training fold.
- Ridge alpha is selected with `RidgeCV(cv=None)` for a fast deterministic CPU baseline.
- Expression is not used because current expression files are reference/tissue matrices rather than AMP accession-level expression.
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    RESULTS.mkdir(parents=True, exist_ok=True)
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    inputs = read_inputs()
    samples = inputs["samples"]
    population = inputs["population"]
    phenotype = inputs["phenotype"]
    dosage = inputs["dosage"]

    split = make_splits(population, args.random_state)
    save_splits(split)

    pop_features = build_population_features(population)
    pca_features, pca_variance = build_genotype_pca(dosage, samples, args.n_pcs, args.random_state)
    pca_features.to_csv(V01 / "genotype_pca.tsv", sep="\t", index=False)
    pca_variance.to_csv(V01 / "genotype_pca_variance.tsv", sep="\t", index=False)

    mean_feature = pd.DataFrame({"accession_id_norm": samples["accession_id_norm"].astype(str), "constant": 1.0})
    geno_pop = pca_features.merge(pop_features, on="accession_id_norm", how="left")
    feature_sets = {
        "mean_baseline": mean_feature,
        "population_ridge": pop_features,
        "genotype_pca_ridge": pca_features,
        "genotype_pca_population_ridge": geno_pop,
    }

    trait_qc, metrics = run_trait_models(
        phenotype,
        split,
        feature_sets,
        args.min_total_n,
        args.min_train_n,
        args.min_eval_n,
    )
    summary, top_traits = summarize_metrics(metrics)

    trait_qc.to_csv(RESULTS / "trait_qc.tsv", sep="\t", index=False)
    metrics.to_csv(RESULTS / "trait_metrics.tsv", sep="\t", index=False)
    summary.to_csv(RESULTS / "model_comparison.tsv", sep="\t", index=False)
    top_traits.to_csv(RESULTS / "top_predictable_traits.tsv", sep="\t", index=False)

    run_config = vars(args).copy()
    run_config["feature_sets"] = list(feature_sets)
    (RESULTS / "run_config.json").write_text(json.dumps(run_config, indent=2), encoding="utf-8")
    write_report(args, split, pca_variance, trait_qc, summary)


if __name__ == "__main__":
    main()
