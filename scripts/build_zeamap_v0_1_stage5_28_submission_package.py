#!/usr/bin/env python3
"""Build Stage 5.28 final submission package index and journal route materials."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
LATEST_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-gene-name-hardened-manuscript.md"
LATEST_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-final-submission-gate.tsv"

PACKAGE_INDEX = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-submission-package-index.md"
COVER_LETTER = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-cover-letter-the-plant-genome.md"
JOURNAL_TABLE = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-journal-route-table.tsv"
AUTHOR_CHECKLIST = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-author-final-input-checklist.tsv"
RELEASE_CHECKLIST = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-release-final-checklist.tsv"
FINAL_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-28-ars-submission-package-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"


def git_head() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.SubprocessError, FileNotFoundError):
        return "UNKNOWN"


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def journal_routes() -> pd.DataFrame:
    rows = [
        {
            "rank": 1,
            "journal": "The Plant Genome",
            "route": "recommended_first_target",
            "fit": "Crop genomics, GWAS, genomic prediction, public-resource reanalysis and candidate-locus resource fit the paper's current strengths.",
            "current_probability_estimate": "45-60%",
            "what_would_improve_odds": "Final author metadata, figure polish, repository release DOI/PID and concise cover letter.",
            "main_risk": "Editor may view the work as secondary analysis unless benchmark and calibrated-GWAS contribution are clear.",
            "official_source": "https://acsess.onlinelibrary.wiley.com/journal/19403372",
        },
        {
            "rank": 2,
            "journal": "G3: Genes|Genomes|Genetics",
            "route": "strong_backup_or_pragmatic_first_target",
            "fit": "Good fit for transparent genetics/genomics, GWAS and genomic prediction work.",
            "current_probability_estimate": "40-60%",
            "what_would_improve_odds": "Emphasize reproducible genetics rather than novelty; keep claim boundaries explicit.",
            "main_risk": "Pure public-data prediction/GWAS can be judged incremental without a sharply framed reusable resource contribution.",
            "official_source": "https://academic.oup.com/g3journal/pages/About",
        },
        {
            "rank": 3,
            "journal": "BMC Plant Biology",
            "route": "highest_probability_backup",
            "fit": "Broad plant biology/genomics scope and scientifically valid analysis route are compatible with the current evidence level.",
            "current_probability_estimate": "55-75%",
            "what_would_improve_odds": "Clear methods, clean data/code availability, and no causal overclaiming.",
            "main_risk": "Needs a stronger biological story to avoid reading as a technical report.",
            "official_source": "https://bmcplantbiol.biomedcentral.com/submission-guidelines/aims-and-scope",
        },
        {
            "rank": 4,
            "journal": "The Crop Journal",
            "route": "crop_science_backup",
            "fit": "Maize seed-quality traits, genomic prediction and GWAS can fit a crop-improvement audience.",
            "current_probability_estimate": "25-45%",
            "what_would_improve_odds": "More breeding-oriented framing and clearer practical value for oil-trait improvement.",
            "main_risk": "May expect stronger agronomic or breeding validation than the current public-data reanalysis provides.",
            "official_source": "https://www.sciencedirect.com/journal/the-crop-journal",
        },
        {
            "rank": 5,
            "journal": "Frontiers in Plant Science",
            "route": "broad_open_access_backup",
            "fit": "Plant genomics and crop quantitative genetics are plausible; the paper's resource/reanalysis nature is acceptable if methods are rigorous.",
            "current_probability_estimate": "50-70%",
            "what_would_improve_odds": "Target a genetics/genomics specialty section and make data reuse/reproducibility central.",
            "main_risk": "APC and article-type fit should be checked before submission.",
            "official_source": "https://www.frontiersin.org/journals/plant-science",
        },
        {
            "rank": 6,
            "journal": "Journal of Experimental Botany",
            "route": "ambitious_after_validation",
            "fit": "Possible if framed around fatty-acid biology, but current evidence remains association/candidate-level.",
            "current_probability_estimate": "15-25%",
            "what_would_improve_odds": "Independent validation, expression support or functional evidence.",
            "main_risk": "Likely too descriptive for current evidence level.",
            "official_source": "https://academic.oup.com/jxb/pages/About",
        },
        {
            "rank": 7,
            "journal": "Nature Plants",
            "route": "not_recommended_without_new_validation",
            "fit": "Topic is relevant, but current manuscript lacks the broad conceptual or mechanistic advance expected.",
            "current_probability_estimate": "<3-6%",
            "what_would_improve_odds": "Independent validation, functional assays, broader multi-population replication or a stronger conceptual framework.",
            "main_risk": "Desk rejection as careful but incremental public-data reanalysis.",
            "official_source": "https://www.nature.com/nplants/aims",
        },
    ]
    return pd.DataFrame(rows)


def author_checklist() -> pd.DataFrame:
    rows = [
        {"item": "author_order", "status": "author_required", "needed_input": "Final author order and exact spelling."},
        {"item": "affiliations", "status": "author_required", "needed_input": "Institution names, departments, city/country and numbered affiliation mapping."},
        {"item": "corresponding_author", "status": "author_required", "needed_input": "Name, email, postal address if journal requires it."},
        {"item": "orcid_ids", "status": "recommended", "needed_input": "ORCID for each author if available."},
        {"item": "credit_roles", "status": "author_required", "needed_input": "CRediT roles for each author: conceptualization, data curation, software, formal analysis, visualization, writing, supervision, funding acquisition."},
        {"item": "funding_statement", "status": "author_required", "needed_input": "Grant agency, grant number, funder role statement or no-specific-funding statement."},
        {"item": "acknowledgements", "status": "author_required", "needed_input": "People/groups to thank and exact approved wording."},
        {"item": "competing_interests", "status": "author_required", "needed_input": "Final author-approved COI statement."},
        {"item": "figure_approval", "status": "author_required", "needed_input": "Final visual approval of Figures 1-3 at target-journal page size."},
        {"item": "target_journal", "status": "author_required", "needed_input": "Confirm first target: recommended The Plant Genome; backups G3 and BMC Plant Biology."},
    ]
    return pd.DataFrame(rows)


def release_checklist(head: str) -> pd.DataFrame:
    rows = [
        {"step": "pre_release_status", "command_or_action": "git status --short", "when": "after author metadata and final figure approval"},
        {"step": "final_commit", "command_or_action": "commit author metadata, final manuscript and release-note updates", "when": "before tagging"},
        {"step": "tag", "command_or_action": "git tag -a zeamap-oil-v0.1-submission -m \"ZEAMAP maize oil-trait manuscript submission package\"", "when": "after final clean status"},
        {"step": "push_tag", "command_or_action": "git push origin zeamap-oil-v0.1-submission", "when": "after local tag creation"},
        {"step": "github_release", "command_or_action": "Create GitHub release from tag with manuscript title and data-source notes.", "when": "after tag push"},
        {"step": "archive_pid", "command_or_action": "Archive GitHub release in Zenodo/Figshare if required by target journal.", "when": "after GitHub release"},
        {"step": "record_pid", "command_or_action": "Insert archive DOI/PID into Data Availability and repository release docs.", "when": "after archive PID is issued"},
    ]
    df = pd.DataFrame(rows)
    df["current_pre_stage5_28_head"] = head
    return df


def final_gate() -> pd.DataFrame:
    previous = pd.read_csv(LATEST_GATE, sep="\t")
    rows = previous.to_dict("records")
    rows.insert(
        0,
        {
            "gate": "submission_package_compiled",
            "status": "pass",
            "evidence": "Stage 5.28 compiled manuscript index, The Plant Genome cover letter, journal route table, author checklist and release checklist.",
        },
    )
    return pd.DataFrame(rows)


def write_cover_letter() -> None:
    text = """# Cover Letter Draft: The Plant Genome Route

