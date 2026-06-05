# Target-Journal Manuscript Assembly Draft

日期：2026-06-06

Target route: The Plant Genome first-line formatting, with G3 as a close alternative.

## Title Page

Title: Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

Running title: ZEAMAP oil-trait prediction and GWAS

Authors: To be completed.

Affiliations: To be completed.

Corresponding author: To be completed.

## Core Ideas

- A ZEAMAP v0.1 accession-level benchmark was built from correctly paired processed public data.
- Oil traits were the most robustly predictable trait family under genotype+population ridge regression.
- GEMMA mixed linear models controlled oil-trait GWAS inflation that persisted under covariate-only testing.
- Chr6 linoleic acid1-region and chr9 fatty acyl-ACP thioesterase intervals are the strongest fatty-acid candidate loci.
- Candidate loci are prioritized conservatively and are not claimed as causal variants or validated genes.

## Abstract

Maize kernel oil content and fatty-acid composition are genetically complex seed-quality traits. Public multi-omics resources provide an opportunity to integrate prediction and association analyses, but maize diversity panels require careful accession harmonization and stringent correction for population structure. We constructed a ZEAMAP v0.1 accession-level benchmark from processed public data, retaining 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified 66 robust traits and showed that oil-related traits had the strongest prediction performance under a genotype+population ridge model (oil median Pearson/R2 = 0.596/0.321). A diagnostic covariate-only GWAS for 10 high-priority oil traits showed severe genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC to 0.984-1.018. We annotated GEMMA lead loci with B73 RefGen_v4 gene models and prioritized 184 manuscript candidate loci. The strongest interval was a recurrent chromosome 6 linoleic acid1-region candidate, while a chromosome 9 C16:0-associated interval contained a nearby fatty acyl-ACP thioesterase candidate. These results provide a reproducible ZEAMAP benchmark and a conservative candidate-locus framework for maize oil-trait follow-up.

## Keywords

maize; ZEAMAP; oil traits; fatty acid composition; genotype-to-phenotype prediction; ridge regression; GEMMA; GWAS; candidate loci

## Main Text Word Count

Approximate main text word count excluding title page, abstract, references and supplementary legends: 1919

## Introduction

Kernel oil content and fatty-acid composition are central maize seed-quality traits. They influence feed value, food quality, industrial uses and the long-term ability to breed maize germplasm with tailored biochemical profiles. These traits are also attractive for genetics because several components of fatty-acid metabolism are biologically interpretable, yet the observed quantitative variation is distributed across population structure, relatedness, local linkage disequilibrium and many candidate regulatory loci.

The availability of ZEAMAP processed data creates an opportunity to revisit maize oil-trait genetics through a reproducible accession-level workflow (Gui et al., 2020). However, a public multi-table resource cannot be treated as a ready-made machine-learning matrix. Sample identifiers must be reconciled, partially paired modalities must be separated from fully paired accessions and expression or epigenomic files must not be forced into accession-level models when the biological unit does not match. We therefore designed the first version of this project as a conservative v0.1 benchmark rather than as a high-capacity multi-omics foundation model.

This conservative choice is important for statistical reasons. The retained v0.1 dataset contains 461 accessions and nearly 200,000 SNPs, creating a high-dimensional prediction problem. DNA methylation coverage is available for only 236 accessions, and the expression files currently available in this project describe reference/tissue expression rather than accession-level AMP expression. Under this sample scale, complex neural networks are more likely to overfit than to provide interpretable biological insight. Regularized linear models, population baselines and multi-seed trait screening are therefore a stronger first manuscript route.

We used prediction as a triage step rather than as an endpoint. Genotype-to-phenotype benchmarking identified oil-related traits as the most robustly predictable family. This result motivated focused GWAS on 10 high-priority oil traits. Because maize diversity panels are strongly structured, we explicitly compared a diagnostic covariate-only GWAS with a mixed linear model. The diagnostic model showed inflation, whereas GEMMA mixed-model association controlled genomic inflation near one. Finally, we annotated GEMMA lead loci with B73 RefGen_v4 gene models and non-vertebrate genome-resource provenance (Jiao et al., 2017; Yates et al., 2022), integrated prediction-attribution overlap and ranked candidate regions with explicit claim boundaries.

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

Prediction results prioritized oil traits for association mapping. A first covariate-only GWAS using population covariates was useful as a diagnostic baseline but showed severe genomic inflation. We therefore used GEMMA mixed linear models with genotype-derived kinship and the same covariates for the manuscript-facing GWAS (Zhou and Stephens, 2012; Zhou and Stephens, 2014).

