#!/usr/bin/env python3
"""Build Stage 5.13 final submission gate materials."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "v0_1_baseline"
GEMMA = RESULTS / "gemma_lmm_v0_1"
TABLES = GEMMA / "manuscript_tables"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def reference_records() -> list[dict[str, str]]:
    return [
        {
            "id": "Gui2020_ZEAMAP",
            "draft_reference": "Gui, S. et al. ZEAMAP, a comprehensive database adapted to the maize multi-omics era. iScience 23, 101241 (2020).",
            "doi": "10.1016/j.isci.2020.101241",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1016/j.isci.2020.101241",
            "submission_action": "Mandatory data-resource citation.",
        },
        {
            "id": "Jiao2017_B73RefGenV4",
            "draft_reference": "Jiao, Y. et al. Improved maize reference genome with single-molecule technologies. Nature 546, 524-527 (2017).",
            "doi": "10.1038/nature22971",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1038/nature22971",
            "submission_action": "Mandatory B73 RefGen_v4/reference-genome citation.",
        },
        {
            "id": "Yates2022_EnsemblGenomes",
            "draft_reference": "Yates, A. D. et al. Ensembl Genomes 2022: an expanding genome resource for non-vertebrates. Nucleic Acids Research 50, D996-D1003 (2022).",
            "doi": "10.1093/nar/gkab1007",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1093/nar/gkab1007",
            "submission_action": "Use for Ensembl Plants/Gramene-style annotation provenance if required.",
        },
        {
            "id": "Zhou2012_GEMMA",
            "draft_reference": "Zhou, X. and Stephens, M. Genome-wide efficient mixed-model analysis for association studies. Nature Genetics 44, 821-824 (2012).",
            "doi": "10.1038/ng.2310",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.1038/ng.2310",
            "submission_action": "Mandatory GEMMA/univariate mixed-model citation.",
        },
        {
            "id": "Zhou2014_MV_LMM",
            "draft_reference": "Zhou, X. and Stephens, M. Efficient multivariate linear mixed model algorithms for genome-wide association studies. Nature Methods 11, 407-409 (2014).",
            "doi": "10.1038/nmeth.2848",
            "audit_status": "optional",
            "source_url": "https://doi.org/10.1038/nmeth.2848",
            "submission_action": "Optional background; remove if journal wants lean references because current analysis is univariate.",
        },
        {
            "id": "Benjamini1995_FDR",
            "draft_reference": "Benjamini, Y. and Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. Journal of the Royal Statistical Society Series B 57, 289-300 (1995).",
            "doi": "10.1111/j.2517-6161.1995.tb02031.x",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.1111/j.2517-6161.1995.tb02031.x",
            "submission_action": "Use for FDR method citation.",
        },
        {
            "id": "Li2013_MaizeOilGWAS",
            "draft_reference": "Li, H. et al. Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels. Nature Genetics 45, 43-50 (2013).",
            "doi": "10.1038/ng.2484",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1038/ng.2484",
            "submission_action": "Mandatory maize oil GWAS citation.",
        },
        {
            "id": "Alrefai1995_FattyAcidQTL",
            "draft_reference": "Alrefai, R. et al. Chromosomal locations of maize genes controlling fatty acid composition of the embryo oil. Genome 38, 827-838 (1995).",
            "doi": "10.1139/g95-108",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1139/g95-108",
            "submission_action": "Use for chromosome-level fatty-acid QTL context.",
        },
        {
            "id": "Cook2012_KernelComposition",
            "draft_reference": "Cook, J. P. et al. Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels. Plant Physiology 158, 824-834 (2012).",
            "doi": "10.1104/pp.111.185033",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.1104/pp.111.185033",
            "submission_action": "Use for kernel-composition genetic architecture.",
        },
        {
            "id": "Zheng2008_DGAT",
            "draft_reference": "Zheng, P. et al. A phenylalanine in DGAT is a key determinant of oil content and composition in maize. Nature Genetics 40, 367-372 (2008).",
            "doi": "10.1038/ng.85",
            "audit_status": "corrects_stage5_10_reference",
            "source_url": "https://doi.org/10.1038/ng.85",
            "submission_action": "Replace the earlier draft's incorrect 'PLoS Genetics 2012' entry.",
        },
        {
            "id": "Khan2022_FattyAcidContent",
            "draft_reference": "Khan, N. et al. Genetic variation of fatty acid content in maize. Frontiers in Nutrition 9, 906530 (2022).",
            "doi": "10.3389/fnut.2022.906530",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.3389/fnut.2022.906530",
            "submission_action": "Use for fatty-acid composition background.",
        },
        {
            "id": "Liu2023_OilRelatedTraits",
            "draft_reference": "Liu, H. et al. Genome-wide association study reveals the genetic architecture of oil-related traits in maize. Frontiers in Plant Science 14, 1174985 (2023).",
            "doi": "10.3389/fpls.2023.1174985",
            "audit_status": "doi_ready_verify_author_list",
            "source_url": "https://doi.org/10.3389/fpls.2023.1174985",
            "submission_action": "Use for recent oil-trait GWAS context.",
        },
        {
            "id": "Pedregosa2011_sklearn",
            "draft_reference": "Pedregosa, F. et al. Scikit-learn: machine learning in Python. Journal of Machine Learning Research 12, 2825-2830 (2011).",
            "doi": "",
            "audit_status": "no_standard_doi_use_jmlr_url",
            "source_url": "https://jmlr.org/papers/v12/pedregosa11a.html",
            "submission_action": "Use if software citations are included in Methods/Supplement.",
        },
        {
            "id": "Harris2020_NumPy",
            "draft_reference": "Harris, C. R. et al. Array programming with NumPy. Nature 585, 357-362 (2020).",
            "doi": "10.1038/s41586-020-2649-2",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.1038/s41586-020-2649-2",
            "submission_action": "Software citation.",
        },
        {
            "id": "Virtanen2020_SciPy",
            "draft_reference": "Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods 17, 261-272 (2020).",
            "doi": "10.1038/s41592-019-0686-2",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.1038/s41592-019-0686-2",
            "submission_action": "Software citation.",
        },
        {
            "id": "McKinney2010_pandas",
            "draft_reference": "McKinney, W. Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference, 56-61 (2010).",
            "doi": "10.25080/Majora-92bf1922-00a",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.25080/Majora-92bf1922-00a",
            "submission_action": "Software citation.",
        },
        {
            "id": "Hunter2007_Matplotlib",
            "draft_reference": "Hunter, J. D. Matplotlib: A 2D graphics environment. Computing in Science & Engineering 9, 90-95 (2007).",
            "doi": "10.1109/MCSE.2007.55",
            "audit_status": "doi_ready",
            "source_url": "https://doi.org/10.1109/MCSE.2007.55",
            "submission_action": "Figure-generation software citation.",
        },
    ]


def build_reference_audit() -> pd.DataFrame:
    df = pd.DataFrame(reference_records())
    out = DOCS / "2026-06-06-zeamap-v0-1-reference-doi-audit.tsv"
    df.to_csv(out, sep="\t", index=False)
    return df


def reference_audit_report(df: pd.DataFrame) -> str:
    missing = int((df["doi"] == "").sum())
    corrections = df.loc[df["audit_status"].str.contains("corrects"), "id"].tolist()
    return f"""# ZEAMAP v0.1 Reference DOI Audit

