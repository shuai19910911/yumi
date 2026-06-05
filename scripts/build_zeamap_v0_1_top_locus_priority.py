#!/usr/bin/env python3
"""Prioritize GEMMA candidate loci and draw Nature-style regional locus figures."""

from __future__ import annotations

import argparse
import gzip
import json
from pathlib import Path
from urllib.parse import unquote

import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd

from run_zeamap_v0_1_baseline import RESULTS, V01
from run_zeamap_v0_1_genotype_attribution import load_standardized_genotype


ROOT = Path(__file__).resolve().parents[1]
GEMMA_SUMMARY_DIR = RESULTS / "gemma_lmm_v0_1"
RAW_GEMMA_DIR = RESULTS / "gemma_v0_1"
CANDIDATE_DIR = GEMMA_SUMMARY_DIR / "candidate_loci"
OUT_DIR = GEMMA_SUMMARY_DIR / "top_loci"
FIG_DIR = GEMMA_SUMMARY_DIR / "regional_figures"
REPORT = ROOT / "docs/2026-06-05-zeamap-v0-1-top-locus-priority-report.md"
GFF = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/reference/B73_RefGen_v4/Zea_mays.B73_RefGen_v4.47.chr.gff3.gz")


LITERATURE_EVIDENCE = [
    {
        "evidence_id": "Hui2013_NatGenet_oil_GWAS",
        "url": "https://www.ars.usda.gov/research/publications/publication/?seqNo115=281966",
        "evidence_scope": "maize_oil_gwas",
        "summary": "GWAS identified genes influencing maize kernel oil content and fatty acid composition; validated genes included DGAT1-2, FATB and FAD2.",
        "applies_to_keywords": "DGAT1-2;FATB;FAD2;ACP;LACS;WRI1a;COPII;oil;fatty acid",
    },
    {
        "evidence_id": "Alrefai1995_Genome_fatty_acid_QTL",
        "url": "https://pubmed.ncbi.nlm.nih.gov/18470215/",
        "evidence_scope": "maize_fatty_acid_qtl",
        "summary": "A chromosome 6 QTL near linoleic acid1 explained a large fraction of 18:1/18:2 ratio variation in maize kernel oil.",
        "applies_to_keywords": "linoleic acid1;ln1;C18_1;C18_2;chromosome 6",
    },
    {
        "evidence_id": "Liu2023_Frontiers_oil_QTL",
        "url": "https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full",
        "evidence_scope": "maize_oil_qtl_candidate_genes",
        "summary": "Maize oil QTL review/analysis notes qHO6 encoding DGAT1-2, QTL-Pal9 with FATB/acyl-ACP thioesterase, and KCS/FAD/SACD/LACS genes in oil-related QTL intervals.",
        "applies_to_keywords": "DGAT1-2;FATB;acyl-ACP thioesterase;KCS;FAD;SACD;LACS;TAG",
    },
    {
        "evidence_id": "Frontiers2023_maize_oil_composition",
        "url": "https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full",
        "evidence_scope": "maize_oil_trait_context",
        "summary": "Maize oil mainly accumulates in embryo and is dominated by palmitic, stearic, oleic, linoleic and linolenic acids.",
        "applies_to_keywords": "C16_0;C18_0;C18_1;C18_2;C18_3;oil",
    },
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidate-dir", type=Path, default=CANDIDATE_DIR)
    parser.add_argument("--raw-gemma-dir", type=Path, default=RAW_GEMMA_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--fig-dir", type=Path, default=FIG_DIR)
    parser.add_argument("--gff", type=Path, default=GFF)
    parser.add_argument("--top-regions", type=int, default=8)
    parser.add_argument("--regional-window-bp", type=int, default=2_000_000)
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
            "axes.spines.top": False,
            "axes.spines.right": False,
        }
    )


def save_all(fig: mpl.figure.Figure, stem: Path) -> None:
    for suffix in (".pdf", ".svg", ".png"):
        fig.savefig(stem.with_suffix(suffix), dpi=600)