Across 10 high-priority oil traits, GEMMA tested 440 non-missing accessions and 199,856 SNPs per trait. Genomic inflation was controlled to lambda GC 0.984-1.018 (median 0.998), and the likelihood-ratio p-value column (`p_lrt`) was used consistently for manuscript-facing summaries. The Bonferroni threshold was 0.05/199,856 = 2.502e-07, while p <= 1.0e-05 and Benjamini-Hochberg false-discovery summaries were used only for candidate-locus triage and supplementary ranking (Benjamini and Hochberg, 1995). Bonferroni-significant hits ranged from 1 to 21 per trait, and trait-level QQ/Manhattan plot paths and top lead SNPs are listed in the GWAS diagnostic appendix. These calibrated association results form the manuscript's primary GWAS layer, but they do not prove causal variants or validated genes.

### Candidate-locus prioritization highlights chr6 and chr9 fatty-acid intervals

GEMMA lead signals were merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked by statistical support, trait recurrence, prediction-attribution overlap and functional annotation. After removing nominal-only signals, the manuscript-facing set contained 184 candidate loci, including 18 tier-1 main-text loci. Eight top regional targets were selected for regional association and gene-track visualization.

The leading region was R01_Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). This chromosome 6 interval was recurrent across 7 oil traits and contained Zm00001d036982, annotated locally as linoleic acid1 in B73 RefGen_v4. Targeted literature support links maize fatty-acid and kernel-oil biology to historical fatty-acid QTLs, kernel-composition association studies, maize oil GWAS and DGAT/linoleic-acid pathways (Alrefai et al., 1995; Cook et al., 2012; Li et al., 2013; Zheng et al., 2008; Zhang et al., 2023), so we present the chr6 signal as the strongest recurrent fatty-acid candidate interval in the current analysis, not as a validated causal gene.

The second key biological interval was R08_Zm00001d045383, centred on chr9.s_20246143 for C16:0 (best P = 7.76e-17). The local interval contains or lies near Zm00001d045387, annotated as fatty acyl-ACP thioesterase2 near the lead region. Maize Zmfatb/FatB literature and general FATB pathway biology support this as a high-priority C16:0 fatty-acid candidate interval (Katral et al., 2022; Bonaventure et al., 2003), while the lead SNP, exact causal gene and causal allele remain unresolved.

Other recurrent tier-1 loci on chromosomes 1, 4 and 8 showed strong statistical and ridge-attribution support but currently carry broader regulatory, transport or protein-family annotations. These regions should be reported as recurrent candidate intervals rather than as mechanistically resolved oil genes.

## Discussion

This study establishes a practical route from a public maize multi-table resource to a manuscript-facing oil-trait genetics analysis. The main contribution is not a new large model. Instead, it is a conservative accession-level benchmark, a clear demonstration that oil traits are the strongest predictable trait family in the current ZEAMAP v0.1 matrix and a calibrated GEMMA LMM GWAS layer that avoids the inflation observed with simpler covariate-only testing.

The prediction results are biologically useful because they prioritize where downstream genetic analysis is most likely to be productive. Oil traits showed stronger and more stable predictability than the median trait, suggesting that the genotype and population features in the v0.1 matrix capture meaningful genetic signal for seed oil and fatty-acid composition. This does not mean the model explains all oil-trait variance, but it provides a defensible basis for focusing GWAS and candidate annotation on oil traits.

The contrast between covariate-only GWAS and GEMMA is central to the paper. Without mixed-model correction, the oil-trait GWAS layer showed substantial inflation. With genotype-derived kinship, GEMMA controlled lambda GC near one across all tested oil traits. This result should be presented prominently because it protects the paper from a common criticism of diversity-panel GWAS: that top hits may reflect residual population structure rather than trait-associated loci.

The candidate-locus results should be interpreted in tiers. The chromosome 6 linoleic acid1-region locus is the strongest main-text candidate because it combines extreme statistical significance, recurrence across oil traits, lipid-related local annotation, ridge-attribution support and prior maize fatty-acid/oil evidence. The chromosome 9 C16:0 interval is biologically compelling for a different reason: it is trait-specific and contains or lies near fatty acyl-ACP thioesterase annotation, a pathway class directly relevant to saturated fatty-acid composition. The two intervals should therefore be described with different levels of specificity: chr6 as the strongest recurrent fatty-acid candidate interval and chr9 as a high-priority C16:0/FatB-like candidate interval. Recurrent regions with MYB, transport or broad protein-family annotations are valuable but should remain hypothesis-generating until external annotation or experimental evidence is stronger.

Several limitations remain. First, the v0.1 dataset is small relative to the SNP feature space. Second, methylation is only partially paired and therefore cannot support a strong multi-omics claim in the main model. Third, candidate loci have not been fine-mapped or experimentally validated. Fourth, target-journal reference styling and external gene-name mapping still need a final author-side check before journal submission. These limitations do not invalidate the current manuscript route, but they define the claim boundary: the study prioritizes candidate intervals and reproducible benchmarks; it does not prove causal variants or experimentally validate genes.

