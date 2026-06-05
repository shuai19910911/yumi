#!/usr/bin/env python3
"""Trait-specific sparse gene-window methylation feature selection."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import ElasticNetCV
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from run_zeamap_v0_1_baseline import (
    RESULTS,
    V01,
    build_population_features,
    fit_predict_ridge,
    make_splits,
    metric_row,
)
from run_zeamap_v0_1_gene_methylation_pca import (
    CONTEXT_DIRS,
    aggregate_one,
    load_bedgraph,
    load_genes,
    parse_seeds,
)


REPORT = Path("docs/2026-06-05-zeamap-v0-1-sparse-methylation-selection-report.md")
CANDIDATE_FEATURES = V01 / "methylation_gene_window_sparse_candidates.tsv"
CANDIDATE_METADATA = V01 / "methylation_gene_window_sparse_candidate_metadata.tsv"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-traits", type=int, default=10)
    parser.add_argument("--top-features-per-combo", type=int, default=500)
    parser.add_argument("--max-correlation-features", type=int, default=200)
    parser.add_argument("--promoter-bp", type=int, default=2000)
    parser.add_argument("--cis-bp", type=int, default=10000)
    parser.add_argument("--seeds", default="20260605,20260606,20260607,20260608,20260609")
    parser.add_argument("--min-train-n", type=int, default=25)
    parser.add_argument("--min-eval-n", type=int, default=8)
    parser.add_argument("--force-rebuild-features", action="store_true")
    return parser.parse_args()


def methylation_accessions() -> list[str]:
    mask = pd.read_csv(V01 / "modality_mask.tsv", sep="\t")
    return sorted(mask.loc[mask["has_any_methylation"].astype(bool), "accession_id_norm"].astype(str).tolist())


def safe_feature_name(context: str, region_type: str, gene_id: str) -> str:
    return f"methwin__{context}__{region_type}__{gene_id}"


def build_candidate_features(args: argparse.Namespace, genes: pd.DataFrame, accessions: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if CANDIDATE_FEATURES.exists() and CANDIDATE_METADATA.exists() and not args.force_rebuild_features:
        return pd.read_csv(CANDIDATE_FEATURES, sep="\t"), pd.read_csv(CANDIDATE_METADATA, sep="\t")

    feature_blocks = [pd.DataFrame({"accession_id_norm": accessions})]
    metadata_rows = []
    region_types = ["gene", "promoter", "cis"]

    for context, directory in CONTEXT_DIRS.items():
        for region_type in region_types:
            matrix = np.full((len(accessions), len(genes)), np.nan, dtype=np.float32)
            for i, accession in enumerate(accessions):
                path = directory / f"{accession}.bedgraph.gz"
                if not path.exists():
                    continue
                matrix[i, :] = aggregate_one(genes, load_bedgraph(path), region_type)

            missing_fraction = np.isnan(matrix).mean(axis=0)
            col_medians = np.nanmedian(matrix, axis=0)
            col_medians = np.where(np.isfinite(col_medians), col_medians, 0.0).astype(np.float32)
            rows, cols = np.where(~np.isfinite(matrix))
            matrix[rows, cols] = col_medians[cols]
            variance = matrix.var(axis=0)
            keepable = np.where(variance > 1e-10)[0]
            if len(keepable) == 0:
                continue
            top_n = min(args.top_features_per_combo, len(keepable))
            top_idx = keepable[np.argsort(variance[keepable])[-top_n:]][::-1]
            cols_out = [safe_feature_name(context, region_type, genes.iloc[idx]["gene_id"]) for idx in top_idx]
            feature_blocks.append(pd.DataFrame(matrix[:, top_idx], columns=cols_out))

            for rank, idx in enumerate(top_idx, start=1):
                gene = genes.iloc[idx]
                metadata_rows.append(
                    {
                        "feature": safe_feature_name(context, region_type, gene["gene_id"]),
                        "context": context,
                        "region_type": region_type,
                        "gene_id": gene["gene_id"],
                        "chrom": gene["chrom"],
                        "start_1based": int(gene["start_1based"]),
                        "end_1based": int(gene["end_1based"]),
                        "strand": gene["strand"],
                        "variance_rank_within_combo": rank,
                        "variance": float(variance[idx]),
                        "missing_fraction_before_impute": float(missing_fraction[idx]),
                    }
                )

    features = pd.concat(feature_blocks, axis=1)
    metadata = pd.DataFrame(metadata_rows)
    features.to_csv(CANDIDATE_FEATURES, sep="\t", index=False)
    metadata.to_csv(CANDIDATE_METADATA, sep="\t", index=False)
    return features, metadata


def target_traits(top_n: int) -> list[str]:
    summary = pd.read_csv(RESULTS / "gene_methylation_pca_trait_summary.tsv", sep="\t")
    summary = summary[
        (summary["median_pearson_gain"] > 0)
        & (summary["median_r2_gain"] > 0)
        & (summary["gene_methylation_better_pearson_seeds"] >= 3)
    ].copy()
    return summary.sort_values(["median_pearson_gain", "median_r2_gain"], ascending=False)["trait"].head(top_n).tolist()


def select_by_train_correlation(x_train: np.ndarray, y_train: np.ndarray, max_features: int) -> np.ndarray:
    x = x_train.astype(np.float64, copy=False)
    y = y_train.astype(np.float64, copy=False)
    x_centered = x - x.mean(axis=0)
    y_centered = y - y.mean()
    denom = np.sqrt((x_centered**2).sum(axis=0) * float((y_centered**2).sum()))
    corr = np.divide(x_centered.T @ y_centered, denom, out=np.zeros(x.shape[1]), where=denom > 1e-12)
    finite = np.where(np.isfinite(corr))[0]
    if len(finite) == 0:
        return np.array([], dtype=int)
    n = min(max_features, len(finite))
    return finite[np.argsort(np.abs(corr[finite]))[-n:]][::-1]


def run_one_seed(
    seed: int,
    traits: list[str],
    phenotype: pd.DataFrame,
    population: pd.DataFrame,
    base_features: pd.DataFrame,
    methyl_pca: pd.DataFrame,
    methyl_candidates: pd.DataFrame,
    args: argparse.Namespace,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    accessions = set(methyl_candidates["accession_id_norm"].astype(str))
    population_sub = population[population["accession_id_norm"].isin(accessions)].copy()
    split = make_splits(population_sub, seed)
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno = phenotype[phenotype["accession_id_norm"].isin(accessions)][["accession_id_norm"] + traits].copy()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)

    base = base_features[base_features["accession_id_norm"].isin(accessions)].copy()
    pca_features = base.merge(methyl_pca, on="accession_id_norm", how="inner")
    methyl_cols = [c for c in methyl_candidates.columns if c != "accession_id_norm"]
    metric_rows = []
    selected_rows = []

    for trait in traits:
        y = pd.to_numeric(pheno[trait], errors="coerce")
        train_n = int(y[(pheno["split"] == "train")].notna().sum())
        test_n = int(y[(pheno["split"] == "test")].notna().sum())
        if train_n < args.min_train_n or test_n < args.min_eval_n or y.var(skipna=True) <= 0:
            continue
        work = pheno[["accession_id_norm", "split"]].copy()
        work["y"] = y
        train_y = work[(work["split"] == "train") & work["y"].notna()]["y"].to_numpy(dtype=float)
        y_mean = float(train_y.mean())
        y_std = float(train_y.std())
        if y_std <= 0:
            continue

        for model_name, features in {
            "genotype_population_ridge": base,
            "genotype_population_gene_methylation_pca_ridge": pca_features,
        }.items():
            merged = work.merge(features, on="accession_id_norm", how="inner")
            feature_cols = [c for c in merged.columns if c not in {"accession_id_norm", "split", "y"}]
            train_m = merged[(merged["split"] == "train") & merged["y"].notna()]
            test_m = merged[(merged["split"] == "test") & merged["y"].notna()]
            if len(train_m) < args.min_train_n or len(test_m) < args.min_eval_n:
                continue
            pred_scaled = fit_predict_ridge(
                train_m[feature_cols].to_numpy(dtype=float),
                (train_m["y"].to_numpy(dtype=float) - y_mean) / y_std,
                test_m[feature_cols].to_numpy(dtype=float),
            )
            row = {"seed": seed, "trait": trait, "model": model_name, "split": "test", "train_non_missing": train_n, "test_non_missing": test_n}
            row.update(metric_row(test_m["y"].to_numpy(dtype=float), pred_scaled * y_std + y_mean))
            metric_rows.append(row)

        merged = work.merge(base, on="accession_id_norm", how="inner").merge(methyl_candidates, on="accession_id_norm", how="inner")
        base_cols = [c for c in base.columns if c != "accession_id_norm"]
        train_m = merged[(merged["split"] == "train") & merged["y"].notna()].copy()
        test_m = merged[(merged["split"] == "test") & merged["y"].notna()].copy()
        if len(train_m) < args.min_train_n or len(test_m) < args.min_eval_n:
            continue
        y_train = (train_m["y"].to_numpy(dtype=float) - y_mean) / y_std
        selected_idx = select_by_train_correlation(train_m[methyl_cols].to_numpy(dtype=float), y_train, args.max_correlation_features)
        selected_methyl_cols = [methyl_cols[i] for i in selected_idx]
        feature_cols = base_cols + selected_methyl_cols
        model = make_pipeline(
            StandardScaler(),
            ElasticNetCV(
                l1_ratio=[0.1, 0.5, 0.9],
                alphas=50,
                cv=min(5, max(3, len(train_m) // 25)),
                random_state=seed,
                max_iter=20000,
            ),
        )
        model.fit(train_m[feature_cols].to_numpy(dtype=float), y_train)
        pred = model.predict(test_m[feature_cols].to_numpy(dtype=float)) * y_std + y_mean
        row = {
            "seed": seed,
            "trait": trait,
            "model": "genotype_population_sparse_methylation_elasticnet",
            "split": "test",
            "train_non_missing": train_n,
            "test_non_missing": test_n,
        }
        row.update(metric_row(test_m["y"].to_numpy(dtype=float), pred))
        metric_rows.append(row)

        coefs = model.named_steps["elasticnetcv"].coef_
        for feature, coef in zip(feature_cols, coefs):
            if feature.startswith("methwin__") and abs(coef) > 1e-10:
                selected_rows.append(
                    {
                        "seed": seed,
                        "trait": trait,
                        "feature": feature,
                        "coefficient": float(coef),
                        "abs_coefficient": float(abs(coef)),
                    }
                )

    return pd.DataFrame(metric_rows), pd.DataFrame(selected_rows)


def summarize(metrics: pd.DataFrame, selected: pd.DataFrame, metadata: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
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
    sparse = "genotype_population_sparse_methylation_elasticnet"
    base = "genotype_population_ridge"
    pca = "genotype_population_gene_methylation_pca_ridge"
    wide["pearson_gain_sparse_vs_base"] = wide[f"pearson__{sparse}"] - wide[f"pearson__{base}"]
    wide["r2_gain_sparse_vs_base"] = wide[f"r2__{sparse}"] - wide[f"r2__{base}"]
    wide["pearson_gain_sparse_vs_pca"] = wide[f"pearson__{sparse}"] - wide[f"pearson__{pca}"]
    wide["r2_gain_sparse_vs_pca"] = wide[f"r2__{sparse}"] - wide[f"r2__{pca}"]
    trait_summary = (
        wide.groupby("trait")
        .agg(
            median_pearson_gain_sparse_vs_base=("pearson_gain_sparse_vs_base", "median"),
            median_r2_gain_sparse_vs_base=("r2_gain_sparse_vs_base", "median"),
            median_pearson_gain_sparse_vs_pca=("pearson_gain_sparse_vs_pca", "median"),
            median_r2_gain_sparse_vs_pca=("r2_gain_sparse_vs_pca", "median"),
            sparse_better_than_base_pearson_seeds=("pearson_gain_sparse_vs_base", lambda x: int((x > 0).sum())),
            sparse_better_than_pca_pearson_seeds=("pearson_gain_sparse_vs_pca", lambda x: int((x > 0).sum())),
        )
        .reset_index()
        .sort_values(["median_pearson_gain_sparse_vs_base", "median_r2_gain_sparse_vs_base"], ascending=False)
    )

    if selected.empty:
        selected_summary = pd.DataFrame()
    else:
        selected_summary = (
            selected.groupby(["trait", "feature"])
            .agg(
                selected_seeds=("seed", "nunique"),
                mean_coefficient=("coefficient", "mean"),
                mean_abs_coefficient=("abs_coefficient", "mean"),
            )
            .reset_index()
            .merge(metadata, on="feature", how="left")
            .sort_values(["trait", "selected_seeds", "mean_abs_coefficient"], ascending=[True, False, False])
        )
    return model_summary, trait_summary, selected_summary


def write_report(
    args: argparse.Namespace,
    traits: list[str],
    features: pd.DataFrame,
    model_summary: pd.DataFrame,
    trait_summary: pd.DataFrame,
    selected_summary: pd.DataFrame,
) -> None:
    top_features = selected_summary.head(30) if not selected_summary.empty else selected_summary
    report = f"""# ZEAMAP v0.1 sparse methylation feature selection

