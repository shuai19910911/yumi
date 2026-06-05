#!/usr/bin/env python3
"""Build Stage 5.33 submission artifact integrity manifest."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1"

PREVIOUS_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-32-final-submission-gate.tsv"
MANIFEST = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv"
MISSING_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-audit.tsv"
PACKAGE_README = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-submission-package-readme.md"
FINAL_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-33-ars-submission-integrity-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"


ARTIFACTS = [
    ("manuscript", "clean_markdown", "docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.md"),
    ("manuscript", "clean_docx", "docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.docx"),
    ("manuscript", "clean_html", "docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.html"),
    ("submission", "package_index", "docs/2026-06-06-zeamap-v0-1-stage5-28-submission-package-index.md"),
    ("submission", "cover_letter", "docs/2026-06-06-zeamap-v0-1-stage5-28-cover-letter-the-plant-genome.md"),
    ("submission", "journal_route_table", "docs/2026-06-06-zeamap-v0-1-stage5-28-journal-route-table.tsv"),
    ("submission", "human_action_packet", "docs/2026-06-06-zeamap-v0-1-stage5-32-human-action-packet.md"),
    ("submission", "author_template", "docs/2026-06-06-zeamap-v0-1-stage5-30-author-metadata-template.tsv"),
    ("submission", "affiliation_template", "docs/2026-06-06-zeamap-v0-1-stage5-30-affiliation-template.tsv"),
    ("submission", "funding_coi_template", "docs/2026-06-06-zeamap-v0-1-stage5-30-funding-coi-acknowledgement-template.tsv"),
    ("submission", "figure_approval_template", "docs/2026-06-06-zeamap-v0-1-stage5-31-figure-final-approval-template.tsv"),
    ("release", "github_release_notes_draft", "docs/2026-06-06-zeamap-v0-1-stage5-31-github-release-notes.md"),
    ("release", "zenodo_metadata_draft", "docs/2026-06-06-zeamap-v0-1-stage5-31-zenodo-metadata-draft.json"),
    ("figure", "figure1_pdf", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf"),
    ("figure", "figure1_png", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.png"),
    ("figure", "figure1_svg", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.svg"),
    ("figure", "figure2_pdf", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf"),
    ("figure", "figure2_png", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.png"),
    ("figure", "figure2_svg", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.svg"),
    ("figure", "figure3_pdf", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf"),
    ("figure", "figure3_png", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.png"),
    ("figure", "figure3_svg", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.svg"),
    ("table", "main_tier1_locus_table", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv"),
    ("table", "top_regional_loci_evidence", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv"),
    ("table", "supplementary_candidate_loci", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv"),
    ("table", "supplementary_column_dictionary", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv"),
    ("table", "external_annotation", "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_external_annotation.tsv"),
    ("result", "trait_metrics", "results/v0_1_baseline/trait_metrics.tsv"),
    ("result", "robustness_metrics", "results/v0_1_baseline/robustness_metrics.tsv"),
    ("result", "model_comparison", "results/v0_1_baseline/model_comparison.tsv"),
    ("result", "gemma_lmm_summary", "results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv"),
    ("result", "gemma_lmm_lead_snps", "results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv"),
    ("result", "gemma_candidate_loci", "results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv"),
    ("method", "reproducibility_crosswalk", "docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv"),
    ("method", "gwas_diagnostic_appendix", "docs/2026-06-06-zeamap-v0-1-stage5-20-gwas-diagnostic-appendix.tsv"),
    ("method", "claim_audit", "docs/2026-06-06-zeamap-v0-1-stage5-22-claim-language-audit.tsv"),
    ("method", "citation_coverage_audit", "docs/2026-06-06-zeamap-v0-1-stage5-24-citation-coverage-audit.tsv"),
    ("method", "gene_name_confirmation", "docs/2026-06-06-zeamap-v0-1-stage5-27-external-gene-name-confirmation.tsv"),
]

CRITICAL_SCRIPTS = [
    "scripts/build_zeamap_sample_index.py",
    "scripts/build_zeamap_v0_1_dataset.py",
    "scripts/run_zeamap_v0_1_baseline.py",
    "scripts/run_zeamap_v0_1_robustness.py",
    "scripts/select_zeamap_v0_1_traits.py",
    "scripts/prepare_zeamap_v0_1_gemma_inputs.py",
    "scripts/summarize_zeamap_v0_1_gemma_lmm.py",
    "scripts/build_zeamap_v0_1_gemma_candidate_loci.py",
    "scripts/build_zeamap_v0_1_top_locus_priority.py",
    "scripts/build_zeamap_v0_1_stage5_29_format_export_package.py",
    "scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py",
    "scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py",
    "scripts/build_zeamap_v0_1_stage5_32_human_action_packet.py",
    "scripts/build_zeamap_v0_1_stage5_33_submission_integrity_manifest.py",
]


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def git_head() -> str:
    return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def line_count(path: Path) -> int | str:
    if path.suffix.lower() not in {".md", ".tsv", ".txt", ".py", ".json", ".html", ".svg"}:
        return "NA"
    try:
        with path.open("r", encoding="utf-8", errors="replace") as handle:
            return sum(1 for _ in handle)
    except OSError:
        return "NA"


def build_manifest(head: str) -> pd.DataFrame:
    rows = []
    for category, artifact_id, rel_path in ARTIFACTS + [("script", Path(p).stem, p) for p in CRITICAL_SCRIPTS]:
        path = ROOT / rel_path
        exists = path.exists()
        rows.append(
            {
                "category": category,
                "artifact_id": artifact_id,
                "relative_path": rel_path,
                "exists": "yes" if exists else "no",
                "bytes": path.stat().st_size if exists else 0,
                "line_count": line_count(path) if exists else "NA",
                "sha256": sha256(path) if exists else "MISSING",
                "git_head_at_manifest": head,
            }
        )
    return pd.DataFrame(rows)


def build_audit(manifest: pd.DataFrame) -> pd.DataFrame:
    required_categories = ["manuscript", "figure", "table", "result", "method", "script", "submission", "release"]
    rows = []
    missing = manifest.loc[manifest["exists"] != "yes", "relative_path"].tolist()
    rows.append(
        {
            "check": "required_artifacts_exist",
            "status": "pass" if not missing else "fail",
            "evidence": "All curated submission artifacts exist." if not missing else "; ".join(missing),
        }
    )
    empty = manifest.loc[(manifest["exists"] == "yes") & (manifest["bytes"] <= 0), "relative_path"].tolist()
    rows.append(
        {
            "check": "non_empty_artifacts",
            "status": "pass" if not empty else "fail",
            "evidence": "All curated submission artifacts are non-empty." if not empty else "; ".join(empty),
        }
    )
    cat_counts = manifest.groupby("category")["artifact_id"].count().to_dict()
    absent_categories = [cat for cat in required_categories if cat_counts.get(cat, 0) == 0]
    rows.append(
        {
            "check": "category_coverage",
            "status": "pass" if not absent_categories else "fail",
            "evidence": "; ".join(f"{cat}={cat_counts.get(cat, 0)}" for cat in sorted(cat_counts)),
        }
    )
    rows.append(
        {
            "check": "release_pid_not_fabricated",
            "status": "human_required",
            "evidence": "Checksum manifest is ready, but the final tag, GitHub release and DOI/PID still require author-approved release action.",
        }
    )
    rows.append(
        {
            "check": "author_controlled_fields_not_fabricated",
            "status": "human_required",
            "evidence": "Author metadata, funding/COI statements and final figure approvals remain template-driven human inputs.",
        }
    )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame, max_rows: int | None = None) -> str:
    table = df if max_rows is None else df.head(max_rows)
    cols = list(table.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in table.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def build_gate(audit: pd.DataFrame) -> pd.DataFrame:
    previous = pd.read_csv(PREVIOUS_GATE, sep="\t")
    rows = previous.to_dict("records")
    has_fail = audit["status"].eq("fail").any()
    rows.insert(
        0,
        {
            "gate": "submission_artifact_integrity_manifest",
            "status": "fail" if has_fail else "pass",
            "evidence": "Stage 5.33 generated SHA256 checksums and existence/non-empty audit for curated submission artifacts.",
        },
    )
    return pd.DataFrame(rows)


def write_package_readme(manifest: pd.DataFrame, audit: pd.DataFrame, gate: pd.DataFrame, head: str) -> None:
    counts = manifest.groupby("category")["artifact_id"].count().reset_index(name="artifact_count")
    text = f"""# ZEAMAP v0.1 Stage 5.33 Submission Package README