日期：2026-06-06

Dear Editor,

We are pleased to submit the manuscript entitled "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP" for consideration as a research article in *The Plant Genome*.

This manuscript presents a reproducible accession-level reanalysis of public ZEAMAP processed data focused on maize kernel oil and fatty-acid traits. We constructed a conservative v0.1 benchmark containing 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified oil-related traits as the most robustly predictable trait family under a genotype+population ridge model.

We then used prediction as a triage step for focused oil-trait association mapping. A diagnostic covariate-only GWAS showed strong genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC near one across 10 high-priority oil traits. We annotated candidate intervals using B73 RefGen_v4 gene models, MaizeGDB B73v4-to-B73v5 cross-references, Ensembl/Gramene xrefs, prediction-attribution overlap and targeted fatty-acid literature. The strongest intervals include a recurrent chromosome 6 lipid acyltransferase/DGAT-like candidate interval and a chromosome 9 C16:0 interval with a nearby acyl-ACP hydrolase/palmitoyl-ACP thioesterase candidate.

The paper is intentionally conservative. We do not claim causal variants, causal alleles or experimentally validated genes. Instead, we provide a transparent benchmark, calibrated mixed-model GWAS results, current-ID annotation evidence and prioritized candidate intervals for follow-up maize oil-trait genetics.

