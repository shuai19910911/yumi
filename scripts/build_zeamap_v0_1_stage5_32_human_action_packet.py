#!/usr/bin/env python3
"""Build Stage 5.32 single-entry human action packet and blocker dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
FINAL_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-final-submission-gate.tsv"
AUTHOR_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-30-author-ingestion-dry-run-audit.tsv"
FIGURE_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-figure-approval-audit.tsv"
RELEASE_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-31-release-readiness-audit.tsv"

ACTION_PACKET = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-human-action-packet.md"
BLOCKER_DASHBOARD = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-blocker-dashboard.tsv"
COMMAND_CHECKLIST = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-post-human-input-command-checklist.md"
FINAL_GATE_OUT = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-ars-human-action-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"


AUTHOR_FILES = [
    "docs/2026-06-06-zeamap-v0-1-stage5-30-author-metadata-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-stage5-30-affiliation-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-stage5-30-funding-coi-acknowledgement-template.tsv",
]
FIGURE_FILE = "docs/2026-06-06-zeamap-v0-1-stage5-31-figure-final-approval-template.tsv"
RELEASE_FILES = [
    "docs/2026-06-06-zeamap-v0-1-stage5-31-github-release-notes.md",
    "docs/2026-06-06-zeamap-v0-1-stage5-31-zenodo-metadata-draft.json",
]


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def build_dashboard() -> pd.DataFrame:
    gate = pd.read_csv(FINAL_GATE, sep="\t")
    author = pd.read_csv(AUTHOR_AUDIT, sep="\t")
    figure = pd.read_csv(FIGURE_AUDIT, sep="\t")
    release = pd.read_csv(RELEASE_AUDIT, sep="\t")
    rows = []
    blocker_map = [
        {
            "blocker": "author_metadata",
            "current_status": gate.loc[gate["gate"] == "author_metadata", "status"].iloc[0],
            "what_to_fill": "; ".join(AUTHOR_FILES[:2]),
            "verification_command": "mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py",
            "evidence_after_done": "Stage 5.30 dry-run audit rows author_metadata_fields, author_approval_confirmed, corresponding_author_present and affiliations_complete all pass.",
            "current_missing_summary": "; ".join(author.loc[author["status"] != "pass", "check"].tolist()),
        },
        {
            "blocker": "funding_acknowledgements_coi",
            "current_status": gate.loc[gate["gate"] == "funding_acknowledgements_coi", "status"].iloc[0],
            "what_to_fill": AUTHOR_FILES[2],
            "verification_command": "mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py",
            "evidence_after_done": "Stage 5.30 dry-run audit row funding_acknowledgements_coi_complete passes.",
            "current_missing_summary": "; ".join(author.loc[author["status"] != "pass", "check"].tolist()),
        },
        {
            "blocker": "main_figure_human_visual_review",
            "current_status": gate.loc[gate["gate"] == "main_figure_human_visual_review", "status"].iloc[0],
            "what_to_fill": FIGURE_FILE,
            "verification_command": "mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py",
            "evidence_after_done": "Stage 5.31 figure approval audit rows for Figure 1-3 all pass.",
            "current_missing_summary": "; ".join(figure.loc[figure["status"] != "pass", "figure"].tolist()),
        },
        {
            "blocker": "repository_release_pid",
            "current_status": gate.loc[gate["gate"] == "repository_release_pid", "status"].iloc[0],
            "what_to_fill": "; ".join(RELEASE_FILES),
            "verification_command": "After final author-approved commit: git tag -a zeamap-oil-v0.1-submission -m \"ZEAMAP maize oil-trait manuscript submission package\"; git push origin zeamap-oil-v0.1-submission; create GitHub release; archive in Zenodo/Figshare; record DOI/PID.",
            "evidence_after_done": "Real release tag, GitHub release URL and archive DOI/PID recorded in final manuscript Data/Code Availability and release docs.",
            "current_missing_summary": "; ".join(release.loc[release["status"] != "pass", "check"].tolist()),
        },
    ]
    rows.extend(blocker_map)
    return pd.DataFrame(rows)


def build_final_gate() -> pd.DataFrame:
    gate = pd.read_csv(FINAL_GATE, sep="\t")
    rows = gate.to_dict("records")
    rows.insert(
        0,
        {
            "gate": "single_human_action_packet",
            "status": "pass",
            "evidence": "Stage 5.32 compiled one human action packet mapping every remaining blocker to files, commands and completion evidence.",
        },
    )
    return pd.DataFrame(rows)


def write_action_packet(dashboard: pd.DataFrame, final_gate: pd.DataFrame) -> None:
    text = f"""# ZEAMAP v0.1 Stage 5.32 Human Action Packet

日期：2026-06-06

## Purpose

This is the single entry point for closing the remaining submission blockers. The machine-side manuscript, citation, figure-file, export, annotation and submission-package gates are already prepared. What remains is author-controlled information and approval.

## Remaining blockers

{markdown_table(dashboard)}

## Fill these files first

1. Author metadata and author approval:
   - `{AUTHOR_FILES[0]}`
   - `{AUTHOR_FILES[1]}`

2. Funding, acknowledgements and competing interests:
   - `{AUTHOR_FILES[2]}`

3. Final figure visual approval:
   - `{FIGURE_FILE}`

