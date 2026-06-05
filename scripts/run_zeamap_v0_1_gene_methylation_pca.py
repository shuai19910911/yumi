#!/usr/bin/env python3
"""Aggregate methylation to gene/promoter/cis windows and test PCA features."""

from __future__ import annotations

import argparse
import gzip
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.decomposition import PCA

from run_zeamap_v0_1_baseline import RESULTS, V01, build_population_features, fit_predict_ridge, make_splits, metric_row


LOCAL_ROOT = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP")
GFF = LOCAL_ROOT / "reference/B73_RefGen_v4/Zea_mays.B73_RefGen_v4.47.chr.gff3.gz"
METH_ROOT = LOCAL_ROOT / "epigenome/dna_methylation/01_regions"
REPORT = Path("docs/2026-06-05-zeamap-v0-1-gene-methylation-pca-report.md")
GENE_REGIONS = V01 / "b73_refgen_v4_gene_windows.tsv"
PCA_FEATURES = V01 / "methylation_gene_region_pca.tsv"
PCA_VARIANCE = V01 / "methylation_gene_region_pca_variance.tsv"

CONTEXT_DIRS = {
    "mCG": METH_ROOT / "AMP_mCG_bed",
    "mCHG": METH_ROOT / "AMP_mCHG_bed",
    "mCHH": METH_ROOT / "AMP_mCHH_bed",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--n-pcs", type=int, default=10)
    parser.add_argument("--promoter-bp", type=int, default=2000)
    parser.add_argument("--cis-bp", type=int, default=10000)
    parser.add_argument("--seeds", default="20260605,20260606,20260607,20260608,20260609")
    parser.add_argument("--min-train-n", type=int, default=25)
    parser.add_argument("--min-eval-n", type=int, default=8)
    parser.add_argument("--force-rebuild-features", action="store_true")
    return parser.parse_args()


def parse_seeds(text: str) -> list[int]:
    return [int(x) for x in text.split(",") if x.strip()]


def attr_value(attrs: str, key: str) -> str:
    match = re.search(rf"(?:^|;){key}=([^;]+)", attrs)
    return match.group(1) if match else ""


def load_genes(promoter_bp: int, cis_bp: int) -> pd.DataFrame:
    rows = []
    with gzip.open(GFF, "rt") as handle:
        for line in handle:
            if line.startswith("#"):
                continue
            parts = line.rstrip("\n").split("\t")
            if len(parts) < 9 or parts[2] != "gene":
                continue
            chrom, _, _, start, end, _, strand, _, attrs = parts
            if chrom not in {str(i) for i in range(1, 11)}:
                continue
            gene_id = attr_value(attrs, "gene_id") or attr_value(attrs, "ID").replace("gene:", "")
            start_i = int(start)
            end_i = int(end)
            tss = start_i if strand == "+" else end_i
            if strand == "+":
                promoter_start = max(1, tss - promoter_bp)
                promoter_end = max(promoter_start, tss - 1)
            else:
                promoter_start = min(end_i + 1, tss + 1)
                promoter_end = tss + promoter_bp
            rows.append(
                {
                    "gene_id": gene_id,
                    "chrom": chrom,
                    "start_1based": start_i,
                    "end_1based": end_i,
                    "strand": strand,
                    "gene_start0": start_i - 1,
                    "gene_end": end_i,
                    "promoter_start0": max(0, promoter_start - 1),
                    "promoter_end": promoter_end,
                    "cis_start0": max(0, start_i - cis_bp - 1),
                    "cis_end": end_i + cis_bp,
                }
            )
    genes = pd.DataFrame(rows).sort_values(["chrom", "start_1based", "end_1based", "gene_id"]).reset_index(drop=True)
    genes.to_csv(GENE_REGIONS, sep="\t", index=False)
    return genes


def load_bedgraph(path: Path) -> dict[str, list[tuple[int, int, float]]]:
    by_chrom: dict[str, list[tuple[int, int, float]]] = {}
    with gzip.open(path, "rt") as handle:
        for line in handle:
            if not line.strip():
                continue
            chrom, start, end, value = line.rstrip("\n").split("\t")[:4]
            if chrom not in {str(i) for i in range(1, 11)}:
                continue
            by_chrom.setdefault(chrom, []).append((int(start), int(end), float(value)))
    for chrom in by_chrom:
        by_chrom[chrom].sort()
    return by_chrom


def aggregate_one(
    genes: pd.DataFrame,
    bed: dict[str, list[tuple[int, int, float]]],
    region_type: str,
) -> np.ndarray:
    starts = genes[f"{region_type}_start0"].to_numpy(dtype=np.int64)
    ends = genes[f"{region_type}_end"].to_numpy(dtype=np.int64)
    out = np.full(len(genes), np.nan, dtype=np.float32)
    for chrom, gene_idx in genes.groupby("chrom").groups.items():
        intervals = bed.get(str(chrom), [])
        if not intervals:
            continue
        idxs = np.array(list(gene_idx), dtype=np.int64)
        order = idxs[np.argsort(starts[idxs])]
        pointer = 0
        for gi in order:
            r_start = int(starts[gi])
            r_end = int(ends[gi])
            while pointer < len(intervals) and intervals[pointer][1] <= r_start:
                pointer += 1
            j = pointer
            total = 0
            weighted = 0.0
            while j < len(intervals) and intervals[j][0] < r_end:
                b_start, b_end, value = intervals[j]
                ov = min(r_end, b_end) - max(r_start, b_start)
                if ov > 0:
                    total += ov
                    weighted += ov * value
                j += 1
            if total > 0:
                out[gi] = weighted / total
    return out


def build_pca_features(args: argparse.Namespace, genes: pd.DataFrame, accessions: list[str]) -> tuple[pd.DataFrame, pd.DataFrame]:
    if PCA_FEATURES.exists() and PCA_VARIANCE.exists() and not args.force_rebuild_features:
        return pd.read_csv(PCA_FEATURES, sep="\t"), pd.read_csv(PCA_VARIANCE, sep="\t")

    feature_df = pd.DataFrame({"accession_id_norm": accessions})
    variance_rows = []
    region_types = ["gene", "promoter", "cis"]
    for context, directory in CONTEXT_DIRS.items():
        for region_type in region_types:
            matrix = np.full((len(accessions), len(genes)), np.nan, dtype=np.float32)
            for i, accession in enumerate(accessions):
                path = directory / f"{accession}.bedgraph.gz"
                if not path.exists():
                    continue
                bed = load_bedgraph(path)
                matrix[i, :] = aggregate_one(genes, bed, region_type)
            col_medians = np.nanmedian(matrix, axis=0)
            col_medians = np.where(np.isfinite(col_medians), col_medians, 0.0).astype(np.float32)
            rows, cols = np.where(~np.isfinite(matrix))
            matrix[rows, cols] = col_medians[cols]
            col_std = matrix.std(axis=0)
            keep = col_std > 1e-8
            matrix = matrix[:, keep]
            n_comp = min(args.n_pcs, matrix.shape[0] - 1, matrix.shape[1])
            pca = PCA(n_components=n_comp, svd_solver="randomized", random_state=20260605)
            pcs = pca.fit_transform(matrix)
            for pc_i in range(n_comp):
                col = f"methpc__{context}__{region_type}__pc{pc_i + 1}"
                feature_df[col] = pcs[:, pc_i]
                variance_rows.append(
                    {
                        "context": context,
                        "region_type": region_type,
                        "component": pc_i + 1,
                        "features_before_filter": len(genes),
                        "features_after_filter": int(keep.sum()),
                        "explained_variance_ratio": float(pca.explained_variance_ratio_[pc_i]),
                        "cumulative_explained_variance_ratio": float(np.cumsum(pca.explained_variance_ratio_)[pc_i]),
                    }
                )
    variance = pd.DataFrame(variance_rows)
    feature_df.to_csv(PCA_FEATURES, sep="\t", index=False)
    variance.to_csv(PCA_VARIANCE, sep="\t", index=False)
    return feature_df, variance


def run_seed(
    seed: int,
    phenotype: pd.DataFrame,
    population: pd.DataFrame,
    robust_traits: list[str],
    base_features: pd.DataFrame,
    methyl_pcs: pd.DataFrame,
    min_train_n: int,
    min_eval_n: int,
) -> pd.DataFrame:
    accessions = set(methyl_pcs["accession_id_norm"].astype(str))
    population_sub = population[population["accession_id_norm"].isin(accessions)].copy()
    split = make_splits(population_sub, seed)
    split_map = split.set_index("accession_id_norm")["split"].to_dict()
    pheno = phenotype[phenotype["accession_id_norm"].isin(accessions)][["accession_id_norm"] + robust_traits].copy()
    pheno["split"] = pheno["accession_id_norm"].map(split_map)
    feature_sets = {
        "genotype_population_ridge": base_features[base_features["accession_id_norm"].isin(accessions)],
        "genotype_population_gene_methylation_pca_ridge": base_features.merge(methyl_pcs, on="accession_id_norm", how="inner"),
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
            pred_scaled = fit_predict_ridge(
                train_m[feature_cols].to_numpy(dtype=float),
                y_train,
                test_m[feature_cols].to_numpy(dtype=float),
            )
            y_true = test_m["y"].to_numpy(dtype=float)
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
    wide["pearson_gain_gene_methylation_pca"] = (
        wide["pearson__genotype_population_gene_methylation_pca_ridge"] - wide["pearson__genotype_population_ridge"]
    )
    wide["r2_gain_gene_methylation_pca"] = (
        wide["r2__genotype_population_gene_methylation_pca_ridge"] - wide["r2__genotype_population_ridge"]
    )
    trait_summary = (
        wide.groupby("trait")
        .agg(
            median_pearson_gain=("pearson_gain_gene_methylation_pca", "median"),
            mean_pearson_gain=("pearson_gain_gene_methylation_pca", "mean"),
            median_r2_gain=("r2_gain_gene_methylation_pca", "median"),
            mean_r2_gain=("r2_gain_gene_methylation_pca", "mean"),
            gene_methylation_better_pearson_seeds=("pearson_gain_gene_methylation_pca", lambda x: int((x > 0).sum())),
            gene_methylation_better_r2_seeds=("r2_gain_gene_methylation_pca", lambda x: int((x > 0).sum())),
        )
        .reset_index()
        .sort_values(["median_pearson_gain", "median_r2_gain"], ascending=False)
    )
    return model_summary, trait_summary


def write_report(
    args: argparse.Namespace,
    genes: pd.DataFrame,
    methyl_pcs: pd.DataFrame,
    variance: pd.DataFrame,
    seeds: list[int],
    model_summary: pd.DataFrame,
    trait_summary: pd.DataFrame,
) -> None:
    top_gain = trait_summary.head(10)
    report = f"""# ZEAMAP v0.1 gene methylation PCA experiment

日期：2026-06-05

## Setup

- Annotation: Ensembl Plants release 47 `Zea_mays.B73_RefGen_v4.47.chr.gff3.gz`
- Genes: {len(genes)}
- Region types: gene body, promoter upstream {args.promoter_bp} bp, cis-window +/- {args.cis_bp} bp
- Methylation contexts: mCG, mCHG, mCHH
- Methylation-covered accessions: {len(methyl_pcs)}
- PCA features: {len([c for c in methyl_pcs.columns if c != "accession_id_norm"])}
- Seeds: {", ".join(map(str, seeds))}
- Traits: 66 robust selected traits

## Model Summary

```text
{model_summary.to_string(index=False)}
```

## Top 10 Trait Gains From Gene Methylation PCA

```text
{top_gain.to_string(index=False)}
```

## PCA Variance Summary

```text
{variance.groupby(["context", "region_type"]).agg(components=("component", "count"), final_cumulative_variance=("cumulative_explained_variance_ratio", "max")).reset_index().to_string(index=False)}
```

## Interpretation

- This uses gene/promoter/cis-window methylation aggregation compressed by PCA.
- If this does not materially improve over genotype+population, methylation likely needs trait-specific sparse feature selection or higher-resolution promoter/gene windows instead of more global PCs.

## Outputs

- `data/processed/v0_1/b73_refgen_v4_gene_windows.tsv`
- `data/processed/v0_1/methylation_gene_region_pca.tsv`
- `data/processed/v0_1/methylation_gene_region_pca_variance.tsv`
- `results/v0_1_baseline/gene_methylation_pca_metrics.tsv`
- `results/v0_1_baseline/gene_methylation_pca_model_summary.tsv`
- `results/v0_1_baseline/gene_methylation_pca_trait_summary.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    genes = load_genes(args.promoter_bp, args.cis_bp)
    mask = pd.read_csv(V01 / "modality_mask.tsv", sep="\t")
    accessions = sorted(mask.loc[mask["has_any_methylation"].astype(bool), "accession_id_norm"].astype(str).tolist())
    methyl_pcs, variance = build_pca_features(args, genes, accessions)

    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    pca = pd.read_csv(V01 / "genotype_pca.tsv", sep="\t")
    pop = build_population_features(population)
    base = pca.merge(pop, on="accession_id_norm", how="left")
    robust = pd.read_csv(RESULTS / "robust_selected_traits.tsv", sep="\t")
    robust_traits = robust["trait"].astype(str).tolist()

    metrics = pd.concat(
        [
            run_seed(seed, phenotype, population, robust_traits, base, methyl_pcs, args.min_train_n, args.min_eval_n)
            for seed in seeds
        ],
        ignore_index=True,
    )
    model_summary, trait_summary = summarize(metrics)
    metrics.to_csv(RESULTS / "gene_methylation_pca_metrics.tsv", sep="\t", index=False)
    model_summary.to_csv(RESULTS / "gene_methylation_pca_model_summary.tsv", sep="\t", index=False)
    trait_summary.to_csv(RESULTS / "gene_methylation_pca_trait_summary.tsv", sep="\t", index=False)
    (RESULTS / "gene_methylation_pca_run_config.json").write_text(
        json.dumps(vars(args), indent=2), encoding="utf-8"
    )
    write_report(args, genes, methyl_pcs, variance, seeds, model_summary, trait_summary)


if __name__ == "__main__":
    main()
