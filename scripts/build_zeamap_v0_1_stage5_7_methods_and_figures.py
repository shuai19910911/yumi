#!/usr/bin/env python3
"""Build Stage 5.7 manuscript methods draft and first-pass main figures."""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib as mpl
import matplotlib.image as mpimg
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results/v0_1_baseline"
GEMMA = RESULTS / "gemma_lmm_v0_1"
OUT = GEMMA / "manuscript_figures_stage5_7"
REPORT = ROOT / "docs/2026-06-05-zeamap-v0-1-stage5-7-methods-figures-report.md"
METHODS = ROOT / "docs/2026-06-05-zeamap-v0-1-methods-draft.md"
FIG_PLAN = ROOT / "docs/2026-06-05-zeamap-v0-1-main-figure-plan.md"
CAPTIONS = ROOT / "docs/2026-06-05-zeamap-v0-1-figure-captions-draft.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", type=Path, default=OUT)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--methods", type=Path, default=METHODS)
    parser.add_argument("--figure-plan", type=Path, default=FIG_PLAN)
    return parser.parse_args()


def setup_rc() -> None:
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


def add_panel_label(ax: mpl.axes.Axes, label: str) -> None:
    ax.text(-0.12, 1.06, label, transform=ax.transAxes, fontsize=9, fontweight="bold", va="top", ha="left")


def figure1(out_dir: Path) -> None:
    setup_rc()
    model_summary = pd.read_csv(RESULTS / "lightweight_model_summary.tsv", sep="\t")
    family = pd.read_csv(RESULTS / "final_v0_1_family_summary.tsv", sep="\t")

    fig = plt.figure(figsize=(183 / 25.4, 132 / 25.4), constrained_layout=True)
    gs = GridSpec(2, 2, figure=fig, width_ratios=[1.15, 1.0], height_ratios=[1.0, 1.0])
    ax_a = fig.add_subplot(gs[0, 0])
    ax_b = fig.add_subplot(gs[0, 1])
    ax_c = fig.add_subplot(gs[1, 0])
    ax_d = fig.add_subplot(gs[1, 1])

    # Panel a: compact workflow and cohort sizes.
    ax_a.axis("off")
    boxes = [
        ("ZEAMAP\nprocessed data", 0.04, 0.74, "#dcecc9"),
        ("ID harmonization\n461 accessions", 0.36, 0.74, "#f6e8a6"),
        ("v0.1 matrix\n199,856 SNPs", 0.68, 0.74, "#cfe4f4"),
        ("Prediction\n66 robust traits", 0.20, 0.30, "#ead7f2"),
        ("Oil-trait GWAS\n10 traits, n=440", 0.54, 0.30, "#f4d2c2"),
    ]
    for text, x, y, color in boxes:
        ax_a.add_patch(plt.Rectangle((x, y), 0.26, 0.16, fc=color, ec="#444444", lw=0.6))
        ax_a.text(x + 0.13, y + 0.08, text, ha="center", va="center", fontsize=7)
    arrows = [((0.30, 0.82), (0.36, 0.82)), ((0.62, 0.82), (0.68, 0.82)), ((0.49, 0.74), (0.32, 0.46)), ((0.81, 0.74), (0.67, 0.46))]
    for start, end in arrows:
        ax_a.annotate("", xy=end, xytext=start, arrowprops=dict(arrowstyle="-|>", lw=0.7, color="#444444"))
    ax_a.set_xlim(0, 1)
    ax_a.set_ylim(0, 1)
    add_panel_label(ax_a, "a")

    # Panel b: modality/sample counts.
    labels = ["Strong paired\naccessions", "Methylation\ncoverage", "SNPs\n(x1,000)", "Numeric\ntraits"]
    vals = [461, 236, 199.856, 318]
    colors = ["#3b7ea1", "#8c6bb1", "#4c956c", "#d08b36"]
    ax_b.bar(np.arange(len(vals)), vals, color=colors, width=0.66)
    ax_b.set_xticks(np.arange(len(vals)))
    ax_b.set_xticklabels(labels)
    ax_b.set_ylabel("Count")
    ax_b.set_title("v0.1 data scale")
    for i, v in enumerate(vals):
        ax_b.text(i, v + max(vals) * 0.035, f"{v:g}", ha="center", va="bottom", fontsize=6)
    ax_b.set_ylim(0, 520)
    add_panel_label(ax_b, "b")

    # Panel c: model benchmark.
    model_order = [
        "genotype_population_ridge",
        "genotype_population_elasticnet",
        "population_ridge",
        "genotype_population_small_mlp",
    ]
    plot_models = model_summary.set_index("model").loc[model_order].reset_index()
    y = np.arange(len(plot_models))
    ax_c.barh(y - 0.16, plot_models["median_pearson"], height=0.3, color="#3b7ea1", label="Pearson")
    ax_c.barh(y + 0.16, plot_models["median_r2"], height=0.3, color="#d08b36", label="R2")
    ax_c.axvline(0, color="#333333", lw=0.6)
    ax_c.set_yticks(y)
    ax_c.set_yticklabels(["Ridge\nG+P", "ElasticNet\nG+P", "Ridge\nP only", "Small MLP\nG+P"])
    ax_c.invert_yaxis()
    ax_c.set_xlabel("Median test metric")
    ax_c.set_title("Model comparison on 66 robust traits")
    ax_c.legend(frameon=False, loc="lower right")
    add_panel_label(ax_c, "c")

    # Panel d: trait-family performance.
    fam = family.copy()
    x = np.arange(len(fam))
    width = 0.35
    ax_d.bar(x - width / 2, fam["median_ridge_pearson"], width=width, color="#3b7ea1", label="Pearson")
    ax_d.bar(x + width / 2, fam["median_ridge_r2"], width=width, color="#d08b36", label="R2")
    ax_d.set_xticks(x)
    ax_d.set_xticklabels([s.replace("_", "\n") for s in fam["trait_family"]])
    ax_d.set_ylabel("Median metric")
    ax_d.set_ylim(0, 0.68)
    ax_d.set_title("Ridge benchmark by trait family")
    ax_d.legend(frameon=False, loc="upper right")
    add_panel_label(ax_d, "d")

    save_all(fig, out_dir / "figure1_dataset_prediction_nature")
    plt.close(fig)


