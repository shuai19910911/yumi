#!/usr/bin/env python3
"""Build Stage 5.14 human metadata and release finalization templates."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:
        return "UNKNOWN_COMMIT"


def author_metadata_template() -> pd.DataFrame:
    rows = [
        {
            "author_order": 1,
            "full_name": "TO_COMPLETE",
            "initials": "TO_COMPLETE",
            "email": "TO_COMPLETE",
            "orcid": "TO_COMPLETE",
            "affiliation_id_list": "1",
            "corresponding_author": "yes/no",
            "equal_contribution": "yes/no",
            "contribution_roles": "Conceptualization; Data curation; Formal analysis; Software; Visualization; Writing-original draft; Writing-review/editing",
            "approval_confirmed": "yes/no",
            "coi_confirmed": "yes/no",
            "notes": "Replace placeholders before submission.",
        }
    ]
    return pd.DataFrame(rows)


def affiliation_template() -> pd.DataFrame:
    rows = [
        {
            "affiliation_id": 1,
            "institution": "TO_COMPLETE",
            "department_or_lab": "TO_COMPLETE",
            "city": "TO_COMPLETE",
            "state_or_province": "TO_COMPLETE",
            "country": "TO_COMPLETE",
            "postal_code": "TO_COMPLETE",
            "notes": "Use exact institutional spelling required by target journal.",
        }
    ]
    return pd.DataFrame(rows)


def reviewer_worksheet() -> pd.DataFrame:
    rows = [
        {
            "type": "suggested",
            "name": "TO_COMPLETE",
            "email": "TO_COMPLETE",
            "institution": "TO_COMPLETE",
            "expertise": "Maize quantitative genetics / mixed-model GWAS",
            "reason": "Can evaluate population-structure control, GEMMA LMM and candidate-locus statistics.",
            "conflict_checked": "yes/no",
            "notes": "Avoid ZEAMAP data generators or close collaborators if conflicted.",
        },
        {
            "type": "suggested",
            "name": "TO_COMPLETE",
            "email": "TO_COMPLETE",
            "institution": "TO_COMPLETE",
            "expertise": "Maize seed oil / fatty-acid metabolism",
            "reason": "Can evaluate chr6 linoleic acid1-region and chr9 acyl-ACP thioesterase interpretation.",
            "conflict_checked": "yes/no",
            "notes": "Check for unpublished direct competition on chr6/chr9 loci.",
        },
        {
            "type": "suggested",
            "name": "TO_COMPLETE",
            "email": "TO_COMPLETE",
            "institution": "TO_COMPLETE",
            "expertise": "Crop genomics resource reuse and reproducible analysis",
            "reason": "Can evaluate ZEAMAP accession harmonization and public-resource reuse.",
            "conflict_checked": "yes/no",
            "notes": "Prefer reviewer with no direct role in ZEAMAP construction.",
        },
        {
            "type": "opposed_optional",
            "name": "TO_COMPLETE",
            "email": "TO_COMPLETE",
            "institution": "TO_COMPLETE",
            "expertise": "TO_COMPLETE",
            "reason": "Conflict or direct competition reason.",
            "conflict_checked": "yes/no",
            "notes": "Only include if journal permits opposed reviewers and reason is defensible.",
        },
    ]
    return pd.DataFrame(rows)


def figure_checklist() -> pd.DataFrame:
    figures = [
        ("Figure 1", "figure1_dataset_prediction_nature", "Dataset construction and prediction benchmark"),
        ("Figure 2", "figure_gemma_lmm_summary_nature", "GEMMA LMM calibration and candidate-locus summary"),
        ("Figure 3", "figure3_chr6_chr9_regional_loci_nature", "Chr6 and chr9 regional candidate intervals"),
    ]
    rows = []
    for figure, stem, purpose in figures:
        rows.append(
            {
                "figure": figure,
                "file_stem": stem,
                "purpose": purpose,
                "pdf_opened": "yes/no",
                "svg_opened": "yes/no",
                "png_opened": "yes/no",
                "panel_labels_correct": "yes/no",
                "text_readable_at_journal_size": "yes/no",
                "no_label_overlap": "yes/no",
                "legend_matches_figure": "yes/no",
                "color_accessibility_checked": "yes/no",
                "final_status": "pass/revise",
                "notes": "Manual inspection required.",
            }
        )
    return pd.DataFrame(rows)


def funding_coi_form() -> str:
    return """# Author Contribution, Funding And Competing Interest Form

