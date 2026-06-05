# ZEAMAP v0.1 Methods Draft

日期：2026-06-05

## Data Acquisition And Accession Harmonization

ZEAMAP processed public data were downloaded from CNGBdb project CNP0001565. We focused on accession-level genotype, population, phenotype and metabolome tables. Sample identifiers were inspected across tables and harmonized to a unified accession index. Accessions were retained for the v0.1 dataset when they had genotype, population covariates and at least one phenotype or metabolome measurement. The resulting v0.1 dataset contained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric phenotype/metabolome traits. DNA methylation coverage was tracked as a modality mask for 236 accessions but was not used as a default main-model input.

## Prediction Benchmark

We evaluated accession-level genotype-to-phenotype prediction using train/validation/test splits and repeated multi-seed benchmarking. Genotype features were combined with population covariates where indicated. The main comparison included genotype+population ridge regression, genotype+population ElasticNet, population-only ridge regression and a small multilayer perceptron. Traits were first screened for predictability and then retained as robust traits when performance was stable across seeds. The final benchmark used 66 robust traits and selected genotype+population ridge regression as the primary model because it provided stable test performance and avoided the overfitting observed for the small neural network.

## Methylation Ablation

Methylation was assessed through global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection. Because methylation coverage was available for only 236 accessions and raw sparse methylation features were unstable, methylation was retained as an auxiliary ablation and interpretation modality rather than as a default input to the v0.1 primary model.

## Oil-Trait GWAS

Ten high-priority oil-related traits were selected for association analysis based on the final prediction benchmark. A covariate-only GWAS was first run with PC1-PC3 and K1-K3 covariates to diagnose inflation. Because this model showed severe genomic inflation, the main GWAS used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Association testing used GEMMA likelihood-ratio p-values (`p_lrt`). For each oil trait, 440 non-missing accessions and 199,856 SNPs were tested. Bonferroni and Benjamini-Hochberg FDR thresholds were calculated per trait.

## Candidate-Locus Annotation

GEMMA lead SNPs were clumped into physical loci by trait and chromosome. Candidate genes were assigned using B73 RefGen_v4 gene models, including gene-body, promoter and cis-window relationships. Gene descriptions and biotypes were parsed from the local Ensembl/Gramene GFF3 file. Candidate loci were classified by significance level, ridge-attribution overlap and functional keyword classes. Nominal-only loci were excluded from manuscript-facing candidate-locus tables.

## Top-Locus Prioritization And Evidence Levels

Manuscript candidate loci were ranked using GEMMA significance class, association strength, recurrence across oil traits, ridge-attribution overlap, lipid/fatty-acid keyword support and candidate-gene count. This priority score was used only for manuscript triage and was not treated as a new statistical test. Eight regional loci were selected for regional visualization and evidence curation. Evidence levels were assigned conservatively according to whether the locus had direct prior oil/fatty-acid support, indirect lipid-related annotation, recurrent statistical support or only statistical evidence.

## Regional Association Figures

Regional association figures were drawn for top loci using GEMMA p-values within a fixed local window around the lead SNP. SNPs were coloured by LD r2 to the lead SNP, computed from standardized genotype dosages in the v0.1 dataset. Gene tracks were drawn from B73 RefGen_v4 gene models, with labels restricted to local candidate genes and lipid-related genes to avoid over-annotation. Figures were exported as PDF, SVG and high-resolution PNG with Nature-style double-column sizing and Type-42 font settings.

## Claim Boundary

All reported loci are interpreted as candidate loci or candidate genes. The current analysis does not perform fine-mapping, experimental validation, transgenic tests or biochemical assays. Therefore, no lead SNP is described as causal and no candidate gene is described as experimentally validated by this study.
