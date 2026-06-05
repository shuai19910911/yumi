#!/usr/bin/env python3
"""Build Stage 5.31 figure approval and release-PID readiness package."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
PREVIOUS_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-final-submission-gate.tsv"
FIGURE_QA = DOCS / "2026-06-06-zeamap-v0-1-stage5-26-final-figure-technical-qa.tsv"

FIGURE_APPROVAL_TEMPLATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-figure-final-approval-template.tsv"
FIGURE_APPROVAL_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-figure-approval-audit.tsv"
RELEASE_NOTES = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-github-release-notes.md"
ZENODO_METADATA = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-zenodo-metadata-draft.json"
RELEASE_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-release-readiness-audit.tsv"
FINAL_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-ars-figure-release-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"

RELEASE_TAG = "zeamap-oil-v0.1-submission"
TITLE = "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP"


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()


def git_status_short() -> str:
    return subprocess.check_output(["git", "status", "--short"], cwd=ROOT, text=True).strip()


def ensure_figure_template() -> pd.DataFrame:
    qa = pd.read_csv(FIGURE_QA, sep="\t")
    if not FIGURE_APPROVAL_TEMPLATE.exists():
        rows = []
        for _, row in qa.iterrows():
            rows.append(
                {
                    "figure": row["figure"],
                    "purpose": row["role"],
                    "png_path": row["png_path"],
                    "pdf_path": row["pdf_path"],
                    "svg_path": row["svg_path"],
                    "pdf_opened": "no",
                    "svg_opened": "no",
                    "png_opened": "no",
                    "panel_labels_correct": "no",
                    "text_readable_at_journal_size": "no",
                    "no_label_overlap": "no",
                    "legend_matches_figure": "no",
                    "color_accessibility_checked": "no",
                    "final_status": "revise",
                    "approver": "TO_COMPLETE",
                    "approval_date": "TO_COMPLETE",
                    "notes": "Open PDF/SVG/PNG and approve at target journal size.",
                }
            )
        pd.DataFrame(rows).to_csv(FIGURE_APPROVAL_TEMPLATE, sep="\t", index=False)
    return pd.read_csv(FIGURE_APPROVAL_TEMPLATE, sep="\t").fillna("")


def audit_figures(template: pd.DataFrame) -> pd.DataFrame:
    required_yes = [
        "pdf_opened",
        "svg_opened",
        "png_opened",
        "panel_labels_correct",
        "text_readable_at_journal_size",
        "no_label_overlap",
        "legend_matches_figure",
        "color_accessibility_checked",
    ]
    rows = []
    for _, row in template.iterrows():
        missing = [col for col in required_yes if str(row.get(col, "")).lower() != "yes"]
        approver_missing = str(row.get("approver", "")).strip() in {"", "TO_COMPLETE"}
        date_missing = str(row.get("approval_date", "")).strip() in {"", "TO_COMPLETE"}
        status_ok = str(row.get("final_status", "")).lower() == "pass"
        ok = not missing and not approver_missing and not date_missing and status_ok
        evidence = "Figure approved by author-side visual review." if ok else "Missing: " + "; ".join(missing + (["approver"] if approver_missing else []) + (["approval_date"] if date_missing else []) + ([] if status_ok else ["final_status=pass"]))
        rows.append(
            {
                "figure": row["figure"],
                "status": "pass" if ok else "human_required",
                "evidence": evidence,
            }
        )
    return pd.DataFrame(rows)


def build_release_notes(head: str) -> None:
    text = f"""# GitHub Release Notes Draft

Tag: `{RELEASE_TAG}`

Title:

```text
ZEAMAP maize oil-trait manuscript submission package v0.1
```

Target commit when this draft was generated:

```text
{head}
```

Description:

```text
Submission package for "{TITLE}".

This release contains manuscript-facing scripts, documentation, summary tables, figure outputs, candidate-locus annotation and reproducibility notes for the ZEAMAP maize oil-trait v0.1 analysis. The analysis uses public ZEAMAP processed data and prioritizes candidate intervals for maize oil and fatty-acid traits through accession-level harmonization, genotype-to-phenotype prediction, calibrated GEMMA mixed-model GWAS and conservative gene annotation.

Large raw ZEAMAP inputs and large intermediate matrices are not included in the repository. Their public sources, local paths and regeneration steps are documented in the project README and stage reports.
```