def parse_attrs(attr: str) -> dict[str, str]:
    out = {}
    for item in attr.split(";"):
        if "=" in item:
            key, value = item.split("=", 1)
            out[key] = unquote(value).replace("%2C", ",").replace("%3B", ";")
    return out


def load_gene_models(gff: Path) -> pd.DataFrame:
    rows = []
    opener = gzip.open if gff.suffix == ".gz" else open
    with opener(gff, "rt", encoding="utf-8", errors="replace") as handle:
        for line in handle:
            if not line or line.startswith("#"):
                continue
            fields = line.rstrip("\n").split("\t")
            if len(fields) != 9 or fields[2] != "gene":
                continue
            attrs = parse_attrs(fields[8])
            gene_id = attrs.get("gene_id") or attrs.get("ID", "").replace("gene:", "")
            rows.append(
                {
                    "gene_id": gene_id,
                    "chrom": str(fields[0]),
                    "start": int(fields[3]),
                    "end": int(fields[4]),
                    "strand": fields[6],
                    "description": attrs.get("description", ""),
                }
            )
    return pd.DataFrame(rows)


def read_assoc(raw_dir: Path, trait: str, variants: pd.DataFrame) -> pd.DataFrame:
    path = raw_dir / f"{trait}.gemma_lmm.assoc.txt"
    gwas = pd.read_csv(path, sep=r"\s+", engine="python")
    p_col = "p_lrt" if "p_lrt" in gwas.columns else "p_wald"
    gwas = gwas.rename(columns={"rs": "variant_id", p_col: "p_value"})
    gwas = gwas.drop(columns=[x for x in ("chr", "ps") if x in gwas.columns], errors="ignore")
    gwas = gwas.merge(variants[["variant_id", "chrom", "pos"]], on="variant_id", how="left")
    gwas["trait"] = trait
    gwas["minus_log10_p"] = -np.log10(np.maximum(gwas["p_value"].astype(float), np.finfo(float).tiny))
    return gwas


def rank_loci(loci: pd.DataFrame, genes: pd.DataFrame) -> pd.DataFrame:
    loci = loci.copy()
    gene_recurrence = (
        loci.groupby("top_candidate_gene_id")
        .agg(recurrent_traits=("trait", "nunique"), recurrent_loci=("locus_id", "nunique"), recurrent_min_p=("top_p_value", "min"))
        .reset_index()
    )
    loci = loci.merge(gene_recurrence, on="top_candidate_gene_id", how="left")
    class_score = {"bonferroni_0_05": 40, "fdr_0_05": 18, "suggestive_1e_5": 6}
    loci["priority_score"] = 0.0
    loci["priority_score"] += loci["best_significance_class"].map(class_score).fillna(0)
    loci["priority_score"] += np.minimum(loci["top_minus_log10_p"].astype(float), 30)
    loci["priority_score"] += loci["has_ridge_attribution_support"].astype(bool).astype(int) * 18
    loci["priority_score"] += loci["functional_keyword_classes"].fillna("").str.contains("fatty_acid_lipid").astype(int) * 25
    loci["priority_score"] += loci["functional_keyword_classes"].fillna("").str.contains("transport_membrane").astype(int) * 6
    loci["priority_score"] += loci["functional_keyword_classes"].fillna("").str.contains("hormone_stress_regulatory").astype(int) * 4
    loci["priority_score"] += np.maximum(loci["recurrent_traits"].fillna(1).astype(int) - 1, 0) * 8
    loci["priority_score"] += np.log10(np.maximum(loci["candidate_gene_count"].fillna(1).astype(float), 1))

    lipid_genes = genes[genes["functional_keyword_class"].fillna("").str.contains("fatty_acid_lipid")]
    lipid_by_locus = (
        lipid_genes.groupby("locus_id")["candidate_gene_id"].apply(lambda x: ";".join(sorted(set(x.dropna().astype(str))))).to_dict()
    )
    loci["lipid_keyword_genes"] = loci["locus_id"].map(lipid_by_locus).fillna("")
    loci["priority_tier"] = pd.cut(
        loci["priority_score"],
        bins=[-np.inf, 60, 90, np.inf],
        labels=["tier3_supporting", "tier2_strong", "tier1_main_text"],
    )
    return loci.sort_values(["priority_score", "top_p_value"], ascending=[False, True]).reset_index(drop=True)


