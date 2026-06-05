#!/usr/bin/env python3
"""Build Stage 5.15 author-confirmed release preflight validation outputs."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TABLES = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "manuscript_tables"


REQUIRED_FILES = [
    "README.md",
    "docs/progress-plan.md",
    "docs/2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md",
    "docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md",
    "docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv",
    "docs/2026-06-06-zeamap-v0-1-cover-letter-draft.md",
    "docs/2026-06-06-zeamap-v0-1-reviewer-suggestion-draft.md",
    "docs/2026-06-06-zeamap-v0-1-repository-release-plan.md",
    "docs/2026-06-06-zeamap-v0-1-final-submission-gate-audit.md",
    "docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-affiliation-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md",
    "docs/2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv",
    "docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv",
    "docs/2026-06-06-zeamap-v0-1-release-execution-commands.md",
    "docs/2026-06-06-zeamap-v0-1-human-metadata-readiness-audit.md",
    "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_external_annotation.tsv",
    "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv",
]


HUMAN_TEMPLATE_FILES = [
    "docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-affiliation-template.tsv",
    "docs/2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv",
    "docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv",
    "docs/2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md",
]


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


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def file_manifest() -> pd.DataFrame:
    rows = []
    for rel in REQUIRED_FILES:
        path = ROOT / rel
        rows.append(
            {
                "path": rel,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
                "sha256": sha256(path) if path.exists() else "",
                "release_include": True,
            }
        )
    return pd.DataFrame(rows)


def placeholder_audit() -> pd.DataFrame:
    markers = ["TO_COMPLETE", "yes/no", "[", "]", "pass/revise"]
    rows = []
    for rel in HUMAN_TEMPLATE_FILES:
        path = ROOT / rel
        text = read_text(path) if path.exists() else ""
        for marker in markers:
            count = text.count(marker)
            if count:
                rows.append(
                    {
                        "file": rel,
                        "marker": marker,
                        "count": count,
                        "blocks_release": marker in {"TO_COMPLETE", "yes/no", "pass/revise"},
                    }
                )
    return pd.DataFrame(rows)


def gate_status(manifest: pd.DataFrame, placeholders: pd.DataFrame) -> pd.DataFrame:
    required_missing = int((~manifest["exists"]).sum())
    blocking_placeholders = int(placeholders.loc[placeholders["blocks_release"], "count"].sum()) if not placeholders.empty else 0
    figure_blockers = 0
    if not placeholders.empty:
        figure_rows = placeholders["file"].str.contains("final-figure")
        figure_blockers = int(placeholders.loc[figure_rows & placeholders["blocks_release"], "count"].sum())
    gates = [
        {
            "gate": "required_files_present",
            "status": "pass" if required_missing == 0 else "fail",
            "evidence": f"missing_required_files={required_missing}",
            "blocks_submission": required_missing > 0,
        },
        {
            "gate": "human_metadata_filled",
            "status": "fail" if blocking_placeholders else "pass",
            "evidence": f"blocking_placeholder_count={blocking_placeholders}",
            "blocks_submission": blocking_placeholders > 0,
        },
        {
            "gate": "reference_doi_audit_exists",
            "status": "pass" if (ROOT / "docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv").exists() else "fail",
            "evidence": "reference DOI audit generated at Stage 5.13",
            "blocks_submission": not (ROOT / "docs/2026-06-06-zeamap-v0-1-reference-doi-audit.tsv").exists(),
        },
        {
            "gate": "release_not_yet_executed",
            "status": "pending_until_preflight_passes" if blocking_placeholders else "ready_to_execute",
            "evidence": "release commands are drafted but intentionally not executed before author metadata is confirmed",
            "blocks_submission": blocking_placeholders > 0,
        },
        {
            "gate": "final_figure_manual_check",
            "status": "fail" if figure_blockers else "pass",
            "evidence": f"figure_manual_check_placeholder_count={figure_blockers}",
            "blocks_submission": figure_blockers > 0,
        },
    ]
    return pd.DataFrame(gates)


def actionable_tasks(placeholders: pd.DataFrame) -> pd.DataFrame:
    rows = [
        {
            "priority": 0,
            "task": "Fill the single human-input form first",
            "file": "docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv",
            "owner": "corresponding author",
            "done_when": "No TO_COMPLETE, yes/no or pass/revise placeholders remain; then synchronize it with Stage 5.17 --apply.",
        },
        {
            "priority": 1,
            "task": "Fill author metadata template",
            "file": "docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv",
            "owner": "authors",
            "done_when": "No TO_COMPLETE or yes/no fields remain; author approvals and COI confirmations are yes.",
        },
        {
            "priority": 2,
            "task": "Fill affiliation template",
            "file": "docs/2026-06-06-zeamap-v0-1-affiliation-template.tsv",
            "owner": "authors",
            "done_when": "Exact institution, department, city, country and postal code are final.",
        },
        {
            "priority": 3,
            "task": "Complete funding/COI/acknowledgement form",
            "file": "docs/2026-06-06-zeamap-v0-1-author-contribution-funding-coi-form.md",
            "owner": "corresponding author",
            "done_when": "Funding, acknowledgements and competing-interest statements are final.",
        },
        {
            "priority": 4,
            "task": "Replace reviewer profiles with named reviewers",
            "file": "docs/2026-06-06-zeamap-v0-1-named-reviewer-worksheet.tsv",
            "owner": "corresponding author",
            "done_when": "3-5 suggested reviewers and optional opposed reviewers have names, emails and conflict checks.",
        },
        {
            "priority": 5,
            "task": "Manually inspect Figure 1-3",
            "file": "docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv",
            "owner": "analyst/corresponding author",
            "done_when": "All figure rows are marked pass after PDF/SVG/PNG visual inspection.",
        },
        {
            "priority": 6,
            "task": "Execute repository release/tag and optional archive DOI",
            "file": "docs/2026-06-06-zeamap-v0-1-release-execution-commands.md",
            "owner": "repository owner",
            "done_when": "GitHub release/tag exists and DOI is inserted into Data/Code Availability if required.",
        },
    ]
    if not (ROOT / "docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv").exists():
        rows = [row for row in rows if row["priority"] != 0]
    return pd.DataFrame(rows)


def report(manifest: pd.DataFrame, placeholders: pd.DataFrame, gates: pd.DataFrame, tasks: pd.DataFrame) -> str:
    commit = git_commit()
    missing = int((~manifest["exists"]).sum())
    blocking = int(placeholders.loc[placeholders["blocks_release"], "count"].sum()) if not placeholders.empty else 0
    verdict = "NO_SUBMIT_AUTHOR_METADATA_PENDING" if missing or blocking else "READY_FOR_RELEASE_EXECUTION"
    return f"""# ZEAMAP v0.1 Stage 5.15 Preflight Validation Report