Pre-release rule:

Do not create this release until author metadata, funding/COI statements, final figure approval and final clean manuscript export have been completed.
"""
    write_text(RELEASE_NOTES, text)


def build_zenodo_metadata(head: str) -> None:
    metadata = {
        "title": "ZEAMAP maize oil-trait manuscript submission package v0.1",
        "upload_type": "dataset",
        "description": (
            "Submission package for prediction-guided mixed-model GWAS prioritization of maize oil-trait "
            "candidate loci in ZEAMAP. Includes manuscript-facing scripts, documentation, summary tables, "
            "figure outputs and reproducibility notes. Large raw public ZEAMAP inputs and large intermediate "
            "matrices are not included and are documented for regeneration."
        ),
        "creators": [
            {
                "name": "TO_COMPLETE",
                "affiliation": "TO_COMPLETE",
                "orcid": "TO_COMPLETE_OR_NA",
            }
        ],
        "keywords": [
            "maize",
            "ZEAMAP",
            "GWAS",
            "genomic prediction",
            "oil traits",
            "fatty acid composition",
            "GEMMA",
        ],
        "related_identifiers": [
            {
                "identifier": "https://github.com/shuai19910911/yumi",
                "relation": "isSupplementTo",
                "scheme": "url",
            }
        ],
        "version": "v0.1-submission",
        "notes": f"Draft metadata generated at git commit {head}. Replace creator fields before archive submission.",
    }
    write_text(ZENODO_METADATA, json.dumps(metadata, indent=2, ensure_ascii=False))


def release_audit(head: str, status: str) -> pd.DataFrame:
    rows = [
        {
            "check": "release_notes_draft",
            "status": "pass",
            "evidence": f"Release notes draft exists for tag {RELEASE_TAG}.",
        },
        {
            "check": "zenodo_metadata_draft",
            "status": "human_required",
            "evidence": "Zenodo metadata draft exists but creator fields require real author metadata.",
        },
        {
            "check": "clean_git_status_before_release",
            "status": "human_required" if status else "pass",
            "evidence": "Working tree currently has uncommitted changes for Stage 5.31." if status else "Working tree clean at audit time.",
        },
        {
            "check": "tag_not_created_by_agent",
            "status": "human_required",
            "evidence": f"Do not create tag {RELEASE_TAG} until final author-approved manuscript is committed.",
        },
        {
            "check": "archive_pid_not_available",
            "status": "human_required",
            "evidence": "A DOI/PID can only be created after an author-approved release/archive step.",
        },
    ]
    df = pd.DataFrame(rows)
    df["git_head_at_audit"] = head
    return df


def build_gate(figure_audit: pd.DataFrame) -> pd.DataFrame:
    previous = pd.read_csv(PREVIOUS_GATE, sep="\t")
    rows = previous.to_dict("records")
    figure_ok = figure_audit["status"].eq("pass").all()
    rows.insert(
        0,
        {
            "gate": "figure_release_readiness_pipeline",
            "status": "pass",
            "evidence": "Stage 5.31 created figure approval template, release notes draft and Zenodo metadata draft.",
        },
    )
    for row in rows:
        if row["gate"] == "main_figure_human_visual_review":
            row["status"] = "pass" if figure_ok else "human_required"
            row["evidence"] = "All main figures have author-side visual approval." if figure_ok else "Stage 5.31 figure approval template exists, but author-side visual approval is still missing."
        if row["gate"] == "repository_release_pid":
            row["status"] = "human_required"
            row["evidence"] = "Stage 5.31 release notes and Zenodo metadata drafts exist, but tag/release/archive DOI must wait for author-approved final commit."
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_report(figure_audit: pd.DataFrame, rel_audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    pass_count = int((gate["status"] == "pass").sum())
    human_count = int((gate["status"] == "human_required").sum())
    fail_count = int((gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.31 Figure Approval And Release Readiness Report

日期：2026-06-06

## Verdict

`FIGURE_RELEASE_PIPELINE_READY_AUTHOR_APPROVAL_REQUIRED`

## What changed

- Created a structured Figure 1-3 final visual approval template.
- Added a release notes draft for the GitHub submission release.
- Added Zenodo metadata draft with creator fields left as `TO_COMPLETE`.
- Updated final gate without creating a tag, GitHub release or archive DOI.

## Gate summary

- pass/human_required/fail: {pass_count}/{human_count}/{fail_count}

## Figure approval audit

{markdown_table(figure_audit)}

## Release readiness audit

{markdown_table(rel_audit)}
"""
    write_text(REPORT, text)


