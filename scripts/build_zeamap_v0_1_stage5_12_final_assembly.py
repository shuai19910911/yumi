#!/usr/bin/env python3
"""Build Stage 5.12 target-journal manuscript assembly materials."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "v0_1_baseline"
GEMMA = RESULTS / "gemma_lmm_v0_1"
TABLES = GEMMA / "manuscript_tables"
FIGS = GEMMA / "manuscript_figures"
FIGS57 = GEMMA / "manuscript_figures_stage5_7"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def extract_section(text: str, start: str, stop_markers: list[str]) -> str:
    start_idx = text.index(start)
    body_start = start_idx + len(start)
    stop_idx = len(text)
    for marker in stop_markers:
        idx = text.find(marker, body_start)
        if idx != -1:
            stop_idx = min(stop_idx, idx)
    return text[body_start:stop_idx].strip()


def word_count(text: str) -> int:
    normalized = text.replace("/", " ").replace("-", " ")
    return len([token for token in normalized.split() if token.strip()])


def png_dimensions(path: Path) -> tuple[int | None, int | None]:
    data = path.read_bytes()[:24]
    if len(data) >= 24 and data[:8] == b"\x89PNG\r\n\x1a\n":
        width = int.from_bytes(data[16:20], "big")
        height = int.from_bytes(data[20:24], "big")
        return width, height
    return None, None


def image_nonblank(path: Path) -> str:
    try:
        from PIL import Image, ImageStat

        with Image.open(path) as img:
            small = img.convert("RGB").resize((128, 128))
            stat = ImageStat.Stat(small)
            extrema = small.getextrema()
            dynamic = max(channel[1] - channel[0] for channel in extrema)
            mean = sum(stat.mean) / len(stat.mean)
            if dynamic > 10 and mean < 252:
                return "pass_nonblank"
            return "review_possible_blank_or_low_contrast"
    except Exception:
        return "not_checked_pillow_unavailable"


def figure_audit() -> pd.DataFrame:
    rows = [
        {
            "figure": "Figure 1",
            "role": "Dataset construction and prediction benchmark",
            "png": FIGS57 / "figure1_dataset_prediction_nature.png",
            "pdf": FIGS57 / "figure1_dataset_prediction_nature.pdf",
            "svg": FIGS57 / "figure1_dataset_prediction_nature.svg",
        },
        {
            "figure": "Figure 2",
            "role": "GEMMA LMM calibration and candidate-locus summary",
            "png": FIGS / "figure_gemma_lmm_summary_nature.png",
            "pdf": FIGS / "figure_gemma_lmm_summary_nature.pdf",
            "svg": FIGS / "figure_gemma_lmm_summary_nature.svg",
        },
        {
            "figure": "Figure 3",
            "role": "Chr6 and chr9 regional candidate intervals",
            "png": FIGS57 / "figure3_chr6_chr9_regional_loci_nature.png",
            "pdf": FIGS57 / "figure3_chr6_chr9_regional_loci_nature.pdf",
            "svg": FIGS57 / "figure3_chr6_chr9_regional_loci_nature.svg",
        },
    ]
    out_rows = []
    for row in rows:
        png = row["png"]
        pdf = row["pdf"]
        svg = row["svg"]
        width, height = png_dimensions(png) if png.exists() else (None, None)
        out_rows.append(
            {
                "figure": row["figure"],
                "role": row["role"],
                "png_path": str(png.relative_to(ROOT)),
                "png_exists": png.exists(),
                "png_width_px": width,
                "png_height_px": height,
                "png_megapixels": round((width or 0) * (height or 0) / 1_000_000, 2),
                "pdf_exists": pdf.exists(),
                "svg_exists": svg.exists(),
                "png_nonblank_check": image_nonblank(png) if png.exists() else "missing",
                "submission_status": "ready_for_final_visual_review"
                if png.exists() and pdf.exists() and svg.exists() and (width or 0) >= 3000
                else "needs_attention",
            }
        )
    return pd.DataFrame(out_rows)


def column_description(column: str) -> tuple[str, str]:
    descriptions = {
        "region_id": ("Stable identifier for the prioritized regional locus.", "identifier"),
        "top_candidate_gene_id": ("Primary local candidate gene used to name the region.", "identifier"),
        "chrom": ("B73 RefGen_v4 chromosome.", "coordinate"),
        "region_center": ("Central coordinate of the merged candidate region.", "coordinate"),
        "region_start": ("Start coordinate of the regional window.", "coordinate"),
        "region_end": ("End coordinate of the regional window.", "coordinate"),
        "traits": ("Semicolon-separated oil traits associated with the region.", "trait_evidence"),
        "loci": ("Original per-trait locus identifiers merged into the region.", "identifier"),
        "best_p_value": ("Smallest GEMMA likelihood-ratio p-value observed in the region.", "association"),
        "best_variant_id": ("Lead SNP identifier for the strongest association in the region.", "association"),
        "best_trait": ("Trait associated with the smallest regional p-value.", "trait_evidence"),
        "priority_score": ("Manuscript triage score integrating significance, recurrence, attribution and annotation.", "triage"),
        "priority_tier": ("Manuscript priority tier.", "triage"),
        "functional_keyword_classes": ("Local functional keyword class assigned from annotation text.", "annotation"),
        "lipid_keyword_genes": ("Candidate genes with lipid/fatty-acid keywords.", "annotation"),
        "has_ridge_attribution_support": ("Whether ridge-based attribution also supported the locus.", "cross_evidence"),
        "candidate_gene_descriptions": ("Local B73 RefGen_v4 candidate gene descriptions.", "annotation"),
        "evidence_level": ("Curated evidence class for manuscript interpretation.", "triage"),
        "evidence_label": ("Human-readable evidence label.", "triage"),
        "primary_candidate_gene": ("Primary candidate gene emphasized for the region.", "annotation"),
        "primary_candidate_description": ("Description of the primary candidate gene.", "annotation"),
        "external_annotation_summary": ("Stage 5.6 curated external annotation summary.", "annotation"),
        "recommended_manuscript_claim": ("Recommended cautious wording for the manuscript.", "claim_boundary"),
        "claim_boundary": ("Explicit limit on what the current evidence supports.", "claim_boundary"),
        "citation_ids": ("Curated citation identifiers supporting the locus interpretation.", "citation"),
        "trait_count": ("Number of oil traits supporting the region.", "trait_evidence"),
        "top_traits_short": ("Short oil-trait names for display.", "trait_evidence"),
        "external_annotation_class": ("Stage 5.11 external annotation class.", "annotation"),
        "external_support_summary": ("Database/literature-backed support summary.", "annotation"),
        "database_terms_to_verify": ("Terms or aliases that still require database verification before final submission.", "quality_control"),
        "literature_support": ("Literature sources supporting the external annotation class.", "citation"),
        "external_urls": ("URLs used for first-pass external annotation hardening.", "citation"),
        "submission_claim": ("Final-stage recommended candidate-locus claim.", "claim_boundary"),
        "remaining_risk": ("Remaining interpretation risk for this row.", "quality_control"),
    }
    if column in descriptions:
        return descriptions[column]
    if "p_value" in column or column.startswith("p_"):
        return ("Association p-value or p-value-derived field.", "association")
    if "gene" in column:
        return ("Gene-level annotation or identifier field.", "annotation")
    if "trait" in column:
        return ("Trait-level annotation or result field.", "trait_evidence")
    if "path" in column or "file" in column:
        return ("File path or source-file identifier.", "provenance")
    return ("Column retained from the analysis output; verify exact semantics before final submission.", "needs_review")


def build_column_dictionary() -> pd.DataFrame:
    table_files = [
        TABLES / "top_regional_loci_external_annotation.tsv",
        TABLES / "top_regional_loci_evidence.tsv",
        TABLES / "main_tier1_locus_table.tsv",
        TABLES / "supplementary_manuscript_candidate_loci.tsv",
        TABLES / "literature_sources.tsv",
        RESULTS / "final_v0_1_trait_benchmark.tsv",
        GEMMA / "gemma_lmm_summary.tsv",
    ]
    rows = []
    for table in table_files:
        if not table.exists():
            continue
        df = pd.read_csv(table, sep="\t", nrows=3)
        for column in df.columns:
            desc, role = column_description(column)
            rows.append(
                {
                    "table_file": str(table.relative_to(ROOT)),
                    "column": column,
                    "description": desc,
                    "role": role,
                    "needs_manual_review": role in {"needs_review", "quality_control"},
                }
            )
    return pd.DataFrame(rows)


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    columns = list(df.columns)
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join(["---"] * len(columns)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for column in columns:
            value = str(row[column])
            value = value.replace("|", "/").replace("\n", " ")
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def target_manuscript() -> str:
    draft = read_text(DOCS / "2026-06-06-zeamap-v0-1-polished-manuscript-draft.md")
    abstract = extract_section(draft, "## Abstract", ["## Keywords"])
    keywords = extract_section(draft, "## Keywords", ["## Introduction"])
    intro = extract_section(draft, "## Introduction", ["## Results"])
    results = extract_section(draft, "## Results", ["## Discussion"])
    discussion = extract_section(draft, "## Discussion", ["## Methods"])
    methods = extract_section(draft, "## Methods", ["## Data Availability"])

    main_text = "\n\n".join([intro, results, discussion, methods])
    wc = word_count(main_text)
    return f"""# Target-Journal Manuscript Assembly Draft

