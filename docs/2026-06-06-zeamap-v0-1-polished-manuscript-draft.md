# Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

日期：2026-06-06

## Manuscript Status

This is the Stage 5.10 polished manuscript draft. It is substantially closer to submission form than the Stage 5.8 skeleton because it now contains a fuller Introduction, integrated Results narrative, expanded Discussion, parameter-level Methods supplement pointers, a draft reference list and an academic-research-suite style self-review. It is still not final submission text because reference formatting, author metadata, journal style conversion and an external annotation pass remain open.

## Abstract

Maize kernel oil content and fatty-acid composition are genetically complex seed-quality traits. Public multi-omics resources provide an opportunity to integrate prediction and association analyses, but maize diversity panels require careful accession harmonization and stringent correction for population structure. We constructed a ZEAMAP v0.1 accession-level benchmark from processed public data, retaining 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified 66 robust traits and showed that oil-related traits had the strongest prediction performance under a genotype+population ridge model (oil median Pearson/R2 = 0.596/0.321). A diagnostic covariate-only GWAS for 10 high-priority oil traits showed severe genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC to 0.984-1.018. We annotated GEMMA lead loci with B73 RefGen_v4 gene models and prioritized 184 manuscript candidate loci. The strongest interval was a recurrent chromosome 6 linoleic acid1-region candidate, while a chromosome 9 C16:0-associated interval contained a nearby fatty acyl-ACP thioesterase candidate. These results provide a reproducible ZEAMAP benchmark and a conservative candidate-locus framework for maize oil-trait follow-up.

## Keywords

maize; ZEAMAP; oil traits; fatty acid composition; genotype-to-phenotype prediction; ridge regression; GEMMA; GWAS; candidate loci

## Introduction

Kernel oil content and fatty-acid composition are central maize seed-quality traits. They influence feed value, food quality, industrial uses and the long-term ability to breed maize germplasm with tailored biochemical profiles. These traits are also attractive for genetics because several components of fatty-acid metabolism are biologically interpretable, yet the observed quantitative variation is distributed across population structure, relatedness, local linkage disequilibrium and many candidate regulatory loci.

The availability of ZEAMAP processed data creates an opportunity to revisit maize oil-trait genetics through a reproducible accession-level workflow. However, a public multi-table resource cannot be treated as a ready-made machine-learning matrix. Sample identifiers must be reconciled, partially paired modalities must be separated from fully paired accessions and expression or epigenomic files must not be forced into accession-level models when the biological unit does not match. We therefore designed the first version of this project as a conservative v0.1 benchmark rather than as a high-capacity multi-omics foundation model.

This conservative choice is important for statistical reasons. The retained v0.1 dataset contains 461 accessions and nearly 200,000 SNPs, creating a high-dimensional prediction problem. DNA methylation coverage is available for only 236 accessions, and the expression files currently available in this project describe reference/tissue expression rather than accession-level AMP expression. Under this sample scale, complex neural networks are more likely to overfit than to provide interpretable biological insight. Regularized linear models, population baselines and multi-seed trait screening are therefore a stronger first manuscript route.

We used prediction as a triage step rather than as an endpoint. Genotype-to-phenotype benchmarking identified oil-related traits as the most robustly predictable family. This result motivated focused GWAS on 10 high-priority oil traits. Because maize diversity panels are strongly structured, we explicitly compared a diagnostic covariate-only GWAS with a mixed linear model. The diagnostic model showed inflation, whereas GEMMA mixed-model association controlled genomic inflation near one. Finally, we annotated GEMMA lead loci with B73 RefGen_v4 gene models, integrated prediction-attribution overlap and ranked candidate regions with explicit claim boundaries.

## Results

### ZEAMAP v0.1 defines a conservative accession-level benchmark

We harmonized ZEAMAP processed genotype, population and phenotype/metabolome tables at accession level. The resulting v0.1 dataset retained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric traits. Methylation coverage was recorded for 236 accessions but kept as an auxiliary modality because it was not available for the full v0.1 sample set. Current expression files were excluded from the main model because they did not represent matched AMP accession-level expression measurements.

This design intentionally prioritizes correct biological pairing over maximal feature count. For the current manuscript, the primary model input is genotype plus population covariates, and all downstream claims are restricted to what can be supported by those paired accession-level data.

### Regularized prediction identifies oil traits as the strongest target family

