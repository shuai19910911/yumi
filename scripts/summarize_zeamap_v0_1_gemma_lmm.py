#!/usr/bin/env python3
"""Summarize ZEAMAP v0.1 GEMMA LMM GWAS outputs for paper-oriented review."""

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


RAW_DIR = RESULTS / "gemma_v0_1"
OUT_DIR = RESULTS / "gemma_lmm_v0_1"
FIG_DIR = OUT_DIR / "figures"
REPORT = Path("docs/2026-06-05-zeamap-v0-1-gemma-lmm-report.md")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=RAW_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--p-column", default="")
    parser.add_argument("--clump-window-bp", type=int, default=250000)
    parser.add_argument("--clump-r2", type=float, default=0.2)
    parser.add_argument("--max-leads-per-trait", type=int, default=100)
    parser.add_argument("--cis-bp", type=int, default=10000)
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


def choose_p_column(gwas: pd.DataFrame, requested: str) -> str:
    if requested:
        if requested not in gwas.columns:
            raise ValueError(f"Requested p column is absent: {requested}")
        return requested
    for column in ("p_lrt", "p_wald", "p_score", "p_wald_firth", "p"):
        if column in gwas.columns:
            return column
    raise ValueError(f"No recognized p-value column in GEMMA output: {list(gwas.columns)}")


def safe_trait_name(trait: str) -> str:
    return trait.replace("/", "_").replace(":", "_")


def read_manifest() -> pd.DataFrame:
    manifest_path = V01 / "gemma_gwas_v0_1" / "phenotype_manifest.tsv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Missing GEMMA phenotype manifest: {manifest_path}")
    return pd.read_csv(manifest_path, sep="\t")


def read_gemma_trait(raw_dir: Path, trait: str, p_column: str, variants: pd.DataFrame) -> tuple[pd.DataFrame, str]:
    assoc_path = raw_dir / f"{trait}.gemma_lmm.assoc.txt"
    if not assoc_path.exists():
        raise FileNotFoundError(f"Missing GEMMA association output: {assoc_path}")
    gwas = pd.read_csv(assoc_path, sep=r"\s+", engine="python")
    chosen_p = choose_p_column(gwas, p_column)
    gwas = gwas.rename(columns={"rs": "variant_id", chosen_p: "p_value"})
    gwas = gwas.drop(columns=[x for x in ("chr", "ps") if x in gwas.columns])
    gwas = gwas.merge(variants[["variant_id", "chrom", "pos"]], on="variant_id", how="left")
    gwas = gwas.rename(columns={"chrom": "chr"})
    gwas["trait"] = trait
    gwas["minus_log10_p"] = -np.log10(np.maximum(gwas["p_value"].to_numpy(dtype=float), np.finfo(float).tiny))
    gwas["q_value_bh"] = bh_fdr(gwas["p_value"].to_numpy(dtype=float))
    return gwas, chosen_p


def plot_manhattan(gwas: pd.DataFrame, trait: str, bonferroni: float, out: Path) -> None:
    work = gwas[["chr", "pos", "minus_log10_p"]].copy()
    work["chr"] = work["chr"].astype(str)
    chroms = [str(i) for i in range(1, 11)]
    offsets = {}
    ticks = []
    tick_labels = []
    offset = 0
    for chrom in chroms:
        sub = work[work["chr"] == chrom]
        if sub.empty:
            continue
        offsets[chrom] = offset
        ticks.append(offset + sub["pos"].max() / 2)
        tick_labels.append(chrom)
        offset += int(sub["pos"].max()) + 1_000_000
    work["plot_pos"] = [row.pos + offsets.get(str(row.chr), 0) for row in work.itertuples(index=False)]
    fig, ax = plt.subplots(figsize=(11, 4))
    colors = ["#2f5597", "#c55a11"]
    for i, chrom in enumerate(chroms):
        sub = work[work["chr"] == chrom]
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