def write_ars_review(figure_audit: pd.DataFrame, rel_audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.31 ARS Figure And Release Readiness Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite finalization boundary: figure approval and release PID are author-controlled gates. The agent may prepare templates and drafts, but must not mark them complete without author evidence or create a final release before approval.

## Editorial-style verdict

`PIPELINE_READY_FINAL_APPROVAL_REQUIRED`

## Reviewer synthesis

- Figure reviewer: machine technical QA already passed, but author-side visual approval remains missing until every figure checklist row is set to pass with approver/date.
- Reproducibility reviewer: GitHub release notes and Zenodo metadata drafts are now prepared, but the final tag and archive DOI must wait for author-approved final commit.
- Integrity reviewer: creator metadata is intentionally `TO_COMPLETE`; no author identity was fabricated.
- Devil's advocate: the release PID blocker is not closed by draft metadata. It closes only after a real tagged release and archive PID exist.

## Final gate

{markdown_table(gate)}
"""
    write_text(ARS_REVIEW, text)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package 和 Stage 5.30 author metadata ingestion pipeline。",
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package、Stage 5.30 author metadata ingestion pipeline 和 Stage 5.31 figure/release readiness pipeline。"
    )
    text = text.replace(
        "Current status: Stage 5.30 has prepared an executable author metadata ingestion pipeline and dry-run validation templates. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID.",
        "Current status: Stage 5.31 has prepared executable figure approval and release/Zenodo metadata workflows. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID."
    )
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    addition = """

### Stage 5.31 - Figure approval and release readiness pipeline

通俗解读：这一阶段继续处理剩余人工关卡。机器已经确认 Figure 1-3 文件存在且分辨率足够，但最终投稿前还需要作者逐张打开 PDF/SVG/PNG，确认标签、文字、重叠、legend 和颜色。Stage 5.31 把这些确认项做成可填写模板。同时生成 GitHub release notes 和 Zenodo metadata 草稿，但不创建 tag、不发布 release、不申请 DOI。

阶段结论：图件批准和 release DOI/PID 的执行流程已经准备好；但这两个 blocker 仍不能关闭，因为还缺作者最终批准、最终提交版本和真实 creator 信息。
"""
    if "### Stage 5.31 - Figure approval and release readiness pipeline" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def main() -> None:
    head = git_head()
    status = git_status_short()
    figure_template = ensure_figure_template()
    figure_audit = audit_figures(figure_template)
    build_release_notes(head)
    build_zenodo_metadata(head)
    rel_audit = release_audit(head, status)
    gate = build_gate(figure_audit)
    figure_audit.to_csv(FIGURE_APPROVAL_AUDIT, sep="\t", index=False)
    rel_audit.to_csv(RELEASE_AUDIT, sep="\t", index=False)
    gate.to_csv(FINAL_GATE, sep="\t", index=False)
    write_report(figure_audit, rel_audit, gate)
    write_ars_review(figure_audit, rel_audit, gate)
    update_readme()
    update_progress()
    print(f"Wrote {FIGURE_APPROVAL_TEMPLATE}")
    print(f"Wrote {FIGURE_APPROVAL_AUDIT}")
    print(f"Wrote {RELEASE_NOTES}")
    print(f"Wrote {ZENODO_METADATA}")
    print(f"Wrote {RELEASE_AUDIT}")
    print(f"Wrote {FINAL_GATE}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