def build_region_table(priority: pd.DataFrame, top_n: int) -> pd.DataFrame:
    work = priority.copy()
    work["region_key"] = work.apply(
        lambda r: f"chr{r.chrom}:{int((r.locus_start + r.locus_end) // 2 // 2_000_000)}:{r.top_candidate_gene_id}",
        axis=1,
    )
    rows = []
    for _, sub in work.groupby("top_candidate_gene_id", sort=False):
        sub = sub.sort_values(["priority_score", "top_p_value"], ascending=[False, True])
        top = sub.iloc[0]
        rows.append(
            {
                "region_id": f"R{len(rows)+1:02d}_{top.top_candidate_gene_id}",
                "top_candidate_gene_id": top.top_candidate_gene_id,
                "chrom": str(top.chrom),
                "region_center": int(top.top_pos),
                "region_start": int(max(1, top.top_pos - 2_000_000)),
                "region_end": int(top.top_pos + 2_000_000),
                "traits": ";".join(sorted(sub["trait"].unique())),
                "loci": ";".join(sub["locus_id"].astype(str)),
                "best_p_value": float(sub["top_p_value"].min()),
                "best_variant_id": top.top_variant_id,
                "best_trait": top.trait,
                "priority_score": float(top.priority_score),
                "priority_tier": str(top.priority_tier),
                "functional_keyword_classes": top.functional_keyword_classes,
                "lipid_keyword_genes": top.lipid_keyword_genes,
                "has_ridge_attribution_support": bool(sub["has_ridge_attribution_support"].any()),
                "candidate_gene_descriptions": top.candidate_gene_descriptions,
            }
        )
        if len(rows) >= top_n:
            break
    return pd.DataFrame(rows)


