#!/usr/bin/env python3
"""Covariate-adjusted GWAS baseline for ZEAMAP v0.1 paper-oriented analyses."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

from run_zeamap_v0_1_baseline import RESULTS, V01
from run_zeamap_v0_1_genotype_attribution import load_standardized_genotype, map_variant_to_gene


GWAS_DIR = RESULTS / "gwas_v0_1"
FIG_DIR = GWAS_DIR / "figures"
REPORT = Path("docs/2026-06-05-zeamap-v0-1-gwas-baseline-report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--trait-family", default="oil")
    parser.add_argument("--priority-tier", default="high")
    parser.add_argument("--max-traits", type=int, default=10)
    parser.add_argument("--covariates", default="PC1,PC2,PC3,K1,K2,K3")
    parser.add_argument("--clump-window-bp", type=int, default=250000)
    parser.add_argument("--clump-r2", type=float, default=0.2)
    parser.add_argument("--max-leads-per-trait", type=int, default=100)
    parser.add_argument("--cis-bp", type=int, default=10000)
    parser.add_argument("--reuse-per-trait", action="store_true")
    return parser.parse_args()


def bh_fdr(p_values: np.ndarray) -> np.ndarray:
    p = np.asarray(p_values, dtype=np.float64)
    out = np.full(len(p), np.nan, dtype=np.float64)
    valid = np.isfinite(p)
    pv = p[valid]
    order = np.argsort(pv)
    ranked = pv[order]
    n = len(ranked)
    q = ranked * n / np.arange(1, n + 1)
    q = np.minimum.accumulate(q[::-1])[::-1]
    q = np.clip(q, 0, 1)
    valid_idx = np.where(valid)[0]
    out[valid_idx[order]] = q
    return out


def target_traits(args: argparse.Namespace) -> list[str]:
    final = pd.read_csv(RESULTS / "final_v0_1_trait_benchmark.tsv", sep="\t")
    selected = final[(final["trait_family"] == args.trait_family) & (final["priority_tier"] == args.priority_tier)].copy()
    if selected.empty:
        selected = final[final["trait_family"] == args.trait_family].copy()
    return selected.sort_values(["ridge_median_pearson", "ridge_median_r2"], ascending=False)["trait"].head(args.max_traits).tolist()


def build_covariate_matrix(population: pd.DataFrame, sample_ids: pd.Series, covariate_cols: list[str]) -> pd.DataFrame:
    pop = population.set_index("accession_id_norm").reindex(sample_ids.astype(str))
    cov = pop[covariate_cols].apply(pd.to_numeric, errors="coerce")
    cov = cov.fillna(cov.median())
    cov.insert(0, "intercept", 1.0)
    return cov


def residualize(matrix: np.ndarray, covariates: np.ndarray) -> np.ndarray:
    q, _ = np.linalg.qr(covariates)
    return matrix - q @ (q.T @ matrix)


def gwas_one_trait(
    x: np.ndarray,
    y: np.ndarray,
    covariates: np.ndarray,
    variants: pd.DataFrame,
    trait: str,
) -> tuple[pd.DataFrame, dict[str, float | int | str]]:
    valid = np.isfinite(y)
    y_valid = y[valid].astype(np.float64)
    x_valid = x[valid, :].astype(np.float64)
    cov_valid = covariates[valid, :].astype(np.float64)

    y_res = residualize(y_valid.reshape(-1, 1), cov_valid).ravel()
    x_res = residualize(x_valid, cov_valid)
    y_res = y_res - y_res.mean()
    x_res = x_res - x_res.mean(axis=0)

    y_sumsq = float(np.sum(y_res * y_res))
    x_sumsq = np.sum(x_res * x_res, axis=0)
    denom = np.sqrt(np.maximum(x_sumsq, 1e-12) * y_sumsq)
    corr = np.divide(x_res.T @ y_res, denom, out=np.zeros(x.shape[1], dtype=np.float64), where=denom > 1e-12)
    corr = np.clip(corr, -0.999999, 0.999999)
    df = max(1, int(valid.sum()) - cov_valid.shape[1] - 1)
    t_stat = corr * np.sqrt(df / np.maximum(1.0 - corr * corr, 1e-12))
    p_value = 2.0 * stats.t.sf(np.abs(t_stat), df=df)
    q_value = bh_fdr(p_value)
    minus_log10_p = -np.log10(np.maximum(p_value, np.finfo(float).tiny))

    result = variants.copy()
    result.insert(0, "trait", trait)
    result["n_non_missing"] = int(valid.sum())
    result["beta_residual_scale"] = corr
    result["partial_correlation"] = corr
    result["t_stat"] = t_stat
    result["p_value"] = p_value
    result["q_value_bh"] = q_value
    result["minus_log10_p"] = minus_log10_p

    chi2 = stats.chi2.isf(np.clip(p_value, np.finfo(float).tiny, 1.0), df=1)
    finite_chi = chi2[np.isfinite(chi2)]
    lambda_gc = float(np.median(finite_chi) / stats.chi2.ppf(0.5, df=1)) if len(finite_chi) else np.nan
    bonf = 0.05 / len(result)
    summary = {
        "trait": trait,
        "n_non_missing": int(valid.sum()),
        "variants_tested": int(len(result)),
        "bonferroni_0_05": float(bonf),
        "fdr_0_05_hits": int((result["q_value_bh"] <= 0.05).sum()),
        "bonferroni_hits": int((result["p_value"] <= bonf).sum()),
        "min_p_value": float(np.nanmin(p_value)),
        "lambda_gc": lambda_gc,
    }
    return result, summary


def ld_clump_trait(gwas: pd.DataFrame, x: np.ndarray, window_bp: int, r2_threshold: float, max_leads: int) -> pd.DataFrame:
    ordered = gwas.sort_values(["p_value", "minus_log10_p"], ascending=[True, False]).reset_index(drop=True)
    selected: list[pd.Series] = []
    selected_meta: list[tuple[str, int, int]] = []
    for _, row in ordered.iterrows():
        if len(selected) >= max_leads:
            break
        variant_idx = int(row["variant_index"])
        chrom = str(row["chrom"])
        pos = int(row["pos"])
        dosage = x[:, variant_idx]
        dosage_centered = dosage - dosage.mean()
        dosage_ss = float(np.dot(dosage_centered, dosage_centered))
        keep = True
        for kept_chrom, kept_pos, kept_variant_idx in selected_meta:
            if kept_chrom != chrom or abs(kept_pos - pos) > window_bp:
                continue
            kept_dosage = x[:, kept_variant_idx]
            kept_centered = kept_dosage - kept_dosage.mean()
            kept_ss = float(np.dot(kept_centered, kept_centered))
            if dosage_ss <= 1e-12 or kept_ss <= 1e-12:
                continue
            r = float(np.dot(dosage_centered, kept_centered) / np.sqrt(dosage_ss * kept_ss))
            if r * r >= r2_threshold:
                keep = False
                break
        if keep:
            selected_meta.append((chrom, pos, variant_idx))
            selected.append(row)
    if not selected:
        return pd.DataFrame(columns=gwas.columns)
    out = pd.DataFrame(selected).reset_index(drop=True)
    out.insert(1, "lead_rank", np.arange(1, len(out) + 1))
    return out


def plot_manhattan(gwas: pd.DataFrame, trait: str, bonferroni: float, out: Path) -> None:
    work = gwas[["chrom", "pos", "minus_log10_p"]].copy()
    work["chrom"] = work["chrom"].astype(str)
    chroms = [str(i) for i in range(1, 11)]
    offsets = {}
    ticks = []
    tick_labels = []
    offset = 0
    for chrom in chroms:
        sub = work[work["chrom"] == chrom]
        if sub.empty:
            continue
        offsets[chrom] = offset
        ticks.append(offset + sub["pos"].max() / 2)
        tick_labels.append(chrom)
        offset += int(sub["pos"].max()) + 1_000_000
    work["plot_pos"] = [row.pos + offsets.get(row.chrom, 0) for row in work.itertuples(index=False)]
    colors = ["#2f5597", "#c55a11"]
    fig, ax = plt.subplots(figsize=(11, 4))
    for i, chrom in enumerate(chroms):
        sub = work[work["chrom"] == chrom]
        ax.scatter(sub["plot_pos"], sub["minus_log10_p"], s=4, c=colors[i % 2], linewidths=0, alpha=0.8)
    ax.axhline(-np.log10(bonferroni), color="#7f0000", linestyle="--", linewidth=1)
    ax.set_xticks(ticks)
    ax.set_xticklabels(tick_labels)
    ax.set_xlabel("Chromosome")
    ax.set_ylabel("-log10(P)")
    ax.set_title(trait)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def plot_qq(gwas: pd.DataFrame, trait: str, out: Path) -> None:
    p = gwas["p_value"].to_numpy(dtype=float)
    p = p[np.isfinite(p) & (p > 0) & (p <= 1)]
    observed = -np.log10(np.sort(p))
    expected = -np.log10((np.arange(1, len(p) + 1) - 0.5) / len(p))
    lim = max(float(np.nanmax(expected)), float(np.nanmax(observed))) * 1.02
    fig, ax = plt.subplots(figsize=(4.5, 4.5))
    ax.scatter(expected, observed, s=5, c="#2f5597", linewidths=0, alpha=0.8)
    ax.plot([0, lim], [0, lim], color="#7f7f7f", linewidth=1)
    ax.set_xlabel("Expected -log10(P)")
    ax.set_ylabel("Observed -log10(P)")
    ax.set_title(trait)
    fig.tight_layout()
    fig.savefig(out, dpi=180)
    plt.close(fig)


def write_report(args: argparse.Namespace, traits: list[str], summary: pd.DataFrame, leads: pd.DataFrame) -> None:
    report = f"""# ZEAMAP v0.1 covariate-adjusted GWAS baseline

