# Stage 5.33 ARS Submission Integrity Review

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

| check | status | evidence |
| --- | --- | --- |
| required_artifacts_exist | pass | All curated submission artifacts exist. |
| non_empty_artifacts | pass | All curated submission artifacts are non-empty. |
| category_coverage | pass | figure=9; manuscript=3; method=5; release=2; result=6; script=14; submission=8; table=5 |
| release_pid_not_fabricated | human_required | Checksum manifest is ready, but the final tag, GitHub release and DOI/PID still require author-approved release action. |
| author_controlled_fields_not_fabricated | human_required | Author metadata, funding/COI statements and final figure approvals remain template-driven human inputs. |

## Final gate

| gate | status | evidence |
| --- | --- | --- |
| submission_artifact_integrity_manifest | pass | Stage 5.33 generated SHA256 checksums and existence/non-empty audit for curated submission artifacts. |
| single_human_action_packet | pass | Stage 5.32 compiled one human action packet mapping every remaining blocker to files, commands and completion evidence. |
| figure_release_readiness_pipeline | pass | Stage 5.31 created figure approval template, release notes draft and Zenodo metadata draft. |
| author_metadata_ingestion_pipeline | pass | Stage 5.30 created structured author/affiliation/funding/COI templates and a validation/fill-preview script. |
| clean_submission_manuscript_exported | pass | Stage 5.29 generated clean Markdown, DOCX and HTML manuscript exports via pandoc. |
| format_compliance_check | pass | Stage 5.29 checked title, core ideas, abstract, references, statements, legends and claim boundaries. |
| submission_package_compiled | pass | Stage 5.28 compiled manuscript index, The Plant Genome cover letter, journal route table, author checklist and release checklist. |
| manuscript_reference_style | pass | Stage 5.25 target-journal author-year reference gate passed with 18/18 references. |
| main_figure_technical_files | pass | Figures 1-3 have PNG/PDF/SVG files, valid headers and expected high-resolution PNG dimensions. |
| main_figure_human_visual_review | human_required | Stage 5.31 figure approval template exists, but author-side visual approval is still missing. |
| author_metadata | human_required | Stage 5.30 templates exist, but real author metadata and approvals are still missing. |
| funding_acknowledgements_coi | human_required | Stage 5.30 statement template exists, but author-approved text is still missing. |
| repository_release_pid | human_required | Stage 5.31 release notes and Zenodo metadata drafts exist, but tag/release/archive DOI must wait for author-approved final commit. |
| external_gene_name_confirmation | pass | Stage 5.27 confirmed MaizeGDB B73v4-to-B73v5 mappings for chr6/chr9 target genes and collected Ensembl/Gramene-side xref functional evidence; wording remains candidate-interval bounded. |

## Manifest scope

- curated artifacts: 52
- categories: figure, manuscript, method, release, result, script, submission, table