def ld_clump_trait(gwas: pd.DataFrame, x: np.ndarray, variant_to_index: dict[str, int], window_bp: int, r2_threshold: float, max_leads: int) -> pd.DataFrame:
    ordered = gwas.sort_values(["p_value", "minus_log10_p"], ascending=[True, False]).reset_index(drop=True)
    selected: list[pd.Series] = []
    selected_meta: list[tuple[str, int, int]] = []
    for _, row in ordered.iterrows():
        if len(selected) >= max_leads:
            break
        variant_id = str(row["variant_id"])
        if variant_id not in variant_to_index:
            continue
        variant_idx = int(variant_to_index[variant_id])
        chrom = str(row["chr"])
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
    out.insert(2, "variant_index", [variant_to_index[str(v)] for v in out["variant_id"]])
    return out


def summarize_trait(gwas: pd.DataFrame, trait: str, n_non_missing: int, p_source_column: str) -> dict[str, float | int | str]:
    p_value = gwas["p_value"].to_numpy(dtype=float)
    chi2 = stats.chi2.isf(np.clip(p_value, np.finfo(float).tiny, 1.0), df=1)
    finite_chi = chi2[np.isfinite(chi2)]
    bonf = 0.05 / len(gwas)
    return {
        "trait": trait,
        "n_non_missing": int(n_non_missing),
        "variants_tested": int(len(gwas)),
        "p_source_column": p_source_column,
        "bonferroni_0_05": float(bonf),
        "fdr_0_05_hits": int((gwas["q_value_bh"] <= 0.05).sum()),
        "bonferroni_hits": int((gwas["p_value"] <= bonf).sum()),
        "min_p_value": float(np.nanmin(p_value)),
        "lambda_gc": float(np.median(finite_chi) / stats.chi2.ppf(0.5, df=1)) if len(finite_chi) else np.nan,
    }


