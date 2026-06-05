# Stage 5.27 ARS External Gene-Name Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite integrity gate logic: external database evidence is checked separately from biological interpretation. The review asks whether the manuscript can safely cite current gene IDs and functional evidence without overstating causality.

## Editorial-style verdict

`MINOR_REVISION_AUTHOR_METADATA_REMAINS`

## Reviewer synthesis

- Domain reviewer: chr6 functional evidence is stronger after current-ID xref confirmation and is consistent with lipid/acyltransferase biology.
- Domain reviewer: chr9 must be written carefully. The lead-host gene and the nearby fatty-acid thioesterase candidate are different genes.
- Methods reviewer: no new association statistics were introduced; gene-name confirmation only changes annotation confidence.
- Devil's advocate: even with external evidence, the study still lacks fine-mapping and functional validation, so causal language remains prohibited.

## Current-ID evidence summary

| region_id | v4_gene_id | maizegdb_v5_gene_id | role | expected_function_terms_hit | mapping_verdict |
| --- | --- | --- | --- | --- | --- |
| R01_Zm00001d036982 | Zm00001d036982 | Zm00001eb277490 | chr6 lead-region candidate gene | diacylglycerol o-acyltransferase; o-acyltransferase; triglyceride biosynthetic process; lipid metabolic process | external_source_confirmed |
| R08_Zm00001d045383 | Zm00001d045383 | Zm00001eb377300 | chr9 lead SNP host gene | 1-deoxy-d-xylulose-5-phosphate synthase; isoprenoid biosynthetic process; terpenoid biosynthetic process | external_source_confirmed |
| R08_Zm00001d045383 | Zm00001d045387 | Zm00001eb377350 | chr9 nearby fatty-acid pathway candidate | acyl-[acyl-carrier-protein] hydrolase; palmitoyl-acyl carrier protein thioesterase; fatty acid biosynthetic process; chloroplast | external_source_confirmed |

## Updated final gate

| gate | status | evidence |
| --- | --- | --- |
| manuscript_reference_style | pass | Stage 5.25 target-journal author-year reference gate passed with 18/18 references. |
| main_figure_technical_files | pass | Figures 1-3 have PNG/PDF/SVG files, valid headers and expected high-resolution PNG dimensions. |
| main_figure_human_visual_review | human_required | Agent visual spot-check found figures readable, with Figure 1 schematic simplicity and Figure 3 chr9 label crowding as polish items; final author approval at journal page size is still required. |
| author_metadata | human_required | Author names, affiliations, corresponding author and CRediT roles are not known to the agent. |
| funding_acknowledgements_coi | human_required | Funding, acknowledgements and final competing-interest confirmation need author approval. |
| repository_release_pid | human_required | A final GitHub release/tag and archive DOI/PID should be created only after author approval. |
| external_gene_name_confirmation | pass | Stage 5.27 confirmed MaizeGDB B73v4-to-B73v5 mappings for chr6/chr9 target genes and collected Ensembl/Gramene-side xref functional evidence; wording remains candidate-interval bounded. |
