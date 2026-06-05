# Methods/Data Availability Insert: Reproducibility Crosswalk

日期：2026-06-06

Suggested manuscript insertion:

> To support reproducibility, each main result, figure and manuscript-facing table was mapped to its generating script, primary inputs, primary outputs and key parameter decisions. This result-to-script crosswalk is provided in `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`, with a file-level inventory in `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`. Large public ZEAMAP inputs are not committed to the repository; their source project and local processing paths are documented, while derived manuscript tables, reports and generated figures are included where size permits.

Key crosswalk rows for main-text results:

| result_id | script | primary_outputs | key_parameters_or_decisions |
| --- | --- | --- | --- |
| R02_processed_dataset | scripts/build_zeamap_v0_1_dataset.py | data/processed/v0_1/accessions.tsv;data/processed/v0_1/phenotype.parquet;data/processed/v0_1/population.parquet;data/processed/v0_1/modality_mask.tsv;data/processed/v0_1/genotype_dosage_int8.npz | Common high-call biallelic SNPs; accession has genotype, population and at least one phenotype/metabolome measurement. |
| R08_final_prediction_benchmark | scripts/build_zeamap_v0_1_final_benchmark.py | docs/2026-06-05-zeamap-v0-1-final-benchmark.md | 66 robust traits; final model genotype_population_ridge; oil median Pearson/R2 0.596/0.321. |
| R12_gemma_lmm_summary | scripts/summarize_zeamap_v0_1_gemma_lmm.py | results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv;results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_lead_snps.tsv;docs/2026-06-05-zeamap-v0-1-gemma-lmm-report.md | p_lrt as main p-value; Bonferroni/FDR/suggestive summaries; QQ/Manhattan figures generated. |
| R13_candidate_loci_annotation | scripts/build_zeamap_v0_1_gemma_candidate_loci.py | results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv;results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_genes.tsv;docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md | Nominal-only loci excluded from manuscript set; 184 candidate loci and 147 genes retained. |
| R16_main_figures | scripts/build_zeamap_v0_1_stage5_7_methods_and_figures.py | results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf;results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf;results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf;docs/2026-06-05-zeamap-v0-1-stage5-7-methods-figures-report.md | Nature-style double-column PDF/SVG/PNG; manual final inspection remains required. |
