# ZEAMAP v0.1 Stage 5.33 Submission Package README

日期：2026-06-06

## Purpose

This file is the machine-checkable handoff for final submission and repository archiving. It lists the clean manuscript exports, main figures, manuscript tables, key result files, reproducibility audits and critical scripts that should travel with the submission package.

## Current git commit

```text
203fc84
```

## Main submission files

- Clean manuscript: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.md`
- DOCX export: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.docx`
- HTML export: `docs/2026-06-06-zeamap-v0-1-stage5-29-submission-clean-manuscript.html`
- Human action packet: `docs/2026-06-06-zeamap-v0-1-stage5-32-human-action-packet.md`
- Checksum manifest: `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv`

## Artifact category counts

| category | artifact_count |
| --- | --- |
| figure | 9 |
| manuscript | 3 |
| method | 5 |
| release | 2 |
| result | 6 |
| script | 14 |
| submission | 8 |
| table | 5 |

## Integrity audit

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

## How to use before submission

1. Fill author, affiliation, funding/COI and figure approval templates listed in the Stage 5.32 human action packet.
2. Rerun Stage 5.30, Stage 5.31, Stage 5.29, Stage 5.32 and Stage 5.33.
3. Confirm no `fail` remains in this audit and no unresolved `human_required` remains except the release DOI/PID if the archive is intentionally created after final commit.
4. Create the GitHub release and external archive DOI/PID only after final author approval.