4. Release and archive metadata:
   - `{RELEASE_FILES[0]}`
   - `{RELEASE_FILES[1]}`

## Rerun commands after filling author/figure templates

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_29_format_export_package.py
```

## Release only after all author-controlled gates pass

Do not create the final tag or release until author metadata, statements and figure approvals are complete and committed.

```bash
git status --short
git add README.md docs scripts
git commit -m "finalize submission metadata"
git tag -a zeamap-oil-v0.1-submission -m "ZEAMAP maize oil-trait manuscript submission package"
git push origin main
git push origin zeamap-oil-v0.1-submission
```

Then create a GitHub release from the tag and archive it with Zenodo/Figshare if required by the target journal. Record the DOI/PID in the manuscript Data Availability/Code Availability section.

## Final gate snapshot

{markdown_table(final_gate)}
"""
    write_text(ACTION_PACKET, text)


def write_command_checklist() -> None:
    text = """# Stage 5.32 Post-Human-Input Command Checklist

日期：2026-06-06

Run this only after filling the Stage 5.30 and Stage 5.31 templates.

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_29_format_export_package.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_32_human_action_packet.py
git diff --check
git status --short
```

Expected before release:

- Stage 5.30 author/funding audit rows all `pass`.
- Stage 5.31 figure approval rows all `pass`.
- Final gate has no `fail` and no `human_required` except release PID if the archive DOI is intentionally created after journal upload.
- DOCX/HTML export is regenerated from the filled manuscript.
"""
    write_text(COMMAND_CHECKLIST, text)


def write_report(dashboard: pd.DataFrame, final_gate: pd.DataFrame) -> None:
    pass_count = int((final_gate["status"] == "pass").sum())
    human_count = int((final_gate["status"] == "human_required").sum())
    fail_count = int((final_gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.32 Human Action Packet Report

日期：2026-06-06

## Verdict

`HUMAN_ACTION_PACKET_READY_FINAL_AUTHOR_INPUT_REQUIRED`

## What changed

- Compiled every remaining blocker into one action packet.
- Mapped each blocker to the exact template file, rerun command and completion evidence.
- Added a post-human-input command checklist.
- Preserved all author-controlled gates as `human_required`.

## Gate summary

- pass/human_required/fail: {pass_count}/{human_count}/{fail_count}

## Remaining blocker count

- {len(dashboard)} author-controlled blockers remain.
"""
    write_text(REPORT, text)


def write_ars_review(dashboard: pd.DataFrame, final_gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.32 ARS Human Action Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite finalization rule: human-controlled authorship, approval and release actions cannot be completed by the agent. The correct machine-side action is to make every remaining blocker explicit, executable and auditable.

## Editorial-style verdict

`READY_FOR_HUMAN_COMPLETION_NOT_READY_FOR_SUBMISSION`

## Reviewer synthesis

- Integrity reviewer: the packet does not fabricate author identity, funding, COI, figure approval or DOI.
- Format reviewer: all needed files and commands are now listed in one place.
- Reproducibility reviewer: after templates are filled, rerunning Stage 5.29-5.32 regenerates submission exports and gates.
- Devil's advocate: the manuscript is still not formally submission-ready until all four blocker rows are closed with evidence.

## Blocker dashboard

{markdown_table(dashboard)}

## Final gate

{markdown_table(final_gate)}
"""
    write_text(ARS_REVIEW, text)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package、Stage 5.30 author metadata ingestion pipeline 和 Stage 5.31 figure/release readiness pipeline。",
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package、Stage 5.30 author metadata ingestion pipeline、Stage 5.31 figure/release readiness pipeline 和 Stage 5.32 single human action packet。"
    )
    text = text.replace(
        "Current status: Stage 5.31 has prepared executable figure approval and release/Zenodo metadata workflows. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID.",
        "Current status: Stage 5.32 has compiled all remaining author-only blockers into one human action packet with exact files, commands and completion evidence. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID."
    )
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    addition = """

### Stage 5.32 - Single human action packet

通俗解读：这一阶段把最后剩下的 4 个人工关卡集中到一个文件里。现在作者不需要翻很多阶段文档，只需要打开 Stage 5.32 human action packet，按顺序填作者信息、Funding/COI/致谢、Figure 1-3 最终批准表，再按命令重跑脚本。release/tag/DOI 也列出了执行顺序，但仍必须等作者批准后再做。

阶段结论：机器侧已经把最后人工步骤整理成可执行清单；论文仍不能标记为最终投稿完成，因为真实作者信息、图件批准和 release DOI/PID 还没有发生。
"""
    if "### Stage 5.32 - Single human action packet" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def main() -> None:
    dashboard = build_dashboard()
    final_gate = build_final_gate()
    dashboard.to_csv(BLOCKER_DASHBOARD, sep="\t", index=False)
    final_gate.to_csv(FINAL_GATE_OUT, sep="\t", index=False)
    write_action_packet(dashboard, final_gate)
    write_command_checklist()
    write_report(dashboard, final_gate)
    write_ars_review(dashboard, final_gate)
    update_readme()
    update_progress()
    print(f"Wrote {ACTION_PACKET}")
    print(f"Wrote {BLOCKER_DASHBOARD}")
    print(f"Wrote {COMMAND_CHECKLIST}")
    print(f"Wrote {FINAL_GATE_OUT}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