We believe the manuscript will interest readers of *The Plant Genome* because it combines public crop-genomics resource reuse, genotype-to-phenotype prediction, mixed-model GWAS calibration and candidate-locus prioritization for seed-quality traits. The repository includes scripts, manuscript-facing summary tables, reproducibility documentation and figure outputs. Large raw inputs and large intermediate matrices are not committed to GitHub, but their public sources and regeneration paths are documented.

The corresponding author should confirm before submission that the manuscript is original, is not under consideration elsewhere, has been approved by all authors and has complete funding, acknowledgements and competing-interest statements.

Sincerely,

[Corresponding author name]
"""
    write_text(COVER_LETTER, text)


def write_package_index(journals: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# ZEAMAP v0.1 Stage 5.28 Submission Package Index

日期：2026-06-06

## Recommended route

First target: **The Plant Genome**.

Backups: **G3: Genes|Genomes|Genetics** and **BMC Plant Biology**.

Reason: the current manuscript is strongest as a crop genomics/resource reanalysis paper with calibrated mixed-model GWAS and reproducible candidate-locus prioritization. It is not yet a Nature Plants/JXB-level mechanistic paper because it lacks independent validation, fine-mapping and functional assays.

## Current submission files

- Latest manuscript: `{LATEST_MANUSCRIPT.relative_to(ROOT)}`
- Cover letter draft: `{COVER_LETTER.relative_to(ROOT)}`
- Journal route table: `{JOURNAL_TABLE.relative_to(ROOT)}`
- Author final-input checklist: `{AUTHOR_CHECKLIST.relative_to(ROOT)}`
- Release checklist: `{RELEASE_CHECKLIST.relative_to(ROOT)}`
- Final gate: `{FINAL_GATE.relative_to(ROOT)}`
- ARS submission-package review: `{ARS_REVIEW.relative_to(ROOT)}`

## Final gate snapshot

{markdown_table(gate)}

## Journal route snapshot

{markdown_table(journals[["rank", "journal", "route", "current_probability_estimate", "main_risk"]])}

## Important caveat

The probability estimates are pragmatic editorial-risk estimates based on fit and evidence level, not official journal acceptance rates. They should guide submission strategy, not be cited in the manuscript.
"""
    write_text(PACKAGE_INDEX, text)


