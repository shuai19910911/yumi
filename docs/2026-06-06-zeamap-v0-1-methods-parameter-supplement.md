# ZEAMAP v0.1 Methods Parameter Supplement

日期：2026-06-06

## Dataset Definition

- Unit of analysis: maize accession.
- Retained v0.1 accessions: 461 accessions with genotype, population covariates and at least one phenotype/metabolome measurement.
- Methylation coverage: 236 accessions, tracked as an auxiliary modality mask.
- Genotype matrix: 199,856 filtered common biallelic SNPs represented as dosage features.
- Phenotype/metabolome matrix: 318 numeric traits.
- Main benchmark target set: 66 robust traits selected by multi-seed stability.

## Prediction Benchmark Parameters

- Primary model: genotype plus population ridge regression.
- Comparator models: population-only ridge, genotype plus population ElasticNet and a small multilayer perceptron.
- Trait-level training: independent single-trait regression, excluding missing target values per trait.
- Robustness design: repeated random-seed train/validation/test evaluation before final trait selection.
- Main reason for ridge selection: best stability under high-dimensional SNP features and limited accession count; the small neural network showed overfitting/poor R2 under the same sample scale.

## Methylation Ablation Parameters

- Methylation tested as: accession global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection.
- Main decision: methylation remains auxiliary in v0.1 because coverage is incomplete and raw sparse features were unstable.
- Permitted manuscript statement: methylation PCA showed limited auxiliary signal.
- Prohibited manuscript statement: methylation is a validated causal regulator of the oil GWAS loci.

## GEMMA LMM GWAS Parameters

- Traits tested: 10 high-priority oil traits.
- Non-missing accessions per trait: median 440.
- SNPs tested per trait: 199,856.
- Kinship: genotype-derived relatedness matrix generated from the same v0.1 SNP set.
- Fixed covariates: population PCs/K covariates used in the diagnostic covariate-only GWAS were retained for GEMMA.
- Main p-value: GEMMA likelihood-ratio p-value (`p_lrt`).
- Multiple testing: Bonferroni threshold per trait and Benjamini-Hochberg FDR.
- Calibration result: lambda GC 0.984-1.018; median 0.998.
- Bonferroni hits: 1-21 per oil trait.

## Candidate-Locus Rules

- Lead SNPs are interpreted as interval markers, not causal variants.
- Candidate genes are assigned using B73 RefGen_v4 local annotation around lead loci.
- Locus priority integrates GEMMA significance, trait recurrence, ridge-attribution overlap and local lipid/fatty-acid annotation.
- The priority score is a triage score, not a statistical p-value.
- Top regional figures use local association strength, LD to lead SNP and B73 RefGen_v4 gene tracks.

## Minimum Reproducibility Files

- Dataset: `data/processed/v0_1/`
- Final benchmark: `results/v0_1_baseline/final_v0_1_trait_benchmark.tsv`
- GEMMA summaries: `results/v0_1_baseline/gemma_lmm_v0_1/gemma_lmm_summary.tsv`
- Candidate tables: `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/`
- Figures: `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures*/`