def figure3(out_dir: Path) -> None:
    setup_rc()
    r01 = GEMMA / "regional_figures/R01_Zm00001d036982_regional_locus_nature.png"
    r08 = GEMMA / "regional_figures/R08_Zm00001d045383_regional_locus_nature.png"
    img1 = mpimg.imread(r01)
    img2 = mpimg.imread(r08)

    fig = plt.figure(figsize=(183 / 25.4, 110 / 25.4), constrained_layout=True)
    gs = GridSpec(1, 2, figure=fig, width_ratios=[1, 1])
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(gs[0, 1])]
    for ax, img, label, title in zip(
        axes,
        [img1, img2],
        ["a", "b"],
        ["chr6 linoleic acid1 candidate interval", "chr9 C16:0 fatty acyl-ACP thioesterase interval"],
    ):
        ax.imshow(img)
        ax.axis("off")
        ax.set_title(title, fontsize=8, pad=2)
        ax.text(-0.02, 1.02, label, transform=ax.transAxes, fontsize=9, fontweight="bold", va="bottom", ha="left")
    save_all(fig, out_dir / "figure3_chr6_chr9_regional_loci_nature")
    plt.close(fig)


def write_methods(path: Path) -> None:
    text = """# ZEAMAP v0.1 Methods Draft

日期：2026-06-05

## Data Acquisition And Accession Harmonization

ZEAMAP processed public data were downloaded from CNGBdb project CNP0001565. We focused on accession-level genotype, population, phenotype and metabolome tables. Sample identifiers were inspected across tables and harmonized to a unified accession index. Accessions were retained for the v0.1 dataset when they had genotype, population covariates and at least one phenotype or metabolome measurement. The resulting v0.1 dataset contained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric phenotype/metabolome traits. DNA methylation coverage was tracked as a modality mask for 236 accessions but was not used as a default main-model input.

## Prediction Benchmark

We evaluated accession-level genotype-to-phenotype prediction using train/validation/test splits and repeated multi-seed benchmarking. Genotype features were combined with population covariates where indicated. The main comparison included genotype+population ridge regression, genotype+population ElasticNet, population-only ridge regression and a small multilayer perceptron. Traits were first screened for predictability and then retained as robust traits when performance was stable across seeds. The final benchmark used 66 robust traits and selected genotype+population ridge regression as the primary model because it provided stable test performance and avoided the overfitting observed for the small neural network.

## Methylation Ablation

Methylation was assessed through global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection. Because methylation coverage was available for only 236 accessions and raw sparse methylation features were unstable, methylation was retained as an auxiliary ablation and interpretation modality rather than as a default input to the v0.1 primary model.

## Oil-Trait GWAS

Ten high-priority oil-related traits were selected for association analysis based on the final prediction benchmark. A covariate-only GWAS was first run with PC1-PC3 and K1-K3 covariates to diagnose inflation. Because this model showed severe genomic inflation, the main GWAS used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Association testing used GEMMA likelihood-ratio p-values (`p_lrt`). For each oil trait, 440 non-missing accessions and 199,856 SNPs were tested. Bonferroni and Benjamini-Hochberg FDR thresholds were calculated per trait.

## Candidate-Locus Annotation

GEMMA lead SNPs were clumped into physical loci by trait and chromosome. Candidate genes were assigned using B73 RefGen_v4 gene models, including gene-body, promoter and cis-window relationships. Gene descriptions and biotypes were parsed from the local Ensembl/Gramene GFF3 file. Candidate loci were classified by significance level, ridge-attribution overlap and functional keyword classes. Nominal-only loci were excluded from manuscript-facing candidate-locus tables.

## Top-Locus Prioritization And Evidence Levels

Manuscript candidate loci were ranked using GEMMA significance class, association strength, recurrence across oil traits, ridge-attribution overlap, lipid/fatty-acid keyword support and candidate-gene count. This priority score was used only for manuscript triage and was not treated as a new statistical test. Eight regional loci were selected for regional visualization and evidence curation. Evidence levels were assigned conservatively according to whether the locus had direct prior oil/fatty-acid support, indirect lipid-related annotation, recurrent statistical support or only statistical evidence.

## Regional Association Figures

Regional association figures were drawn for top loci using GEMMA p-values within a fixed local window around the lead SNP. SNPs were coloured by LD r2 to the lead SNP, computed from standardized genotype dosages in the v0.1 dataset. Gene tracks were drawn from B73 RefGen_v4 gene models, with labels restricted to local candidate genes and lipid-related genes to avoid over-annotation. Figures were exported as PDF, SVG and high-resolution PNG with Nature-style double-column sizing and Type-42 font settings.

## Claim Boundary

All reported loci are interpreted as candidate loci or candidate genes. The current analysis does not perform fine-mapping, experimental validation, transgenic tests or biochemical assays. Therefore, no lead SNP is described as causal and no candidate gene is described as experimentally validated by this study.
"""
    path.write_text(text, encoding="utf-8")


