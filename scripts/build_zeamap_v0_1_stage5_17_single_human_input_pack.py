#!/usr/bin/env python3
"""Build Stage 5.17 single human-input package.

The package reduces the final author-side submission blockers to one editable
TSV. It can later sync that TSV back into the existing Stage 5.14 templates,
but this default run does not fabricate metadata or execute a release.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"

SINGLE_FORM = DOCS / "2026-06-06-zeamap-v0-1-single-human-input-form.tsv"
AUTHOR_TSV = DOCS / "2026-06-06-zeamap-v0-1-author-metadata-template.tsv"
AFFILIATION_TSV = DOCS / "2026-06-06-zeamap-v0-1-affiliation-template.tsv"
REVIEWER_TSV = DOCS / "2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv"
FIGURE_TSV = DOCS / "2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv"
FUNDING_COI_MD = DOCS / "2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md"


FORM_COLUMNS = [
    "section",
    "record_id",
    "field",
    "value",
    "required",
    "target_file",
    "guidance",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_table(path: Path) -> pd.DataFrame:
    return pd.read_csv(path, sep="\t").fillna("")


def has_placeholder(value: object) -> bool:
    text = str(value)
    return any(marker in text for marker in ["TO_COMPLETE", "yes/no", "pass/revise", "[", "]"])


def load_existing_or_empty(path: Path) -> pd.DataFrame:
    if path.exists():
        return read_table(path)
    return pd.DataFrame()


def rows_from_wide(section: str, df: pd.DataFrame, record_col: str, target_file: Path, guidance: dict[str, str]) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    if df.empty:
        return rows
    seen: set[str] = set()
    for idx, row in df.iterrows():
        candidate_id = str(row.get(record_col, "")).strip()
        if not candidate_id or has_placeholder(candidate_id) or candidate_id in seen:
            candidate_id = f"{section}_{idx + 1}"
        seen.add(candidate_id)
        for field in df.columns:
            rows.append(
                {
                    "section": section,
                    "record_id": candidate_id,
                    "field": field,
                    "value": row.get(field, ""),
                    "required": "yes",
                    "target_file": str(target_file.relative_to(ROOT)),
                    "guidance": guidance.get(field, ""),
                }
            )
    return rows


def default_statement_rows() -> list[dict[str, object]]:
    statements = [
        (
            "funding_statement",
            "TO_COMPLETE",
            "Use exact grant agency and grant numbers, or state that no specific funding was received.",
        ),
        (
            "competing_interest_statement",
            "TO_COMPLETE",
            "Use the final journal-approved competing-interest wording.",
        ),
        (
            "acknowledgements",
            "TO_COMPLETE",
            "List only people/groups who approved acknowledgement where required.",
        ),
        (
            "author_approval_statement",
            "TO_COMPLETE",
            "Confirm all authors approved manuscript, author order, affiliations, contributions and submission.",
        ),
    ]
    return [
        {
            "section": "manuscript_statement",
            "record_id": key,
            "field": "value",
            "value": value,
            "required": "yes",
            "target_file": str(FUNDING_COI_MD.relative_to(ROOT)),
            "guidance": guidance,
        }
        for key, value, guidance in statements
    ]


def build_initial_form() -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    rows.extend(
        rows_from_wide(
            "author",
            load_existing_or_empty(AUTHOR_TSV),
            "author_order",
            AUTHOR_TSV,
            {
                "full_name": "Full author name exactly as submitted to the journal.",
                "initials": "Initials used in CRediT contribution statement.",
                "email": "Email for corresponding authors; optional for non-corresponding authors if journal permits.",
                "orcid": "ORCID iD, or NA if not used.",
                "affiliation_id_list": "Semicolon-separated affiliation IDs from the affiliation section.",
                "corresponding_author": "yes or no.",
                "equal_contribution": "yes or no.",
                "contribution_roles": "Semicolon-separated CRediT roles.",
                "approval_confirmed": "yes only after author approval is documented.",
                "coi_confirmed": "yes only after competing-interest disclosure is documented.",
            },
        )
    )
    rows.extend(
        rows_from_wide(
            "affiliation",
            load_existing_or_empty(AFFILIATION_TSV),
            "affiliation_id",
            AFFILIATION_TSV,
            {
                "institution": "Exact official institutional spelling.",
                "department_or_lab": "Exact department, lab, college or institute.",
                "city": "City for journal affiliation line.",
                "state_or_province": "State/province; use NA if not applicable.",
                "country": "Country/region name required by target journal.",
                "postal_code": "Postal code; use NA if target journal does not require it.",
            },
        )
    )
    rows.extend(
        rows_from_wide(
            "reviewer",
            load_existing_or_empty(REVIEWER_TSV),
            "name",
            REVIEWER_TSV,
            {
                "type": "suggested or opposed_optional.",
                "email": "Institutional email preferred.",
                "institution": "Current institution.",
                "expertise": "Short expertise label.",
                "reason": "Why this reviewer is appropriate or why opposed reviewer has conflict.",
                "conflict_checked": "yes only after checking conflicts.",
            },
        )
    )
    rows.extend(
        rows_from_wide(
            "figure_check",
            load_existing_or_empty(FIGURE_TSV),
            "figure",
            FIGURE_TSV,
            {
                "pdf_opened": "yes after opening final PDF.",
                "svg_opened": "yes after opening final SVG.",
                "png_opened": "yes after opening final PNG.",
                "panel_labels_correct": "yes after visual inspection.",
                "text_readable_at_journal_size": "yes after checking print-size readability.",
                "no_label_overlap": "yes after checking labels and annotations.",
                "legend_matches_figure": "yes after checking caption/legend consistency.",
                "color_accessibility_checked": "yes after colorblind-safe inspection.",
                "final_status": "pass only when all visual checks pass.",
            },
        )
    )
    rows.extend(default_statement_rows())
    return pd.DataFrame(rows, columns=FORM_COLUMNS)


def ensure_single_form() -> pd.DataFrame:
    if SINGLE_FORM.exists():
        df = read_table(SINGLE_FORM)
        missing = [col for col in FORM_COLUMNS if col not in df.columns]
        if missing:
            raise SystemExit(f"Single form is missing columns: {missing}")
        return df[FORM_COLUMNS]
    df = build_initial_form()
    df.to_csv(SINGLE_FORM, sep="\t", index=False)
    return df


def pivot_section(df: pd.DataFrame, section: str, record_field: str) -> pd.DataFrame:
    sub = df.loc[df["section"].eq(section)].copy()
    if sub.empty:
        return pd.DataFrame()
    wide = sub.pivot_table(index="record_id", columns="field", values="value", aggfunc="first").reset_index(drop=True)
    if record_field in wide.columns:
        wide = wide.sort_values(record_field, key=lambda s: s.astype(str))
    return wide.fillna("")


def build_funding_coi_text(df: pd.DataFrame) -> str:
    values = {
        row["record_id"]: row["value"]
        for _, row in df.loc[df["section"].eq("manuscript_statement")].iterrows()
    }
    return f"""# Author Contribution, Funding And Competing Interest Form

