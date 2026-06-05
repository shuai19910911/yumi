#!/usr/bin/env python3
"""Build Stage 5.16 metadata ingestion dry-run outputs.

This script prepares the final author/release insertion workflow without
fabricating author metadata or executing a release.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"


AUTHOR_TSV = DOCS / "2026-06-06-zeamap-v0-1-author-metadata-template.tsv"
AFFILIATION_TSV = DOCS / "2026-06-06-zeamap-v0-1-affiliation-template.tsv"
REVIEWER_TSV = DOCS / "2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv"
FIGURE_TSV = DOCS / "2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv"
TARGET_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_placeholder(value: object) -> bool:
    text = str(value)
    return any(marker in text for marker in ["TO_COMPLETE", "yes/no", "pass/revise"])


def placeholder_cell_count(df: pd.DataFrame) -> int:
    if df.empty:
        return 0
    return int(df.astype(str).map(has_placeholder).sum().sum())


def audit_table(path: Path, required_columns: list[str]) -> dict[str, object]:
    if not path.exists():
        return {
            "file": str(path.relative_to(ROOT)),
            "exists": False,
            "rows": 0,
            "missing_columns": ";".join(required_columns),
            "placeholder_cells": 0,
            "ready": False,
        }
    df = pd.read_csv(path, sep="\t")
    missing = [col for col in required_columns if col not in df.columns]
    placeholder_cells = placeholder_cell_count(df)
    return {
        "file": str(path.relative_to(ROOT)),
        "exists": True,
        "rows": int(df.shape[0]),
        "missing_columns": ";".join(missing),
        "placeholder_cells": placeholder_cells,
        "ready": not missing and placeholder_cells == 0 and df.shape[0] > 0,
    }


def build_ingestion_audit() -> pd.DataFrame:
    specs = [
        (
            AUTHOR_TSV,
            [
                "author_order",
                "full_name",
                "email",
                "affiliation_id_list",
                "corresponding_author",
                "contribution_roles",
                "approval_confirmed",
                "coi_confirmed",
            ],
        ),
        (AFFILIATION_TSV, ["affiliation_id", "institution", "city", "country"]),
        (REVIEWER_TSV, ["type", "name", "email", "institution", "conflict_checked"]),
        (FIGURE_TSV, ["figure", "final_status"]),
    ]
    return pd.DataFrame([audit_table(path, columns) for path, columns in specs])


def authors_preview() -> str:
    if not AUTHOR_TSV.exists() or not AFFILIATION_TSV.exists():
        return "Author metadata templates are missing."
    authors = pd.read_csv(AUTHOR_TSV, sep="\t")
    affiliations = pd.read_csv(AFFILIATION_TSV, sep="\t")
    if placeholder_cell_count(authors) or placeholder_cell_count(affiliations):
        return "Author and affiliation metadata still contain placeholders; final title page cannot be generated."

    authors = authors.sort_values("author_order")
    author_line = ", ".join(authors["full_name"].astype(str).tolist())
    aff_lines = []
    for _, row in affiliations.sort_values("affiliation_id").iterrows():
        aff_lines.append(
            f"{row['affiliation_id']}. {row['department_or_lab']}, {row['institution']}, {row['city']}, {row['country']}"
        )
    corresponding = authors.loc[authors["corresponding_author"].astype(str).str.lower().eq("yes")]
    corr_lines = []
    for _, row in corresponding.iterrows():
        corr_lines.append(f"{row['full_name']}: {row['email']}")
    return "\n".join(
        [
            f"Authors: {author_line}",
            "",
            "Affiliations:",
            *aff_lines,
            "",
            "Corresponding author:",
            *corr_lines,
        ]
    )


def contribution_preview() -> str:
    if not AUTHOR_TSV.exists():
        return "Author metadata template is missing."
    authors = pd.read_csv(AUTHOR_TSV, sep="\t")
    if placeholder_cell_count(authors):
        return "Contribution statement cannot be generated until author metadata placeholders are resolved."
    lines = []
    for _, row in authors.sort_values("author_order").iterrows():
        lines.append(f"{row['full_name']}: {row['contribution_roles']}.")
    return "\n".join(lines)


def dryrun_report(audit: pd.DataFrame) -> str:
    ready = bool(audit["ready"].all())
    verdict = "READY_TO_INSERT_METADATA" if ready else "DRY_RUN_FAILED_PLACEHOLDERS_REMAIN"
    placeholder_total = int(audit["placeholder_cells"].sum())
    return f"""# ZEAMAP v0.1 Stage 5.16 Metadata Ingestion Dry-Run Report

