#!/usr/bin/env python3
"""Train-split SNP correlation attribution for ZEAMAP v0.1 top traits."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from run_zeamap_v0_1_baseline import V01, RESULTS, make_splits
from run_zeamap_v0_1_gene_methylation_pca import parse_seeds


REPORT = Path("docs/2026-06-05-zeamap-v0-1-genotype-attribution-report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-traits", type=int, default=15)
    parser.add_argument("--top-snps-per-seed", type=int, default=200)
    parser.add_argument("--report-top-snps-per-trait", type=int, default=50)
    parser.add_argument("--cis-bp", type=int, default=10000)
    parser.add_argument("--seeds", default="20260605,20260606,20260607,20260608,20260609")
    return parser.parse_args()


def load_standardized_genotype() -> tuple[np.ndarray, pd.DataFrame, pd.DataFrame]:
    npz = np.load(V01 / "genotype_dosage_int8.npz", allow_pickle=False)
    x = npz["dosage"].T.astype(np.float32)
    missing = x < 0
    if missing.any():
        means = np.nanmean(np.where(missing, np.nan, x), axis=0).astype(np.float32)
        rows, cols = np.where(missing)
        x[rows, cols] = means[cols]
    mean = x.mean(axis=0, dtype=np.float64).astype(np.float32)
    std = x.std(axis=0, dtype=np.float64).astype(np.float32)
    std[std < 1e-8] = 1.0
    x -= mean
    x /= std
    samples = pd.read_csv(V01 / "genotype_samples.tsv", sep="\t")
    variants = pd.read_csv(V01 / "genotype_variants.tsv", sep="\t")
    return x, samples, variants


def target_traits(top_n: int) -> list[str]:
    final = pd.read_csv(RESULTS / "final_v0_1_trait_benchmark.tsv", sep="\t")
    return final.sort_values(["ridge_median_pearson", "ridge_median_r2"], ascending=False)["trait"].head(top_n).tolist()


def compute_seed_x_stats(x: np.ndarray, train_idx: np.ndarray) -> np.ndarray:
    x_train = x[train_idx, :]
    x_mean = x_train.mean(axis=0)
    x_centered = x_train - x_mean
    return np.sum(x_centered * x_centered, axis=0)


def top_correlations(x: np.ndarray, train_idx: np.ndarray, y: np.ndarray, x_sumsq: np.ndarray, top_n: int) -> tuple[np.ndarray, np.ndarray]:
    y_train = y[train_idx]
    valid = np.isfinite(y_train)
    idx = train_idx[valid]
    y_valid = y_train[valid].astype(np.float64)
    y_centered = y_valid - y_valid.mean()
    y_sumsq = float(np.sum(y_centered * y_centered))
    if len(idx) < 25 or y_sumsq <= 1e-12:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    numer = x[idx, :].T @ y_centered.astype(np.float32)
    denom = np.sqrt(np.maximum(x_sumsq, 1e-12) * y_sumsq)
    corr = np.divide(numer, denom, out=np.zeros_like(numer, dtype=np.float32), where=denom > 1e-12)
    finite = np.where(np.isfinite(corr))[0]
    if len(finite) == 0:
        return np.array([], dtype=int), np.array([], dtype=np.float32)
    n = min(top_n, len(finite))
    top = finite[np.argsort(np.abs(corr[finite]))[-n:]][::-1]
    return top, corr[top]


def map_variant_to_gene(summary: pd.DataFrame, genes: pd.DataFrame, cis_bp: int) -> pd.DataFrame:
    genes_by_chrom = {str(chrom): frame.reset_index(drop=True) for chrom, frame in genes.groupby("chrom")}
    mapped_rows = []
    for row in summary.itertuples(index=False):
        chrom = str(row.chrom)
        pos = int(row.pos)
        chrom_genes = genes_by_chrom.get(chrom)
        gene_id = ""
        relation = "intergenic"
        distance = np.nan
        if chrom_genes is not None:
            pos0 = pos - 1
            in_gene = chrom_genes[(chrom_genes["gene_start0"] <= pos0) & (pos0 < chrom_genes["gene_end"])]
            if not in_gene.empty:
                best = in_gene.iloc[0]
                gene_id = best["gene_id"]
                relation = "gene_body"
                distance = 0
            else:
                in_promoter = chrom_genes[(chrom_genes["promoter_start0"] <= pos0) & (pos0 < chrom_genes["promoter_end"])]
                if not in_promoter.empty:
                    best = in_promoter.iloc[0]
                    gene_id = best["gene_id"]
                    relation = "promoter"
                    distance = 0
                else:
                    starts = chrom_genes["start_1based"].to_numpy()
                    ends = chrom_genes["end_1based"].to_numpy()
                    dist = np.minimum(np.abs(starts - pos), np.abs(ends - pos))
                    best_i = int(np.argmin(dist))
                    best = chrom_genes.iloc[best_i]
                    gene_id = best["gene_id"]
                    distance = int(dist[best_i])
                    relation = "cis_window" if distance <= cis_bp else "nearest"
        mapped = row._asdict()
        mapped.update({"nearest_gene_id": gene_id, "gene_relation": relation, "distance_to_gene_bp": distance})
        mapped_rows.append(mapped)
    return pd.DataFrame(mapped_rows)


def write_report(args: argparse.Namespace, traits: list[str], snp_summary: pd.DataFrame, gene_summary: pd.DataFrame) -> None:
    top_snps = snp_summary.head(30)
    top_genes = gene_summary.head(30)
    report = f"""# ZEAMAP v0.1 genotype attribution screen