日期：2026-06-06

## Verdict

`{verdict}`

Current commit checked: `{commit}`

## Summary

- Required files checked: {manifest.shape[0]}
- Missing required files: {missing}
- Blocking placeholder count: {blocking}
- Gate rows: {gates.shape[0]}
- Actionable remaining tasks: {tasks.shape[0]}

## Interpretation

The manuscript package is technically assembled and all required project artifacts are present. However, the release/submission gate remains closed because author-side metadata templates still contain placeholders and yes/no confirmations. This is expected: the current process should not create a release tag, DOI or final submission claim until author metadata and figure checks are completed.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-15-file-manifest.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-15-placeholder-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-15-gate-status.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-15-action-items.tsv`

## Next Step

Preferred route: fill the Stage 5.17 single human-input form, synchronize it, then rerun this preflight:

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_17_single_human_input_pack.py --apply
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
```

Direct Stage 5.14 template editing is still possible, but the single form reduces inconsistent author/reviewer/figure metadata.

Legacy direct-template route:

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py
```

Only execute the release commands when this report changes to `READY_FOR_RELEASE_EXECUTION`.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.15 author-confirmed release execution | 下一步 | 填入真实作者信息、命名审稿人、人工图件确认、GitHub release/DOI 并写回最终稿 |",
        "| 阶段 5.15 preflight validation | 已完成校验器 | 已输出文件 manifest、placeholder audit、gate status 和 action items；真实 release 仍需作者填表后执行 |\n| 阶段 5.16 author-confirmed release execution | 下一步 | 填入真实元数据后重跑 preflight，通过后创建 tag/release/DOI 并写回最终稿 |",
    )
    if "Preflight manifest: 1 file" not in text:
        text = text.replace(
            "Release command draft: 1 file",
            "Release command draft: 1 file\nPreflight manifest: 1 file\nPlaceholder audit: 1 file\nGate status table: 1 file\nAction-item table: 1 file",
        )
    if "## 阶段 5.16：author-confirmed release execution" not in text:
        text += """

## 阶段 5.16：author-confirmed release execution

状态：下一步，需要真实作者元数据。

目标：

在 Stage 5.15 preflight 通过后，执行真正的 release/tag/DOI，并把 release DOI 写回最终稿件。

执行条件：

- author metadata template 无 `TO_COMPLETE`。
- 所有 yes/no 字段已确认。
- final figure manual checklist 全部 pass。
- reviewer worksheet 有命名审稿人并完成 conflict check。
- repository visibility 已确认。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.14 human metadata/release templates 初版。",
        "Stage 5.14 human metadata/release templates 和 Stage 5.15 preflight validation 初版。",
    )
    text = text.replace(
        "Stage 5.13 final submission gate 和 Stage 5.14 human metadata/release templates 和 Stage 5.15 preflight validation 初版。",
        "Stage 5.13 final submission gate、Stage 5.14 human metadata/release templates 和 Stage 5.15 preflight validation 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    manifest = file_manifest()
    placeholders = placeholder_audit()
    gates = gate_status(manifest, placeholders)
    tasks = actionable_tasks(placeholders)

    manifest.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-15-file-manifest.tsv", sep="\t", index=False)
    placeholders.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-15-placeholder-audit.tsv", sep="\t", index=False)
    gates.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-15-gate-status.tsv", sep="\t", index=False)
    tasks.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-15-action-items.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-15-preflight-report.md", report(manifest, placeholders, gates, tasks))
    update_docs()
    print("Stage 5.15 preflight validation generated.")


if __name__ == "__main__":
    main()