日期：2026-06-06

## Author Approval

Each author must confirm before submission:

- I have reviewed the final manuscript.
- I approve submission to the selected journal.
- I agree with the author order.
- I agree with my listed affiliations.
- I agree with the contribution statement.
- I have disclosed all competing interests.

## CRediT Contribution Roles

Use these roles where applicable:

- Conceptualization
- Data curation
- Formal analysis
- Funding acquisition
- Investigation
- Methodology
- Project administration
- Resources
- Software
- Supervision
- Validation
- Visualization
- Writing-original draft
- Writing-review/editing

## Funding Statement Template

This work was supported by [funding agency] under grant [grant number]. The funders had no role in study design, data analysis, decision to publish or manuscript preparation.

If no external funding:

The authors received no specific funding for this work.

## Competing Interest Statement Template

The authors declare no competing interests.

If competing interests exist, replace with a specific statement approved by all authors.

## Acknowledgements Template

We thank [names/groups] for [specific assistance]. Public ZEAMAP data were used as described in the Data Availability statement.
"""


def release_commands(commit: str) -> str:
    tag = "zeamap-oil-v0.1-submission"
    return f"""# Release Execution Commands Draft

日期：2026-06-06

Current checked commit when this draft was generated:

```text
{commit}
```

## Preconditions

Do not execute the release until:

- author list, affiliations, funding and competing interests are finalized;
- final target journal is selected;
- Figure 1-3 have passed manual visual inspection;
- final reference list has been exported in journal style;
- repository visibility has been confirmed.

## Local Tag Commands

```bash
git status --short
git tag -a {tag} -m "ZEAMAP maize oil-trait manuscript submission package"
git push origin {tag}
```

## GitHub Release Notes Draft

Title:

```text
ZEAMAP maize oil-trait manuscript submission package v0.1
```

Description:

```text
Submission package for "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP". Includes manuscript-facing documentation, summary tables, candidate-locus annotation, figure outputs and scripts. Large raw ZEAMAP inputs and large intermediate matrices are not included and should be retrieved from the public ZEAMAP/CNGBdb source documented in the repository.
```

## DOI Archive

After creating the GitHub release, archive it with Zenodo or Figshare if required by the target journal. Record the archive DOI in:

- `docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md`
- final manuscript Data Availability statement
- cover letter, if journal requests repository/DOI detail
"""


def metadata_audit(commit: str) -> str:
    return f"""# Human Metadata Readiness Audit

日期：2026-06-06

## Status

Stage 5.14 prepares the human metadata package, but it cannot complete final submission because several fields require author confirmation.

Current commit used for this audit: `{commit}`

## Prepared Artifacts

- `docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv`
- `docs/2026-06-06-zeamap-v0-1-affiliation-template.tsv`
- `docs/2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md`
- `docs/2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv`
- `docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv`
- `docs/2026-06-06-zeamap-v0-1-release-execution-commands.md`

## Still Missing For Actual Submission

| Item | Status | Why It Cannot Be Auto-Filled |
|---|---|---|
| Author names and order | Missing | Requires author decision |
| Affiliations | Missing | Requires exact institutional metadata |
| Corresponding author | Missing | Requires author decision |
| ORCID identifiers | Missing | Requires author-provided identifiers |
| Funding | Missing | Requires grant information |
| Acknowledgements | Missing | Requires author approval |
| Competing interests | Missing | Requires author declarations |
| Named reviewers | Missing | Requires conflict checking |
| Opposed reviewers | Optional/missing | Requires conflict justification |
| Repository release DOI | Not created | Should wait until final manuscript is locked |
| Final figure manual inspection | Not completed | Requires visual human inspection |

