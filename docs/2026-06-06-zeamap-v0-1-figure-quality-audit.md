# ZEAMAP v0.1 Figure Quality Audit

日期：2026-06-06

## Scope

This audit checks the three manuscript-facing figures generated for the current ZEAMAP v0.1 submission package. It verifies file presence, PNG dimensions, vector-format presence and a basic nonblank image check when Pillow is available.

## Figure File Audit

| figure | role | png_path | png_exists | png_width_px | png_height_px | png_megapixels | pdf_exists | svg_exists | png_nonblank_check | submission_status |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Figure 1 | Dataset construction and prediction benchmark | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.png | True | 4320 | 3116 | 13.46 | True | True | pass_nonblank | ready_for_final_visual_review |
| Figure 2 | GEMMA LMM calibration and candidate-locus summary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.png | True | 4320 | 2879 | 12.44 | True | True | pass_nonblank | ready_for_final_visual_review |
| Figure 3 | Chr6 and chr9 regional candidate intervals | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.png | True | 4320 | 1135 | 4.9 | True | True | pass_nonblank | ready_for_final_visual_review |

## Interpretation

- All manuscript figures should be submitted as vector PDF/SVG where allowed, with PNG retained for review and repository preview.
- PNG dimensions are above 3,000 px width for all main figures, supporting high-resolution review.
- Final submission still requires manual visual inspection at journal page size for label collisions, font consistency and panel-letter placement.
- If the target journal requires TIFF/EPS, convert from PDF/SVG rather than from low-resolution screenshots.
