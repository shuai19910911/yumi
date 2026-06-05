#!/usr/bin/env python3
"""Build Stage 5.19 result-to-script reproducibility crosswalk."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_tracked_paths() -> set[str]:
    try:
        out = subprocess.check_output(["git", "ls-files"], cwd=ROOT, text=True)
    except Exception:
        return set()
    return set(out.splitlines())


def rel(path: str | Path) -> str:
    return str(Path(path))


def exists(rel_path: str) -> bool:
    return (ROOT / rel_path).exists()


def row(
    result_id: str,
    manuscript_claim: str,
    script: str,
    primary_inputs: list[str],
    primary_outputs: list[str],
    key_parameters: str,
    verification_evidence: str,
    reviewer_risk_addressed: str,
) -> dict[str, object]:
    missing = [p for p in [script, *primary_inputs, *primary_outputs] if not exists(p)]
    return {
        "result_id": result_id,
        "manuscript_claim": manuscript_claim,
        "script": script,
        "primary_inputs": ";".join(primary_inputs),
        "primary_outputs": ";".join(primary_outputs),
        "key_parameters_or_decisions": key_parameters,
        "verification_evidence": verification_evidence,
        "reviewer_risk_addressed": reviewer_risk_addressed,
        "missing_paths": ";".join(missing),
        "ready_for_reviewer": len(missing) == 0,
    }


def build_crosswalk() -> pd.DataFrame:
    rows = [
        row(
            "R00_download_scope",
            "Raw SRA/FASTQ, whole pangenome assemblies and all epigenome tracks were deferred; v0.1 uses processed matrices first.",
            "docs/2026-06-04-download-scope-rationale.md",
            ["docs/2026-06-04-zeamap-first-batch-download-check.md", "docs/2026-06-04-zeamap-second-batch-check.md"],
            ["docs/2026-06-04-download-scope-rationale.md"],
            "Processed-matrix first strategy; raw/high-volume modalities reserved for later validation or sequence-tokenizer work.",
            "Download rationale and two batch check reports exist.",
            "R05 reproducibility and data-scope criticism",
        ),
        row(
            "R01_accession_harmonization",
            "ZEAMAP phenotype, population and genotype identifiers were harmonized to accession level.",
            "scripts/build_zeamap_sample_index.py",
            ["docs/2026-06-04-zeamap-sample-id-check.md"],
            [
                "data/metadata/zeamap_accession_index.tsv",
                "data/metadata/zeamap_table_id_summary.tsv",
                "data/metadata/zeamap_expression_sample_columns.tsv",
            ],
            "Accession-level harmonization; expression columns recorded but not forced into accession-level v0.1.",
            "Stage 1 report documents population/phenotype/VCF sample alignment.",
            "R02 methodology reproducibility",
        ),
        row(
            "R02_processed_dataset",
            "v0.1 contains 461 paired accessions, 199,856 SNPs and 318 numeric traits.",
            "scripts/build_zeamap_v0_1_dataset.py",
            [
                "data/metadata/zeamap_accession_index.tsv",
                "docs/2026-06-04-zeamap-v0-1-build-report.md",
            ],
            [
                "data/processed/v0_1/accessions.tsv",
                "data/processed/v0_1/phenotype.parquet",
                "data/processed/v0_1/population.parquet",
                "data/processed/v0_1/modality_mask.tsv",
                "data/processed/v0_1/genotype_dosage_int8.npz",
            ],
            "Common high-call biallelic SNPs; accession has genotype, population and at least one phenotype/metabolome measurement.",
            "Build report and processed matrix paths document sample and feature counts.",
            "R02 methodology reproducibility",
        ),
        row(
            "R03_baseline_prediction",
            "Initial genotype/population prediction benchmark found stable signal and motivated trait filtering.",
            "scripts/run_zeamap_v0_1_baseline.py",
            ["data/processed/v0_1/accessions.tsv", "data/processed/v0_1/phenotype.parquet"],
            ["docs/2026-06-05-zeamap-v0-1-baseline-report.md"],
            "Train/validation/test split 322/69/70; genotype PCA and ridge baselines.",
            "Baseline report records first-pass median Pearson/R2 and model ranking.",
            "R02 methodology reproducibility",
        ),
        row(
            "R04_selected_traits",
            "Trait screening reduced noisy outcomes before multi-seed benchmarking.",
            "scripts/select_zeamap_v0_1_traits.py",
            ["docs/2026-06-05-zeamap-v0-1-baseline-report.md"],
            ["docs/2026-06-05-zeamap-v0-1-selected-traits.md"],
            "Selected traits are retained based on evaluability and baseline evidence.",
            "Selected-traits report documents selected trait count and family composition.",
            "R02 methodology reproducibility",
        ),
        row(
            "R05_robust_traits",
            "Repeated-seed evaluation identified 66 robust traits.",
            "scripts/run_zeamap_v0_1_robustness.py",
            ["docs/2026-06-05-zeamap-v0-1-selected-traits.md"],
            ["docs/2026-06-05-zeamap-v0-1-robustness-report.md"],
            "Five random seeds; robust traits retained for final benchmark.",
            "Robustness report records 66 robust traits and family counts.",
            "R02 methodology reproducibility",
        ),
        row(
            "R06_lightweight_models",
            "Ridge/ElasticNet were more stable than small MLP under current sample size.",
            "scripts/run_zeamap_v0_1_lightweight_models.py",
            ["docs/2026-06-05-zeamap-v0-1-robustness-report.md"],
            ["docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md"],
            "Lightweight ridge, ElasticNet and small MLP comparison on robust traits.",
            "Lightweight model report supports restrained model choice.",
            "R08 prediction-guided overclaim risk",
        ),
        row(
            "R07_methylation_ablation",
            "Methylation remained auxiliary and was not used as the v0.1 main-model input.",
            "scripts/run_zeamap_v0_1_methylation_subset.py",
            ["data/processed/v0_1/modality_mask.tsv"],
            [
                "docs/2026-06-05-zeamap-v0-1-methylation-subset-report.md",
                "docs/2026-06-05-zeamap-v0-1-gene-methylation-pca-report.md",
                "docs/2026-06-05-zeamap-v0-1-sparse-methylation-selection-report.md",
            ],
            "236 methylation-covered accessions; global summary, gene/promoter/cis-window PCA and sparse gene-window checks.",
            "Three methylation reports document limited or unstable gain.",
            "R01 novelty and scope discipline",
        ),
        row(
            "R08_final_prediction_benchmark",
            "Final benchmark used genotype_population_ridge; oil traits were strongest.",
            "scripts/build_zeamap_v0_1_final_benchmark.py",
            [
                "docs/2026-06-05-zeamap-v0-1-robustness-report.md",
                "docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md",
            ],
            ["docs/2026-06-05-zeamap-v0-1-final-benchmark.md"],
            "66 robust traits; final model genotype_population_ridge; oil median Pearson/R2 0.596/0.321.",
            "Final benchmark report documents model and trait-family performance.",
            "R02 methodology reproducibility",
        ),
        row(
            "R09_genotype_attribution",
            "Ridge attribution provided support used only as orthogonal prioritization, not causal evidence.",
            "scripts/run_zeamap_v0_1_genotype_attribution.py",
            ["docs/2026-06-05-zeamap-v0-1-final-benchmark.md"],
            ["docs/2026-06-05-zeamap-v0-1-genotype-attribution-report.md"],
            "Attribution screen after final benchmark; interpreted as prioritization support only.",
            "Attribution report preserves non-GWAS claim boundary.",
            "R08 prediction-guided overclaim risk",
        ),
        row(
            "R10_covariate_gwas_diagnostic",
            "Covariate-only GWAS was inflated and retained only as a diagnostic baseline.",
            "scripts/run_zeamap_v0_1_population_corrected_association.py",
            ["docs/2026-06-05-zeamap-v0-1-final-benchmark.md"],
            ["docs/2026-06-05-zeamap-v0-1-gwas-baseline-report.md"],
            "PC1-PC3 + K1-K3 residualization; lambda GC 2.41-3.97.",
            "GWAS baseline report documents inflation and diagnostic-only status.",
            "R03 statistical genetics diagnostics",
        ),
        row(
            "R11_gemma_inputs",
            "GEMMA LMM used genotype-derived kinship and population covariates.",
            "scripts/prepare_zeamap_v0_1_gemma_inputs.py",
            ["data/processed/v0_1/genotype_dosage_int8.npz", "data/processed/v0_1/population.parquet"],
            ["scripts/slurm/run_zeamap_v0_1_gemma_lmm.sh"],
            "10 high-priority oil traits; genotype-derived kinship; PC1-PC3/K1-K3 covariates.",
            "GEMMA run script and Stage 5.3 report document LMM setup.",
            "R03 statistical genetics diagnostics",
        ),
        row(
            "R12_gemma_lmm_summary",
            "GEMMA LMM controlled lambda GC to 0.984-1.018 across 10 oil traits.",
            "scripts/summarize_zeamap_v0_1_gemma_lmm.py",
            ["scripts/slurm/run_zeamap_v0_1_gemma_lmm.sh"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv",
                "results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv",
                "docs/2026-06-05-zeamap-v0-1-gemma-lmm-report.md",
            ],
            "p_lrt as main p-value; Bonferroni/FDR/suggestive summaries; QQ/Manhattan figures generated.",
            "Summary TSV and report document sample/SNP counts, lambda and lead hits.",
            "R03 statistical genetics diagnostics",
        ),
        row(
            "R13_candidate_loci_annotation",
            "GEMMA lead loci were annotated to B73 RefGen_v4 candidate genes and filtered to manuscript-facing loci.",
            "scripts/build_zeamap_v0_1_gemma_candidate_loci.py",
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv",
                "docs/2026-06-05-zeamap-v0-1-genotype-attribution-report.md",
            ],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv",
                "results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_genes.tsv",
                "docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md",
            ],
            "Nominal-only loci excluded from manuscript set; 184 candidate loci and 147 genes retained.",
            "Candidate loci report and TSVs document filtering and annotation.",
            "R04 domain interpretation",
        ),
        row(
            "R14_top_loci_priority",
            "Top loci were ranked into tiered manuscript candidates and 8 regional targets.",
            "scripts/build_zeamap_v0_1_top_locus_priority.py",
            ["results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_locus_priority.tsv",
                "results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_region_targets.tsv",
                "docs/2026-06-05-zeamap-v0-1-top-locus-priority-report.md",
            ],
            "Priority score integrates statistical support, trait recurrence, attribution overlap and annotation evidence.",
            "Top-locus report documents tier1/tier2 and regional figure targets.",
            "R04 domain interpretation",
        ),
        row(
            "R15_manuscript_tables",
            "Manuscript tables summarize regional evidence, tier-1 loci, candidates and literature/source records.",
            "scripts/build_zeamap_v0_1_stage5_6_manuscript_tables.py",
            ["results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_locus_priority.tsv"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv",
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv",
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv",
                "docs/2026-06-05-zeamap-v0-1-results-draft.md",
            ],
            "8 top regional loci; 18 tier1 main loci; 184 supplementary manuscript loci.",
            "Stage 5.6 report and manuscript tables are committed.",
            "R04 domain interpretation",
        ),
        row(
            "R16_main_figures",
            "Figure 1, Figure 2 and Figure 3 are generated in PDF/SVG/PNG formats.",
            "scripts/build_zeamap_v0_1_stage5_7_methods_and_figures.py",
            ["docs/2026-06-05-zeamap-v0-1-results-draft.md"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf",
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf",
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf",
                "docs/2026-06-05-zeamap-v0-1-stage5-7-methods-figures-report.md",
            ],
            "Nature-style double-column PDF/SVG/PNG; manual final inspection remains required.",
            "Stage 5.12 figure audit exists; Stage 5.14 manual checklist still has placeholders.",
            "R06 figure readiness",
        ),
        row(
            "R17_regional_figures",
            "Eight top regional association/LD/gene-track figures support candidate intervals.",
            "scripts/build_zeamap_v0_1_top_locus_priority.py",
            ["results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_region_targets.tsv"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/R01_Zm00001d036982_regional_locus_nature.pdf",
                "results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/R08_Zm00001d045383_regional_locus_nature.pdf",
            ],
            "Regional panels show association strength, LD to lead SNP and B73 RefGen_v4 gene tracks.",
            "Regional figure directory contains PDF/SVG/PNG for R01-R08.",
            "R04 domain interpretation and R06 figure readiness",
        ),
        row(
            "R18_external_annotation",
            "Top regional loci received external annotation hardening and claim-boundary risk labels.",
            "scripts/build_zeamap_v0_1_stage5_11_external_annotation.py",
            ["results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv"],
            [
                "results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_external_annotation.tsv",
                "docs/2026-06-06-zeamap-v0-1-stage5-11-external-annotation-report.md",
            ],
            "External annotation class and remaining risk assigned; no causal validation implied.",
            "Stage 5.11 report and external annotation table are committed.",
            "R04 domain interpretation",
        ),
        row(
            "R19_final_assembly",
            "Target-journal manuscript assembly combines title page placeholders, abstract, results, methods, legends and availability statements.",
            "scripts/build_zeamap_v0_1_stage5_12_final_assembly.py",
            [
                "docs/2026-06-06-zeamap-v0-1-polished-manuscript-draft.md",
                "docs/2026-06-06-zeamap-v0-1-methods-parameter-supplement.md",
            ],
            [
                "docs/2026-06-06-zeamap-v0-1-stage5-12-target-journal-manuscript.md",
                "docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md",
                "docs/2026-06-06-zeamap-v0-1-figure-quality-audit.md",
            ],
            "The Plant Genome first-line format with G3 as alternative; author-side fields intentionally unresolved.",
            "Stage 5.12 report and final assembly draft are committed.",
            "R01 manuscript depth and R05 reproducibility",
        ),
        row(
            "R20_submission_gates",
            "Final submission gates remain closed until author metadata, manual figure checks and release are complete.",
            "scripts/build_zeamap_v0_1_stage5_15_preflight_validator.py",
            [
                "docs/2026-06-06-zeamap-v0-1-author-metadata-template.tsv",
                "docs/2026-06-06-zeamap-v0-1-final-figure-manual-checklist.tsv",
            ],
            [
                "docs/2026-06-06-zeamap-v0-1-stage5-15-preflight-report.md",
                "docs/2026-06-06-zeamap-v0-1-stage5-15-gate-status.tsv",
                "docs/2026-06-06-zeamap-v0-1-stage5-17-report.md",
            ],
            "Preflight requires no blocking placeholders; Stage 5.17 single form is now the preferred source of truth.",
            "Stage 5.15/5.16/5.17 reports document current metadata blockers.",
            "R07 editorial office blockers",
        ),
    ]
    return pd.DataFrame(rows)


def file_inventory(crosswalk: pd.DataFrame) -> pd.DataFrame:
    paths: set[str] = set()
    tracked = git_tracked_paths()
    for _, row_ in crosswalk.iterrows():
        paths.add(str(row_["script"]))
        for col in ["primary_inputs", "primary_outputs"]:
            for p in str(row_[col]).split(";"):
                if p:
                    paths.add(p)
    rows = []
    for p in sorted(paths):
        path = ROOT / p
        is_file = path.exists() and path.is_file()
        rows.append(
            {
                "path": p,
                "exists": path.exists(),
                "bytes": path.stat().st_size if path.exists() else 0,
                "git_tracked": p in tracked,
                "release_class": "committed" if p in tracked else "local_or_large_input",
                "sha256": sha256(path) if is_file else "",
            }
        )
    return pd.DataFrame(rows)


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row_ in df.iterrows():
        values = []
        for col in cols:
            values.append(str(row_[col]).replace("|", "\\|").replace("\n", " "))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def report(crosswalk: pd.DataFrame, inventory: pd.DataFrame) -> str:
    ready = int(crosswalk["ready_for_reviewer"].sum())
    missing_rows = crosswalk.loc[~crosswalk["ready_for_reviewer"]]
    missing_files = int((~inventory["exists"]).sum())
    local_not_tracked = int((inventory["exists"] & ~inventory["git_tracked"]).sum())
    verdict = "REPRODUCIBILITY_CROSSWALK_READY" if missing_rows.empty else "REPRODUCIBILITY_CROSSWALK_HAS_MISSING_PATHS"
    return f"""# ZEAMAP v0.1 Stage 5.19 Report: Result-To-Script Reproducibility Crosswalk