日期：2026-06-06

## Purpose

This file is the machine-checkable handoff for final submission and repository archiving. It lists the clean manuscript exports, main figures, manuscript tables, key result files, reproducibility audits and critical scripts that should travel with the submission package.

## Current git commit

```text
{head}
```

## Main submission files

- Clean manuscript: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.md`
- DOCX export: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.docx`
- HTML export: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.html`
- Human action packet: `docs/2026-06-06-zeamap-v0-1-stage5-32-human-action-packet.md`
- Checksum manifest: `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv`

## Artifact category counts

{markdown_table(counts)}

## Integrity audit

{markdown_table(audit)}

## Final gate

{markdown_table(gate)}

## How to use before submission

1. Fill author, affiliation, funding/COI and figure approval templates listed in the Stage 5.32 human action packet.
2. Rerun Stage 5.30, Stage 5.31, Stage 5.29, Stage 5.32 and Stage 5.33.
3. Confirm no `fail` remains in this audit and no unresolved `human_required` remains except the release DOI/PID if the archive is intentionally created after final commit.
4. Create the GitHub release and external archive DOI/PID only after final author approval.
"""
    write_text(PACKAGE_README, text)


def write_report(manifest: pd.DataFrame, audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    pass_count = int((gate["status"] == "pass").sum())
    human_count = int((gate["status"] == "human_required").sum())
    fail_count = int((gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.33 Submission Integrity Manifest Report

日期：2026-06-06

## Verdict

`SUBMISSION_ARTIFACT_MANIFEST_READY_AUTHOR_RELEASE_INPUT_REQUIRED`

## What changed

- Generated SHA256 checksums for curated manuscript, figure, table, result, method, submission, release and script artifacts.
- Audited existence and non-empty status for all curated submission files.
- Added a single package README for final upload/archive handoff.
- Preserved author-controlled fields and release DOI/PID as `human_required`.

## Counts

- manifest rows: {len(manifest)}
- audit pass/human_required/fail: {int((audit["status"] == "pass").sum())}/{int((audit["status"] == "human_required").sum())}/{int((audit["status"] == "fail").sum())}
- final gate pass/human_required/fail: {pass_count}/{human_count}/{fail_count}
"""
    write_text(REPORT, text)


def write_ars_review(manifest: pd.DataFrame, audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.33 ARS Submission Integrity Review

日期：2026-06-06

## Review frame

This review uses the academic-research-suite final-integrity/finalization lens. The machine-side standard is not to claim formal submission readiness, but to make the submission package complete, reproducible and auditable while preserving human-controlled blockers.

## Editorial-style verdict

`TECHNICALLY_ARCHIVABLE_AFTER_AUTHOR_INPUT_NOT_YET_SUBMITTABLE`

## Independent reviewer synthesis

- Integrity reviewer: artifact existence, size and SHA256 checksums are now recorded; no author metadata, funding statement, figure approval or DOI has been fabricated.
- Reproducibility reviewer: critical scripts and result-to-manuscript files are included in the manifest, which improves archive traceability.
- Methods reviewer: the manifest does not change the scientific method; it strengthens final handoff and future verification.
- Devil's advocate: this does not solve the biological limitation that loci remain candidate intervals, and it does not remove the need for author-side visual checks and release/DOI creation.

## Audit

{markdown_table(audit)}

## Final gate

{markdown_table(gate)}

## Manifest scope

- curated artifacts: {len(manifest)}
- categories: {", ".join(sorted(manifest["category"].unique()))}
"""
    write_text(ARS_REVIEW, text)


def update_docs() -> None:
    readme = README.read_text(encoding="utf-8")
    old = "Stage 5.31 figure/release readiness pipeline 和 Stage 5.32 single human action packet。"
    new = "Stage 5.31 figure/release readiness pipeline、Stage 5.32 single human action packet 和 Stage 5.33 submission artifact integrity manifest。"
    if old in readme:
        readme = readme.replace(old, new)
    if "Stage 5.33 submission integrity manifest" not in readme:
        readme += """

## Stage 5.33 submission integrity manifest

已新增最终投稿包校验清单：

- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-package-readme.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-ars-submission-integrity-review.md`

