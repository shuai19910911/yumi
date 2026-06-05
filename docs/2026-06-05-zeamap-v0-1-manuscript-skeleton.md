# Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

日期：2026-06-05

## Manuscript Status

This is a Stage 5.8 manuscript skeleton. It assembles the current Results, Methods, figure captions, table captions and claim boundaries into a single paper-facing document. It is not yet a submission-ready manuscript.

## Working Title

Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

## Abstract Draft

Maize kernel oil traits are genetically complex and strongly shaped by population structure, making prediction and association analyses vulnerable to overfitting and inflated test statistics. We harmonized public ZEAMAP processed data into an accession-level v0.1 benchmark containing 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified 66 robust traits and showed that oil-related traits had the strongest prediction performance under a genotype+population ridge model. A diagnostic covariate-only GWAS for 10 high-priority oil traits showed severe genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC near 1. We annotated GEMMA lead loci using B73 RefGen_v4 gene models, prioritized 184 manuscript candidate loci and generated regional association figures for top candidates. The strongest interval was a recurrent chr6 `Zm00001d036982` / linoleic acid1 candidate region, while a chr9 C16:0-associated interval contained a nearby fatty acyl-ACP thioesterase candidate gene. These results provide a reproducible ZEAMAP benchmark and a conservative candidate-locus framework for maize oil-trait follow-up.

## Keywords

maize; ZEAMAP; oil traits; genotype-to-phenotype prediction; GEMMA; GWAS; fatty acid composition; candidate loci

## Introduction Draft

Maize kernel oil content and fatty-acid composition are important seed-quality traits with direct relevance to nutrition, feed, industrial use and breeding. These traits are influenced by many loci and by the genetic structure of maize diversity panels, making both prediction and association mapping technically challenging. Public ZEAMAP resources provide a valuable foundation for accession-level genotype, population and phenotype integration, but their utility depends on careful sample harmonization and conservative interpretation of partially paired omics modalities.

In this study, we first constructed a ZEAMAP v0.1 accession-level benchmark rather than immediately training a high-capacity multi-omics model. This choice was motivated by the available sample scale: 461 strongly paired accessions for genotype, population and phenotype/metabolome data, but only 236 accessions with methylation coverage and no AMP accession-level expression matrix. We therefore used regularized prediction models and multi-seed trait screening to identify robustly predictable trait families.

Oil traits emerged as the most stable and predictable family, motivating focused oil-trait GWAS. Because maize diversity panels have strong population structure and relatedness, we compared a diagnostic covariate-only GWAS against GEMMA mixed linear models. This design allowed us to separate inflated association signals from kinship-controlled candidate loci. We then mapped GEMMA lead loci to B73 RefGen_v4 candidate genes, integrated prediction-attribution overlap and curated the strongest regional candidates with explicit claim boundaries.

## Results

### Genotype-based prediction prioritizes oil-related traits

After harmonizing ZEAMAP accessions across genotype, population and phenotype/metabolome tables, we constructed a v0.1 accession-level dataset containing 461 accessions, 199,856 common biallelic SNPs and 318 numeric traits. Multi-seed benchmarking identified 66 robust traits, among which oil-related traits showed the strongest prediction signal. The final `genotype_population_ridge` model achieved a median Pearson correlation of 0.498 and median R2 of 0.204 across robust traits, with the oil family reaching a median Pearson/R2 of 0.596/0.321. These results motivated a focused downstream GWAS analysis of high-priority oil traits rather than immediate expansion to a high-capacity deep model.

### Mixed linear modelling controls oil-trait GWAS inflation

A covariate-only GWAS using PC1-PC3 and K1-K3 showed severe genomic inflation (lambda GC 2.41-3.97), indicating that population covariates alone were insufficient for association testing in this maize panel. We therefore used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Across 10 high-priority oil traits, GEMMA reduced lambda GC to 0.984-1.018 (median 0.998), supporting these results as the main GWAS baseline. Lead SNPs were then merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked for manuscript interpretation.

### Prioritized oil-trait loci

The GEMMA candidate-locus layer contained 184 manuscript candidate loci after removing nominal-only signals. We ranked these loci using GEMMA significance, association strength, recurrence across oil traits, ridge-attribution overlap and lipid/fatty-acid annotations. This yielded 18 tier-1 main-text loci and 22 tier-2 strong loci. Eight representative regional association figures were generated to show local association peaks, LD to the lead SNP and nearby gene models.