日期：2026-06-06

## Verdict

`{verdict}`

## Summary

- Metadata files audited: {audit.shape[0]}
- Ready files: {int(audit["ready"].sum())}
- Placeholder cells remaining: {placeholder_total}

## Interpretation

This dry-run prepares the final manuscript metadata insertion workflow. It intentionally does not modify the target-journal manuscript, does not create a Git tag and does not execute a repository release.

Current result: author/reviewer/figure metadata are still placeholders, so final insertion is blocked. Once the templates are filled, rerun this script to generate a title-page preview and contribution statement ready to insert into the final manuscript.

## Audit Table

See:

- `docs/2026-06-06-zeamap-v0-1-stage5-16-metadata-ingestion-audit.tsv`

## Generated Previews

- `docs/2026-06-06-zeamap-v0-1-stage5-16-title-page-preview.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-16-author-contribution-preview.md`

## Next Required Action

Fill these templates:

- `docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv`
- `docs/2026-06-06-zeamap-v0-1-affiliation-template.tsv`
- `docs/2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv`
- `docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv`

Then rerun:

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_16_metadata_ingestion_dryrun.py
```
"""


def stage_report(audit: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.16 Report: Metadata Ingestion Dry-Run

日期：2026-06-06

## Completed

- Built metadata ingestion dry-run script.
- Audited author, affiliation, reviewer and final figure templates.
- Generated title-page and author-contribution previews.
- Confirmed current templates are not yet ready for final insertion.
- Updated README and progress plan.

## Current State

Ready metadata files: {int(audit["ready"].sum())}/{audit.shape[0]}

The workflow is ready, but the templates still require true author-side information. No release/tag/DOI was created.

## Next Stage

Stage 5.17 should run after real metadata are filled. It should insert metadata into the target manuscript, rerun preflight and then execute the repository release if all gates pass.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.16 author-confirmed release execution | 下一步 | 填入真实元数据后重跑 preflight，通过后创建 tag/release/DOI 并写回最终稿 |",
        "| 阶段 5.16 metadata ingestion dry-run | 已完成 dry-run | 已输出 metadata ingestion audit、title-page preview 和 contribution preview；真实元数据仍未填 |\n| 阶段 5.17 final metadata insertion and release | 下一步 | 真实元数据填完后写回最终稿、重跑 preflight、创建 release/tag/DOI |",
    )
    if "Metadata ingestion dry-run: 1 file" not in text:
        text = text.replace(
            "Action-item table: 1 file",
            "Action-item table: 1 file\nMetadata ingestion dry-run: 1 file\nTitle-page preview: 1 file\nContribution preview: 1 file",
        )
    if "## 阶段 5.17：final metadata insertion and release" not in text:
        text += """

## 阶段 5.17：final metadata insertion and release

状态：下一步，需要真实作者元数据。

目标：

在 author/reviewer/figure 模板全部填完后，将真实元数据写回目标期刊稿件，并执行 release/tag/DOI。

执行条件：

- Stage 5.15 preflight 为 `READY_FOR_RELEASE_EXECUTION`。
- Stage 5.16 metadata ingestion dry-run 为 `READY_TO_INSERT_METADATA`。
- 通讯作者确认 final upload package。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.15 preflight validation 初版。",
        "Stage 5.15 preflight validation 和 Stage 5.16 metadata ingestion dry-run 初版。",
    )
    text = text.replace(
        "Stage 5.14 human metadata/release templates 和 Stage 5.15 preflight validation 和 Stage 5.16 metadata ingestion dry-run 初版。",
        "Stage 5.14 human metadata/release templates、Stage 5.15 preflight validation 和 Stage 5.16 metadata ingestion dry-run 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    audit = build_ingestion_audit()
    audit.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-16-metadata-ingestion-audit.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-16-title-page-preview.md", authors_preview())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-16-author-contribution-preview.md", contribution_preview())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-16-dryrun-report.md", dryrun_report(audit))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-16-report.md", stage_report(audit))
    update_docs()
    print("Stage 5.16 metadata ingestion dry-run generated.")


if __name__ == "__main__":
    main()