def write_report(journals: pd.DataFrame, gate: pd.DataFrame) -> None:
    pass_count = int((gate["status"] == "pass").sum())
    human_count = int((gate["status"] == "human_required").sum())
    fail_count = int((gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.28 Submission Package Report

日期：2026-06-06

## Verdict

`SUBMISSION_PACKAGE_COMPILED_AUTHOR_ACTION_REMAINING`

## What changed

- Created a single submission-package index.
- Updated the cover letter for the The Plant Genome route and Stage 5.27 gene-name evidence.
- Added a journal route table with multiple targets and pragmatic acceptance-probability estimates.
- Added final author-input and release checklists.
- Added an updated final gate.

## Gate summary

- pass/human_required/fail: {pass_count}/{human_count}/{fail_count}
- Machine-side compilation now passes.
- Remaining gates are author-only: figure approval, author metadata, funding/COI/acknowledgements and repository release PID.

## Recommended target order

1. The Plant Genome
2. G3
3. BMC Plant Biology
4. The Crop Journal or Frontiers in Plant Science as broader backups
5. JXB only after additional validation
6. Nature Plants only after a substantially stronger mechanistic or validation package
"""
    write_text(REPORT, text)


def write_ars_review(journals: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.28 ARS Submission-Package Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite finalization logic: manuscript readiness, journal fit, author-only blockers and reproducibility release steps are checked separately. This is not a claim that the paper is submitted; it is a structured handoff package for final author action.

## Editorial-style verdict

`READY_FOR_AUTHOR_COMPLETION_BEFORE_SUBMISSION`

## Reviewer synthesis

- Editor-in-chief view: The Plant Genome is the strongest first target because the work is crop-genomics focused and methodologically careful.
- Methods reviewer: the package now contains a defensible statistical story: prediction triage, inflated covariate-only GWAS, calibrated GEMMA LMM and bounded candidate-locus interpretation.
- Domain reviewer: Stage 5.27 materially reduced chr6/chr9 annotation risk, especially by separating the chr9 lead-host gene from the nearby fatty-acid thioesterase candidate.
- Reproducibility reviewer: release steps are now explicit, but a final PID cannot be created until the author-approved final commit is tagged.
- Devil's advocate: The remaining blockers are real submission blockers, not polish: no author metadata, no funding/COI approval, no final figure approval and no repository release PID.

## Current final gate

{markdown_table(gate)}

## Journal strategy

{markdown_table(journals[["rank", "journal", "current_probability_estimate", "main_risk"]])}
"""
    write_text(ARS_REVIEW, text)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA 和 Stage 5.27 external gene-name confirmation。",
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation 和 Stage 5.28 final submission package。"
    )
    text = text.replace(
        "Current status: Stage 5.27 has confirmed the chr6/chr9 MaizeGDB B73v4-to-B73v5 gene mappings and Ensembl/Gramene-side functional xrefs. Remaining blockers are author-only: metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID.",
        "Current status: Stage 5.28 has compiled the final submission package for a The Plant Genome first-target route. Remaining blockers are author-only: metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID."
    )
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    addition = """

### Stage 5.28 - Final submission package

通俗解读：这一阶段把“快能投稿了，但东西散在很多文件里”的问题收束成一个投稿包。现在有最新稿件、The Plant Genome 路线 cover letter、期刊备选表、作者最终需要补的信息清单、release/tag/DOI 清单和 ARS 投稿包审查。这样下一步不需要重新理解所有阶段，只要按清单补作者信息、确认图、做 release。

阶段结论：机器侧投稿包已经编译完成；推荐第一目标是 The Plant Genome，备选是 G3 和 BMC Plant Biology。剩余硬门槛仍是作者信息、Funding/Acknowledgements/COI、Figure 1-3 最终人工确认和 GitHub release DOI/PID。
"""
    if "### Stage 5.28 - Final submission package" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def main() -> None:
    head = git_head()
    journals = journal_routes()
    authors = author_checklist()
    releases = release_checklist(head)
    gate = final_gate()
    write_cover_letter()
    journals.to_csv(JOURNAL_TABLE, sep="\t", index=False)
    authors.to_csv(AUTHOR_CHECKLIST, sep="\t", index=False)
    releases.to_csv(RELEASE_CHECKLIST, sep="\t", index=False)
    gate.to_csv(FINAL_GATE, sep="\t", index=False)
    write_package_index(journals, gate)
    write_report(journals, gate)
    write_ars_review(journals, gate)
    update_readme()
    update_progress()
    print(f"Wrote {PACKAGE_INDEX}")
    print(f"Wrote {COVER_LETTER}")
    print(f"Wrote {JOURNAL_TABLE}")
    print(f"Wrote {AUTHOR_CHECKLIST}")
    print(f"Wrote {RELEASE_CHECKLIST}")
    print(f"Wrote {FINAL_GATE}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