The strongest region was chr6 Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). This region was recurrent across 7 oil traits and included a local gene annotated as linoleic acid1 in local B73 RefGen_v4 annotation. Prior maize studies reported chromosome 6 linoleic-acid/oil-related QTL evidence and broader maize oil GWAS support for lipid-metabolism loci. We therefore treat this chr6 interval as the leading candidate fatty-acid composition locus, while maintaining the conservative interpretation that the lead SNP marks a candidate interval rather than a proven causal variant.

The chr9 C16:0-associated region around chr9.s_20246143 (best P = 7.76e-17) is also biologically notable. Although it is not recurrent across multiple oil traits, the interval contains Zm00001d045387, annotated as fatty acyl-ACP thioesterase2 near the lead region. Previous maize studies mapped palmitic-acid variation to FatB/acyl-ACP thioesterase biology on chromosome 9, making this a high-priority candidate interval for fatty-acid composition follow-up.

Other recurrent tier-1 regions on chromosomes 4, 1 and 8 were strongly supported statistically and by ridge-attribution overlap, but their current annotations are regulatory, transport-related or broad protein-family descriptions rather than direct oil-biosynthetic genes. These loci should be presented as recurrent candidate regions and prioritized for external database annotation and experimental follow-up.

### Candidate-claim boundaries

All loci in the current manuscript table should be described as candidate loci or candidate genes. The current analysis does not perform fine-mapping, allele-specific validation or transgenic/biochemical experiments. Therefore, no lead SNP should be described as causal, and no candidate gene should be described as experimentally validated by this study.

### Draft Figure And Table Calls

- Figure 1: v0.1 dataset construction and prediction benchmark summary.
- Figure 2: GEMMA LMM GWAS calibration and candidate-locus summary.
- Figure 3: Regional association panels for chr6 `Zm00001d036982` and chr9 `Zm00001d045387` candidate intervals.
- Table 1: Eight top regional loci with evidence levels and cautious manuscript claims.
- Supplementary Table 1: 184 manuscript candidate loci.
- Supplementary Table 2: Tier-1 locus-level candidate table.

### References For This Draft

- Li2013_NatGenet: Li et al., 2013, Nature Genetics. https://www.nature.com/articles/ng.2484
- Alrefai1995_Genome: Alrefai et al., 1995, Genome. https://pubmed.ncbi.nlm.nih.gov/18470215/
- Cook2012_PlantPhysiol: Cook et al., 2012, Plant Physiology. https://pmc.ncbi.nlm.nih.gov/articles/PMC3271770/
- Zheng2012_PLoSGenet: Zheng et al., 2012, PLoS Genetics. https://pmc.ncbi.nlm.nih.gov/articles/PMC3172307/
- Khan2022_FrontNutr: Khan et al., 2022, Frontiers in Nutrition. https://pmc.ncbi.nlm.nih.gov/articles/PMC9120846/
- Liu2023_FrontPlantSci: Liu et al., 2023, Frontiers in Plant Science. https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full

## Discussion Outline

### Main Interpretation

The current ZEAMAP v0.1 analysis supports a pragmatic manuscript narrative: robust genotype-based prediction identifies oil traits as the strongest target family, and GEMMA LMM provides a calibrated GWAS framework for candidate-locus discovery in those traits. The chr6 `Zm00001d036982` / linoleic acid1 region is the strongest main-text candidate because it combines multi-trait recurrence, Bonferroni significance, lipid annotation, ridge-attribution overlap and prior fatty-acid/oil evidence. The chr9 C16:0 interval is biologically focused because of the nearby fatty acyl-ACP thioesterase candidate.

### Biological Implications

The top candidates are consistent with a model in which oil-trait variation reflects both direct fatty-acid metabolism and broader regulatory or transport-related processes. Direct lipid/fatty-acid candidates should be emphasized first, while recurrent regulatory or transport candidates should be framed as hypotheses for follow-up.

### Methodological Implications

The contrast between covariate-only GWAS inflation and GEMMA LMM calibration is central. It shows that population covariates alone were not sufficient in this panel and that mixed-model correction is necessary before making candidate-locus claims.

### Limitations

