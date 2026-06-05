# ZEAMAP v0.1 Figure Captions Draft

日期：2026-06-05

## Figure 1. ZEAMAP v0.1 dataset construction and prediction benchmark.

a, Overview of the ZEAMAP processed-data workflow used to construct the accession-level v0.1 benchmark and downstream oil-trait GWAS. b, Scale of the v0.1 dataset, including 461 strongly paired accessions, 236 accessions with methylation coverage, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. c, Median test performance of candidate prediction models across 66 robust traits. Genotype+population ridge and ElasticNet models outperformed the population-only baseline, whereas the small multilayer perceptron showed poorer R2 under the current sample size. d, Trait-family performance of the final genotype+population ridge benchmark. Oil-related traits showed the strongest median Pearson correlation and R2, motivating focused GEMMA mixed-linear-model GWAS for oil traits.

## Figure 2. GEMMA mixed-linear-model GWAS calibration and candidate-locus summary.

a, Comparison of genomic inflation between the diagnostic covariate-only GWAS and GEMMA LMM across 10 high-priority oil traits. b, Per-trait GEMMA LMM association summary, including Bonferroni and FDR-significant signals. c, Manuscript candidate-locus classes after merging GEMMA lead SNPs and excluding nominal-only loci. d, Functional and prediction-attribution support among manuscript candidate loci. GEMMA LMM controlled genomic inflation near lambda GC = 1 and produced a manuscript candidate-locus set for downstream annotation.

## Figure 3. Prioritized regional candidate intervals for maize oil traits.

a, Regional association plot for the chr6 `Zm00001d036982` / linoleic acid1 candidate interval. Points show GEMMA LMM association strength for local SNPs and are coloured by LD r2 to the lead SNP. The region was recurrent across seven oil traits and represents the strongest prioritized candidate interval. b, Regional association plot for the chr9 C16:0-associated interval containing nearby `Zm00001d045387`, annotated as fatty acyl-ACP thioesterase2. This region is highlighted as a biologically focused fatty-acid composition candidate interval. In both panels, gene tracks show B73 RefGen_v4 local gene models; loci are interpreted as candidate intervals rather than fine-mapped causal variants.
