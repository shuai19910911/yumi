#!/usr/bin/env python3
"""Build Stage 5.18 reviewer-risk register and revision roadmap."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md"
PREFLIGHT = DOCS / "2026-06-06-zeamap-v0-1-stage5-15-preflight-report.md"
DRYRUN = DOCS / "2026-06-06-zeamap-v0-1-stage5-16-dryrun-report.md"
SINGLE_FORM_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-17-single-form-sync-audit.tsv"


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            value = str(row[col]).replace("|", "\\|").replace("\n", " ")
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def extract_verdict(path: Path) -> str:
    if not path.exists():
        return "MISSING"
    text = read_text(path)
    match = re.search(r"`([A-Z0-9_]+)`", text)
    return match.group(1) if match else "UNKNOWN"


def manuscript_metrics() -> dict[str, object]:
    text = read_text(MANUSCRIPT)
    sections = re.findall(r"^##+ ", text, flags=re.MULTILINE)
    words = re.findall(r"[A-Za-z0-9_+\-/]+", text)
    placeholder_terms = ["To be completed", "TO_COMPLETE", "Authors:", "Funding\n\nTo be completed"]
    return {
        "word_count_proxy": len(words),
        "heading_count": len(sections),
        "contains_author_placeholders": any(term in text for term in placeholder_terms),
        "has_claim_boundary_language": "not causal" in text.lower() or "candidate intervals" in text.lower(),
        "has_gemma_lambda": "0.984-1.018" in text,
        "has_data_availability": "## Data Availability Statement" in text,
        "has_code_availability": "## Code Availability Statement" in text,
    }


def single_form_summary() -> dict[str, int]:
    if not SINGLE_FORM_AUDIT.exists():
        return {"sections": 0, "ready_sections": 0, "placeholder_rows": -1}
    audit = pd.read_csv(SINGLE_FORM_AUDIT, sep="\t")
    return {
        "sections": int(audit.shape[0]),
        "ready_sections": int(audit["ready"].sum()),
        "placeholder_rows": int(audit["placeholder_or_bracket_rows"].sum()),
    }


def reviewer_risks(metrics: dict[str, object], preflight: str, dryrun: str, form: dict[str, int]) -> pd.DataFrame:
    rows = [
        {
            "risk_id": "R01",
            "reviewer_role": "Editor-in-chief",
            "likely_comment": "The manuscript is promising but may read as a short resource note unless the novelty and journal fit are sharpened.",
            "severity": "major",
            "current_evidence": f"proxy_word_count={metrics['word_count_proxy']}; target_route=The Plant Genome/G3",
            "response_strategy": "Expand the Introduction and Discussion around why prediction-guided GWAS adds value beyond a standard ZEAMAP reanalysis.",
            "required_action": "Add a stronger novelty paragraph and explicit contribution statement before final submission.",
            "owner": "machine_plus_author",
            "blocks_submission": True,
        },
        {
            "risk_id": "R02",
            "reviewer_role": "Methodology reviewer",
            "likely_comment": "Trait filtering, train/test splitting, covariates and kinship construction need enough detail for exact reproduction.",
            "severity": "major",
            "current_evidence": "Methods and parameter supplement exist, but the assembled main methods are concise.",
            "response_strategy": "Keep concise main methods but add a reproducibility checklist that maps each result to script, input, output and parameter choices.",
            "required_action": "Create a result-to-script reproducibility crosswalk and cite it in Methods/Data Availability.",
            "owner": "machine",
            "blocks_submission": False,
        },
        {
            "risk_id": "R03",
            "reviewer_role": "Statistical genetics reviewer",
            "likely_comment": "The GWAS result is calibrated by lambda GC, but reviewers may ask about QQ plots, MAF filtering, missingness and multiple-testing thresholds.",
            "severity": "major",
            "current_evidence": f"has_gemma_lambda={metrics['has_gemma_lambda']}; Stage 5.15={preflight}",
            "response_strategy": "Expose the exact GEMMA filters, thresholds and diagnostic files in a compact reviewer-facing table.",
            "required_action": "Add GWAS diagnostic appendix table covering lambda, Bonferroni/FDR/suggestive thresholds, sample count and SNP count per trait.",
            "owner": "machine",
            "blocks_submission": False,
        },
        {
            "risk_id": "R04",
            "reviewer_role": "Domain reviewer",
            "likely_comment": "The chr6 and chr9 biological interpretations need stronger literature support before they can carry the main biological story.",
            "severity": "major",
            "current_evidence": "Stage 5.11 external annotation hardening exists; current manuscript says final reference audit is still needed.",
            "response_strategy": "Keep causal language conservative, add a targeted oil/fatty-acid literature verification table and mark which claims are annotation-only.",
            "required_action": "Expand literature support for linoleic acid1 and fatty acyl-ACP thioesterase intervals.",
            "owner": "machine_plus_author",
            "blocks_submission": False,
        },
        {
            "risk_id": "R05",
            "reviewer_role": "Reproducibility reviewer",
            "likely_comment": "Large inputs are outside GitHub; the paper must make it easy to obtain the exact public sources and regenerate derivative outputs.",
            "severity": "major",
            "current_evidence": f"has_data_availability={metrics['has_data_availability']}; has_code_availability={metrics['has_code_availability']}",
            "response_strategy": "Add a release checklist tying CNGBdb accession, local excluded files, committed derivatives and scripts.",
            "required_action": "Create a data/code reproducibility crosswalk before release.",
            "owner": "machine",
            "blocks_submission": False,
        },
        {
            "risk_id": "R06",
            "reviewer_role": "Figure reviewer",
            "likely_comment": "The figure files are generated, but manual inspection at journal size has not been certified.",
            "severity": "major",
            "current_evidence": f"single_form_ready_sections={form['ready_sections']}/{form['sections']}; placeholder_rows={form['placeholder_rows']}",
            "response_strategy": "Do not claim final figure readiness until Figure 1-3 PDF/SVG/PNG checks are marked pass.",
            "required_action": "Complete final figure manual checklist after visual inspection.",
            "owner": "author_or_analyst",
            "blocks_submission": True,
        },
        {
            "risk_id": "R07",
            "reviewer_role": "Editorial office",
            "likely_comment": "Author metadata, COI, funding, reviewer names and release DOI are incomplete.",
            "severity": "blocking",
            "current_evidence": f"Stage 5.15={preflight}; Stage 5.16={dryrun}; single_form_placeholders={form['placeholder_rows']}",
            "response_strategy": "Use Stage 5.17 single human-input form as the only source of truth, then rerun preflight before release.",
            "required_action": "Fill single human-input form, synchronize templates, rerun Stage 5.15/5.16, then execute release.",
            "owner": "corresponding_author",
            "blocks_submission": True,
        },
        {
            "risk_id": "R08",
            "reviewer_role": "Devil's advocate",
            "likely_comment": "The manuscript may overstate prediction-guided discovery if the prediction model is not directly used in the association model.",
            "severity": "moderate",
            "current_evidence": f"claim_boundary_language={metrics['has_claim_boundary_language']}",
            "response_strategy": "Frame prediction as trait triage and orthogonal attribution support, not as causal discovery.",
            "required_action": "Audit Abstract, Discussion and captions for any wording implying validation or causal inference.",
            "owner": "machine",
            "blocks_submission": False,
        },
    ]
    return pd.DataFrame(rows)


def revision_roadmap(risks: pd.DataFrame) -> pd.DataFrame:
    order = {
        "blocking": 0,
        "major": 1,
        "moderate": 2,
        "minor": 3,
    }
    rows = []
    for _, row in risks.sort_values("severity", key=lambda s: s.map(order)).iterrows():
        rows.append(
            {
                "priority": len(rows) + 1,
                "risk_id": row["risk_id"],
                "severity": row["severity"],
                "action": row["required_action"],
                "owner": row["owner"],
                "done_when": "Evidence file or filled form exists and the relevant Stage 5 gate passes.",
            }
        )
    return pd.DataFrame(rows)


def gate_matrix(metrics: dict[str, object], preflight: str, dryrun: str, form: dict[str, int]) -> pd.DataFrame:
    rows = [
        {
            "gate": "scientific_core_package",
            "status": "pass" if metrics["has_gemma_lambda"] and metrics["has_claim_boundary_language"] else "revise",
            "evidence": "Target manuscript includes GEMMA calibration and conservative candidate-interval language.",
            "next_action": "Keep claim boundary during all edits.",
        },
        {
            "gate": "manuscript_depth",
            "status": "revise" if int(metrics["word_count_proxy"]) < 3500 else "pass",
            "evidence": f"proxy_word_count={metrics['word_count_proxy']}",
            "next_action": "Expand novelty, methods reproducibility and discussion before final upload.",
        },
        {
            "gate": "human_metadata",
            "status": "fail" if preflight != "READY_FOR_RELEASE_EXECUTION" else "pass",
            "evidence": f"Stage 5.15 verdict={preflight}",
            "next_action": "Fill Stage 5.17 single human-input form and rerun preflight.",
        },
        {
            "gate": "metadata_ingestion",
            "status": "fail" if dryrun != "READY_TO_INSERT_METADATA" else "pass",
            "evidence": f"Stage 5.16 verdict={dryrun}",
            "next_action": "Rerun dry-run after synchronized metadata templates contain no placeholders.",
        },
        {
            "gate": "single_form",
            "status": "fail" if form["placeholder_rows"] else "pass",
            "evidence": f"ready_sections={form['ready_sections']}/{form['sections']}; placeholder_rows={form['placeholder_rows']}",
            "next_action": "Use single form as source of truth for human metadata.",
        },
    ]
    return pd.DataFrame(rows)


def report(metrics: dict[str, object], risks: pd.DataFrame, gates: pd.DataFrame) -> str:
    blocking = int(risks["blocks_submission"].sum())
    major = int(risks["severity"].eq("major").sum())
    verdict = "NOT_FINAL_SUBMISSION_READY_REVIEWER_RISKS_REMAIN"
    return f"""# ZEAMAP v0.1 Stage 5.18 Report: Reviewer Risk Register

