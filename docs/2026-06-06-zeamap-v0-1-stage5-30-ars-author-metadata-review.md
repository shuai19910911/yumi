# Stage 5.30 ARS Author Metadata Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite finalization rule that author identity, contribution, funding and COI statements cannot be invented by the agent. The stage is successful only as a pipeline/template preparation step unless real author-approved metadata are present.

## Editorial-style verdict

`PIPELINE_READY_AUTHOR_INPUT_REQUIRED`

## Reviewer synthesis

- Integrity reviewer: no author names, affiliations, grants or COI statements were fabricated.
- Format reviewer: the template fields match the manuscript sections that still block submission.
- Reproducibility reviewer: the same script can be rerun after real metadata are supplied to create a filled manuscript preview.
- Devil's advocate: this does not close the author metadata blocker; it only makes closure executable once authors provide verified information.

## Audit

| check | status | evidence |
| --- | --- | --- |
| author_metadata_fields | human_required | Missing or placeholder fields: full_name; initials; email |
| author_approval_confirmed | human_required | Every author row must set approval_confirmed=yes. |
| author_coi_confirmed | human_required | Every author row must set coi_confirmed=yes. |
| corresponding_author_present | pass | At least one corresponding author present. |
| affiliations_complete | human_required | Affiliation text and approval_confirmed=yes are required. |
| funding_acknowledgements_coi_complete | human_required | Funding, acknowledgements and COI statement_text plus approval_confirmed=yes are required. |

## Gate

| gate | status | evidence |
| --- | --- | --- |
| author_metadata_ingestion_pipeline | pass | Stage 5.30 created structured author/affiliation/funding/COI templates and a validation/fill-preview script. |
| clean_submission_manuscript_exported | pass | Stage 5.29 generated clean Markdown, DOCX and HTML manuscript exports via pandoc. |
| format_compliance_check | pass | Stage 5.29 checked title, core ideas, abstract, references, statements, legends and claim boundaries. |
| submission_package_compiled | pass | Stage 5.28 compiled manuscript index, The Plant Genome cover letter, journal route table, author checklist and release checklist. |
| manuscript_reference_style | pass | Stage 5.25 target-journal author-year reference gate passed with 18/18 references. |
| main_figure_technical_files | pass | Figures 1-3 have PNG/PDF/SVG files, valid headers and expected high-resolution PNG dimensions. |
| main_figure_human_visual_review | human_required | Agent visual spot-check found figures readable, with Figure 1 schematic simplicity and Figure 3 chr9 label crowding as polish items; final author approval at journal page size is still required. |
| author_metadata | human_required | Stage 5.30 templates exist, but real author metadata and approvals are still missing. |
| funding_acknowledgements_coi | human_required | Stage 5.30 statement template exists, but author-approved text is still missing. |
| repository_release_pid | human_required | A final GitHub release/tag and archive DOI/PID should be created only after author approval. |
| external_gene_name_confirmation | pass | Stage 5.27 confirmed MaizeGDB B73v4-to-B73v5 mappings for chr6/chr9 target genes and collected Ensembl/Gramene-side xref functional evidence; wording remains candidate-interval bounded. |
