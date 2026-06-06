# ZEAMAP v0.1 Stage 5.34 Figure And Table Quality Review

日期：2026-06-06

## Overall judgement

`FIGURE_TABLE_PACKAGE_APPROPRIATE_WITH_MINOR_FIGURE_READABILITY_ATTENTION`

## Quantity assessment

- Main figures: 3. This is appropriate for a compact plant genomics manuscript: one workflow/prediction figure, one GWAS summary figure and one regional candidate-locus figure.
- Main tables: 1. This is appropriate because the top regional evidence table is small enough for the main text.
- Supplementary tables: 4. This is appropriate because candidate-locus lists and column dictionaries are necessary but too large for the main text.
- Supplementary regional figures: 8 regional locus figures. This is useful for reviewer inspection, but should remain supplementary unless the target journal asks for more main-text regional evidence.

## Quality assessment

- Figure 1: acceptable and useful, but visually simpler than Figures 2-3. It can stay as the overview figure.
- Figure 2: strongest main figure; it carries the statistical argument and should remain central.
- Figure 3: biologically important; final human review should check chr9 label crowding at journal page size.
- Tables: table quantity and structure are appropriate; the table set supports reproducibility and avoids overcrowding the main text.

## Figure audit

| figure | role | png_path | png_width | png_height | png_resolution_status | pdf_status | svg_status | quality_status | review_note |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Figure 1 | Dataset construction and prediction benchmark | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.png | 4320 | 3116 | pass | pass | pass | pass_with_minor_attention | Scientifically useful overview; visually a little schematic/simple, but acceptable for a compact main workflow figure. |
| Figure 2 | GEMMA calibration and candidate-locus summary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.png | 4320 | 2879 | pass | pass | pass | pass | Strongest information-density figure; appropriate as the statistical core figure. |
| Figure 3 | Chr6 and chr9 prioritized regional candidate intervals | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.png | 4320 | 1135 | check | pass | pass | pass_with_minor_attention | Biologically important figure; chr9 local labels remain the main page-size readability risk. |
| Supplementary regional figures | Eight prioritized local association/LD/gene-track figures | 8 PNG files in results/v0_1_baseline/gemma_lmm_v0_1/regional_figures | various | various | pass | pass | pass | supplementary_pass | Quantity is appropriate for supplement; not all eight should be forced into the main text. |

## Table audit

| table | role | placement | path | exists | rows | columns | quality_status | assessment |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Table 1 | Top regional candidate loci | main | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv | yes | 8 | 27 | pass | Main-text table count is appropriate; eight rows are readable and support the top-locus narrative. |
| Supplementary Table 1 | Manuscript candidate loci | supplementary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv | yes | 184 | 24 | pass | Appropriate as supplementary table because the full locus set is too large for the main text. |
| Supplementary Table 2 | Tier-1 candidate loci | supplementary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv | yes | 18 | 21 | pass | Appropriate as supplementary table because the full locus set is too large for the main text. |
| Supplementary Table 3 | External annotation hardening | supplementary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_external_annotation.tsv | yes | 8 | 34 | pass | Appropriate supplementary support for annotation and prioritization claims. |
| Supplementary Table 4 | Supplementary column dictionary | supplementary | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_table_column_dictionary.tsv | yes | 152 | 5 | pass | Required for reproducibility and reviewer interpretation of supplementary columns. |
