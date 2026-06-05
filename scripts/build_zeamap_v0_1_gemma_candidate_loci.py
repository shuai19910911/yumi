#!/usr/bin/env python3
"""Build manuscript-facing candidate loci and Nature-style summary figures."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from urllib.parse import unquote

import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GEMMA_DIR = ROOT / "results/v0_1_baseline/gemma_lmm_v0_1"
GWAS_DIR = ROOT / "results/v0_1_baseline/gwas_v0_1"
ATTR_GENE = ROOT / "results/v0_1_baseline/genotype_attribution_gene_summary.tsv"
ATTR_SNP = ROOT / "results/v0_1_baseline/genotype_attribution_snp_summary.tsv"
GFF = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/reference/B73_RefGen_v4/Zea_mays.B73_RefGen_v4.47.chr.gff3.gz")
OUT_DIR = GEMMA_DIR / "candidate_loci"
FIG_DIR = GEMMA_DIR / "manuscript_figures"
REPORT = ROOT / "docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gemma-dir", type=Path, default=GEMMA_DIR)
    parser.add_argument("--covariate-gwas-dir", type=Path, default=GWAS_DIR)
    parser.add_argument("--gff", type=Path, default=GFF)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--fig-dir", type=Path, default=FIG_DIR)
    parser.add_argument("--locus-window-bp", type=int, default=1_000_000)
    parser.add_argument("--suggestive-p", type=float, default=1e-5)
    return parser.parse_args()


def setup_nature_rc() -> None:
    mpl.rcParams.update(
        {
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            "font.family": "sans-serif",
            "font.sans-serif": ["Arial", "Helvetica", "DejaVu Sans"],
            "font.size": 7,
            "axes.labelsize": 7,
            "axes.titlesize": 8,
            "xtick.labelsize": 6,
            "ytick.labelsize": 6,
            "legend.fontsize": 6,
            "figure.dpi": 120,
            "savefig.dpi": 600,
            "savefig.bbox": "tight",
            "savefig.pad_inches": 0.04,
            "axes.linewidth": 0.5,
            "xtick.major.width": 0.5,
            "ytick.major.width": 0.5,
            "xtick.major.size": 2.2,
            "ytick.major.size": 2.2,
            "lines.linewidth": 1.0,
            "patch.linewidth": 0.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def parse_gff_attributes(attr: str) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in str(attr).split(";"):
        if not item or "=" not in item:
            continue
        key, value = item.split("=", 1)
        out[key] = unquote(value).replace("%2C", ",").replace("%3B", ";")
    return out


def load_gene_annotations(gff: Path) -> pd.DataFrame:
    rows = []
    opener = gzip.open if gff.suffix == ".gz" else open
    with opener(gff, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            attrs = parse_gff_attributes(fields[8])
            gene_id = attrs.get("gene_id") or attrs.get("ID", "").replace("gene:", "")
            if not gene_id:
                continue
            rows.append(
                {
                    "gene_id": gene_id,
                    "gene_chrom": fields[0],
                    "gene_start": int(fields[3]),
                    "gene_end": int(fields[4]),
                    "strand": fields[6],
                    "gene_biotype": attrs.get("biotype", ""),
                    "gene_description": attrs.get("description", ""),
                    "annotation_source": "Ensembl Plants release 47 B73 RefGen_v4 GFF3",
                }
            )
    return pd.DataFrame(rows).drop_duplicates("gene_id")


def significance_label(p: float, q: float, bonf: float, suggestive: float) -> str:
    if np.isfinite(p) and p <= bonf:
        return "bonferroni_0_05"
    if np.isfinite(q) and q <= 0.05:
        return "fdr_0_05"
    if np.isfinite(p) and p <= suggestive:
        return "suggestive_1e_5"
    return "nominal"


def functional_keyword_class(text: object) -> str:
    value = str(text or "").lower()
    groups = {
        "fatty_acid_lipid": [
            "fatty",
            "acyl",
            "lipid",
            "lipase",
            "linoleic",
            "thioesterase",
            "desaturase",
            "elongase",
            "ketoacyl",
            "wax",
            "galactolipase",
            "ceramidase",
            "sterol",
            "phospholipid",
            "oil",
        ],
        "seed_storage": ["seed", "storage protein", "oleosin"],
        "transport_membrane": ["abc transporter", "transporter", "membrane"],
        "hormone_stress_regulatory": ["ethylene", "auxin", "jasmonic", "transcription factor", "myb", "nac", "bzip"],
    }
    hits = [name for name, terms in groups.items() if any(term in value for term in terms)]
    return ";".join(hits) if hits else ""


def load_inputs(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary = pd.read_csv(args.gemma_dir / "gemma_lmm_summary.tsv", sep="\t")
    leads = pd.read_csv(args.gemma_dir / "gemma_lmm_lead_snps.tsv", sep="\t")
    gene_annot = load_gene_annotations(args.gff)
    attr_gene = pd.read_csv(ATTR_GENE, sep="\t") if ATTR_GENE.exists() else pd.DataFrame()
    attr_snp = pd.read_csv(ATTR_SNP, sep="\t") if ATTR_SNP.exists() else pd.DataFrame()
    attr = pd.DataFrame()
    if not attr_gene.empty:
        attr = attr_gene.rename(
            columns={
                "nearest_gene_id": "candidate_gene_id",
                "variants": "ridge_attribution_variants",
                "max_selected_seeds": "ridge_attribution_max_selected_seeds",
                "mean_abs_train_correlation": "ridge_attribution_mean_abs_train_correlation",
            }
        )
        keep = [
            "trait",
            "candidate_gene_id",
            "ridge_attribution_variants",
            "ridge_attribution_max_selected_seeds",
            "ridge_attribution_mean_abs_train_correlation",
        ]
        attr = attr[[col for col in keep if col in attr.columns]]
    if not attr_snp.empty:
        snp_counts = (
            attr_snp.groupby(["trait", "nearest_gene_id"], dropna=False)
            .agg(ridge_attribution_snp_hits=("variant_id", "nunique"))
            .reset_index()
            .rename(columns={"nearest_gene_id": "candidate_gene_id"})
        )
        attr = attr.merge(snp_counts, on=["trait", "candidate_gene_id"], how="outer") if not attr.empty else snp_counts
    return summary, leads, gene_annot, attr


def build_candidate_loci(args: argparse.Namespace) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    summary, leads, gene_annot, attr = load_inputs(args)
    bonf_by_trait = dict(zip(summary["trait"], summary["bonferroni_0_05"], strict=False))
    leads = leads.copy()
    leads["significance_class"] = [
        significance_label(row.p_value, row.q_value_bh, bonf_by_trait.get(row.trait, np.nan), args.suggestive_p)
        for row in leads.itertuples(index=False)
    ]
    keep_order = {"bonferroni_0_05": 0, "fdr_0_05": 1, "suggestive_1e_5": 2, "nominal": 3}
    leads["significance_rank"] = leads["significance_class"].map(keep_order).fillna(99).astype(int)
    leads = leads.sort_values(["trait", "chrom", "pos", "p_value"]).reset_index(drop=True)

    locus_ids = []
    locus_counter: dict[str, int] = {}
    last_key: tuple[str, str] | None = None
    last_end = -1
    for row in leads.itertuples(index=False):
        key = (str(row.trait), str(row.chrom))
        pos = int(row.pos)
        new_locus = key != last_key or pos - last_end > args.locus_window_bp
        if new_locus:
            locus_counter[row.trait] = locus_counter.get(row.trait, 0) + 1
            last_key = key
            last_end = pos
        else:
            last_end = max(last_end, pos)
        locus_ids.append(f"{row.trait}__L{locus_counter[row.trait]:03d}")
    leads["locus_id"] = locus_ids

    gene_cols = [
        "gene_id",
        "gene_chrom",
        "gene_start",
        "gene_end",
        "strand",
        "gene_biotype",
        "gene_description",
        "annotation_source",
    ]
    leads = leads.merge(gene_annot[gene_cols], left_on="nearest_gene_id", right_on="gene_id", how="left")
    leads = leads.rename(columns={"nearest_gene_id": "candidate_gene_id"})
    leads = leads.drop(columns=["gene_id"], errors="ignore")
    if not attr.empty:
        leads = leads.merge(attr, on=["trait", "candidate_gene_id"], how="left")
    leads["has_ridge_attribution_support"] = leads.get("ridge_attribution_snp_hits", pd.Series(index=leads.index, dtype=float)).fillna(0).astype(float) > 0

    loci_rows = []
    for locus_id, sub in leads.groupby("locus_id", sort=False):
        top = sub.sort_values(["p_value", "significance_rank"]).iloc[0]
        genes = [x for x in sub["candidate_gene_id"].dropna().astype(str).unique() if x and x != "nan"]
        desc = (
            sub[["candidate_gene_id", "gene_description"]]
            .dropna()
            .drop_duplicates()
            .assign(pair=lambda x: x["candidate_gene_id"] + ": " + x["gene_description"].replace("", "no description"))
        )
        loci_rows.append(
            {
                "locus_id": locus_id,
                "trait": top["trait"],
                "chrom": top["chrom"],
                "locus_start": int(sub["pos"].min()),
                "locus_end": int(sub["pos"].max()),
                "locus_span_bp": int(sub["pos"].max() - sub["pos"].min() + 1),
                "lead_snps_in_locus": int(sub["variant_id"].nunique()),
                "top_variant_id": top["variant_id"],
                "top_pos": int(top["pos"]),
                "top_p_value": float(top["p_value"]),
                "top_q_value_bh": float(top["q_value_bh"]),
                "top_minus_log10_p": float(top["minus_log10_p"]),
                "top_beta": top.get("beta", np.nan),
                "top_af": top.get("af", np.nan),
                "best_significance_class": top["significance_class"],
                "top_candidate_gene_id": top["candidate_gene_id"],
                "top_gene_relation": top["gene_relation"],
                "top_distance_to_gene_bp": top["distance_to_gene_bp"],
                "candidate_genes": ";".join(genes),
                "candidate_gene_count": len(genes),
                "candidate_gene_descriptions": " | ".join(desc["pair"].head(12).tolist()),
                "has_ridge_attribution_support": bool(sub["has_ridge_attribution_support"].any()),
                "ridge_supported_genes": ";".join(
                    sorted(sub.loc[sub["has_ridge_attribution_support"], "candidate_gene_id"].dropna().astype(str).unique())
                ),
            }
        )
    loci = pd.DataFrame(loci_rows).sort_values(["trait", "top_p_value", "locus_id"]).reset_index(drop=True)

    gene_summary = (
        leads.groupby(["trait", "locus_id", "candidate_gene_id"], dropna=False)
        .agg(
            lead_snps=("variant_id", "nunique"),
            min_p_value=("p_value", "min"),
            min_q_value_bh=("q_value_bh", "min"),
            best_significance_rank=("significance_rank", "min"),
            best_relation=("gene_relation", "first"),
            min_distance_to_gene_bp=("distance_to_gene_bp", "min"),
            has_ridge_attribution_support=("has_ridge_attribution_support", "max"),
            gene_description=("gene_description", "first"),
            gene_biotype=("gene_biotype", "first"),
            annotation_source=("annotation_source", "first"),
        )
        .reset_index()
        .sort_values(["trait", "min_p_value", "lead_snps"], ascending=[True, True, False])
    )
    inv_rank = {v: k for k, v in keep_order.items()}
    gene_summary["best_significance_class"] = gene_summary["best_significance_rank"].map(inv_rank)
    gene_summary["functional_keyword_class"] = gene_summary["gene_description"].map(functional_keyword_class)
    gene_keyword_map = (
        gene_summary[["trait", "locus_id", "candidate_gene_id", "functional_keyword_class"]]
        .dropna()
        .query("functional_keyword_class != ''")
    )
    if not gene_keyword_map.empty:
        keyword_by_locus = (
            gene_keyword_map.groupby("locus_id")["functional_keyword_class"]
            .apply(lambda x: ";".join(sorted(set(";".join(x).split(";")))))
            .to_dict()
        )
        loci["functional_keyword_classes"] = loci["locus_id"].map(keyword_by_locus).fillna("")
    else:
        loci["functional_keyword_classes"] = ""
    return loci, gene_summary, leads


def nature_panel_label(ax: mpl.axes.Axes, label: str) -> None:
    ax.text(-0.16, 1.08, label, transform=ax.transAxes, fontsize=8, fontweight="bold", va="top", ha="left")


def save_all(fig: mpl.figure.Figure, stem: Path) -> None:
    for suffix in (".pdf", ".svg", ".png"):
        fig.savefig(stem.with_suffix(suffix), dpi=600)


def plot_summary_figure(args: argparse.Namespace, loci: pd.DataFrame) -> None:
    setup_nature_rc()
    summary = pd.read_csv(args.gemma_dir / "gemma_lmm_summary.tsv", sep="\t")
    baseline_path = args.covariate_gwas_dir / "gwas_summary.tsv"
    cov = pd.read_csv(baseline_path, sep="\t") if baseline_path.exists() else pd.DataFrame()
    merged = summary.copy()
    if not cov.empty:
        merged = cov[["trait", "lambda_gc", "bonferroni_hits"]].merge(
            summary[["trait", "lambda_gc", "bonferroni_hits", "min_p_value"]],
            on="trait",
            suffixes=("_covariate", "_gemma"),
        )
    else:
        merged = summary.rename(columns={"lambda_gc": "lambda_gc_gemma", "bonferroni_hits": "bonferroni_hits_gemma"})
        merged["lambda_gc_covariate"] = np.nan
        merged["bonferroni_hits_covariate"] = np.nan

    trait_order = summary.sort_values("min_p_value")["trait"].tolist()
    short = [x.replace("agri_aa_oil__Oil_", "").replace("agri_aa_oil__Oil", "Oil") for x in trait_order]
    order_map = {trait: i for i, trait in enumerate(trait_order)}
    merged["order"] = merged["trait"].map(order_map)
    merged = merged.sort_values("order")
    manuscript_loci = loci[loci["best_significance_class"] != "nominal"].copy()
    sig_counts = (
        manuscript_loci.pivot_table(index="trait", columns="best_significance_class", values="locus_id", aggfunc="nunique", fill_value=0)
        .reindex(trait_order)
        .fillna(0)
    )
    for col in ["bonferroni_0_05", "fdr_0_05", "suggestive_1e_5"]:
        if col not in sig_counts.columns:
            sig_counts[col] = 0

    fig = plt.figure(figsize=(183 / 25.4, 122 / 25.4), constrained_layout=True)
    gs = fig.add_gridspec(2, 2, width_ratios=[1.05, 1.0], height_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    x = np.arange(len(merged))
    colors = {"cov": "#999999", "gemma": "#0072B2"}
    ax_a.plot(x, merged["lambda_gc_covariate"], "o-", color=colors["cov"], markersize=3, label="Covariate LM")
    ax_a.plot(x, merged["lambda_gc_gemma"], "o-", color=colors["gemma"], markersize=3, label="GEMMA LMM")
    ax_a.axhline(1.0, color="#333333", linewidth=0.6, linestyle=":")
    ax_a.set_xticks(x)
    ax_a.set_xticklabels(short, rotation=45, ha="right")
    ax_a.set_ylabel(r"$\lambda_{GC}$")
    ax_a.set_title("Genomic inflation")
    ax_a.legend(frameon=False, loc="upper right")
    nature_panel_label(ax_a, "a")

    width = 0.38
    ax_b.bar(x - width / 2, merged["bonferroni_hits_covariate"], width=width, color=colors["cov"], label="Covariate LM")
    ax_b.bar(x + width / 2, merged["bonferroni_hits_gemma"], width=width, color=colors["gemma"], label="GEMMA LMM")
    ax_b.set_yscale("log")
    ax_b.set_xticks(x)
    ax_b.set_xticklabels(short, rotation=45, ha="right")
    ax_b.set_ylabel("Bonferroni hits")
    ax_b.set_title("Lead signal contraction")
    ax_b.legend(frameon=False, loc="upper right")
    nature_panel_label(ax_b, "b")

    y = -np.log10(summary.set_index("trait").loc[trait_order, "min_p_value"].to_numpy(dtype=float))
    ax_c.bar(x, y, color="#009E73", edgecolor="black", linewidth=0.3)
    ax_c.set_xticks(x)
    ax_c.set_xticklabels(short, rotation=45, ha="right")
    ax_c.set_ylabel(r"Top $-\log_{10}(P_{LRT})$")
    ax_c.set_title("Strongest GEMMA association")
    nature_panel_label(ax_c, "c")

    bottom = np.zeros(len(trait_order), dtype=float)
    stack = [
        ("bonferroni_0_05", "Bonferroni", "#D55E00"),
        ("fdr_0_05", "FDR", "#E69F00"),
        ("suggestive_1e_5", "Suggestive", "#56B4E9"),
    ]
    for col, label, color in stack:
        vals = sig_counts[col].to_numpy(dtype=float)
        ax_d.bar(x, vals, bottom=bottom, color=color, edgecolor="black", linewidth=0.25, label=label)
        bottom += vals
    ax_d.set_xticks(x)
    ax_d.set_xticklabels(short, rotation=45, ha="right")
    ax_d.set_ylabel("Candidate loci")
    ax_d.set_title("Manuscript candidate loci")
    ax_d.legend(frameon=False, loc="upper right", ncol=1, borderaxespad=0.2)
    nature_panel_label(ax_d, "d")

    args.fig_dir.mkdir(parents=True, exist_ok=True)
    save_all(fig, args.fig_dir / "figure_gemma_lmm_summary_nature")
    plt.close(fig)


def write_report(args: argparse.Namespace, loci: pd.DataFrame, genes: pd.DataFrame, leads: pd.DataFrame) -> None:
    class_counts = loci["best_significance_class"].value_counts().to_dict()
    manuscript_loci = loci[loci["best_significance_class"] != "nominal"].copy()
    manuscript_genes = genes[genes["best_significance_class"] != "nominal"].copy()
    top_loci = loci.sort_values(["top_p_value", "trait"]).head(30)
    desc_missing = int(genes["gene_description"].fillna("").eq("").sum())
    manuscript_desc_missing = int(manuscript_genes["gene_description"].fillna("").eq("").sum())
    report = f"""# ZEAMAP v0.1 GEMMA candidate loci