日期：2026-06-06

## Author Approval

{values.get("author_approval_statement", "TO_COMPLETE")}

## Funding Statement

{values.get("funding_statement", "TO_COMPLETE")}

## Competing Interest Statement

{values.get("competing_interest_statement", "TO_COMPLETE")}

## Acknowledgements

{values.get("acknowledgements", "TO_COMPLETE")}

## CRediT Contribution Roles

Author-specific CRediT roles are synchronized from `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`.
"""


def sync_targets(df: pd.DataFrame) -> None:
    targets = [
        ("author", "author_order", AUTHOR_TSV),
        ("affiliation", "affiliation_id", AFFILIATION_TSV),
        ("reviewer", "name", REVIEWER_TSV),
        ("figure_check", "figure", FIGURE_TSV),
    ]
    for section, record_field, path in targets:
        wide = pivot_section(df, section, record_field)
        if not wide.empty:
            wide.to_csv(path, sep="\t", index=False)
    write_text(FUNDING_COI_MD, build_funding_coi_text(df))


def audit_form(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for section, sub in df.groupby("section", sort=False):
        required = sub.loc[sub["required"].astype(str).str.lower().eq("yes")]
        placeholder_count = int(required["value"].map(has_placeholder).sum())
        blank_count = int(required["value"].astype(str).str.strip().eq("").sum())
        rows.append(
            {
                "section": section,
                "rows": int(sub.shape[0]),
                "required_rows": int(required.shape[0]),
                "placeholder_or_bracket_rows": placeholder_count,
                "blank_required_rows": blank_count,
                "ready": placeholder_count == 0 and blank_count == 0,
            }
        )
    return pd.DataFrame(rows)


def sync_dryrun_report(audit: pd.DataFrame, apply: bool) -> str:
    ready = bool(audit["ready"].all()) if not audit.empty else False
    verdict = "READY_TO_SYNC_AND_PREFLIGHT" if ready else "NOT_READY_HUMAN_FIELDS_REMAIN"
    mode = "applied to Stage 5.14 templates" if apply else "dry-run only; Stage 5.14 templates were not overwritten"
    return f"""# ZEAMAP v0.1 Stage 5.17 Single Human-Input Sync Report