def write_figure_plan(path: Path) -> None:
    text = """# ZEAMAP v0.1 Main Figure Plan

日期：2026-06-05

## Figure 1: Dataset And Prediction Benchmark

File:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf`

Panels:

- a: ZEAMAP processed data to v0.1 benchmark/GWAS workflow.
- b: v0.1 data scale: 461 paired accessions, 236 methylation-covered accessions, 199,856 SNPs and 318 numeric traits.
- c: model comparison on 66 robust traits.
- d: ridge benchmark by trait family, highlighting oil traits as the strongest family.

Main message:

Oil traits are the most stable prediction target family, justifying focused oil-trait GWAS.

## Figure 2: GEMMA LMM GWAS Calibration And Candidate-Locus Summary

Current file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf`

Main message:

Covariate-only GWAS was inflated, GEMMA LMM controlled lambda GC near 1, and 184 manuscript candidate loci were identified after excluding nominal-only loci.

Next polish:

- Keep this as the statistical GWAS summary figure.
- Add a clean figure caption tying lambda GC, Bonferroni/FDR hits and candidate-locus counts together.

## Figure 3: Top Regional Candidate Intervals

File:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf`

Panels:

- a: chr6 `Zm00001d036982` / linoleic acid1 candidate interval.
- b: chr9 C16:0 candidate interval containing nearby `Zm00001d045387` fatty acyl-ACP thioesterase2.

Main message:

The strongest prioritized loci include a recurrent chr6 fatty-acid candidate interval and a biologically focused chr9 C16:0 FatB/acyl-ACP-thioesterase candidate interval.

## Table Plan

- Table 1: `top_regional_loci_evidence.tsv`
- Supplementary Table 1: `supplementary_manuscript_candidate_loci.tsv`
- Supplementary Table 2: `main_tier1_locus_table.tsv`
"""
    path.write_text(text, encoding="utf-8")