def plot_region(region: pd.Series, traits: list[str], genes: pd.DataFrame, x: np.ndarray, variant_to_idx: dict[str, int], variants: pd.DataFrame, args: argparse.Namespace) -> None:
    setup_nature_rc()
    chrom = str(region.chrom)
    start = int(region.region_start)
    end = int(region.region_end)
    lead_id = str(region.best_variant_id)
    lead_idx = variant_to_idx.get(lead_id)
    if lead_idx is None:
        return
    lead_dosage = x[:, lead_idx]
    lead_centered = lead_dosage - lead_dosage.mean()
    lead_ss = float(np.dot(lead_centered, lead_centered))
    region_variants = variants[(variants["chrom"].astype(str) == chrom) & (variants["pos"] >= start) & (variants["pos"] <= end)].copy()
    r2_map = {}
    for row in region_variants.itertuples(index=False):
        idx = int(row.variant_index)
        dosage = x[:, idx]
        centered = dosage - dosage.mean()
        ss = float(np.dot(centered, centered))
        if ss <= 1e-12 or lead_ss <= 1e-12:
            r2 = np.nan
        else:
            r = float(np.dot(centered, lead_centered) / np.sqrt(ss * lead_ss))
            r2 = r * r
        r2_map[str(row.variant_id)] = r2

    trait_frames = []
    for trait in traits[:6]:
        assoc = read_assoc(args.raw_gemma_dir, trait, variants)
        assoc = assoc[(assoc["chrom"].astype(str) == chrom) & (assoc["pos"] >= start) & (assoc["pos"] <= end)].copy()
        assoc["ld_r2_to_lead"] = assoc["variant_id"].map(r2_map)
        trait_frames.append(assoc)
    plot_df = pd.concat(trait_frames, ignore_index=True)
    gene_df = genes[(genes["chrom"].astype(str) == chrom) & (genes["end"] >= start) & (genes["start"] <= end)].copy()

    fig = plt.figure(figsize=(183 / 25.4, 88 / 25.4), constrained_layout=True)
    gs = GridSpec(2, 1, figure=fig, height_ratios=[3.0, 1.0])
    ax = fig.add_subplot(gs[0])
    ax_gene = fig.add_subplot(gs[1], sharex=ax)

    cmap = mpl.colormaps["viridis"]
    for trait, sub in plot_df.groupby("trait", sort=False):
        ax.scatter(
            sub["pos"] / 1e6,
            sub["minus_log10_p"],
            c=sub["ld_r2_to_lead"].fillna(0),
            cmap=cmap,
            vmin=0,
            vmax=1,
            s=9,
            alpha=0.75,
            edgecolors="none",
            rasterized=True,
            label=trait.replace("agri_aa_oil__Oil_", "").replace("agri_aa_oil__Oil", "Oil"),
        )
    ax.axvline(int(region.region_center) / 1e6, color="#D55E00", linewidth=0.8, linestyle="--")
    ax.set_ylabel(r"$-\log_{10}(P_{LRT})$")
    ax.set_title(f"{region.region_id}: {region.top_candidate_gene_id} ({chrom}:{start:,}-{end:,})")
    ax.legend(frameon=False, ncol=3, loc="upper right", markerscale=1.2)
    sm = mpl.cm.ScalarMappable(cmap=cmap, norm=mpl.colors.Normalize(vmin=0, vmax=1))
    cb = fig.colorbar(sm, ax=ax, pad=0.01, shrink=0.78)
    cb.set_label(r"$r^2$ to lead SNP")

    y_levels = [0.8, 0.55, 0.3, 0.05]
    label_count = 0
    label_levels = [0.96, 0.76, 0.56, 0.36]
    for i, row in enumerate(gene_df.itertuples(index=False)):
        y = y_levels[i % len(y_levels)]
        color = "#D55E00" if str(row.gene_id) == str(region.top_candidate_gene_id) else "#4D4D4D"
        ax_gene.plot([row.start / 1e6, row.end / 1e6], [y, y], color=color, linewidth=1.4 if color == "#D55E00" else 0.8)
        desc = str(row.description)
        is_key_gene = str(row.gene_id) == str(region.top_candidate_gene_id)
        is_lipid_gene = any(term in desc.lower() for term in ("linoleic", "fatty", "acyl", "ketoacyl", "lipid", "dgat"))
        gene_center = (int(row.start) + int(row.end)) / 2
        near_lead = abs(gene_center - int(region.region_center)) <= 450_000
        if is_key_gene or (is_lipid_gene and near_lead):
            label = f"{row.gene_id}\n{desc[:32]}"
            label_y = label_levels[label_count % len(label_levels)]
            label_count += 1
            ax_gene.text((row.start + row.end) / 2 / 1e6, label_y, label, ha="center", va="bottom", fontsize=5.2, color=color)
    ax_gene.set_ylim(-0.05, 1.1)
    ax_gene.set_yticks([])
    ax_gene.set_xlabel(f"Chromosome {chrom} position (Mb)")
    ax_gene.set_ylabel("Genes")
    ax_gene.spines[["left", "right", "top"]].set_visible(False)

    args.fig_dir.mkdir(parents=True, exist_ok=True)
    stem = args.fig_dir / f"{region.region_id}_regional_locus_nature"
    save_all(fig, stem)
    plt.close(fig)


