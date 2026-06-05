# ZEAMAP v0.1 Stage 5.11 External Annotation Hardening Report

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

- Top regional loci annotated: 8
- Direct fatty-acid candidate intervals: 2
- Regulatory candidate intervals: 2
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