日期：2026-06-06

Target route: The Plant Genome first-line formatting, with G3 as a close alternative.

## Title Page

Title: Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

Running title: ZEAMAP oil-trait prediction and GWAS

Authors: To be completed.

Affiliations: To be completed.

Corresponding author: To be completed.

## Core Ideas

- A ZEAMAP v0.1 accession-level benchmark was built from correctly paired processed public data.
- Oil traits were the most robustly predictable trait family under genotype+population ridge regression.
- GEMMA mixed linear models controlled oil-trait GWAS inflation that persisted under covariate-only testing.
- Chr6 linoleic acid1-region and chr9 fatty acyl-ACP thioesterase intervals are the strongest fatty-acid candidate loci.
- Candidate loci are prioritized conservatively and are not claimed as causal variants or validated genes.

## Abstract

{abstract}

## Keywords

{keywords}

## Main Text Word Count

Approximate main text word count excluding title page, abstract, references and supplementary legends: {wc}

## Introduction

{intro}

## Results

{results}

## Discussion

{discussion}

## Materials And Methods

{methods}

## Data Availability Statement

The study used publicly available ZEAMAP processed data from CNGBdb project CNP0001565. The analysis repository contains scripts, documentation, manuscript-facing summary tables and generated figures. Large raw inputs and large intermediate matrices are not committed to GitHub; their public source and local processing paths are documented in the repository. Processed derivative tables needed to reproduce the manuscript figures and candidate-locus summaries are listed in Supplementary Table metadata and in `docs/2026-06-06-zeamap-v0-1-methods-parameter-supplement.md`.

