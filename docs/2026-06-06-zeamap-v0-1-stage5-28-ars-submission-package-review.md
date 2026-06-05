# Stage 5.28 ARS Submission-Package Review

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

| gate | status | evidence |
| --- | --- | --- |
| submission_package_compiled | pass | Stage 5.28 compiled manuscript index, The Plant Genome cover letter, journal route table, author checklist and release checklist. |
| manuscript_reference_style | pass | Stage 5.25 target-journal author-year reference gate passed with 18/18 references. |
| main_figure_technical_files | pass | Figures 1-3 have PNG/PDF/SVG files, valid headers and expected high-resolution PNG dimensions. |
| main_figure_human_visual_review | human_required | Agent visual spot-check found figures readable, with Figure 1 schematic simplicity and Figure 3 chr9 label crowding as polish items; final author approval at journal page size is still required. |
| author_metadata | human_required | Author names, affiliations, corresponding author and CRediT roles are not known to the agent. |
| funding_acknowledgements_coi | human_required | Funding, acknowledgements and final competing-interest confirmation need author approval. |
| repository_release_pid | human_required | A final GitHub release/tag and archive DOI/PID should be created only after author approval. |
| external_gene_name_confirmation | pass | Stage 5.27 confirmed MaizeGDB B73v4-to-B73v5 mappings for chr6/chr9 target genes and collected Ensembl/Gramene-side xref functional evidence; wording remains candidate-interval bounded. |

## Journal strategy

| rank | journal | current_probability_estimate | main_risk |
| --- | --- | --- | --- |
| 1 | The Plant Genome | 45-60% | Editor may view the work as secondary analysis unless benchmark and calibrated-GWAS contribution are clear. |
| 2 | G3: Genes\|Genomes\|Genetics | 40-60% | Pure public-data prediction/GWAS can be judged incremental without a sharply framed reusable resource contribution. |
| 3 | BMC Plant Biology | 55-75% | Needs a stronger biological story to avoid reading as a technical report. |
| 4 | The Crop Journal | 25-45% | May expect stronger agronomic or breeding validation than the current public-data reanalysis provides. |
| 5 | Frontiers in Plant Science | 50-70% | APC and article-type fit should be checked before submission. |
| 6 | Journal of Experimental Botany | 15-25% | Likely too descriptive for current evidence level. |
| 7 | Nature Plants | <3-6% | Desk rejection as careful but incremental public-data reanalysis. |