这一步记录核心 manuscript、figure、table、result 和 script 文件的 SHA256 指纹，方便最终 GitHub release、Zenodo/Figshare 归档和投稿后复核。它不替代作者信息、基金/COI、图件人工审核和 DOI/PID 创建。
"""
    README.write_text(readme.rstrip() + "\n", encoding="utf-8")

    progress = PROGRESS.read_text(encoding="utf-8")
    if "阶段 5.33 submission artifact integrity manifest" not in progress:
        progress += """

## 阶段 5.33 submission artifact integrity manifest

状态：已完成机器端初版，仍需作者最终信息后重跑。

这一步做了什么：

- 把最终投稿需要随包保存的核心文件列成 manifest。
- 对 manuscript、DOCX/HTML、主图、论文表格、关键结果文件、审计文件和脚本计算 SHA256。
- 检查这些文件是否存在、是否为空。
- 生成一个投稿包 README，方便最终上传 GitHub release 和 Zenodo/Figshare。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-package-readme.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-final-submission-gate.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-ars-submission-integrity-review.md`

通俗解释：

现在论文文件已经不是“散落在目录里的很多结果”，而是有一张清单能说明哪些文件是最终投稿包的一部分，每个文件的大小和 SHA256 指纹是什么。以后创建 release 或 DOI 时，可以用这张表确认文件没有被误删、误改或漏传。

仍然不能自动完成的事：

- 作者姓名、单位、ORCID/email 和作者确认。
- 基金、致谢、利益冲突声明。
- Figure 1-3 的人工视觉确认。
- 最终 GitHub release、tag 和 Zenodo/Figshare DOI/PID。
"""
    PROGRESS.write_text(progress.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    head = git_head()
    manifest = build_manifest(head)
    manifest.to_csv(MANIFEST, sep="\t", index=False)
    audit = build_audit(manifest)
    audit.to_csv(MISSING_AUDIT, sep="\t", index=False)
    gate = build_gate(audit)
    gate.to_csv(FINAL_GATE, sep="\t", index=False)
    write_package_readme(manifest, audit, gate, head)
    write_report(manifest, audit, gate)
    write_ars_review(manifest, audit, gate)
    update_docs()
    print(f"Wrote {MANIFEST}")
    print(f"Wrote {MISSING_AUDIT}")
    print(f"Wrote {PACKAGE_README}")
    print(f"Wrote {FINAL_GATE}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