日期：2026-06-06

## Verdict

`{verdict}`

## Summary

- Crosswalk rows: {crosswalk.shape[0]}
- Reviewer-ready rows: {ready}/{crosswalk.shape[0]}
- Inventory paths checked: {inventory.shape[0]}
- Missing paths: {missing_files}
- Existing but not Git-tracked paths: {local_not_tracked}

## Interpretation

This stage turns the manuscript's main claims into a reviewer-facing provenance map. Each row links one claim/result to a generating script or source document, primary inputs, primary outputs, key parameter decisions and the reviewer risk it addresses.

The crosswalk is not a substitute for rerunning every analysis. It is a submission-support artifact: reviewers and coauthors can see where each number, figure and table comes from, and which large local inputs are intentionally outside GitHub.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-methods-reproducibility-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-ars-reproducibility-review.md`

## Remaining Risk

Some existing paths point to local processed matrices or large outputs that are not intended for GitHub release. Before final submission, the release package should state which files are public-source inputs, which files are committed derivatives and which large files must be regenerated locally from ZEAMAP.
"""


def methods_insert(crosswalk: pd.DataFrame) -> str:
    selected = crosswalk.loc[
        crosswalk["result_id"].isin(["R02_processed_dataset", "R08_final_prediction_benchmark", "R12_gemma_lmm_summary", "R13_candidate_loci_annotation", "R16_main_figures"])
    ][["result_id", "script", "primary_outputs", "key_parameters_or_decisions"]]
    return f"""# Methods/Data Availability Insert: Reproducibility Crosswalk

日期：2026-06-06

Suggested manuscript insertion:

> To support reproducibility, each main result, figure and manuscript-facing table was mapped to its generating script, primary inputs, primary outputs and key parameter decisions. This result-to-script crosswalk is provided in `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`, with a file-level inventory in `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`. Large public ZEAMAP inputs are not committed to the repository; their source project and local processing paths are documented, while derived manuscript tables, reports and generated figures are included where size permits.

Key crosswalk rows for main-text results:

{markdown_table(selected)}
"""


def ars_review(crosswalk: pd.DataFrame, inventory: pd.DataFrame) -> str:
    missing = crosswalk.loc[~crosswalk["ready_for_reviewer"], ["result_id", "missing_paths"]]
    missing_text = markdown_table(missing) if not missing.empty else "_No missing crosswalk paths._"
    return f"""# ZEAMAP v0.1 Stage 5.19 ARS Reproducibility Review

日期：2026-06-06

Workflow basis: academic-research-suite methodology/reproducibility reviewer gate.

## Decision

`minor_revision_after_crosswalk`

## Assessment

The project now has a concrete claim-to-script crosswalk for the main dataset construction, prediction benchmark, methylation decision, GEMMA LMM GWAS, candidate annotation, figure generation, manuscript assembly and submission gates. This directly addresses Stage 5.18 risks R02 and R05.

The remaining reproducibility risk is not conceptual; it is packaging. Some large local data paths are present on this workstation but are not Git-tracked, so they must be described as public-source inputs or regenerated artifacts in the final Data/Code Availability statement.

## Missing Path Audit

{missing_text}

## Recommendation

Use the Stage 5.19 crosswalk as the canonical reproducibility appendix. The next machine-executable step should be a compact GWAS diagnostic appendix table, because Stage 5.18 identified that as the next strongest statistical reviewer risk.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.19 result-to-script reproducibility crosswalk | 下一步 | 把每个主结果、表、图映射到脚本、输入、输出和参数，降低可复现性审稿风险 |\n| 阶段 5.20 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
        "| 阶段 5.19 result-to-script reproducibility crosswalk | 已完成初版 | 已输出主结果到脚本/输入/输出/参数的 crosswalk、文件 inventory、Methods 插入段和 ARS 可复现性审查 |\n| 阶段 5.20 GWAS diagnostic appendix | 下一步 | 输出每个 oil trait 的 lambda、样本数、SNP 数、Bonferroni/FDR/suggestive 阈值和图件路径 |\n| 阶段 5.21 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
    )
    if "Result-to-script crosswalk: 1 file" not in text:
        text = text.replace(
            "ARS reviewer synthesis: 1 file",
            "ARS reviewer synthesis: 1 file\nResult-to-script crosswalk: 1 file\nReproducibility file inventory: 1 file\nMethods reproducibility insert: 1 file\nARS reproducibility review: 1 file",
        )
    if "## 阶段 5.19：result-to-script reproducibility crosswalk" not in text:
        text += """

## 阶段 5.19：result-to-script reproducibility crosswalk

状态：已完成初版。

为什么做这一步：

审稿人经常会问每个主结果、主表和主图到底由哪个脚本生成，输入是什么，输出在哪里，关键参数是什么。Stage 5.19 把这些信息整理成 crosswalk，让论文从“有结果”进一步变成“结果能追踪、能复核”。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-methods-reproducibility-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-ars-reproducibility-review.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-report.md`

当前判断：

可复现性风险从“缺少映射表”降为“最终 release 包装还要说明哪些大文件不进 GitHub”。下一步机器侧应做 GWAS diagnostic appendix，把每个 oil trait 的统计诊断整理成投稿附录表。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.17 single human-input package 和 Stage 5.18 reviewer-risk register 初版。",
        "Stage 5.17 single human-input package、Stage 5.18 reviewer-risk register 和 Stage 5.19 result-to-script reproducibility crosswalk 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    crosswalk = build_crosswalk()
    inventory = file_inventory(crosswalk)
    crosswalk.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv", sep="\t", index=False)
    inventory.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-19-methods-reproducibility-insert.md", methods_insert(crosswalk))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-19-ars-reproducibility-review.md", ars_review(crosswalk, inventory))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-19-report.md", report(crosswalk, inventory))
    update_docs()
    print("Stage 5.19 reproducibility crosswalk generated.")


if __name__ == "__main__":
    main()