We evaluated genotype-to-phenotype prediction across numeric ZEAMAP traits and used repeated random-seed benchmarking to select robust traits. The final model, genotype+population ridge regression, achieved median Pearson/R2 of 0.498/0.204 across 66 robust traits. Oil traits were the strongest family, with median Pearson/R2 of 0.596/0.321 across 29 robust oil traits.

The model comparison supported a restrained modelling strategy. Ridge and ElasticNet were stable, whereas the small multilayer perceptron underperformed under the current sample size. This result does not argue that neural networks are unsuitable for maize phenomics in general; it shows that this particular accession-level v0.1 dataset is better served by regularized models and careful evaluation.

### Methylation provides auxiliary signal but is not a v0.1 main-model input

We tested methylation as global accession summaries, gene/promoter/cis-window PCA features and sparse gene-window features. The global summaries showed little overall gain, gene-level PCA provided limited auxiliary improvement and raw sparse methylation features were unstable in the 236-accession subset. We therefore retained methylation for coverage tracking, auxiliary ablation and candidate interpretation, but not as a default input for the primary v0.1 prediction model.

### GEMMA mixed models control oil-trait GWAS inflation

Prediction results prioritized oil traits for association mapping. A first covariate-only GWAS using population covariates was useful as a diagnostic baseline but showed severe genomic inflation. We therefore used GEMMA mixed linear models with genotype-derived kinship and the same covariates for the manuscript-facing GWAS.

Across 10 high-priority oil traits, GEMMA tested a median of 440 non-missing accessions and 199,856 SNPs per trait. Genomic inflation was controlled to lambda GC 0.984-1.018 (median 0.998). Bonferroni-significant hits ranged from 1 to 21 per trait. These calibrated association results form the manuscript's primary GWAS layer.

### Candidate-locus prioritization highlights chr6 and chr9 fatty-acid intervals

GEMMA lead signals were merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked by statistical support, trait recurrence, prediction-attribution overlap and functional annotation. After removing nominal-only signals, the manuscript-facing set contained 184 candidate loci, including 18 tier-1 main-text loci. Eight top regional targets were selected for regional association and gene-track visualization.

The leading region was R01_Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). This chromosome 6 interval was recurrent across 7 oil traits and contained Zm00001d036982, annotated locally as linoleic acid1 in local B73 RefGen_v4 annotation. Because prior maize fatty-acid and oil studies support chromosome-6 oil-related biology, we present this as the strongest candidate fatty-acid composition locus in the current analysis.

The second key biological interval was R08_Zm00001d045383, centred on chr9.s_20246143 for C16:0 (best P = 7.76e-17). The local interval contains Zm00001d045387, annotated as fatty acyl-ACP thioesterase2 near the lead region. This makes the chromosome 9 interval a high-priority fatty-acid composition candidate, although the lead SNP, causal gene and causal allele remain unresolved.

Other recurrent tier-1 loci on chromosomes 1, 4 and 8 showed strong statistical and ridge-attribution support but currently carry broader regulatory, transport or protein-family annotations. These regions should be reported as recurrent candidate intervals rather than as mechanistically resolved oil genes.

## Discussion

This study establishes a practical route from a public maize multi-table resource to a manuscript-facing oil-trait genetics analysis. The main contribution is not a new large model. Instead, it is a conservative accession-level benchmark, a clear demonstration that oil traits are the strongest predictable trait family in the current ZEAMAP v0.1 matrix and a calibrated GEMMA LMM GWAS layer that avoids the inflation observed with simpler covariate-only testing.

The prediction results are biologically useful because they prioritize where downstream genetic analysis is most likely to be productive. Oil traits showed stronger and more stable predictability than the median trait, suggesting that the genotype and population features in the v0.1 matrix capture meaningful genetic signal for seed oil and fatty-acid composition. This does not mean the model explains all oil-trait variance, but it provides a defensible basis for focusing GWAS and candidate annotation on oil traits.

The contrast between covariate-only GWAS and GEMMA is central to the paper. Without mixed-model correction, the oil-trait GWAS layer showed substantial inflation. With genotype-derived kinship, GEMMA controlled lambda GC near one across all tested oil traits. This result should be presented prominently because it protects the paper from a common criticism of diversity-panel GWAS: that top hits may reflect residual population structure rather than trait-associated loci.