日期：2026-06-05

## Setup

- Target traits: top {len(traits)} final benchmark traits by ridge median Pearson
- Seeds: {args.seeds}
- Per seed: top {args.top_snps_per_seed} SNPs by absolute train-split SNP-trait correlation
- Output per trait: top {args.report_top_snps_per_trait} stable SNPs after seed aggregation
- Gene mapping: B73 RefGen_v4 gene/promoter/cis windows, cis threshold {args.cis_bp} bp

## Target Traits

```text
{chr(10).join(traits)}
```

## Top SNP Candidates

```text
{top_snps.to_string(index=False)}
```

## Top Gene Candidates

```text
{top_genes.to_string(index=False)}
```

## Interpretation

- This is an exploratory attribution screen, not a formal GWAS.
- Correlations are computed only on train splits for each seed and then aggregated, reducing direct test-set leakage.
- Stable SNP/gene candidates should be treated as hypotheses for later validation with stricter association models or external biological evidence.

## Outputs

- `results/v0_1_baseline/genotype_attribution_snp_summary.tsv`
- `results/v0_1_baseline/genotype_attribution_gene_summary.tsv`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    seeds = parse_seeds(args.seeds)
    traits = target_traits(args.top_traits)
    x, samples, variants = load_standardized_genotype()
    sample_to_idx = {sample: i for i, sample in enumerate(samples["accession_id_norm"].astype(str))}
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t")
    phenotype = phenotype.set_index("accession_id_norm")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")

    rows = []
    for seed in seeds:
        split = make_splits(population, seed)
        train_ids = split.loc[split["split"] == "train", "accession_id_norm"].astype(str)
        train_idx = np.array([sample_to_idx[xid] for xid in train_ids if xid in sample_to_idx], dtype=int)
        x_sumsq = compute_seed_x_stats(x, train_idx)
        for trait in traits:
            y = phenotype.reindex(samples["accession_id_norm"].astype(str))[trait].to_numpy(dtype=float)
            top_idx, corr = top_correlations(x, train_idx, y, x_sumsq, args.top_snps_per_seed)
            for rank, variant_idx in enumerate(top_idx, start=1):
                rows.append(
                    {
                        "seed": seed,
                        "trait": trait,
                        "seed_rank": rank,
                        "variant_index": int(variant_idx),
                        "train_correlation": float(corr[rank - 1]),
                        "abs_train_correlation": float(abs(corr[rank - 1])),
                    }
                )

    selected = pd.DataFrame(rows)
    selected = selected.merge(variants, on="variant_index", how="left")
    summary = (
        selected.groupby(["trait", "variant_index", "chrom", "pos", "variant_id", "ref", "alt", "info_maf", "info_ns"])
        .agg(
            selected_seeds=("seed", "nunique"),
            mean_train_correlation=("train_correlation", "mean"),
            mean_abs_train_correlation=("abs_train_correlation", "mean"),
            max_abs_train_correlation=("abs_train_correlation", "max"),
            median_seed_rank=("seed_rank", "median"),
        )
        .reset_index()
        .sort_values(["trait", "selected_seeds", "mean_abs_train_correlation"], ascending=[True, False, False])
    )
    summary = summary.groupby("trait", group_keys=False).head(args.report_top_snps_per_trait).reset_index(drop=True)

    genes = pd.read_csv(V01 / "b73_refgen_v4_gene_windows.tsv", sep="\t")
    summary = map_variant_to_gene(summary, genes, args.cis_bp)
    gene_summary = (
        summary.groupby(["trait", "nearest_gene_id", "gene_relation"])
        .agg(
            variants=("variant_id", "nunique"),
            max_selected_seeds=("selected_seeds", "max"),
            mean_abs_train_correlation=("mean_abs_train_correlation", "mean"),
            min_distance_to_gene_bp=("distance_to_gene_bp", "min"),
        )
        .reset_index()
        .sort_values(["trait", "max_selected_seeds", "variants", "mean_abs_train_correlation"], ascending=[True, False, False, False])
    )

    summary.to_csv(RESULTS / "genotype_attribution_snp_summary.tsv", sep="\t", index=False)
    gene_summary.to_csv(RESULTS / "genotype_attribution_gene_summary.tsv", sep="\t", index=False)
    write_report(args, traits, summary, gene_summary)


if __name__ == "__main__":
    main()