日期：2026-06-06

## Verdict

`{verdict}`

Mode: {mode}

## What This Adds

Stage 5.17 makes the submission-blocking human fields easier to handle. Instead of editing several files independently, the corresponding author can fill one table:

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`

After the table has no placeholders, rerun this script with `--apply` to synchronize the author, affiliation, reviewer, funding/COI and figure-check templates. Then rerun Stage 5.15 and Stage 5.16.

## Audit Summary

- Sections checked: {audit.shape[0]}
- Ready sections: {int(audit["ready"].sum()) if not audit.empty else 0}
- Placeholder/bracket rows remaining: {int(audit["placeholder_or_bracket_rows"].sum()) if not audit.empty else 0}
- Blank required rows remaining: {int(audit["blank_required_rows"].sum()) if not audit.empty else 0}

## Next Command After Filling The Form

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_17_single_human_input_pack.py --apply
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_16_metadata_ingestion_dryrun.py
```
"""


def filling_guide() -> str:
    return """# ZEAMAP v0.1 Single Human-Input Form Guide

日期：2026-06-06

## 为什么新增这个文件

投稿最后卡住的不是计算结果，而是人工确认信息：作者顺序、单位、ORCID、基金、利益冲突、审稿人、最终图件人工检查和 release 确认。之前这些信息分散在多个模板里，容易漏填或互相不一致。

现在只需要优先填写：

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`

## 怎么填

每一行是一个需要确认的字段：

- `section`：信息类型，例如 `author`、`affiliation`、`reviewer`、`figure_check`。
- `record_id`：同一类信息中的记录编号或名称。
- `field`：具体字段名。
- `value`：真正要填写的值。
- `required`：是否投稿前必填。
- `guidance`：填写提示。

把 `value` 里的 `TO_COMPLETE`、`yes/no`、`pass/revise` 和方括号示例全部替换为真实值。不能确认的信息不要猜，留给通讯作者确认。

## 填完后做什么

运行：

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_17_single_human_input_pack.py --apply
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_16_metadata_ingestion_dryrun.py
```

只有 Stage 5.15 显示 `READY_FOR_RELEASE_EXECUTION`，Stage 5.16 显示 `READY_TO_INSERT_METADATA`，才进入真实 tag/release/DOI 步骤。
"""


def ars_self_review(audit: pd.DataFrame) -> str:
    ready = bool(audit["ready"].all()) if not audit.empty else False
    decision = "provisional_minor_revision_after_author_metadata" if ready else "major_revision_metadata_blocker"
    return f"""# ZEAMAP v0.1 Stage 5.17 ARS-Style Submission Self-Review

日期：2026-06-06

Workflow basis: academic-research-suite academic-pipeline + academic-paper-reviewer gates.

## Editorial Decision

`{decision}`

## Gate Assessment

