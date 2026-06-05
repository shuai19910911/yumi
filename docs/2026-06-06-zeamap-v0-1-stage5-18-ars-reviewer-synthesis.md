# ZEAMAP v0.1 Stage 5.18 ARS Reviewer Synthesis

日期：2026-06-06

## Editorial Synthesis

Decision: `major_revision_before_submission`

The strongest parts of the manuscript are the conservative accession-level ZEAMAP v0.1 construction, the oil-trait prediction signal, the explicit rejection of inflated covariate-only GWAS as the main result and the calibrated GEMMA LMM candidate-locus framework. The strongest biological story is the chr6 linoleic acid1-region together with the chr9 C16:0 fatty acyl-ACP thioesterase interval.

The manuscript should not be submitted yet. The blocking reasons are practical and editorial rather than a failure of the core analysis: author-side metadata are absent, final figure inspection is not certified and release/tag/DOI are not executed. In addition, a reviewer-facing reproducibility crosswalk and stronger GWAS diagnostic appendix would materially reduce review risk.

## Highest-Risk Reviewer Comments

| risk_id | reviewer_role | severity | likely_comment | required_action |
| --- | --- | --- | --- | --- |
| R01 | Editor-in-chief | major | The manuscript is promising but may read as a short resource note unless the novelty and journal fit are sharpened. | Add a stronger novelty paragraph and explicit contribution statement before final submission. |
| R02 | Methodology reviewer | major | Trait filtering, train/test splitting, covariates and kinship construction need enough detail for exact reproduction. | Create a result-to-script reproducibility crosswalk and cite it in Methods/Data Availability. |
| R03 | Statistical genetics reviewer | major | The GWAS result is calibrated by lambda GC, but reviewers may ask about QQ plots, MAF filtering, missingness and multiple-testing thresholds. | Add GWAS diagnostic appendix table covering lambda, Bonferroni/FDR/suggestive thresholds, sample count and SNP count per trait. |
| R04 | Domain reviewer | major | The chr6 and chr9 biological interpretations need stronger literature support before they can carry the main biological story. | Expand literature support for linoleic acid1 and fatty acyl-ACP thioesterase intervals. |
| R05 | Reproducibility reviewer | major | Large inputs are outside GitHub; the paper must make it easy to obtain the exact public sources and regenerate derivative outputs. | Create a data/code reproducibility crosswalk before release. |
| R06 | Figure reviewer | major | The figure files are generated, but manual inspection at journal size has not been certified. | Complete final figure manual checklist after visual inspection. |
| R07 | Editorial office | blocking | Author metadata, COI, funding, reviewer names and release DOI are incomplete. | Fill single human-input form, synchronize templates, rerun Stage 5.15/5.16, then execute release. |
| R08 | Devil's advocate | moderate | The manuscript may overstate prediction-guided discovery if the prediction model is not directly used in the association model. | Audit Abstract, Discussion and captions for any wording implying validation or causal inference. |

## Gate Matrix

| gate | status | evidence | next_action |
| --- | --- | --- | --- |
| scientific_core_package | pass | Target manuscript includes GEMMA calibration and conservative candidate-interval language. | Keep claim boundary during all edits. |
| manuscript_depth | revise | proxy_word_count=2505 | Expand novelty, methods reproducibility and discussion before final upload. |
| human_metadata | fail | Stage 5.15 verdict=NO_SUBMIT_AUTHOR_METADATA_PENDING | Fill Stage 5.17 single human-input form and rerun preflight. |
| metadata_ingestion | fail | Stage 5.16 verdict=DRY_RUN_FAILED_PLACEHOLDERS_REMAIN | Rerun dry-run after synchronized metadata templates contain no placeholders. |
| single_form | fail | ready_sections=0/5; placeholder_rows=62 | Use single form as source of truth for human metadata. |

## Claim Boundary To Preserve

Use "candidate locus", "candidate interval", "prioritized region" and "follow-up target". Avoid "causal variant", "validated gene", "fine-mapped gene" and "confirmed mechanism" unless independent validation is added.