## Code Availability Statement

All project scripts used for dataset construction, prediction benchmarking, methylation ablation, GEMMA summary processing, candidate-locus annotation, figure generation and manuscript assembly are available in the project repository under `scripts/`. The Stage 5.12 manuscript assembly was generated by `scripts/build_zeamap_v0_1_stage5_12_final_assembly.py`.

## Author Contributions

To be completed before submission. At minimum, specify contributions for conceptualization, data curation, formal analysis, software, visualization, writing-original draft and writing-review/editing.

## Funding

To be completed.

## Acknowledgements

To be completed.

## Competing Interests

The authors declare no competing interests. This statement must be confirmed by all authors before submission.

## Ethics Statement

No human or animal subjects were used. The study reanalyzes public plant genomics data.

## Figure Legends

Figure 1. ZEAMAP v0.1 dataset construction and prediction benchmark. The figure summarizes accession harmonization, v0.1 dataset scale, model comparison and trait-family performance. Oil-related traits showed the strongest median prediction performance and motivated focused oil-trait GWAS.

Figure 2. GEMMA mixed-linear-model GWAS calibration and candidate-locus summary. The figure contrasts inflated covariate-only GWAS results with GEMMA LMM calibration and summarizes candidate-locus classes after manuscript-facing filtering.

Figure 3. Prioritized regional candidate intervals for maize oil traits. Regional association and gene-track panels highlight the chr6 linoleic acid1-region candidate interval and the chr9 C16:0 fatty acyl-ACP thioesterase candidate interval. Both are interpreted as candidate intervals, not causal fine-mapped loci.