The candidate-locus results should be interpreted in tiers. The chromosome 6 linoleic acid1-region locus is the strongest main-text candidate because it combines extreme statistical significance, recurrence across oil traits, lipid-related local annotation, ridge-attribution support and prior maize fatty-acid/oil evidence. The chromosome 9 C16:0 interval is also biologically compelling because of the nearby fatty acyl-ACP thioesterase annotation and the trait-specific link to palmitic-acid composition. Recurrent regions with MYB, transport or broad protein-family annotations are valuable but should remain hypothesis-generating until external annotation or experimental evidence is stronger.

Several limitations remain. First, the v0.1 dataset is small relative to the SNP feature space. Second, methylation is only partially paired and therefore cannot support a strong multi-omics claim in the main model. Third, candidate loci have not been fine-mapped or experimentally validated. Fourth, the reference list and external gene-annotation layer still need a final audit before journal submission. These limitations do not invalidate the current manuscript route, but they define the claim boundary: the study prioritizes candidate intervals and reproducible benchmarks; it does not prove causal variants or experimentally validate genes.

For submission, the strongest journal positioning is a methods-aware plant genomics paper: a ZEAMAP oil-trait prediction benchmark linked to calibrated mixed-model GWAS and candidate-locus prioritization. The Plant Genome, G3 and BMC Plant Biology remain realistic first-line targets after final annotation and figure polishing. A higher-impact plant journal would require added independent validation, functional assays, a stronger external annotation layer or a broader multi-population replication analysis.

## Methods

### Data acquisition and accession harmonization

ZEAMAP processed public data were downloaded from CNGBdb project CNP0001565. We focused on accession-level genotype, population, phenotype and metabolome tables. Sample identifiers were inspected across tables and harmonized to a unified accession index. Accessions were retained for the v0.1 dataset when they had genotype, population covariates and at least one phenotype or metabolome measurement. The resulting dataset contained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric traits.

### Prediction benchmark

We evaluated genotype-to-phenotype prediction using repeated train/validation/test evaluation. Candidate models included genotype+population ridge regression, genotype+population ElasticNet, population-only ridge regression and a small multilayer perceptron. Traits were retained for final reporting only when performance was stable across seeds. The main model was genotype+population ridge regression because it provided stable test performance under high-dimensional SNP features and limited sample size.

### Methylation ablation

Methylation was tested as global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection. Because methylation coverage was available for only 236 accessions and sparse methylation features were unstable, methylation was retained as an auxiliary modality rather than as a default v0.1 input.

### GWAS and candidate-locus annotation

Ten high-priority oil traits were selected from the final benchmark for association analysis. A covariate-only GWAS was used as a diagnostic inflation check. The main GWAS used GEMMA mixed linear models with genotype-derived kinship and population covariates. GEMMA likelihood-ratio p-values were used for association summaries. Lead signals were merged into physical loci, annotated with B73 RefGen_v4 gene models and ranked for manuscript interpretation. Candidate genes were interpreted as hypotheses unless supported by independent functional evidence.

### Figure generation

Main and regional figures were generated as PDF, SVG and high-resolution PNG outputs with Nature-style double-column sizing. Regional panels show local association strength, LD to the lead SNP and B73 RefGen_v4 gene tracks. Gene labels were restricted to candidate genes and lipid-related genes to avoid over-annotation.

## Data Availability

The study uses publicly available ZEAMAP processed data from CNGBdb project CNP0001565. Local processed derivatives and manuscript-facing summaries are stored in this project workspace. Large raw or intermediate files are not committed to GitHub.

## Code Availability

Scripts used for v0.1 dataset construction, prediction benchmarking, methylation ablation, GEMMA summary processing, candidate-locus annotation, figure generation and manuscript assembly are stored under `scripts/`.

## Claim Boundary

All reported loci are candidate loci or candidate genes. The current study does not perform fine-mapping, transgenic validation, biochemical validation or allele-specific functional assays. No lead SNP should be described as causal, and no candidate gene should be described as experimentally validated by this study.

## Figure And Table Plan

- Figure 1: ZEAMAP v0.1 dataset construction and prediction benchmark.
- Figure 2: GEMMA LMM calibration and candidate-locus summary.
- Figure 3: chromosome 6 linoleic acid1-region and chromosome 9 fatty acyl-ACP thioesterase candidate intervals.
- Table 1: eight prioritized regional candidate loci.
- Supplementary Table 1: full manuscript candidate-locus set.
- Supplementary Table 2: tier-1 candidate loci.
- Supplementary Table 3: literature and database source audit.