日期：2026-06-06

## Verdict

`{verdict}`

## What Was Added

This stage converts academic-research-suite style pre-submission review into concrete project files. It does not change the scientific claims and does not execute release/tag/DOI.

## Current Assessment

- Reviewer-risk rows: {risks.shape[0]}
- Blocking submission risks: {blocking}
- Major revision risks: {major}
- Gate rows: {gates.shape[0]}
- Manuscript proxy word count: {metrics['word_count_proxy']}

The manuscript is no longer just a result dump: it has a manuscript assembly, figures, tables, citation audit and preflight gates. It is still not final submission-ready because human metadata are missing and because several reviewer-facing support files should be strengthened before upload.

## Main Next Machine-Executable Tasks

1. Build a result-to-script reproducibility crosswalk.
2. Build a compact GWAS diagnostic appendix table.
3. Expand targeted fatty-acid/lipid literature support for chr6 and chr9.
4. Audit manuscript wording for prediction-guided overclaiming.

## Main Human-Required Tasks

1. Fill the Stage 5.17 single human-input form.
2. Manually inspect Figure 1-3 PDF/SVG/PNG at journal size.
3. Confirm author order, funding, COI, acknowledgements and reviewer suggestions.
4. Execute release/tag/archive DOI only after Stage 5.15 and Stage 5.16 pass.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-18-reviewer-risk-register.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-revision-roadmap.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-submission-gate-matrix.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-ars-reviewer-synthesis.md`
"""


def reviewer_synthesis(risks: pd.DataFrame, gates: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.18 ARS Reviewer Synthesis

日期：2026-06-06

## Editorial Synthesis

Decision: `major_revision_before_submission`

The strongest parts of the manuscript are the conservative accession-level ZEAMAP v0.1 construction, the oil-trait prediction signal, the explicit rejection of inflated covariate-only GWAS as the main result and the calibrated GEMMA LMM candidate-locus framework. The strongest biological story is the chr6 linoleic acid1-region together with the chr9 C16:0 fatty acyl-ACP thioesterase interval.

The manuscript should not be submitted yet. The blocking reasons are practical and editorial rather than a failure of the core analysis: author-side metadata are absent, final figure inspection is not certified and release/tag/DOI are not executed. In addition, a reviewer-facing reproducibility crosswalk and stronger GWAS diagnostic appendix would materially reduce review risk.

## Highest-Risk Reviewer Comments

{markdown_table(risks.loc[:, ["risk_id", "reviewer_role", "severity", "likely_comment", "required_action"]])}

## Gate Matrix

{markdown_table(gates)}

## Claim Boundary To Preserve

Use "candidate locus", "candidate interval", "prioritized region" and "follow-up target". Avoid "causal variant", "validated gene", "fine-mapped gene" and "confirmed mechanism" unless independent validation is added.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.18 final metadata insertion and release | 下一步 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
        "| 阶段 5.18 reviewer-risk register | 已完成初版 | 已输出模拟审稿风险表、修订路线图、submission gate matrix 和 ARS reviewer synthesis |\n| 阶段 5.19 result-to-script reproducibility crosswalk | 下一步 | 把每个主结果、表、图映射到脚本、输入、输出和参数，降低可复现性审稿风险 |\n| 阶段 5.20 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
    )
    if "Reviewer-risk register: 1 file" not in text:
        text = text.replace(
            "Stage 5.17 ARS self-review: 1 file",
            "Stage 5.17 ARS self-review: 1 file\nReviewer-risk register: 1 file\nRevision roadmap: 1 file\nSubmission gate matrix: 1 file\nARS reviewer synthesis: 1 file",
        )
    if "## 阶段 5.18：reviewer-risk register" not in text:
        text += """

## 阶段 5.18：reviewer-risk register

状态：已完成初版。

为什么做这一步：

论文投稿前最容易被审稿人攻击的点已经不是“有没有结果”，而是：稿件是否足够完整、方法能否复现、GWAS 诊断是否透明、chr6/chr9 文献支撑是否足够、prediction-guided 这个说法有没有过度、以及作者/图件/release 信息是否齐全。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-18-reviewer-risk-register.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-revision-roadmap.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-submission-gate-matrix.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-ars-reviewer-synthesis.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-report.md`