日期：2026-06-05

## Purpose

This is the paper-oriented v0.1 GWAS baseline for the strongest ZEAMAP traits. It uses all non-missing accessions for each trait, adjusts phenotype and SNP dosage for population covariates, applies genome-wide multiple-testing thresholds, performs LD clumping, maps lead SNPs to B73 RefGen_v4 genes, and writes Manhattan/QQ plots.

## Setup

- Target family/tier: {args.trait_family} / {args.priority_tier}
- Traits: {len(traits)}
- Covariates: {args.covariates}
- SNPs tested per trait: 199,856
- Bonferroni threshold: 0.05 / tested SNPs
- FDR: Benjamini-Hochberg q <= 0.05
- LD clumping: +/- {args.clump_window_bp} bp, r2 < {args.clump_r2}, max {args.max_leads_per_trait} lead SNPs per trait
- Gene mapping: B73 RefGen_v4 gene/promoter/cis windows, cis threshold {args.cis_bp} bp

## Target Traits

```text
{chr(10).join(traits)}
```

## Trait-Level Summary

```text
{summary.to_string(index=False)}
```

## Top Lead SNPs

```text
{leads.head(40).to_string(index=False) if not leads.empty else "No lead SNPs retained."}
```

## Paper-Readiness Assessment

- This is suitable as a reproducible v0.1 covariate-adjusted GWAS baseline.
- Before a final manuscript claim, run a mixed-linear-model GWAS with kinship correction, compare lambda GC/QQ plots, and check whether lead loci replicate across model specifications.
- Lead SNPs and mapped genes are paper candidates, not causal claims by themselves.