日期：2026-06-06

## Summary

- References audited: {df.shape[0]}
- DOI-ready records: {int((df["doi"] != "").sum())}
- Records without standard DOI: {missing}
- Critical correction found: {", ".join(corrections) if corrections else "none"}

Machine-readable audit:

- `docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv`

## Critical Correction

The Stage 5.10 reference draft listed the DGAT oil-composition paper as a 2012 PLoS Genetics article. The correct citation is:

Zheng, P. et al. A phenylalanine in DGAT is a key determinant of oil content and composition in maize. *Nature Genetics* 40, 367-372 (2008). DOI: `10.1038/ng.85`.

This correction must be applied in the final formatted bibliography before submission.

## Submission Actions

1. Export final references from Zotero/EndNote or another citation manager using the selected journal style.
2. Keep ZEAMAP, B73 RefGen_v4, GEMMA, maize oil GWAS, FDR and software citations.
3. Remove optional multivariate GEMMA citation if the final manuscript needs a shorter bibliography.
4. Check author lists for all `verify_author_list` records.
"""


def cover_letter() -> str:
    return """# Cover Letter Draft: ZEAMAP Maize Oil-Trait Manuscript

日期：2026-06-06

Dear Editor,

We are pleased to submit the manuscript entitled "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP" for consideration as a research article.

