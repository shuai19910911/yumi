#!/usr/bin/env python3
"""Build Stage 5.30 author metadata ingestion templates and dry-run gate."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.md"
PREVIOUS_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-29-final-submission-gate.tsv"

AUTHOR_TEMPLATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-author-metadata-template.tsv"
AFFILIATION_TEMPLATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-affiliation-template.tsv"
STATEMENT_TEMPLATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-funding-coi-acknowledgement-template.tsv"
DRY_RUN_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-author-ingestion-dry-run-audit.tsv"
FILLED_PREVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-author-metadata-filled-manuscript-preview.md"
FINAL_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-ars-author-metadata-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"


AUTHOR_COLUMNS = [
    "author_order",
    "full_name",
    "initials",
    "email",
    "orcid",
    "affiliation_id_list",
    "corresponding_author",
    "equal_contribution",
    "contribution_roles",
    "approval_confirmed",
    "coi_confirmed",
    "notes",
]

AFFILIATION_COLUMNS = ["affiliation_id", "affiliation_text", "approval_confirmed", "notes"]
STATEMENT_COLUMNS = ["statement_type", "statement_text", "approval_confirmed", "notes"]


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def ensure_templates() -> None:
    if not AUTHOR_TEMPLATE.exists():
        pd.DataFrame(
            [
                {
                    "author_order": 1,
                    "full_name": "TO_COMPLETE",
                    "initials": "TO_COMPLETE",
                    "email": "TO_COMPLETE",
                    "orcid": "TO_COMPLETE_OR_NA",
                    "affiliation_id_list": "1",
                    "corresponding_author": "yes",
                    "equal_contribution": "no",
                    "contribution_roles": "Conceptualization; Data curation; Formal analysis; Software; Visualization; Writing-original draft; Writing-review/editing",
                    "approval_confirmed": "no",
                    "coi_confirmed": "no",
                    "notes": "Replace placeholders before submission.",
                }
            ],
            columns=AUTHOR_COLUMNS,
        ).to_csv(AUTHOR_TEMPLATE, sep="\t", index=False)
    if not AFFILIATION_TEMPLATE.exists():
        pd.DataFrame(
            [
                {
                    "affiliation_id": 1,
                    "affiliation_text": "TO_COMPLETE",
                    "approval_confirmed": "no",
                    "notes": "Use official institution wording.",
                }
            ],
            columns=AFFILIATION_COLUMNS,
        ).to_csv(AFFILIATION_TEMPLATE, sep="\t", index=False)
    if not STATEMENT_TEMPLATE.exists():
        pd.DataFrame(
            [
                {
                    "statement_type": "funding",
                    "statement_text": "TO_COMPLETE",
                    "approval_confirmed": "no",
                    "notes": "Insert grant names/numbers or no-specific-funding statement.",
                },
                {
                    "statement_type": "acknowledgements",
                    "statement_text": "TO_COMPLETE",
                    "approval_confirmed": "no",
                    "notes": "Insert author-approved acknowledgements.",
                },
                {
                    "statement_type": "competing_interests",
                    "statement_text": "TO_COMPLETE",
                    "approval_confirmed": "no",
                    "notes": "Insert author-approved COI statement.",
                },
            ],
            columns=STATEMENT_COLUMNS,
        ).to_csv(STATEMENT_TEMPLATE, sep="\t", index=False)


def read_templates() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    authors = pd.read_csv(AUTHOR_TEMPLATE, sep="\t").fillna("")
    affiliations = pd.read_csv(AFFILIATION_TEMPLATE, sep="\t").fillna("")
    statements = pd.read_csv(STATEMENT_TEMPLATE, sep="\t").fillna("")
    return authors, affiliations, statements


def has_placeholder(value: object) -> bool:
    text = str(value).strip()
    return not text or "TO_COMPLETE" in text or text.lower() in {"yes/no", "na/complete"}


def validate(authors: pd.DataFrame, affiliations: pd.DataFrame, statements: pd.DataFrame) -> pd.DataFrame:
    rows = []
    missing_author_fields = []
    for col in ["full_name", "initials", "email", "affiliation_id_list", "contribution_roles"]:
        if col not in authors.columns or authors[col].map(has_placeholder).any():
            missing_author_fields.append(col)
    approval_ok = "approval_confirmed" in authors.columns and authors["approval_confirmed"].str.lower().eq("yes").all()
    coi_ok = "coi_confirmed" in authors.columns and authors["coi_confirmed"].str.lower().eq("yes").all()
    corr_ok = "corresponding_author" in authors.columns and authors["corresponding_author"].str.lower().eq("yes").any()
    rows.append(
        {
            "check": "author_metadata_fields",
            "status": "pass" if not missing_author_fields else "human_required",
            "evidence": "All required author fields populated." if not missing_author_fields else "Missing or placeholder fields: " + "; ".join(missing_author_fields),
        }
    )
    rows.append(
        {
            "check": "author_approval_confirmed",
            "status": "pass" if approval_ok else "human_required",
            "evidence": "All authors have approval_confirmed=yes." if approval_ok else "Every author row must set approval_confirmed=yes.",
        }
    )
    rows.append(
        {
            "check": "author_coi_confirmed",
            "status": "pass" if coi_ok else "human_required",
            "evidence": "All authors have coi_confirmed=yes." if coi_ok else "Every author row must set coi_confirmed=yes.",
        }
    )
    rows.append(
        {
            "check": "corresponding_author_present",
            "status": "pass" if corr_ok else "human_required",
            "evidence": "At least one corresponding author present." if corr_ok else "At least one author row must set corresponding_author=yes.",
        }
    )
    affiliation_ok = (
        set(AFFILIATION_COLUMNS).issubset(affiliations.columns)
        and not affiliations["affiliation_text"].map(has_placeholder).any()
        and affiliations["approval_confirmed"].str.lower().eq("yes").all()
    )
    rows.append(
        {
            "check": "affiliations_complete",
            "status": "pass" if affiliation_ok else "human_required",
            "evidence": "Affiliations populated and approved." if affiliation_ok else "Affiliation text and approval_confirmed=yes are required.",
        }
    )
    required_statements = {"funding", "acknowledgements", "competing_interests"}
    present = set(statements.get("statement_type", pd.Series(dtype=str)).astype(str))
    statements_ok = (
        required_statements.issubset(present)
        and not statements["statement_text"].map(has_placeholder).any()
        and statements["approval_confirmed"].str.lower().eq("yes").all()
    )
    rows.append(
        {
            "check": "funding_acknowledgements_coi_complete",
            "status": "pass" if statements_ok else "human_required",
            "evidence": "Funding, acknowledgements and COI statements populated and approved." if statements_ok else "Funding, acknowledgements and COI statement_text plus approval_confirmed=yes are required.",
        }
    )
    return pd.DataFrame(rows)


def superscript_number(number: object) -> str:
    mapping = str.maketrans("0123456789,", "⁰¹²³⁴⁵⁶⁷⁸⁹,")
    return str(number).translate(mapping)


def format_authors(authors: pd.DataFrame) -> str:
    parts = []
    for _, row in authors.sort_values("author_order").iterrows():
        marker = superscript_number(row["affiliation_id_list"])
        corr = "*" if str(row["corresponding_author"]).lower() == "yes" else ""
        parts.append(f"{row['full_name']}{marker}{corr}")
    return ", ".join(parts)


def format_affiliations(affiliations: pd.DataFrame) -> str:
    parts = []
    for _, row in affiliations.sort_values("affiliation_id").iterrows():
        parts.append(f"{superscript_number(row['affiliation_id'])} {row['affiliation_text']}")
    return "\n\n".join(parts)


def format_corresponding(authors: pd.DataFrame) -> str:
    corr = authors[authors["corresponding_author"].str.lower() == "yes"]
    parts = []
    for _, row in corr.sort_values("author_order").iterrows():
        parts.append(f"{row['full_name']} ({row['email']})")
    return "; ".join(parts)


def format_contributions(authors: pd.DataFrame) -> str:
    lines = []
    for _, row in authors.sort_values("author_order").iterrows():
        lines.append(f"{row['initials']}: {row['contribution_roles']}.")
    return "\n\n".join(lines)


def statement_lookup(statements: pd.DataFrame, key: str) -> str:
    match = statements[statements["statement_type"] == key]
    if len(match) == 0:
        return "TO_COMPLETE"
    return str(match.iloc[0]["statement_text"])


def build_preview(authors: pd.DataFrame, affiliations: pd.DataFrame, statements: pd.DataFrame, audit: pd.DataFrame) -> str:
    text = SOURCE_MANUSCRIPT.read_text(encoding="utf-8")
    ready = audit["status"].eq("pass").all()
    if not ready:
        text = text.replace(
            "Authors: To be completed.",
            "Authors: TO_COMPLETE (Stage 5.30 dry run: fill author metadata template first).",
        )
        text = text.replace(
            "Affiliations: To be completed.",
            "Affiliations: TO_COMPLETE (Stage 5.30 dry run: fill affiliation template first).",
        )
        text = text.replace(
            "Corresponding author: To be completed.",
            "Corresponding author: TO_COMPLETE (Stage 5.30 dry run: fill corresponding author email first).",
        )
        return text

    text = text.replace("Authors: To be completed.", "Authors: " + format_authors(authors))
    text = text.replace("Affiliations: To be completed.", "Affiliations:\n\n" + format_affiliations(affiliations))
    text = text.replace("Corresponding author: To be completed.", "Corresponding author: " + format_corresponding(authors))
    text = re.sub(
        r"## Author Contributions\n\n.*?\n\n## Funding",
        "## Author Contributions\n\n" + format_contributions(authors) + "\n\n## Funding",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"## Funding\n\n.*?\n\n## Acknowledgements",
        "## Funding\n\n" + statement_lookup(statements, "funding") + "\n\n## Acknowledgements",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"## Acknowledgements\n\n.*?\n\n## Competing Interests",
        "## Acknowledgements\n\n" + statement_lookup(statements, "acknowledgements") + "\n\n## Competing Interests",
        text,
        flags=re.S,
    )
    text = re.sub(
        r"## Competing Interests\n\n.*?\n\n## Ethics Statement",
        "## Competing Interests\n\n" + statement_lookup(statements, "competing_interests") + "\n\n## Ethics Statement",
        text,
        flags=re.S,
    )
    return text


def build_gate(audit: pd.DataFrame) -> pd.DataFrame:
    previous = pd.read_csv(PREVIOUS_GATE, sep="\t")
    rows = previous.to_dict("records")
    all_ready = audit["status"].eq("pass").all()
    rows.insert(
        0,
        {
            "gate": "author_metadata_ingestion_pipeline",
            "status": "pass",
            "evidence": "Stage 5.30 created structured author/affiliation/funding/COI templates and a validation/fill-preview script.",
        },
    )
    for row in rows:
        if row["gate"] == "author_metadata":
            row["status"] = "pass" if all_ready else "human_required"
            row["evidence"] = "Stage 5.30 templates validated and author metadata preview can be filled." if all_ready else "Stage 5.30 templates exist, but real author metadata and approvals are still missing."
        if row["gate"] == "funding_acknowledgements_coi":
            row["status"] = "pass" if all_ready else "human_required"
            row["evidence"] = "Funding/acknowledgements/COI statements validated from Stage 5.30 template." if all_ready else "Stage 5.30 statement template exists, but author-approved text is still missing."
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_report(audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    pass_count = int((gate["status"] == "pass").sum())
    human_count = int((gate["status"] == "human_required").sum())
    fail_count = int((gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.30 Author Metadata Ingestion Report

日期：2026-06-06

## Verdict

`AUTHOR_METADATA_PIPELINE_READY_REAL_AUTHOR_INPUT_REQUIRED`

## What changed

- Created structured author, affiliation, funding, acknowledgements and COI templates.
- Added validation checks for author approval, COI confirmation, corresponding author, affiliations and statements.
- Generated a dry-run manuscript preview without inventing author metadata.
- Updated the final gate while keeping author-only blockers as `human_required`.

## Gate summary

- pass/human_required/fail: {pass_count}/{human_count}/{fail_count}

## Dry-run audit

{markdown_table(audit)}

## Required author action

Fill these files with real, author-approved values and rerun `mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py`:

- `{AUTHOR_TEMPLATE.relative_to(ROOT)}`
- `{AFFILIATION_TEMPLATE.relative_to(ROOT)}`
- `{STATEMENT_TEMPLATE.relative_to(ROOT)}`
"""
    write_text(REPORT, text)