日期：2026-06-05

## Purpose

This report converts GEMMA LMM lead SNPs into manuscript-facing candidate loci and candidate gene tables. It is the first Stage 5.4 result after the paper-oriented GWAS run.

## Inputs

- GEMMA lead SNP table: `{args.gemma_dir / "gemma_lmm_lead_snps.tsv"}`
- GEMMA trait summary: `{args.gemma_dir / "gemma_lmm_summary.tsv"}`
- Gene annotation source: `{args.gff}`
- Locus merge rule: same trait and chromosome, adjacent retained lead SNPs within {args.locus_window_bp:,} bp
- Suggestive threshold: p <= {args.suggestive_p}

## Outputs

- `{args.out_dir / "gemma_candidate_loci.tsv"}`
- `{args.out_dir / "gemma_manuscript_candidate_loci.tsv"}`
- `{args.out_dir / "gemma_candidate_genes.tsv"}`
- `{args.out_dir / "gemma_manuscript_candidate_genes.tsv"}`
- `{args.out_dir / "gemma_candidate_lead_snps_annotated.tsv"}`
- `{args.fig_dir / "figure_gemma_lmm_summary_nature.pdf"}`
- `{args.fig_dir / "figure_gemma_lmm_summary_nature.svg"}`
- `{args.fig_dir / "figure_gemma_lmm_summary_nature.png"}`