This manuscript presents a reproducible accession-level reanalysis of public ZEAMAP processed data focused on maize kernel oil and fatty-acid traits. We first constructed a conservative v0.1 benchmark containing 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed prediction benchmarking showed that oil-related traits were the most robustly predictable trait family under a genotype+population ridge model. We then used those prediction results to motivate focused mixed-model GWAS on 10 high-priority oil traits.

The main statistical contribution is the calibrated GWAS workflow. A diagnostic covariate-only GWAS showed strong genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC near one across oil traits. The resulting candidate-locus set was annotated with B73 RefGen_v4 gene models, prediction-attribution overlap and external literature/database evidence. The strongest candidate intervals include a recurrent chromosome 6 linoleic acid1-region locus and a chromosome 9 C16:0 interval containing a nearby fatty acyl-ACP thioesterase candidate.

We believe the manuscript will interest readers working in crop genomics, maize quantitative genetics, public resource reuse, genotype-to-phenotype prediction and seed-quality trait dissection. The work is deliberately conservative: we do not claim causal variants or experimentally validated genes. Instead, we provide a transparent benchmark, calibrated association results and prioritized candidate intervals for follow-up.

All analyses use publicly available ZEAMAP data, and the repository includes scripts, manuscript-facing summary tables, figure outputs and reproducibility documentation. Large raw and intermediate files are not committed to GitHub but are linked to their public sources and documented for regeneration.

Before submission, the corresponding author should confirm that the manuscript is original, is not under consideration elsewhere, has been approved by all authors and has complete conflict-of-interest and funding statements.

Sincerely,

[Corresponding author name]
"""


def reviewer_suggestions() -> str:
    return """# Reviewer Suggestion Draft

日期：2026-06-06

## Use Policy

This file is a draft for final human curation. Because author identities, collaborators, competitors and conflicts are not yet specified, these are reviewer profiles rather than final named reviewer nominations. Before submission, replace profiles with names only after checking conflicts of interest.

## Recommended Reviewer Profiles

1. Maize quantitative geneticist with GWAS/mixed-model expertise

- Needed expertise: maize diversity panels, population structure, GEMMA/MLM/GWAS calibration.
- Why: the central statistical claim is that GEMMA LMM controls the inflation seen in covariate-only GWAS.
- Avoid: anyone directly involved in ZEAMAP data generation or close collaborators of the authors.

2. Maize seed oil or fatty-acid metabolism expert

- Needed expertise: kernel oil content, fatty-acid composition, FatB/acyl-ACP thioesterase biology, DGAT/oil biosynthesis.
- Why: chr6 and chr9 candidate-locus interpretation requires biological scrutiny.
- Avoid: direct competitors on unpublished maize oil validation work if known.

3. Crop genomics/public resource reuse expert

- Needed expertise: public multi-omics resource integration, accession harmonization, reproducible analysis pipelines.
- Why: the manuscript's value depends on conservative resource reuse and transparent processed-data construction.

4. Statistical genetics reviewer outside maize

- Needed expertise: high-dimensional genotype-to-phenotype prediction, regularized regression, trait selection, claim calibration.
- Why: an outside reviewer can judge whether the prediction-to-GWAS triage is defensible.

## Possible Opposed Reviewer Categories

- Direct authors or maintainers of ZEAMAP if journal policy treats data-resource generators as potentially conflicted.
- Recent close coauthors, current collaborators, same institution, grant collaborators or trainees of the manuscript authors.
- Researchers with direct unpublished competition on the exact chr6/chr9 candidate loci.

## Final Submission Action