def write_report(priority: pd.DataFrame, regions: pd.DataFrame, args: argparse.Namespace) -> None:
    top = priority.head(30)
    literature = pd.DataFrame(LITERATURE_EVIDENCE)
    report = f"""# ZEAMAP v0.1 top locus priority and regional figures

日期：2026-06-05

## Purpose

This Stage 5.5 report prioritizes manuscript candidate loci for main-text interpretation and generates Nature-style regional association figures for the top loci.

## Inputs

- Manuscript candidate loci: `{args.candidate_dir / "gemma_manuscript_candidate_loci.tsv"}`
- Manuscript candidate genes: `{args.candidate_dir / "gemma_manuscript_candidate_genes.tsv"}`
- Raw GEMMA associations: `{args.raw_gemma_dir}`
- B73 RefGen_v4 GFF3: `{args.gff}`

## Priority Rules

The priority score combines GEMMA significance class, top -log10(P), ridge-attribution support, lipid/fatty-acid keyword support, recurrence across oil traits, and candidate-gene count. It is a ranking aid, not a new statistical test.

## Summary

- Prioritized loci: {len(priority)}
- Tier 1 main-text loci: {int((priority["priority_tier"] == "tier1_main_text").sum())}
- Tier 2 strong loci: {int((priority["priority_tier"] == "tier2_strong").sum())}
- Top regional figures generated: {len(regions)}

## Top Prioritized Loci

```text
{top[["locus_id", "trait", "chrom", "locus_start", "locus_end", "top_variant_id", "top_p_value", "best_significance_class", "top_candidate_gene_id", "priority_score", "priority_tier", "recurrent_traits", "functional_keyword_classes", "lipid_keyword_genes", "has_ridge_attribution_support"]].to_string(index=False)}
```

## Top Regional Figures

```text
{regions.to_string(index=False)}
```

## Literature Evidence Used For Automated Triage

```text
{literature.to_string(index=False)}
```

## Interpretation

- The chromosome 6 `Zm00001d036982` region is the strongest main-text candidate because it is recurrent across multiple oil traits, Bonferroni significant, lipid/fatty-acid annotated, and ridge-supported.
- Literature triage supports treating DGAT1-2/linoleic acid1-related chromosome 6 signals and FATB/acyl-ACP/KCS-type lipid-metabolism signals as high-priority candidate biology.
- Regional figures are association and LD-context visualizations. They are not fine-mapping or causal proof.

## Outputs

- `{args.out_dir / "gemma_top_locus_priority.tsv"}`
- `{args.out_dir / "gemma_top_region_targets.tsv"}`
- `{args.out_dir / "gemma_literature_evidence_seed.tsv"}`
- `{args.fig_dir}/*regional_locus_nature.pdf`
- `{args.fig_dir}/*regional_locus_nature.svg`
- `{args.fig_dir}/*regional_locus_nature.png`
"""
    REPORT.write_text(report, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.fig_dir.mkdir(parents=True, exist_ok=True)
    loci = pd.read_csv(args.candidate_dir / "gemma_manuscript_candidate_loci.tsv", sep="\t")
    genes = pd.read_csv(args.candidate_dir / "gemma_manuscript_candidate_genes.tsv", sep="\t")
    priority = rank_loci(loci, genes)
    regions = build_region_table(priority, args.top_regions)
    priority.to_csv(args.out_dir / "gemma_top_locus_priority.tsv", sep="\t", index=False)
    regions.to_csv(args.out_dir / "gemma_top_region_targets.tsv", sep="\t", index=False)
    pd.DataFrame(LITERATURE_EVIDENCE).to_csv(args.out_dir / "gemma_literature_evidence_seed.tsv", sep="\t", index=False)
    (args.out_dir / "top_locus_priority_config.json").write_text(json.dumps(vars(args), indent=2, default=str), encoding="utf-8")

    x, _samples, variants = load_standardized_genotype()
    variant_to_idx = dict(zip(variants["variant_id"].astype(str), variants["variant_index"].astype(int), strict=False))
    gene_models = load_gene_models(args.gff)
    for region in regions.itertuples(index=False):
        traits = str(region.traits).split(";")
        plot_region(pd.Series(region._asdict()), traits, gene_models, x, variant_to_idx, variants, args)
    write_report(priority, regions, args)


if __name__ == "__main__":
    main()