For submission, the strongest journal positioning is a methods-aware plant genomics paper: a ZEAMAP oil-trait prediction benchmark linked to calibrated mixed-model GWAS and candidate-locus prioritization. The Plant Genome, G3 and BMC Plant Biology remain realistic first-line targets after final annotation and figure polishing. A higher-impact plant journal would require added independent validation, functional assays, a stronger external annotation layer or a broader multi-population replication analysis.

## Materials And Methods

### Data acquisition and accession harmonization

ZEAMAP processed public data were downloaded from CNGBdb project CNP0001565 (Gui et al., 2020). We focused on accession-level genotype, population, phenotype and metabolome tables. Sample identifiers were inspected across tables and harmonized to a unified accession index. Accessions were retained for the v0.1 dataset when they had genotype, population covariates and at least one phenotype or metabolome measurement. The resulting dataset contained 461 strongly paired accessions, 199,856 filtered common biallelic SNPs and 318 numeric traits.

### Prediction benchmark

We evaluated genotype-to-phenotype prediction using repeated train/validation/test evaluation. Candidate models included genotype+population ridge regression, genotype+population ElasticNet, population-only ridge regression and a small multilayer perceptron. Traits were retained for final reporting only when performance was stable across seeds. The main model was genotype+population ridge regression because it provided stable test performance under high-dimensional SNP features and limited sample size.

### Methylation ablation

Methylation was tested as global summaries, gene/promoter/cis-window PCA features and sparse gene-window feature selection. Because methylation coverage was available for only 236 accessions and sparse methylation features were unstable, methylation was retained as an auxiliary modality rather than as a default v0.1 input.

### GWAS and candidate-locus annotation

Ten high-priority oil traits were selected from the final benchmark for association analysis. A covariate-only GWAS was used as a diagnostic inflation check. The main GWAS used GEMMA mixed linear models with genotype-derived kinship and population covariates (Zhou and Stephens, 2012). GEMMA likelihood-ratio p-values were used for association summaries. Lead signals were merged into physical loci, annotated with B73 RefGen_v4 gene models and ranked for manuscript interpretation (Jiao et al., 2017; Yates et al., 2022). Candidate genes were interpreted as hypotheses unless supported by independent functional evidence.

### Figure generation

Analyses and figures were implemented with Python scientific-computing and visualization libraries (Pedregosa et al., 2011; Harris et al., 2020; Virtanen et al., 2020; McKinney, 2010; Hunter, 2007). Main and regional figures were generated as PDF, SVG and high-resolution PNG outputs with Nature-style double-column sizing. Regional panels show local association strength, LD to the lead SNP and B73 RefGen_v4 gene tracks. Gene labels were restricted to candidate genes and lipid-related genes to avoid over-annotation.

## Data Availability Statement

The study used publicly available ZEAMAP processed data from CNGBdb project CNP0001565. The analysis repository contains scripts, documentation, manuscript-facing summary tables and generated figures. Large raw inputs and large intermediate matrices are not committed to GitHub; their public source and local processing paths are documented in the repository. To support reproducibility, each main result, figure and manuscript-facing table was mapped to its generating script, primary inputs, primary outputs and key parameter decisions. The result-to-script crosswalk is provided in `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`, with a file-level inventory in `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`. Processed derivative tables needed to reproduce the manuscript figures and candidate-locus summaries are listed in Supplementary Table metadata and in `docs/2026-06-06-zeamap-v0-1-methods-parameter-supplement.md`.

## Code Availability Statement

All project scripts used for dataset construction, prediction benchmarking, methylation ablation, GEMMA summary processing, candidate-locus annotation, figure generation and manuscript assembly are available in the project repository under `scripts/`. The Stage 5.12 manuscript assembly was generated by `scripts/build_zeamap_v0_1_stage5_12_final_assembly.py`; the Stage 5.22 integrated manuscript and claim-language audit were generated by `scripts/build_zeamap_v0_1_stage5_22_integrated_manuscript_claim_audit.py`; the Stage 5.23 bibliography/gene-model verification and Stage 5.24 citation-integrated manuscript were generated by `scripts/build_zeamap_v0_1_stage5_23_bibliography_gene_model_verification.py` and `scripts/build_zeamap_v0_1_stage5_24_citation_integrated_manuscript.py`.

## Author Contributions

To be completed before submission. At minimum, specify contributions for conceptualization, data curation, formal analysis, software, visualization, writing-original draft and writing-review/editing.

## Funding

To be completed.

## Acknowledgements

To be completed.

## Competing Interests

The authors declare no competing interests. This statement must be confirmed by all authors before submission.

## Ethics Statement

No human or animal subjects were used. The study reanalyzes public plant genomics data.

## Figure Legends

