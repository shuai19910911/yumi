#!/usr/bin/env python3
"""Build Stage 5.11 external annotation hardening outputs for top loci."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TABLES = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "manuscript_tables"
TOP = TABLES / "top_regional_loci_evidence.tsv"
OUT = TABLES / "top_regional_loci_external_annotation.tsv"


ANNOTATIONS = {
    "R01_Zm00001d036982": {
        "external_annotation_class": "direct_fatty_acid_candidate",
        "external_support_summary": "Local B73 annotation names Zm00001d036982 as linoleic acid1. Prior maize fatty-acid/oil studies support chromosome-6 fatty-acid composition biology, so this remains the strongest manuscript candidate interval.",
        "database_terms_to_verify": "MaizeGDB gene page; Gramene/Ensembl gene model; lipid/fatty-acid GO terms if available",
        "literature_support": "Alrefai et al. 1995; Cook et al. 2012; Li et al. 2013; Liu et al. 2023",
        "external_urls": "https://pubmed.ncbi.nlm.nih.gov/18470215/;https://pmc.ncbi.nlm.nih.gov/articles/PMC3271770/;https://www.nature.com/articles/ng.2484;https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full",
        "submission_claim": "Strong candidate fatty-acid composition interval; Zm00001d036982 is the leading local candidate gene.",
        "remaining_risk": "Gene symbol and exact RefGen_v4/RefGen_v5 mapping should be verified in MaizeGDB/Gramene before final submission.",
    },
    "R02_Zm00001d049511": {
        "external_annotation_class": "regulatory_candidate",
        "external_support_summary": "Local annotation suggests a MYB-domain gene. Maize MYB-family literature supports a regulatory role for MYB proteins, but there is no direct oil-biosynthetic evidence for this exact candidate yet.",
        "database_terms_to_verify": "MYB/SHAQKYF/R2R3 domain; PlantTFDB family if available; tissue expression if available",
        "literature_support": "R2R3-MYB transcription factor family in maize; Li et al. 2013 for broad oil GWAS context",
        "external_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3370817/;https://academic.oup.com/jxb/article/54/384/1117/631232;https://www.nature.com/articles/ng.2484",
        "submission_claim": "Recurrent oil-associated regulatory candidate interval.",
        "remaining_risk": "Do not describe this as a direct oil-biosynthesis gene without locus-specific functional evidence.",
    },
    "R03_Zm00001d031002": {
        "external_annotation_class": "broad_protein_interaction_candidate",
        "external_support_summary": "Local annotation is a tetratricopeptide repeat-like protein. TPR proteins mediate protein-protein interactions and have maize developmental examples, but the current locus lacks oil-specific annotation.",
        "database_terms_to_verify": "TPR domain; protein interaction/domain architecture; expression in kernel or embryo if available",
        "literature_support": "Maize TPR family/development literature; Li et al. 2013 for broad oil GWAS context",
        "external_urls": "https://pubmed.ncbi.nlm.nih.gov/38047628/;https://www.nature.com/articles/ng.2484",
        "submission_claim": "Recurrent statistical candidate interval with unresolved mechanism.",
        "remaining_risk": "Mechanistic interpretation is weak until external gene-specific annotation or expression support is added.",
    },
    "R04_Zm00001d009150": {
        "external_annotation_class": "seed_development_transport_candidate",
        "external_support_summary": "Local annotation indicates Sec23/Sec24 protein transport biology. A maize membrane-trafficking study reports Zm00001d009150/ZmSec23a as a maize improvement gene involved in seed development, strengthening this candidate beyond generic transport annotation.",
        "database_terms_to_verify": "ZmSec23a alias; COPII/vesicle transport GO terms; seed-development expression",
        "literature_support": "Network/evolutionary analysis of maize membrane trafficking and seed development",
        "external_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9263852/",
        "submission_claim": "Recurrent oil-associated seed-development/transport candidate interval.",
        "remaining_risk": "Still indirect for storage-oil biosynthesis; describe as seed-development/transport candidate rather than direct fatty-acid enzyme.",
    },
    "R05_Zm00001d013603": {
        "external_annotation_class": "inositol_signaling_candidate",
        "external_support_summary": "Local annotation indicates type IV inositol polyphosphate 5-phosphatase. Plant/maize inositol-phosphate phosphatase literature supports signaling/development roles, but the oil-trait link is indirect.",
        "database_terms_to_verify": "5-phosphatase domain; phosphoinositide signaling GO terms; maize homolog aliases",
        "literature_support": "Maize brevis plant1/inositol polyphosphate 5-phosphatase literature; angiosperm 5PTase expansion",
        "external_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC4762392/;https://pmc.ncbi.nlm.nih.gov/articles/PMC6562803/",
        "submission_claim": "Strong statistical candidate with plausible signaling/development annotation.",
        "remaining_risk": "No direct oil-function evidence; should be supplementary or extended main-text candidate.",
    },
    "R06_Zm00001d013849": {
        "external_annotation_class": "trihelix_regulatory_candidate",
        "external_support_summary": "Local annotation indicates a trihelix transcription factor GT-2. Recent maize studies describe trihelix transcription factors in stress and kernel/developmental regulation, supporting a regulatory-candidate interpretation.",
        "database_terms_to_verify": "Trihelix/GT-2 domain; PlantTFDB ZmTHX membership; kernel expression if available",
        "literature_support": "Maize trihelix family and ZmThx20 kernel-development studies",
        "external_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC11675602/;https://pmc.ncbi.nlm.nih.gov/articles/PMC8624104/;https://pmc.ncbi.nlm.nih.gov/articles/PMC10158769/",
        "submission_claim": "Oil-associated regulatory candidate locus.",
        "remaining_risk": "Regulatory plausibility is not direct evidence for fatty-acid metabolism.",
    },
    "R07_Zm00001d008881": {
        "external_annotation_class": "lipid_related_indirect_candidate",
        "external_support_summary": "The interval includes alkaline phytoceramidase in the local gene list, suggesting sphingolipid-related biology. This supports a lipid-related but not storage-oil-specific interpretation.",
        "database_terms_to_verify": "Alkaline phytoceramidase gene model; sphingolipid metabolism GO terms; local LD to candidate gene",
        "literature_support": "General lipid annotation and Li et al. 2013 broad maize oil GWAS context",
        "external_urls": "https://www.nature.com/articles/ng.2484",
        "submission_claim": "Lipid-related candidate interval with unresolved mechanism.",
        "remaining_risk": "Do not equate sphingolipid-related annotation with kernel storage-oil biosynthesis.",
    },
    "R08_Zm00001d045383": {
        "external_annotation_class": "direct_fatty_acid_candidate_interval",
        "external_support_summary": "Local annotation places fatty acyl-ACP thioesterase2 near the C16:0 lead region. Maize Zmfatb/acyl-ACP thioesterase literature directly supports fatty-acid composition relevance, making this a high-priority C16:0 candidate interval.",
        "database_terms_to_verify": "Zmfatb/FATB alias; acyl-ACP thioesterase GO terms; RefGen_v4-to-v5 mapping",
        "literature_support": "Zheng et al. 2012; Khan et al. 2022; recent maize FAT gene-family characterization",
        "external_urls": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3172307/;https://pmc.ncbi.nlm.nih.gov/articles/PMC9120846/;https://pubmed.ncbi.nlm.nih.gov/41009980/",
        "submission_claim": "High-priority C16:0 fatty-acid candidate interval containing fatty acyl-ACP thioesterase2.",
        "remaining_risk": "Exact causal gene/allele remains unresolved without fine-mapping or validation.",
    },
}


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_table() -> pd.DataFrame:
    top = pd.read_csv(TOP, sep="\t")
    rows = []
    for _, row in top.iterrows():
        region_id = row["region_id"]
        ann = ANNOTATIONS.get(region_id, {})
        merged = row.to_dict()
        merged.update(ann)
        rows.append(merged)
    out = pd.DataFrame(rows)
    out.to_csv(OUT, sep="\t", index=False)
    return out


def report(df: pd.DataFrame) -> str:
    direct = int(df["external_annotation_class"].astype(str).str.startswith("direct").sum())
    regulatory = int(df["external_annotation_class"].astype(str).str.contains("regulatory").sum())
    return f"""# ZEAMAP v0.1 Stage 5.11 External Annotation Hardening Report

