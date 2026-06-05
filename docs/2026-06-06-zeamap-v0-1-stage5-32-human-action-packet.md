# ZEAMAP v0.1 Stage 5.32 Human Action Packet

日期：2026-06-06

## Purpose

This is the single entry point for closing the remaining submission blockers. The machine-side manuscript, citation, figure-file, export, annotation and submission-package gates are already prepared. What remains is author-controlled information and approval.

## Remaining blockers

| blocker | current_status | what_to_fill | verification_command | evidence_after_done | current_missing_summary |
| --- | --- | --- | --- | --- | --- |
| author_metadata | human_required | docs/2026-06-06-zeamap-v0-1-stage5-30-author-metadata-template.tsv; docs/2026-06-06-zeamap-v0-1-stage5-30-affiliation-template.tsv | mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py | Stage 5.30 dry-run audit rows author_metadata_fields, author_approval_confirmed, corresponding_author_present and affiliations_complete all pass. | author_metadata_fields; author_approval_confirmed; author_coi_confirmed; affiliations_complete; funding_acknowledgements_coi_complete |
| funding_acknowledgements_coi | human_required | docs/2026-06-06-zeamap-v0-1-stage5-30-funding-coi-acknowledgement-template.tsv | mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py | Stage 5.30 dry-run audit row funding_acknowledgements_coi_complete passes. | author_metadata_fields; author_approval_confirmed; author_coi_confirmed; affiliations_complete; funding_acknowledgements_coi_complete |
| main_figure_human_visual_review | human_required | docs/2026-06-06-zeamap-v0-1-stage5-31-figure-final-approval-template.tsv | mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py | Stage 5.31 figure approval audit rows for Figure 1-3 all pass. | Figure 1; Figure 2; Figure 3 |
| repository_release_pid | human_required | docs/2026-06-06-zeamap-v0-1-stage5-31-github-release-notes.md; docs/2026-06-06-zeamap-v0-1-stage5-31-zenodo-metadata-draft.json | After final author-approved commit: git tag -a zeamap-oil-v0.1-submission -m "ZEAMAP maize oil-trait manuscript submission package"; git push origin zeamap-oil-v0.1-submission; create GitHub release; archive in Zenodo/Figshare; record DOI/PID. | Real release tag, GitHub release URL and archive DOI/PID recorded in final manuscript Data/Code Availability and release docs. | zenodo_metadata_draft; clean_git_status_before_release; tag_not_created_by_agent; archive_pid_not_available |

## Fill these files first

1. Author metadata and author approval:
   - `docs/2026-06-06-zeamap-v0-1-stage5-30-author-metadata-template.tsv`
   - `docs/2026-06-06-zeamap-v0-1-stage5-30-affiliation-template.tsv`

2. Funding, acknowledgements and competing interests:
   - `docs/2026-06-06-zeamap-v0-1-stage5-30-funding-coi-acknowledgement-template.tsv`

3. Final figure visual approval:
   - `docs/2026-06-06-zeamap-v0-1-stage5-31-figure-final-approval-template.tsv`

4. Release and archive metadata:
   - `docs/2026-06-06-zeamap-v0-1-stage5-31-github-release-notes.md`
   - `docs/2026-06-06-zeamap-v0-1-stage5-31-zenodo-metadata-draft.json`

## Rerun commands after filling author/figure templates

```bash
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_30_author_metadata_ingestion.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_31_figure_release_readiness.py
mamba run -n yumi python scripts/build_zeamap_v0_1_stage5_29_format_export_package.py
```

## Release only after all author-controlled gates pass

Do not create the final tag or release until author metadata, statements and figure approvals are complete and committed.

```bash
git status --short
git add README.md docs scripts
git commit -m "finalize submission metadata"
git tag -a zeamap-oil-v0.1-submission -m "ZEAMAP maize oil-trait manuscript submission package"
git push origin main
git push origin zeamap-oil-v0.1-submission
```

Then create a GitHub release from the tag and archive it with Zenodo/Figshare if required by the target journal. Record the DOI/PID in the manuscript Data Availability/Code Availability section.

## Final gate snapshot

| gate | status | evidence |
| --- | --- | --- |
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
