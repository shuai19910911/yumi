# ZEAMAP v0.1 Main Figure Plan

日期：2026-06-05

## Figure 1: Dataset And Prediction Benchmark

File:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf`

Panels:

- a: ZEAMAP processed data to v0.1 benchmark/GWAS workflow.
- b: v0.1 data scale: 461 paired accessions, 236 methylation-covered accessions, 199,856 SNPs and 318 numeric traits.
- c: model comparison on 66 robust traits.
- d: ridge benchmark by trait family, highlighting oil traits as the strongest family.

Main message:

Oil traits are the most stable prediction target family, justifying focused oil-trait GWAS.

## Figure 2: GEMMA LMM GWAS Calibration And Candidate-Locus Summary

Current file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf`

Main message:

Covariate-only GWAS was inflated, GEMMA LMM controlled lambda GC near 1, and 184 manuscript candidate loci were identified after excluding nominal-only loci.

Next polish:

- Keep this as the statistical GWAS summary figure.
- Add a clean figure caption tying lambda GC, Bonferroni/FDR hits and candidate-locus counts together.

## Figure 3: Top Regional Candidate Intervals

File:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf`

Panels:

- a: chr6 `Zm00001d036982` / linoleic acid1 candidate interval.
- b: chr9 C16:0 candidate interval containing nearby `Zm00001d045387` fatty acyl-ACP thioesterase2.

Main message:

The strongest prioritized loci include a recurrent chr6 fatty-acid candidate interval and a biologically focused chr9 C16:0 FatB/acyl-ACP-thioesterase candidate interval.

## Table Plan

- Table 1: `top_regional_loci_evidence.tsv`
- Supplementary Table 1: `supplementary_manuscript_candidate_loci.tsv`
- Supplementary Table 2: `main_tier1_locus_table.tsv`