## Summary

- All candidate loci, including nominal clumped leads: {len(loci)}
- Manuscript candidate loci, excluding nominal leads: {len(manuscript_loci)}
- All candidate genes: {genes["candidate_gene_id"].nunique()}
- Manuscript candidate genes: {manuscript_genes["candidate_gene_id"].nunique()}
- Annotated lead SNPs: {len(leads)}
- Manuscript loci with ridge-attribution support: {int(manuscript_loci["has_ridge_attribution_support"].sum())}
- All candidate gene rows missing GFF description: {desc_missing}
- Manuscript candidate gene rows missing GFF description: {manuscript_desc_missing}
- Manuscript candidate gene rows with lipid/fatty-acid keyword: {int(manuscript_genes["functional_keyword_class"].fillna("").str.contains("fatty_acid_lipid").sum())}
- Locus classes: {json.dumps(class_counts, ensure_ascii=False)}

## Top Candidate Loci

```text
{top_loci[["locus_id", "trait", "chrom", "locus_start", "locus_end", "top_variant_id", "top_p_value", "best_significance_class", "top_candidate_gene_id", "top_gene_relation", "functional_keyword_classes", "candidate_gene_descriptions", "has_ridge_attribution_support"]].to_string(index=False)}
```

## Interpretation

- These loci are candidate loci, not causal variants.
- The strongest paper-ready subset is the Bonferroni/FDR-supported loci with clean GEMMA lambda GC and interpretable nearby genes.
- Functional annotation currently comes from the B73 RefGen_v4 Ensembl/Gramene GFF3 gene descriptions. Additional MaizeGDB/UniProt/Gramene pathway annotation can be layered on top for loci whose GFF description is missing or too generic.
- The generated summary figure uses Nature-style sizing, Type-42 embedded fonts for PDF, CVD-safe colors, and PDF/SVG/PNG outputs.
- Nominal loci are retained in the complete table for transparency, but the manuscript-facing table and figure focus on Bonferroni/FDR/suggestive loci.

## Next Step

Prioritize manual/automated literature annotation for the top Bonferroni loci, especially genes with descriptions related to lipid, fatty-acid, seed, acyltransferase, desaturase, elongase, wax, or membrane metabolism.
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.fig_dir.mkdir(parents=True, exist_ok=True)
    loci, genes, leads = build_candidate_loci(args)
    loci.to_csv(args.out_dir / "gemma_candidate_loci.tsv", sep="\t", index=False)
    genes.to_csv(args.out_dir / "gemma_candidate_genes.tsv", sep="\t", index=False)
    leads.to_csv(args.out_dir / "gemma_candidate_lead_snps_annotated.tsv", sep="\t", index=False)
    loci[loci["best_significance_class"] != "nominal"].to_csv(
        args.out_dir / "gemma_manuscript_candidate_loci.tsv", sep="\t", index=False
    )
    genes[genes["best_significance_class"] != "nominal"].to_csv(
        args.out_dir / "gemma_manuscript_candidate_genes.tsv", sep="\t", index=False
    )
    (args.out_dir / "candidate_loci_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")
    plot_summary_figure(args, loci)
    write_report(args, loci, genes, leads)


if __name__ == "__main__":
    main()
