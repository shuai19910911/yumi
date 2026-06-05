# ZEAMAP v0.1 Results Draft: Prediction-Guided Oil-Trait GWAS

日期：2026-06-05

## Genotype-based prediction prioritizes oil-related traits

After harmonizing ZEAMAP accessions across genotype, population and phenotype/metabolome tables, we constructed a v0.1 accession-level dataset containing 461 accessions, 199,856 common biallelic SNPs and 318 numeric traits. Multi-seed benchmarking identified 66 robust traits, among which oil-related traits showed the strongest prediction signal. The final `genotype_population_ridge` model achieved a median Pearson correlation of 0.498 and median R2 of 0.204 across robust traits, with the oil family reaching a median Pearson/R2 of 0.596/0.321. These results motivated a focused downstream GWAS analysis of high-priority oil traits rather than immediate expansion to a high-capacity deep model.

## Mixed linear modelling controls oil-trait GWAS inflation

A covariate-only GWAS using PC1-PC3 and K1-K3 showed severe genomic inflation (lambda GC 2.41-3.97), indicating that population covariates alone were insufficient for association testing in this maize panel. We therefore used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Across 10 high-priority oil traits, GEMMA reduced lambda GC to 0.984-1.018 (median 0.998), supporting these results as the main GWAS baseline. Lead SNPs were then merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked for manuscript interpretation.

## Prioritized oil-trait loci

The GEMMA candidate-locus layer contained 184 manuscript candidate loci after removing nominal-only signals. We ranked these loci using GEMMA significance, association strength, recurrence across oil traits, ridge-attribution overlap and lipid/fatty-acid annotations. This yielded 18 tier-1 main-text loci and 22 tier-2 strong loci. Eight representative regional association figures were generated to show local association peaks, LD to the lead SNP and nearby gene models.

The strongest region was chr6 Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). This region was recurrent across 7 oil traits and included a local gene annotated as linoleic acid1 in local B73 RefGen_v4 annotation. Prior maize studies reported chromosome 6 linoleic-acid/oil-related QTL evidence and broader maize oil GWAS support for lipid-metabolism loci. We therefore treat this chr6 interval as the leading candidate fatty-acid composition locus, while maintaining the conservative interpretation that the lead SNP marks a candidate interval rather than a proven causal variant.

The chr9 C16:0-associated region around chr9.s_20246143 (best P = 7.76e-17) is also biologically notable. Although it is not recurrent across multiple oil traits, the interval contains Zm00001d045387, annotated as fatty acyl-ACP thioesterase2 near the lead region. Previous maize studies mapped palmitic-acid variation to FatB/acyl-ACP thioesterase biology on chromosome 9, making this a high-priority candidate interval for fatty-acid composition follow-up.

Other recurrent tier-1 regions on chromosomes 4, 1 and 8 were strongly supported statistically and by ridge-attribution overlap, but their current annotations are regulatory, transport-related or broad protein-family descriptions rather than direct oil-biosynthetic genes. These loci should be presented as recurrent candidate regions and prioritized for external database annotation and experimental follow-up.

## Candidate-claim boundaries

All loci in the current manuscript table should be described as candidate loci or candidate genes. The current analysis does not perform fine-mapping, allele-specific validation or transgenic/biochemical experiments. Therefore, no lead SNP should be described as causal, and no candidate gene should be described as experimentally validated by this study.

## Draft Figure And Table Calls

- Figure 1: v0.1 dataset construction and prediction benchmark summary.
- Figure 2: GEMMA LMM GWAS calibration and candidate-locus summary.
- Figure 3: Regional association panels for chr6 `Zm00001d036982` and chr9 `Zm00001d045387` candidate intervals.
- Table 1: Eight top regional loci with evidence levels and cautious manuscript claims.
- Supplementary Table 1: 184 manuscript candidate loci.
- Supplementary Table 2: Tier-1 locus-level candidate table.

## References For This Draft

- Li2013_NatGenet: Li et al., 2013, Nature Genetics. https://www.nature.com/articles/ng.2484
- Alrefai1995_Genome: Alrefai et al., 1995, Genome. https://pubmed.ncbi.nlm.nih.gov/18470215/
- Cook2012_PlantPhysiol: Cook et al., 2012, Plant Physiology. https://pmc.ncbi.nlm.nih.gov/articles/PMC3271770/
- Zheng2012_PLoSGenet: Zheng et al., 2012, PLoS Genetics. https://pmc.ncbi.nlm.nih.gov/articles/PMC3172307/
- Khan2022_FrontNutr: Khan et al., 2022, Frontiers in Nutrition. https://pmc.ncbi.nlm.nih.gov/articles/PMC9120846/
- Liu2023_FrontPlantSci: Liu et al., 2023, Frontiers in Plant Science. https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full