The v0.1 dataset is still small relative to the SNP feature space. Methylation coverage is incomplete, and expression files currently available for this project are reference/tissue expression rather than accession-level AMP expression. Candidate loci have not been fine-mapped or experimentally validated. External functional annotation is still a first pass and must be expanded before submission.

### Next Experiments Or Analyses

The strongest next analyses are external database annotation for the eight top regional loci, polishing Figure 1-3, expanding the literature review, and preparing a final manuscript version with full references and software versions. Experimental validation, allele-specific tests or independent population replication would be required to move from candidate loci to causal claims.

## Methods

### Data Acquisition And Accession Harmonization

ZEAMAP processed public data were downloaded from CNGBdb project CNP0001565. We focused on accession-level genotype, population, phenotype and metabolome tables. Sample identifiers were inspected across tables and harmonized to a unified accession index. Accessions were retained for the v0.1 dataset when they had genotype, population covariates and at least one phenotype or metabolome measurement. The resulting v0.1 dataset contained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric phenotype/metabolome traits. DNA methylation coverage was tracked as a modality mask for 236 accessions but was not used as a default main-model input.

### Prediction Benchmark

We evaluated accession-level genotype-to-phenotype prediction using train/validation/test splits and repeated multi-seed benchmarking. Genotype features were combined with population covariates where indicated. The main comparison included genotype+population ridge regression, genotype+population ElasticNet, population-only ridge regression and a small multilayer perceptron. Traits were first screened for predictability and then retained as robust traits when performance was stable across seeds. The final benchmark used 66 robust traits and selected genotype+population ridge regression as the primary model because it provided stable test performance and avoided the overfitting observed for the small neural network.

### Methylation Ablation

Methylation was assessed through global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection. Because methylation coverage was available for only 236 accessions and raw sparse methylation features were unstable, methylation was retained as an auxiliary ablation and interpretation modality rather than as a default input to the v0.1 primary model.

### Oil-Trait GWAS

Ten high-priority oil-related traits were selected for association analysis based on the final prediction benchmark. A covariate-only GWAS was first run with PC1-PC3 and K1-K3 covariates to diagnose inflation. Because this model showed severe genomic inflation, the main GWAS used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Association testing used GEMMA likelihood-ratio p-values (`p_lrt`). For each oil trait, 440 non-missing accessions and 199,856 SNPs were tested. Bonferroni and Benjamini-Hochberg FDR thresholds were calculated per trait.

### Candidate-Locus Annotation

GEMMA lead SNPs were clumped into physical loci by trait and chromosome. Candidate genes were assigned using B73 RefGen_v4 gene models, including gene-body, promoter and cis-window relationships. Gene descriptions and biotypes were parsed from the local Ensembl/Gramene GFF3 file. Candidate loci were classified by significance level, ridge-attribution overlap and functional keyword classes. Nominal-only loci were excluded from manuscript-facing candidate-locus tables.

### Top-Locus Prioritization And Evidence Levels

Manuscript candidate loci were ranked using GEMMA significance class, association strength, recurrence across oil traits, ridge-attribution overlap, lipid/fatty-acid keyword support and candidate-gene count. This priority score was used only for manuscript triage and was not treated as a new statistical test. Eight regional loci were selected for regional visualization and evidence curation. Evidence levels were assigned conservatively according to whether the locus had direct prior oil/fatty-acid support, indirect lipid-related annotation, recurrent statistical support or only statistical evidence.

### Regional Association Figures

Regional association figures were drawn for top loci using GEMMA p-values within a fixed local window around the lead SNP. SNPs were coloured by LD r2 to the lead SNP, computed from standardized genotype dosages in the v0.1 dataset. Gene tracks were drawn from B73 RefGen_v4 gene models, with labels restricted to local candidate genes and lipid-related genes to avoid over-annotation. Figures were exported as PDF, SVG and high-resolution PNG with Nature-style double-column sizing and Type-42 font settings.

### Claim Boundary

All reported loci are interpreted as candidate loci or candidate genes. The current analysis does not perform fine-mapping, experimental validation, transgenic tests or biochemical assays. Therefore, no lead SNP is described as causal and no candidate gene is described as experimentally validated by this study.

## Figure Captions

### Figure 1. ZEAMAP v0.1 dataset construction and prediction benchmark.