日期：2026-06-05

## Setup

- Target traits: {len(traits)}
- Candidate methylation features: {features.shape[1] - 1}
- Candidate rule: top {args.top_features_per_combo} variable genes per methylation context x region type
- Train-only correlation prefilter per trait/seed: top {args.max_correlation_features}
- Sparse model: genotype+population features plus selected gene-window methylation features, ElasticNetCV
- Seeds: {args.seeds}

## Target Traits

```text
{chr(10).join(traits)}
```

## Model Summary

```text
{model_summary.to_string(index=False)}
```

## Trait Summary

```text
{trait_summary.to_string(index=False)}
```

## Top Selected Methylation Features

```text
{top_features.to_string(index=False) if not top_features.empty else "No non-zero methylation features selected."}
```

## Interpretation

- This is a trait-specific sparse screen, not a final biological claim.
- A useful methylation signal should beat genotype+population across multiple seeds and repeatedly select the same gene/context/region features.
- If sparse methylation does not beat the PCA methylation result, the current methylation modality is best kept as low-priority auxiliary metadata in v0.1.

## Outputs

- `data/processed/v0_1/methylation_gene_window_sparse_candidates.tsv`
- `data/processed/v0_1/methylation_gene_window_sparse_candidate_metadata.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_metrics.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_model_summary.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_trait_summary.tsv`
- `results/v0_1_baseline/sparse_methylation_selected_features.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    genes = load_genes(args.promoter_bp, args.cis_bp)
    accessions = methylation_accessions()
    features, metadata = build_candidate_features(args, genes, accessions)
    traits = target_traits(args.top_traits)

    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    pca = pd.read_csv(V01 / "genotype_pca.tsv", sep="\t")
    pop = build_population_features(population)
    base = pca.merge(pop, on="accession_id_norm", how="left")
    methyl_pca = pd.read_csv(V01 / "methylation_gene_region_pca.tsv", sep="\t")

    runs = [
        run_one_seed(seed, traits, phenotype, population, base, methyl_pca, features, args)
        for seed in seeds
    ]
    metrics = pd.concat([x[0] for x in runs], ignore_index=True)
    selected = pd.concat([x[1] for x in runs], ignore_index=True) if any(not x[1].empty for x in runs) else pd.DataFrame()
    model_summary, trait_summary, selected_summary = summarize(metrics, selected, metadata)

    metrics.to_csv(RESULTS / "sparse_methylation_selection_metrics.tsv", sep="\t", index=False)
    model_summary.to_csv(RESULTS / "sparse_methylation_selection_model_summary.tsv", sep="\t", index=False)
    trait_summary.to_csv(RESULTS / "sparse_methylation_selection_trait_summary.tsv", sep="\t", index=False)
    selected_summary.to_csv(RESULTS / "sparse_methylation_selected_features.tsv", sep="\t", index=False)
    (RESULTS / "sparse_methylation_selection_run_config.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")
    write_report(args, traits, features, model_summary, trait_summary, selected_summary)


if __name__ == "__main__":
    main()
