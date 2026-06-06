# ZEAMAP v0.1 Stage 5.36 DOCX Font Optimization Report

日期：2026-06-06

## Verdict

`DOCX_FONT_OPTIMIZED`

## What changed

- Created new optimized Word files instead of overwriting the Stage 5.35 exports.
- Set Latin text to `Times New Roman`.
- Set East Asian text to `宋体`.
- Applied fonts both at style/default level and at run level in `word/document.xml`.

## Outputs

- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx`
- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.png`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.png`

## Audit

| path | status | bytes | ascii_font | east_asia_font | styles_has_ascii_font | styles_has_east_asia_font | document_has_east_asia_font |
| --- | --- | --- | --- | --- | --- | --- | --- |
| docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx | pass | 22023 | Times New Roman | 宋体 | True | True | True |
| docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx | pass | 25577 | Times New Roman | 宋体 | True | True | True |

## Workflow/model figure audit

figure	png	pdf	svg	status	purpose
overall_workflow	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.png	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.pdf	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.svg	pass	Make the analysis and model structure understandable at a glance.
model_structure	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.png	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.pdf	results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.svg	pass	Make the analysis and model structure understandable at a glance.