## Academic-Research-Suite Interpretation

The manuscript is now technically organized for submission, but the final upload package is not complete until the human metadata and release gates above are resolved. The next productive step is not more model work; it is author-level finalization and repository release execution.
"""


def stage_report() -> str:
    return """# ZEAMAP v0.1 Stage 5.14 Report: Human Metadata And Release Finalization Templates

日期：2026-06-06

## Completed

- Generated author metadata template.
- Generated affiliation template.
- Generated author approval / CRediT / funding / competing-interest form.
- Generated named reviewer worksheet.
- Generated final figure manual inspection checklist.
- Generated release execution commands draft.
- Generated human metadata readiness audit.
- Updated README and progress plan.

## Current State

The manuscript package is technically ready for author-side finalization. It is not yet an actual final submission because author metadata, declarations, reviewer names and repository DOI/release execution require human decisions.

## Next Stage

Stage 5.15 should be author-confirmed release execution:

1. fill author metadata templates;
2. fill reviewer worksheet with named reviewers;
3. inspect figures manually;
4. create release tag and public archive DOI;
5. insert final DOI and metadata into the manuscript package.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.14 human metadata and release finalization | 下一步 | 作者/单位/基金/利益冲突、命名审稿人、GitHub release/DOI、最终人工图件检查 |",
        "| 阶段 5.14 human metadata and release finalization templates | 已完成模板包 | 已输出作者/单位/基金/COI、命名审稿人、图件人工检查和 release 命令模板 |\n| 阶段 5.15 author-confirmed release execution | 下一步 | 填入真实作者信息、命名审稿人、人工图件确认、GitHub release/DOI 并写回最终稿 |",
    )
    if "Author metadata template: 1 file" not in text:
        text = text.replace(
            "Final submission gate audit: 1 file",
            "Final submission gate audit: 1 file\nAuthor metadata template: 1 file\nAffiliation template: 1 file\nReviewer worksheet: 1 file\nFigure manual checklist: 1 file\nRelease command draft: 1 file",
        )
    if "## 阶段 5.15：author-confirmed release execution" not in text:
        text += """

## 阶段 5.15：author-confirmed release execution

状态：下一步，需要作者信息。

目标：

把 Stage 5.14 的模板填成真实投稿元数据，并执行最终 release/DOI。

需要人工输入：

- 作者姓名、排序、单位、邮箱、ORCID。
- 通讯作者和共同一作信息。
- CRediT contribution。
- funding、acknowledgements、competing interests。
- 命名推荐审稿人和回避审稿人。
- Figure 1-3 人工视觉确认。
- 是否创建 GitHub release 和 Zenodo/Figshare DOI。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.13 final submission gate 初版。",
        "Stage 5.13 final submission gate 和 Stage 5.14 human metadata/release templates 初版。",
    )
    text = text.replace(
        "Stage 5.12 final manuscript assembly 和 Stage 5.13 final submission gate 和 Stage 5.14 human metadata/release templates 初版。",
        "Stage 5.12 final manuscript assembly、Stage 5.13 final submission gate 和 Stage 5.14 human metadata/release templates 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    commit = git_commit()
    author_metadata_template().to_csv(DOCS / "2026-06-06-zeamap-v0-1-author-metadata-template.tsv", sep="\t", index=False)
    affiliation_template().to_csv(DOCS / "2026-06-06-zeamap-v0-1-affiliation-template.tsv", sep="\t", index=False)
    reviewer_worksheet().to_csv(DOCS / "2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv", sep="\t", index=False)
    figure_checklist().to_csv(DOCS / "2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md", funding_coi_form())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-release-execution-commands.md", release_commands(commit))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-human-metadata-readiness-audit.md", metadata_audit(commit))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-14-report.md", stage_report())
    update_docs()
    print("Stage 5.14 human metadata package generated.")


if __name__ == "__main__":
    main()