当前判断：

核心分析主线可以继续向论文推进，但还不是最终投稿包。机器侧下一步应优先做 result-to-script reproducibility crosswalk 和 GWAS diagnostic appendix；人工侧仍需填写 Stage 5.17 单表并完成图件人工检查。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.16 metadata ingestion dry-run 和 Stage 5.17 single human-input package 初版。",
        "Stage 5.16 metadata ingestion dry-run、Stage 5.17 single human-input package 和 Stage 5.18 reviewer-risk register 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    metrics = manuscript_metrics()
    preflight = extract_verdict(PREFLIGHT)
    dryrun = extract_verdict(DRYRUN)
    form = single_form_summary()

    risks = reviewer_risks(metrics, preflight, dryrun, form)
    roadmap = revision_roadmap(risks)
    gates = gate_matrix(metrics, preflight, dryrun, form)

    risks.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-18-reviewer-risk-register.tsv", sep="\t", index=False)
    roadmap.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-18-revision-roadmap.tsv", sep="\t", index=False)
    gates.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-18-submission-gate-matrix.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-18-ars-reviewer-synthesis.md", reviewer_synthesis(risks, gates))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-18-report.md", report(metrics, risks, gates))
    update_docs()
    print("Stage 5.18 reviewer-risk register generated.")


if __name__ == "__main__":
    main()