## Outputs

- `results/v0_1_baseline/gwas_v0_1/gwas_summary.tsv`
- `results/v0_1_baseline/gwas_v0_1/gwas_lead_snps.tsv`
- `results/v0_1_baseline/gwas_v0_1/gwas_gene_summary.tsv`
- `results/v0_1_baseline/gwas_v0_1/per_trait/*.tsv`
- `results/v0_1_baseline/gwas_v0_1/figures/*manhattan.png`
- `results/v0_1_baseline/gwas_v0_1/figures/*qq.png`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    GWAS_DIR.mkdir(parents=True, exist_ok=True)
    (GWAS_DIR / "per_trait").mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)

    traits = target_traits(args)
    x, samples, variants = load_standardized_genotype()
    phenotype = pd.read_csv(V01 / "phenotype.tsv", sep="\t").set_index("accession_id_norm")
    population = pd.read_csv(V01 / "population.tsv", sep="\t")
    covariate_cols = [x.strip() for x in args.covariates.split(",") if x.strip()]
    covariates = build_covariate_matrix(population, samples["accession_id_norm"], covariate_cols).to_numpy(dtype=float)
    genes = pd.read_csv(V01 / "b73_refgen_v4_gene_windows.tsv", sep="\t")

    summary_rows = []
    lead_frames = []
    for trait in traits:
        out_name = trait.replace("/", "_").replace(":", "_")
        per_trait_path = GWAS_DIR / "per_trait" / f"{out_name}.gwas.tsv"
        if args.reuse_per_trait and per_trait_path.exists():
            gwas = pd.read_csv(per_trait_path, sep="\t")
            bonf = 0.05 / len(gwas)
            p_value = gwas["p_value"].to_numpy(dtype=float)
            chi2 = stats.chi2.isf(np.clip(p_value, np.finfo(float).tiny, 1.0), df=1)
            finite_chi = chi2[np.isfinite(chi2)]
            trait_summary = {
                "trait": trait,
                "n_non_missing": int(gwas["n_non_missing"].iloc[0]),
                "variants_tested": int(len(gwas)),
                "bonferroni_0_05": float(bonf),
                "fdr_0_05_hits": int((gwas["q_value_bh"] <= 0.05).sum()),
                "bonferroni_hits": int((gwas["p_value"] <= bonf).sum()),
                "min_p_value": float(np.nanmin(p_value)),
                "lambda_gc": float(np.median(finite_chi) / stats.chi2.ppf(0.5, df=1)) if len(finite_chi) else np.nan,
            }
        else:
            y = phenotype.reindex(samples["accession_id_norm"].astype(str))[trait].to_numpy(dtype=float)
            gwas, trait_summary = gwas_one_trait(x, y, covariates, variants, trait)
            gwas = map_variant_to_gene(gwas, genes, args.cis_bp)
            gwas.to_csv(per_trait_path, sep="\t", index=False)
        leads = ld_clump_trait(gwas, x, args.clump_window_bp, args.clump_r2, args.max_leads_per_trait)
        if not leads.empty:
            lead_frames.append(leads)
        plot_manhattan(gwas, trait, trait_summary["bonferroni_0_05"], FIG_DIR / f"{out_name}.manhattan.png")
        plot_qq(gwas, trait, FIG_DIR / f"{out_name}.qq.png")
        summary_rows.append(trait_summary)

    summary = pd.DataFrame(summary_rows)
    leads_all = pd.concat(lead_frames, ignore_index=True) if lead_frames else pd.DataFrame()
    if not leads_all.empty:
        leads_all = leads_all.sort_values(["trait", "p_value", "lead_rank"], ascending=[True, True, True])
    gene_summary = (
        leads_all.groupby(["trait", "nearest_gene_id", "gene_relation"], dropna=False)
        .agg(
            lead_snps=("variant_id", "nunique"),
            min_p_value=("p_value", "min"),
            min_q_value_bh=("q_value_bh", "min"),
            max_minus_log10_p=("minus_log10_p", "max"),
            mean_abs_partial_correlation=("partial_correlation", lambda x: float(np.mean(np.abs(x)))),
            min_distance_to_gene_bp=("distance_to_gene_bp", "min"),
        )
        .reset_index()
        .sort_values(["trait", "min_p_value", "lead_snps"], ascending=[True, True, False])
        if not leads_all.empty
        else pd.DataFrame()
    )

    summary.to_csv(GWAS_DIR / "gwas_summary.tsv", sep="\t", index=False)
    leads_all.to_csv(GWAS_DIR / "gwas_lead_snps.tsv", sep="\t", index=False)
    gene_summary.to_csv(GWAS_DIR / "gwas_gene_summary.tsv", sep="\t", index=False)
    (GWAS_DIR / "gwas_run_config.json").write_text(json.dumps(vars(args), indent=2), encoding="utf-8")
    write_report(args, traits, summary, leads_all)


if __name__ == "__main__":
    main()