Before submission, identify 3-5 named reviewers and 1-3 opposed reviewers after the author list is fixed.
"""


def release_plan() -> str:
    return """# Repository Release And Data DOI Plan

日期：2026-06-06

## Current Repository

GitHub remote:

```text
git@github.com:shuai19910911/yumi.git
```

Current manuscript package is tracked through staged Git commits. Before journal submission, create a stable public release or archive.

## Recommended Release Steps

1. Ensure the repository is public or accessible to reviewers.
2. Add a release tag such as `zeamap-oil-v0.1-submission`.
3. Archive the release in Zenodo or Figshare if the target journal requires a persistent DOI.
4. Record the release DOI in the Data/Code Availability statement.
5. Keep large raw files outside GitHub; document public ZEAMAP source URLs and local regeneration scripts.

## Minimum Release Contents

- `README.md`
- `docs/progress-plan.md`
- target-journal manuscript draft
- reference DOI audit
- data/code availability statement
- figure quality audit
- manuscript-facing tables
- candidate-locus annotation tables
- scripts used to generate current manuscript package

## Not To Release In GitHub

- raw VCF/matrix files too large for GitHub,
- raw SRA/FASTQ,
- large intermediate GEMMA association outputs unless compressed and explicitly needed,
- private author notes or conflict-of-interest files.
"""


def submission_gate() -> str:
    return """# ZEAMAP v0.1 Final Submission Gate Audit

日期：2026-06-06

## Academic-Research-Suite Gate Verdict

Status: near-submission package, not final uploaded manuscript.

The project now satisfies the technical manuscript package requirements for a realistic target journal: dataset definition, Methods, Results, Discussion, figure set, table set, reference audit, data/code availability draft, external annotation table, figure audit and cover-letter draft.

It is not yet a final submission because human-specific metadata remain missing: author list, affiliations, funding, acknowledgements, competing interests confirmation, named reviewer suggestions and final repository release/DOI.

## Completed Gates

| Gate | Status | Evidence |
|---|---|---|
| Manuscript assembly | Pass initial | `docs/2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md` |
| Data/code availability | Pass draft | `docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md` |
| Figure package | Pass technical audit | `docs/2026-06-06-zeamap-v0-1-figure-quality-audit.md` |
| Supplementary table dictionary | Pass initial | `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv` |
| External top-locus annotation | Pass initial | `top_regional_loci_external_annotation.tsv` |
| Reference DOI audit | Pass draft, one correction required | `docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv` |
| Cover letter | Pass draft | `docs/2026-06-06-zeamap-v0-1-cover-letter-draft.md` |
| Reviewer suggestions | Profile draft only | `docs/2026-06-06-zeamap-v0-1-reviewer-suggestion-draft.md` |

## Remaining Human Gates

1. Insert final author list, affiliations and corresponding author.
2. Confirm all authors approve submission.
3. Complete funding and acknowledgements.
4. Confirm competing interests.
5. Replace reviewer profiles with named reviewers after conflict checking.
6. Create repository release and DOI if required.
7. Manually inspect Figure 1-3 at final journal page size.
8. Export final reference list in the selected journal style.

## Target Journal Recommendation

First target: The Plant Genome.

Reason: the manuscript is a crop genomics/resource-reuse and quantitative genetics paper with a transparent benchmark and conservative candidate-locus interpretation.

Alternative first target: G3.

Reason: strong fit for genetics, reproducible analysis, GWAS calibration and conservative quantitative interpretation.

## Acceptance Estimate After Stage 5.13