- Scientific dataset, benchmark, GEMMA LMM GWAS, candidate loci, manuscript tables and figures are assembled.
- Claims are appropriately bounded as candidate intervals rather than validated causal variants.
- Citation/reference DOI audit exists, but should still receive human bibliographic review before submission.
- The remaining blocker is human-side metadata and confirmation, not computational reproducibility.

## Required Before Final Submission

1. Fill the single human-input form with real author-side information.
2. Apply the single form back to Stage 5.14 templates.
3. Rerun Stage 5.15 preflight and Stage 5.16 metadata ingestion dry-run.
4. Perform manual visual inspection of Figures 1-3 at journal size.
5. Create repository tag/release and archive DOI only after all gates pass.

## Current Quantitative Gate

- Sections checked in single form: {audit.shape[0]}
- Ready sections: {int(audit["ready"].sum()) if not audit.empty else 0}
- Placeholder/bracket rows remaining: {int(audit["placeholder_or_bracket_rows"].sum()) if not audit.empty else 0}
- Blank required rows remaining: {int(audit["blank_required_rows"].sum()) if not audit.empty else 0}
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = progress.read_text(encoding="utf-8")
    text = text.replace(
        "| 阶段 5.17 final metadata insertion and release | 下一步 | 真实元数据填完后写回最终稿、重跑 preflight、创建 release/tag/DOI |",
        "| 阶段 5.17 single human-input package | 已完成初版 | 已输出单一人工信息总表、同步 dry-run、填写说明和 ARS 投稿闸门自评；真实元数据仍未填 |\n| 阶段 5.18 final metadata insertion and release | 下一步 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
    )
    if "Single human-input form: 1 file" not in text:
        text = text.replace(
            "Contribution preview: 1 file",
            "Contribution preview: 1 file\nSingle human-input form: 1 file\nSingle-form sync audit: 1 file\nSingle-form filling guide: 1 file\nStage 5.17 ARS self-review: 1 file",
        )
    if "## 阶段 5.17：single human-input package" not in text:
        text += """

## 阶段 5.17：single human-input package

状态：已完成初版，但真实作者信息仍未填。

为什么做这一步：

投稿前必须有人确认作者、单位、基金、利益冲突、审稿人和图件人工检查。之前这些内容散在多个模板中，容易漏填。Stage 5.17 把它们收敛成一个总表，填完后可自动同步回 Stage 5.14 模板。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`
- `docs/2026-06-06-zeamap-v0-1-single-human-input-form-guide.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-single-form-sync-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-sync-report.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-ars-self-review.md`

下一步：

真实信息填完后执行 Stage 5.17 `--apply`，再重跑 Stage 5.15 和 Stage 5.16。只有两个门槛都通过后，才进入真实 release/tag/DOI。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.15 preflight validation 和 Stage 5.16 metadata ingestion dry-run 初版。",
        "Stage 5.15 preflight validation、Stage 5.16 metadata ingestion dry-run 和 Stage 5.17 single human-input package 初版。",
    )
    text = text.replace(
        "Stage 5.14 human metadata/release templates、Stage 5.15 preflight validation 和 Stage 5.16 metadata ingestion dry-run 初版。",
        "Stage 5.14 human metadata/release templates、Stage 5.15 preflight validation、Stage 5.16 metadata ingestion dry-run 和 Stage 5.17 single human-input package 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Synchronize the single form back to Stage 5.14 templates.")
    args = parser.parse_args()

    df = ensure_single_form()
    audit = audit_form(df)
    if args.apply:
        sync_targets(df)
    audit.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-17-single-form-sync-audit.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-single-human-input-form-guide.md", filling_guide())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-17-sync-report.md", sync_dryrun_report(audit, args.apply))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-17-ars-self-review.md", ars_self_review(audit))
    write_text(
        DOCS / "2026-06-06-zeamap-v0-1-stage5-17-report.md",
        sync_dryrun_report(audit, args.apply).replace("Sync Report", "Report"),
    )
    update_docs()
    print("Stage 5.17 single human-input package generated.")


if __name__ == "__main__":
    main()