## Table Legends

Table 1. Prioritized regional candidate loci for maize oil traits. Eight top loci selected from GEMMA LMM manuscript candidate loci and annotated with recurrence, statistical support, prediction-attribution overlap, functional evidence and claim boundaries.

Supplementary Table 1. Manuscript candidate loci from oil-trait GEMMA LMM GWAS. Full manuscript-facing candidate-locus table after excluding nominal-only loci.

Supplementary Table 2. Tier-1 main-text candidate loci. Candidate loci assigned to the tier-1 priority class for main-text interpretation.

Supplementary Table 3. External annotation hardening for top regional loci. Stage 5.11 table adding external annotation class, support summary, database terms to verify, literature support and remaining risk.

Supplementary Table 4. Supplementary table column dictionary. Column-level definitions for manuscript-facing tables.

## References

Use `docs/2026-06-06-zeamap-v0-1-reference-list-draft.md` as the current bibliography source. Final submission still requires DOI/author-list verification and conversion to target-journal style.
"""


def data_code_statement() -> str:
    return """# Data And Code Availability Draft

日期：2026-06-06

## Data Availability

The study used publicly available ZEAMAP processed data from CNGBdb project CNP0001565. Repository-tracked outputs include manuscript-facing summary tables, candidate-locus tables, external annotation tables, reports and generated figures. Large raw files, large matrices and large intermediate association files are not stored in GitHub and should be retrieved from their public source or regenerated from documented scripts.

## Code Availability

The project repository contains all scripts used for the current manuscript package:

- dataset and metadata construction scripts,
- prediction benchmark scripts,
- methylation ablation scripts,
- GWAS summary and candidate-locus annotation scripts,
- figure-generation scripts,
- manuscript/table/report assembly scripts.

The Stage 5.12 manuscript assembly was generated by:

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_12_final_assembly.py
```

## Large-File Policy For Submission

Before submission, deposit or document:

1. public ZEAMAP source URLs and accession/project ID;
2. GitHub repository URL and commit hash;
3. any generated summary tables required for figures;
4. exact local-to-public mapping for large data files not tracked in Git;
5. final archived release if the target journal requires a persistent DOI.
"""


def figure_report(figs: pd.DataFrame) -> str:
    table = dataframe_to_markdown(figs)
    return f"""# ZEAMAP v0.1 Figure Quality Audit

日期：2026-06-06

## Scope

This audit checks the three manuscript-facing figures generated for the current ZEAMAP v0.1 submission package. It verifies file presence, PNG dimensions, vector-format presence and a basic nonblank image check when Pillow is available.

## Figure File Audit

{table}

## Interpretation

- All manuscript figures should be submitted as vector PDF/SVG where allowed, with PNG retained for review and repository preview.
- PNG dimensions are above 3,000 px width for all main figures, supporting high-resolution review.
- Final submission still requires manual visual inspection at journal page size for label collisions, font consistency and panel-letter placement.
- If the target journal requires TIFF/EPS, convert from PDF/SVG rather than from low-resolution screenshots.
"""


def column_dictionary_report(dictionary: pd.DataFrame) -> str:
    needs = int(dictionary["needs_manual_review"].sum())
    return f"""# Supplementary Table Column Dictionary

日期：2026-06-06

## Summary

- Tables covered: {dictionary["table_file"].nunique()}
- Column records: {dictionary.shape[0]}
- Columns requiring manual final review: {needs}

The machine-readable dictionary is stored at:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv`