def write_captions(path: Path) -> None:
    text = """# ZEAMAP v0.1 Figure Captions Draft

日期：2026-06-05

## Figure 1. ZEAMAP v0.1 dataset construction and prediction benchmark.

a, Overview of the ZEAMAP processed-data workflow used to construct the accession-level v0.1 benchmark and downstream oil-trait GWAS. b, Scale of the v0.1 dataset, including 461 strongly paired accessions, 236 accessions with methylation coverage, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. c, Median test performance of candidate prediction models across 66 robust traits. Genotype+population ridge and ElasticNet models outperformed the population-only baseline, whereas the small multilayer perceptron showed poorer R2 under the current sample size. d, Trait-family performance of the final genotype+population ridge benchmark. Oil-related traits showed the strongest median Pearson correlation and R2, motivating focused GEMMA mixed-linear-model GWAS for oil traits.

## Figure 2. GEMMA mixed-linear-model GWAS calibration and candidate-locus summary.

a, Comparison of genomic inflation between the diagnostic covariate-only GWAS and GEMMA LMM across 10 high-priority oil traits. b, Per-trait GEMMA LMM association summary, including Bonferroni and FDR-significant signals. c, Manuscript candidate-locus classes after merging GEMMA lead SNPs and excluding nominal-only loci. d, Functional and prediction-attribution support among manuscript candidate loci. GEMMA LMM controlled genomic inflation near lambda GC = 1 and produced a manuscript candidate-locus set for downstream annotation.

## Figure 3. Prioritized regional candidate intervals for maize oil traits.

a, Regional association plot for the chr6 `Zm00001d036982` / linoleic acid1 candidate interval. Points show GEMMA LMM association strength for local SNPs and are coloured by LD r2 to the lead SNP. The region was recurrent across seven oil traits and represents the strongest prioritized candidate interval. b, Regional association plot for the chr9 C16:0-associated interval containing nearby `Zm00001d045387`, annotated as fatty acyl-ACP thioesterase2. This region is highlighted as a biologically focused fatty-acid composition candidate interval. In both panels, gene tracks show B73 RefGen_v4 local gene models; loci are interpreted as candidate intervals rather than fine-mapped causal variants.
"""
    path.write_text(text, encoding="utf-8")


def write_report(path: Path, out_dir: Path) -> None:
    files = [
        out_dir / "figure1_dataset_prediction_nature.pdf",
        out_dir / "figure1_dataset_prediction_nature.svg",
        out_dir / "figure1_dataset_prediction_nature.png",
        out_dir / "figure3_chr6_chr9_regional_loci_nature.pdf",
        out_dir / "figure3_chr6_chr9_regional_loci_nature.svg",
        out_dir / "figure3_chr6_chr9_regional_loci_nature.png",
        METHODS,
        FIG_PLAN,
        CAPTIONS,
    ]
    lines = ["# ZEAMAP v0.1 Stage 5.7 Methods and Main Figure Assembly", "", "日期：2026-06-05", "", "## Outputs", ""]
    for path_item in files:
        lines.append(f"- `{path_item.relative_to(ROOT)}`")
    lines.extend(
        [
            "",
            "## Summary",
            "",
            "Stage 5.7 created a first-pass Methods draft and assembled Figure 1 and Figure 3 manuscript panels.",
            "Figure 2 currently reuses the Stage 5.4 GEMMA LMM summary figure.",
            "",
            "## Remaining Polish",
            "",
            "- Visually inspect Figure 1 and Figure 3 PNG/PDF before manuscript submission.",
            "- Add final figure captions.",
            "- Expand the Methods draft into full manuscript Methods after the Results section stabilizes.",
        ]
    )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    figure1(args.out_dir)
    figure3(args.out_dir)
    write_methods(args.methods)
    write_figure_plan(args.figure_plan)
    write_captions(CAPTIONS)
    write_report(args.report, args.out_dir)


if __name__ == "__main__":
    main()