日期：2026-06-06

## Purpose

This stage hardens the biological interpretation of the eight top regional oil-trait loci. The goal is to move beyond local B73 GFF descriptions and assign submission-facing interpretation classes with external literature/database hooks.

## Output Table

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_external_annotation.tsv`

The table keeps all columns from `top_regional_loci_evidence.tsv` and adds:

- `external_annotation_class`
- `external_support_summary`
- `database_terms_to_verify`
- `literature_support`
- `external_urls`
- `submission_claim`
- `remaining_risk`

## Summary

- Top regional loci annotated: {df.shape[0]}
- Direct fatty-acid candidate intervals: {direct}
- Regulatory candidate intervals: {regulatory}
- Strongest direct candidates: `R01_Zm00001d036982` and `R08_Zm00001d045383`
- Strongest indirect/seed-development candidate: `R04_Zm00001d009150` / ZmSec23a

## Manuscript-Level Interpretation

The external annotation pass strengthens the manuscript's tiered claim structure:

1. Chr6 `Zm00001d036982` remains the leading fatty-acid composition candidate.
2. Chr9 C16:0 `Zm00001d045383` interval remains a high-priority FatB/acyl-ACP-thioesterase candidate interval.
3. Chr8 `Zm00001d009150` gains stronger seed-development/transport support through ZmSec23a literature.
4. Chr4 MYB, chr5 trihelix and chr5 inositol-phosphatase regions should be presented as regulatory/signaling candidates.
5. Chr1 TPR and chr8 lipid-related indirect loci remain hypothesis-generating.

## Submission Readiness Impact

This stage improves biological interpretation from 6/10 to approximately 7/10 in the Stage 5.10 ARS scorecard. It does not remove the main limitation: no independent validation or causal fine-mapping.

## Remaining Required Checks

- Verify exact gene pages in MaizeGDB/Gramene for all eight top candidate genes.
- Export final citation metadata with DOI.
- Confirm whether RefGen_v4 gene IDs have RefGen_v5 aliases needed by the target journal.
- Add column descriptions for the new external annotation table.
"""


def readiness() -> str:
    return """# ZEAMAP v0.1 Submission Readiness Assessment After Stage 5.11

日期：2026-06-06

## Current Verdict

Current state: near pre-submission package for a realistic genetics/resource journal, not final uploaded manuscript.

The project is now credible for targeted journal preparation because it has:

- accession-level dataset construction,
- reproducible prediction benchmark,
- calibrated GEMMA LMM GWAS,
- manuscript candidate-locus tables,
- Nature-style main figures,
- polished manuscript draft,
- reference list draft,
- Methods parameter supplement,
- ARS self-review,
- external annotation hardening for top loci.

## Recommended Target Order

1. The Plant Genome: best balance if Methods, data availability and supplementary tables are polished.
2. G3: strong fit for a genetics-forward, reproducible analysis with conservative claims.
3. BMC Plant Biology: good backup route if framed as public-resource reuse plus candidate discovery.
4. Journal of Experimental Botany: only after stronger biological validation/annotation.

## Updated Acceptance Estimate

- The Plant Genome / G3 after Stage 5.11 polish: eventual acceptance about 60-75%.
- Direct first-round acceptance without major revision: about 10-20%.
- With independent validation or functional experiments: eventual acceptance could rise to 75-85%.
- Higher-impact plant journals remain low probability without validation.

## Final Submission Blockers

1. Final reference DOI/author formatting.
2. Final PDF/SVG font and panel-readability check.
3. Supplementary table column definitions.
4. Data/code availability wording matched to repository and large-file policy.
5. Journal-specific formatting, title page, author contributions and competing interests.
6. MaizeGDB/Gramene gene-page verification for top loci.

## Practical Next Step

Stage 5.12 should be final manuscript assembly: convert the polished draft into a target-journal formatted manuscript and build supplement table legends/column dictionaries.
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = progress.read_text(encoding="utf-8")
    text = text.replace(
        "| 阶段 5.11 external annotation hardening | 下一步 | 补 top loci 外部数据库注释、DOI audit、最终图件/补充表 polish |",
        "| 阶段 5.11 external annotation hardening | 已完成初版 | 已输出 top regional loci 外部注释硬化表和投稿就绪度评估 |\n| 阶段 5.12 final manuscript assembly | 下一步 | 期刊格式化、supplement column dictionary、最终图件检查和 data/code availability |",
    )
    if "## 阶段 5.12：final manuscript assembly" not in text:
        text += """

## 阶段 5.12：final manuscript assembly

状态：下一步。

目标：

把当前预投稿稿件包转成某个目标期刊可直接检查的投稿文件。

需要做：

- 选择目标期刊格式。
- 把 polished manuscript draft 转成 journal-style manuscript。
- 给 supplementary tables 写 column dictionary。
- 最终检查 Figure 1-3 的字体、线宽、panel 标签和 caption。
- 完成 Data availability、Code availability、Author contributions、Competing interests。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.10 polished manuscript package 初版。",
        "Stage 5.10 polished manuscript package 初版，以及 Stage 5.11 top loci external annotation hardening 初版。",
    )
    text = text.replace(
        "Stage 5.9 投稿策略/citation audit，以及 Stage 5.10 polished manuscript package 初版，以及 Stage 5.11 top loci external annotation hardening 初版。",
        "Stage 5.9 投稿策略/citation audit、Stage 5.10 polished manuscript package 初版，以及 Stage 5.11 top loci external annotation hardening 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    df = build_table()
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-11-external-annotation-report.md", report(df))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-submission-readiness-after-stage5-11.md", readiness())
    update_docs()
    print("Stage 5.11 external annotation package generated.")


if __name__ == "__main__":
    main()