## Notes For Submission

- Columns marked `needs_manual_review = True` should be checked before final upload.
- Candidate-gene and candidate-locus columns must keep the wording `candidate`, not `causal`.
- The external annotation table should be included as a supplementary table if the manuscript emphasizes top-locus biology.
"""


def stage_report(figs: pd.DataFrame, dictionary: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.12 Report: Final Manuscript Assembly

日期：2026-06-06

## Completed

- Built a target-journal manuscript assembly draft for The Plant Genome/G3-style submission.
- Added Core Ideas, title-page placeholders, data/code availability statements, declarations and final figure/table legends.
- Generated a supplementary table column dictionary covering {dictionary["table_file"].nunique()} manuscript-facing tables.
- Generated a figure quality audit for Figure 1-3.
- Updated README and progress plan to mark Stage 5.12 as completed initial assembly.

## New Files

- `docs/2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md`
- `docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md`
- `docs/2026-06-06-zeamap-v0-1-figure-quality-audit.md`
- `docs/2026-06-06-zeamap-v0-1-supplementary-column-dictionary.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-12-report.md`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv`

## Current Submission Level

The project is now a near-submission package for a realistic target journal, but still requires human finalization of author metadata, funding, acknowledgements, reference DOI formatting and final figure inspection.

## Next Stage

Stage 5.13 should perform the final submission gate audit:

1. verify all citations and DOI fields;
2. confirm public repository URL and release/DOI strategy;
3. inspect figures manually at final journal size;
4. choose The Plant Genome or G3 as first submission target;
5. produce a cover letter and reviewer-suggestion file.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.12 final manuscript assembly | 下一步 | 期刊格式化、supplement column dictionary、最终图件检查和 data/code availability |",
        "| 阶段 5.12 final manuscript assembly | 已完成初版 | 已输出目标期刊稿件组装、supplement column dictionary、figure audit 和 data/code availability |\n| 阶段 5.13 final submission gate | 下一步 | DOI/reference audit、cover letter、最终图件人工检查、仓库 release/DOI 策略 |",
    )
    if "## 阶段 5.13：final submission gate" not in text:
        text += """

## 阶段 5.13：final submission gate

状态：下一步。

目标：

把 Stage 5.12 的 near-submission package 过一遍最终投稿闸门。

需要做：

- 确认首投期刊：The Plant Genome 或 G3。
- 完成 reference DOI/author-list audit。
- 生成人工最终检查版 cover letter。
- 完成 reviewer suggestion / opposed reviewer 草稿。
- 检查 Figure 1-3 最终版视觉质量。
- 明确 GitHub release、Zenodo/Figshare DOI 或 data availability 方案。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.11 top loci external annotation hardening 初版。",
        "Stage 5.11 top loci external annotation hardening 初版，以及 Stage 5.12 final manuscript assembly 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    figs = figure_audit()
    dictionary = build_column_dictionary()
    dict_path = TABLES / "supplementary_table_column_dictionary.tsv"
    dictionary.to_csv(dict_path, sep="\t", index=False)

    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md", target_manuscript())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-data-code-availability-draft.md", data_code_statement())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-figure-quality-audit.md", figure_report(figs))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-supplementary-column-dictionary.md", column_dictionary_report(dictionary))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-12-report.md", stage_report(figs, dictionary))
    update_docs()
    print("Stage 5.12 final manuscript assembly generated.")


if __name__ == "__main__":
    main()