def write_ars_review(audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.30 ARS Author Metadata Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite finalization rule that author identity, contribution, funding and COI statements cannot be invented by the agent. The stage is successful only as a pipeline/template preparation step unless real author-approved metadata are present.

## Editorial-style verdict

`PIPELINE_READY_AUTHOR_INPUT_REQUIRED`

## Reviewer synthesis

- Integrity reviewer: no author names, affiliations, grants or COI statements were fabricated.
- Format reviewer: the template fields match the manuscript sections that still block submission.
- Reproducibility reviewer: the same script can be rerun after real metadata are supplied to create a filled manuscript preview.
- Devil's advocate: this does not close the author metadata blocker; it only makes closure executable once authors provide verified information.

## Audit

{markdown_table(audit)}

## Gate

{markdown_table(gate)}
"""
    write_text(ARS_REVIEW, text)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package 和 Stage 5.29 DOCX/HTML export package。",
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package 和 Stage 5.30 author metadata ingestion pipeline。"
    )
    text = text.replace(
        "Current status: Stage 5.29 has produced clean Markdown, DOCX and HTML manuscript exports plus a format-compliance gate for the The Plant Genome route. Remaining blockers are author-only: metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID.",
        "Current status: Stage 5.30 has prepared an executable author metadata ingestion pipeline and dry-run validation templates. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID."
    )
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    addition = """

### Stage 5.30 - Author metadata ingestion pipeline

通俗解读：这一阶段没有假装已经知道作者信息，而是把作者信息、单位、Funding、致谢和 COI 拆成可填写的 TSV 模板，并写了一个验证/填稿脚本。作者把真实信息填进去后，脚本可以自动检查每个作者是否确认投稿、是否确认 COI、是否有通讯作者、单位和声明是否完整，然后生成填好作者信息的稿件预览。

阶段结论：作者信息 blocker 还没有关闭，因为真实作者信息仍未提供；但关闭这个 blocker 的机器流程已经准备好。下一步只需要填模板并重跑脚本。
"""
    if "### Stage 5.30 - Author metadata ingestion pipeline" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def main() -> None:
    ensure_templates()
    authors, affiliations, statements = read_templates()
    audit = validate(authors, affiliations, statements)
    preview = build_preview(authors, affiliations, statements, audit)
    gate = build_gate(audit)
    audit.to_csv(DRY_RUN_AUDIT, sep="\t", index=False)
    write_text(FILLED_PREVIEW, preview)
    gate.to_csv(FINAL_GATE, sep="\t", index=False)
    write_report(audit, gate)
    write_ars_review(audit, gate)
    update_readme()
    update_progress()
    print(f"Wrote {AUTHOR_TEMPLATE}")
    print(f"Wrote {AFFILIATION_TEMPLATE}")
    print(f"Wrote {STATEMENT_TEMPLATE}")
    print(f"Wrote {DRY_RUN_AUDIT}")
    print(f"Wrote {FILLED_PREVIEW}")
    print(f"Wrote {FINAL_GATE}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