- The Plant Genome / G3 eventual acceptance after human metadata and final formatting: 65-80%.
- Direct acceptance without major revision: 10-20%.
- With independent population validation or functional experiments: 75-85% eventual acceptance and higher ceiling.
- Higher-impact plant journals remain risky without validation.
"""


def stage_report(df: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.13 Report: Final Submission Gate

日期：2026-06-06

## Completed

- Generated reference DOI audit covering {df.shape[0]} citation records.
- Flagged and corrected the earlier DGAT/Zheng citation problem.
- Generated cover letter draft.
- Generated reviewer suggestion profile draft.
- Generated repository release/data DOI plan.
- Generated final submission gate audit using academic-research-suite style criteria.
- Updated README and progress plan.

## New Files

- `docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-reference-doi-audit.md`
- `docs/2026-06-06-zeamap-v0-1-cover-letter-draft.md`
- `docs/2026-06-06-zeamap-v0-1-reviewer-suggestion-draft.md`
- `docs/2026-06-06-zeamap-v0-1-repository-release-plan.md`
- `docs/2026-06-06-zeamap-v0-1-final-submission-gate-audit.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-13-report.md`

## Current State

The manuscript package is now ready for human finalization. Remaining items require author identity, institutional metadata, conflict checks and final repository-release decisions.
"""


def update_reference_list(df: pd.DataFrame) -> None:
    lines = [
        "# ZEAMAP v0.1 Reference List Draft",
        "",
        "日期：2026-06-06",
        "",
        "This file was updated by Stage 5.13. It keeps draft references but adds DOI audit status and corrects the Zheng/DGAT citation.",
        "",
        "## Audited References",
        "",
    ]
    for i, row in enumerate(df.to_dict("records"), start=1):
        doi = row["doi"] if row["doi"] else "no standard DOI recorded"
        lines.append(f"{i}. {row['draft_reference']} DOI/status: `{doi}` / `{row['audit_status']}`.")
    lines.extend(
        [
            "",
            "## Final Formatting Notes",
            "",
            "- Export final bibliography in the target journal style before submission.",
            "- Verify author lists for records marked `verify_author_list`.",
            "- Keep the corrected Zheng 2008 Nature Genetics entry, not the earlier erroneous 2012 PLoS Genetics text.",
        ]
    )
    write_text(DOCS / "2026-06-06-zeamap-v0-1-reference-list-draft.md", "\n".join(lines))


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.13 final submission gate | 下一步 | DOI/reference audit、cover letter、最终图件人工检查、仓库 release/DOI 策略 |",
        "| 阶段 5.13 final submission gate | 已完成初版 | 已输出 DOI/reference audit、cover letter、reviewer profiles、release plan 和 final gate audit |\n| 阶段 5.14 human metadata and release finalization | 下一步 | 作者/单位/基金/利益冲突、命名审稿人、GitHub release/DOI、最终人工图件检查 |",
    )
    if "Reference DOI audit: 1 file" not in text:
        text = text.replace(
            "Data/code availability draft: 1 file",
            "Data/code availability draft: 1 file\nReference DOI audit: 1 file\nCover letter draft: 1 file\nReviewer suggestion draft: 1 file\nRepository release plan: 1 file\nFinal submission gate audit: 1 file",
        )
    if "## 阶段 5.14：human metadata and release finalization" not in text:
        text += """

## 阶段 5.14：human metadata and release finalization

状态：下一步。

目标：

把已经完成的 near-submission package 转成可由作者确认并实际上传的最终投稿文件。

需要人工信息：

- 作者名单、单位和通讯作者。
- 基金、致谢和利益冲突。
- 命名审稿人和回避审稿人。
- GitHub release/Zenodo DOI 是否执行。
- Figure 1-3 最终人工视觉确认。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.12 final manuscript assembly 初版。",
        "Stage 5.12 final manuscript assembly 和 Stage 5.13 final submission gate 初版。",
    )
    text = text.replace(
        "Stage 5.11 top loci external annotation hardening 和 Stage 5.12 final manuscript assembly 和 Stage 5.13 final submission gate 初版。",
        "Stage 5.11 top loci external annotation hardening、Stage 5.12 final manuscript assembly 和 Stage 5.13 final submission gate 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    df = build_reference_audit()
    update_reference_list(df)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-reference-doi-audit.md", reference_audit_report(df))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-cover-letter-draft.md", cover_letter())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-reviewer-suggestion-draft.md", reviewer_suggestions())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-repository-release-plan.md", release_plan())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-final-submission-gate-audit.md", submission_gate())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-13-report.md", stage_report(df))
    update_docs()
    print("Stage 5.13 final submission gate generated.")


if __name__ == "__main__":
    main()