Figure 1. ZEAMAP v0.1 dataset construction and prediction benchmark. The figure summarizes accession harmonization, v0.1 dataset scale, model comparison and trait-family performance. Oil-related traits showed the strongest median prediction performance and motivated focused oil-trait GWAS.

Figure 2. GEMMA mixed-linear-model GWAS calibration and candidate-locus summary. The figure contrasts inflated covariate-only GWAS results with GEMMA LMM calibration and summarizes candidate-locus classes after manuscript-facing filtering.

Figure 3. Prioritized regional candidate intervals for maize oil traits. Regional association and gene-track panels highlight the chr6 linoleic acid1-region candidate interval and the chr9 C16:0 fatty acyl-ACP thioesterase candidate interval. Both are interpreted as candidate intervals, not causal fine-mapped loci.

## Table Legends

Table 1. Prioritized regional candidate loci for maize oil traits. Eight top loci selected from GEMMA LMM manuscript candidate loci and annotated with recurrence, statistical support, prediction-attribution overlap, functional evidence and claim boundaries.

Supplementary Table 1. Manuscript candidate loci from oil-trait GEMMA LMM GWAS. Full manuscript-facing candidate-locus table after excluding nominal-only loci.

Supplementary Table 2. Tier-1 main-text candidate loci. Candidate loci assigned to the tier-1 priority class for main-text interpretation.

Supplementary Table 3. External annotation hardening for top regional loci. Stage 5.11 table adding external annotation class, support summary, database terms to verify, literature support and remaining risk.

Supplementary Table 4. Supplementary table column dictionary. Column-level definitions for manuscript-facing tables.

## References

1. Gui et al. ZEAMAP, a comprehensive database adapted to the maize multi-omics era. iScience 23, 101241 (2020). DOI: `10.1016/j.isci.2020.101241`.
2. Jiao et al. Improved maize reference genome with single-molecule technologies. Nature 546, 524-527 (2017). DOI: `10.1038/nature22971`.
3. Yates et al. Ensembl Genomes 2022: an expanding genome resource for non-vertebrates. Nucleic Acids Research 50, D996-D1003 (2022). DOI: `10.1093/nar/gkab1007`.
4. Zhou et al. Genome-wide efficient mixed-model analysis for association studies. Nature Genetics 44, 821-824 (2012). DOI: `10.1038/ng.2310`.
5. Zhou et al. Efficient multivariate linear mixed model algorithms for genome-wide association studies. Nature Methods 11, 407-409 (2014). DOI: `10.1038/nmeth.2848`.
6. Benjamini et al. Controlling the false discovery rate: a practical and powerful approach to multiple testing. Journal of the Royal Statistical Society: Series B 57, 289-300 (1995). DOI: `10.1111/j.2517-6161.1995.tb02031.x`.
7. Li et al. Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels. Nature Genetics 45, 43-50 (2013). DOI: `10.1038/ng.2484`.
8. Alrefai et al. Quantitative trait locus analysis of fatty acid concentrations in maize. Genome 38, 894-901 (1995). DOI: `10.1139/g95-118`.
9. Cook et al. Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels. Plant Physiology 158, 824-834 (2012). DOI: `10.1104/pp.111.185033`.
10. Zheng et al. A phenylalanine in DGAT is a key determinant of oil content and composition in maize. Nature Genetics 40, 367-372 (2008). DOI: `10.1038/ng.85`.
11. Katral et al. Allelic variation in Zmfatb gene defines variability for fatty acids composition among diverse maize genotypes. Frontiers in Nutrition 9, 845255 (2022). DOI: `10.3389/fnut.2022.845255`.
12. Zhang et al. Genetic dissection of QTLs for oil content in four maize DH populations. Frontiers in Plant Science 14, 1174985 (2023). DOI: `10.3389/fpls.2023.1174985`.
13. Bonaventure et al. Disruption of the FATB gene in Arabidopsis demonstrates an essential role of saturated fatty acids in plant growth. The Plant Cell 15, 1020-1033 (2003). DOI: `10.1105/tpc.008946`.
14. Pedregosa et al. Scikit-learn: machine learning in Python. Journal of Machine Learning Research 12, 2825-2830 (2011). URL/status: `https://jmlr.org/papers/v12/pedregosa11a.html` / no standard DOI recorded.
15. Harris et al. Array programming with NumPy. Nature 585, 357-362 (2020). DOI: `10.1038/s41586-020-2649-2`.
16. Virtanen et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. Nature Methods 17, 261-272 (2020). DOI: `10.1038/s41592-019-0686-2`.
17. McKinney et al. Data structures for statistical computing in Python. Proceedings of the 9th Python in Science Conference 56-61 (2010). DOI: `10.25080/Majora-92bf1922-00a`.
18. Hunter et al. Matplotlib: A 2D graphics environment. Computing in Science & Engineering 9, 90-95 (2007). DOI: `10.1109/MCSE.2007.55`.