def write_report(summary: pd.DataFrame, leads: pd.DataFrame, gene_summary: pd.DataFrame, args: argparse.Namespace) -> None:
    baseline_path = RESULTS / "gwas_v0_1" / "gwas_summary.tsv"
    comparison_text = "Covariate-adjusted baseline summary was not found."
    if baseline_path.exists():
        baseline = pd.read_csv(baseline_path, sep="\t")[["trait", "lambda_gc", "bonferroni_hits", "fdr_0_05_hits"]]
        merged = baseline.merge(
            summary[["trait", "lambda_gc", "bonferroni_hits", "fdr_0_05_hits"]],
            on="trait",
            how="inner",
            suffixes=("_covariate_lm", "_gemma_lmm"),
        )
        comparison_text = merged.to_string(index=False)

    lambda_median = float(summary["lambda_gc"].median()) if not summary.empty else np.nan
    min_lambda = float(summary["lambda_gc"].min()) if not summary.empty else np.nan
    max_lambda = float(summary["lambda_gc"].max()) if not summary.empty else np.nan
    top_leads = leads.head(40).to_string(index=False) if not leads.empty else "No lead SNPs retained."
    top_genes = gene_summary.head(40).to_string(index=False) if not gene_summary.empty else "No mapped lead genes."

    report = f"""# ZEAMAP v0.1 GEMMA LMM GWAS

日期：2026-06-05

## Purpose

This is the paper-oriented mixed-linear-model GWAS upgrade for the ZEAMAP v0.1 oil-trait analysis. It uses GEMMA with a genotype-derived relatedness matrix, population covariates, multiple-testing correction, LD clumping, B73 RefGen_v4 gene mapping, and Manhattan/QQ plots.

## Setup

- Raw GEMMA directory: `{args.raw_dir}`
- Summary directory: `{args.out_dir}`
- Traits: {len(summary)}
- SNPs tested per trait: {int(summary["variants_tested"].median()) if not summary.empty else "NA"}
- GEMMA p-value column used: `{summary["p_source_column"].iloc[0] if not summary.empty else "NA"}`
- Bonferroni threshold: 0.05 / tested SNPs
- FDR: Benjamini-Hochberg q <= 0.05
- LD clumping: +/- {args.clump_window_bp} bp, r2 < {args.clump_r2}, max {args.max_leads_per_trait} lead SNPs per trait
- Gene mapping: B73 RefGen_v4 gene/promoter/cis windows, cis threshold {args.cis_bp} bp

## Trait-Level Summary

```text
{summary.to_string(index=False)}
```

## Lambda GC Assessment

- GEMMA LMM lambda GC range: {min_lambda:.3f}-{max_lambda:.3f}
- GEMMA LMM median lambda GC: {lambda_median:.3f}
- Interpretation rule for manuscript use: lambda GC close to 1 with clean QQ plots is acceptable; persistent inflation requires stricter model/QC before making locus claims.

## Covariate LM vs GEMMA LMM

```text
{comparison_text}
```

## Top Lead SNPs

```text
{top_leads}
```

## Top Lead Genes

```text
{top_genes}
```

## Paper-Readiness Assessment

- GEMMA LMM is the current manuscript-facing GWAS baseline; the earlier covariate-only linear GWAS is kept only as a diagnostic baseline.
- Lead SNPs are manuscript candidates only if lambda GC/QQ are acceptable and the locus remains after LD clumping.
- Final paper claims still need biological interpretation, candidate-gene literature checks, and preferably an external or split/cohort replication strategy.

## Outputs

- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_gene_summary.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/figures/*manhattan.png`
- `results/v0_1_baseline/gemma_lmm_v0_1/figures/*qq.png`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    manifest = read_manifest()
    x, _samples, variants = load_standardized_genotype()
    variant_to_index = dict(zip(variants["variant_id"].astype(str), variants["variant_index"].astype(int), strict=False))
    genes = pd.read_csv(V01 / "b73_refgen_v4_gene_windows.tsv", sep="\t")

    summary_rows = []
    lead_frames = []
    for row in manifest.itertuples(index=False):
        trait = str(row.trait)
        gwas, p_source = read_gemma_trait(args.raw_dir, trait, args.p_column, variants)
        summary_row = summarize_trait(gwas, trait, int(row.non_missing), p_source)
        summary_rows.append(summary_row)
        bonf = float(summary_row["bonferroni_0_05"])
        trait_name = safe_trait_name(trait)
        plot_manhattan(gwas, trait, bonf, FIG_DIR / f"{trait_name}.manhattan.png")
        plot_qq(gwas, trait, FIG_DIR / f"{trait_name}.qq.png")
        leads = ld_clump_trait(gwas, x, variant_to_index, args.clump_window_bp, args.clump_r2, args.max_leads_per_trait)
        if not leads.empty:
            leads = leads.rename(columns={"chr": "chrom"})
            leads = map_variant_to_gene(leads, genes, args.cis_bp)
            lead_frames.append(leads)

    summary = pd.DataFrame(summary_rows).sort_values(["min_p_value", "trait"], ascending=[True, True])
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
            min_distance_to_gene_bp=("distance_to_gene_bp", "min"),
        )
        .reset_index()
        .sort_values(["trait", "min_p_value", "lead_snps"], ascending=[True, True, False])
        if not leads_all.empty
        else pd.DataFrame()
    )

    summary.to_csv(args.out_dir / "gemma_lmm_summary.tsv", sep="\t", index=False)
    leads_all.to_csv(args.out_dir / "gemma_lmm_lead_snps.tsv", sep="\t", index=False)
    gene_summary.to_csv(args.out_dir / "gemma_lmm_gene_summary.tsv", sep="\t", index=False)
    (args.out_dir / "gemma_lmm_summary_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    write_report(summary, leads_all, gene_summary, args)


if __name__ == "__main__":
    main()