a, Overview of the ZEAMAP processed-data workflow used to construct the accession-level v0.1 benchmark and downstream oil-trait GWAS. b, Scale of the v0.1 dataset, including 461 strongly paired accessions, 236 accessions with methylation coverage, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. c, Median test performance of candidate prediction models across 66 robust traits. Genotype+population ridge and ElasticNet models outperformed the population-only baseline, whereas the small multilayer perceptron showed poorer R2 under the current sample size. d, Trait-family performance of the final genotype+population ridge benchmark. Oil-related traits showed the strongest median Pearson correlation and R2, motivating focused GEMMA mixed-linear-model GWAS for oil traits.

### Figure 2. GEMMA mixed-linear-model GWAS calibration and candidate-locus summary.

a, Comparison of genomic inflation between the diagnostic covariate-only GWAS and GEMMA LMM across 10 high-priority oil traits. b, Per-trait GEMMA LMM association summary, including Bonferroni and FDR-significant signals. c, Manuscript candidate-locus classes after merging GEMMA lead SNPs and excluding nominal-only loci. d, Functional and prediction-attribution support among manuscript candidate loci. GEMMA LMM controlled genomic inflation near lambda GC = 1 and produced a manuscript candidate-locus set for downstream annotation.

### Figure 3. Prioritized regional candidate intervals for maize oil traits.

a, Regional association plot for the chr6 `Zm00001d036982` / linoleic acid1 candidate interval. Points show GEMMA LMM association strength for local SNPs and are coloured by LD r2 to the lead SNP. The region was recurrent across seven oil traits and represents the strongest prioritized candidate interval. b, Regional association plot for the chr9 C16:0-associated interval containing nearby `Zm00001d045387`, annotated as fatty acyl-ACP thioesterase2. This region is highlighted as a biologically focused fatty-acid composition candidate interval. In both panels, gene tracks show B73 RefGen_v4 local gene models; loci are interpreted as candidate intervals rather than fine-mapped causal variants.

## Table Captions

### Table 1. Prioritized regional candidate loci for maize oil traits.

Eight top regional loci selected from GEMMA LMM manuscript candidate loci. Columns report the lead trait, lead SNP, genomic interval, best association P value, priority tier, recurrence across oil traits, ridge-attribution support, curated evidence level, primary candidate gene, recommended manuscript claim and claim boundary. Evidence levels are used for conservative manuscript triage and do not represent experimental validation.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv`

### Supplementary Table 1. Manuscript candidate loci from oil-trait GEMMA LMM GWAS.

Full manuscript-facing candidate-locus table after excluding nominal-only loci. Loci were derived from GEMMA LMM lead SNPs across 10 high-priority oil traits and annotated with B73 RefGen_v4 candidate genes, significance class, ridge-attribution overlap, functional keyword class, recurrence across traits and priority tier.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv`

### Supplementary Table 2. Tier-1 main-text candidate loci.

Subset of manuscript candidate loci assigned to the tier-1 main-text priority class. This table is intended to support main-text candidate-locus interpretation and figure selection. Candidate genes are reported as hypotheses, not experimentally validated causal genes.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv`

### Supplementary Table 3. Literature and database sources used for first-pass candidate-locus triage.

Curated source table used to support first-pass evidence labels for prioritized regional loci. This is not a systematic literature review and should be expanded before journal submission.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`

## Data Availability Draft

The analysis used publicly available ZEAMAP processed data from CNGBdb project CNP0001565. Local processed derivatives, scripts, summary tables and manuscript-facing figures are organized in the `yumi` project repository. Large raw or intermediate association files are not committed to GitHub and remain in the local analysis workspace.

## Code Availability Draft

All project scripts used to build the v0.1 dataset, run prediction benchmarks, perform GEMMA summary processing, annotate candidate loci, generate figures and assemble manuscript tables are stored under `scripts/` in the project repository. The current manuscript skeleton was assembled by `scripts/build_zeamap_v0_1_stage5_8_manuscript_skeleton.py`.

## Acknowledgements Placeholder

To be completed.

## Author Contributions Placeholder

To be completed.

## Competing Interests Placeholder

The authors declare no competing interests. This statement should be confirmed before submission.

## References Placeholder

Initial literature/source records are stored in `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`. These entries must be converted into final journal-formatted references before submission.
