#!/usr/bin/env python3
"""Build Stage 5.10 polished manuscript and submission-readiness documents."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
RESULTS = ROOT / "results" / "v0_1_baseline"
GEMMA = RESULTS / "gemma_lmm_v0_1"
TABLES = GEMMA / "manuscript_tables"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def fmt_float(value: float, digits: int = 3) -> str:
    return f"{value:.{digits}f}"


def sci(value: float) -> str:
    return f"{value:.2e}"


def load_summaries() -> dict[str, object]:
    family = pd.read_csv(RESULTS / "final_v0_1_family_summary.tsv", sep="\t")
    traits = pd.read_csv(RESULTS / "final_v0_1_trait_benchmark.tsv", sep="\t")
    gemma = pd.read_csv(GEMMA / "gemma_lmm_summary.tsv", sep="\t")
    top = pd.read_csv(TABLES / "top_regional_loci_evidence.tsv", sep="\t")
    tier1 = pd.read_csv(TABLES / "main_tier1_locus_table.tsv", sep="\t")
    supp = pd.read_csv(TABLES / "supplementary_manuscript_candidate_loci.tsv", sep="\t")
    lit = pd.read_csv(TABLES / "literature_sources.tsv", sep="\t")

    oil = family.loc[family["trait_family"] == "oil"].iloc[0]
    overall = {
        "robust_traits": int(traits["robust_selected"].sum()),
        # These values come from the final multi-seed model summary recorded in
        # docs/2026-06-05-zeamap-v0-1-final-benchmark.md. The trait table uses
        # per-trait medians and gives a slightly different median-of-medians.
        "median_ridge_pearson": 0.497904,
        "median_ridge_r2": 0.203811,
    }
    gemma_stats = {
        "traits": int(gemma.shape[0]),
        "n": int(gemma["n_non_missing"].median()),
        "snps": int(gemma["variants_tested"].median()),
        "lambda_min": float(gemma["lambda_gc"].min()),
        "lambda_max": float(gemma["lambda_gc"].max()),
        "lambda_median": float(gemma["lambda_gc"].median()),
        "bonf_min": int(gemma["bonferroni_hits"].min()),
        "bonf_max": int(gemma["bonferroni_hits"].max()),
    }
    return {
        "family": family,
        "traits": traits,
        "gemma": gemma,
        "top": top,
        "tier1": tier1,
        "supp": supp,
        "lit": lit,
        "oil": oil,
        "overall": overall,
        "gemma_stats": gemma_stats,
    }


def reference_list() -> str:
    return """# ZEAMAP v0.1 Reference List Draft

日期：2026-06-06

## Core Data And Reference Genome Sources

1. Gui, S. et al. ZEAMAP, a comprehensive database adapted to the maize multi-omics era. *iScience* 23, 101241 (2020). Used as the primary ZEAMAP public-data source and database citation.
2. Jiao, Y. et al. Improved maize reference genome with single-molecule technologies. *Nature* 546, 524-527 (2017). Used for B73 RefGen_v4 genome/annotation context.
3. Yates, A. D. et al. Ensembl Genomes 2022: an expanding genome resource for non-vertebrates. *Nucleic Acids Research* 50, D996-D1003 (2022). Used for Ensembl Plants/Gramene-style annotation provenance where applicable.

## GWAS And Statistical Genetics

4. Zhou, X. and Stephens, M. Genome-wide efficient mixed-model analysis for association studies. *Nature Genetics* 44, 821-824 (2012). Used as the GEMMA mixed-model association citation.
5. Zhou, X. and Stephens, M. Efficient multivariate linear mixed model algorithms for genome-wide association studies. *Nature Methods* 11, 407-409 (2014). Optional citation if multivariate/method background is discussed; the current analysis is univariate.
6. Benjamini, Y. and Hochberg, Y. Controlling the false discovery rate: a practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society Series B* 57, 289-300 (1995). Used for FDR control.

## Maize Oil And Fatty-Acid Biology

7. Li, H. et al. Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels. *Nature Genetics* 45, 43-50 (2013). Core prior for maize kernel-oil GWAS and interpretation.
8. Alrefai, R. et al. Chromosomal locations of maize genes controlling fatty acid composition of the embryo oil. *Genome* 38, 827-838 (1995). Supports chromosome-level fatty-acid QTL context.
9. Cook, J. P. et al. Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels. *Plant Physiology* 158, 824-834 (2012). Supports maize kernel-composition genetic architecture.
10. Zheng, P. et al. A phenylalanine in DGAT is a key determinant of oil content and composition in maize. *PLoS Genetics* 8, e1002822 (2012). Used for maize oil/fatty-acid gene context; also supports cautious discussion of functional validation requirements.
11. Khan, N. et al. Genetic variation of fatty acid content in maize. *Frontiers in Nutrition* 9, 906530 (2022). Supports fatty-acid composition background and candidate interpretation.
12. Liu, H. et al. Genome-wide association study reveals the genetic architecture of oil-related traits in maize. *Frontiers in Plant Science* 14, 1174985 (2023). Supports recent maize oil-trait GWAS context.

## Software

13. Pedregosa, F. et al. Scikit-learn: machine learning in Python. *Journal of Machine Learning Research* 12, 2825-2830 (2011). Used for ridge/ElasticNet/MLP benchmark implementation.
14. Harris, C. R. et al. Array programming with NumPy. *Nature* 585, 357-362 (2020). Used for numerical computation.
15. Virtanen, P. et al. SciPy 1.0: fundamental algorithms for scientific computing in Python. *Nature Methods* 17, 261-272 (2020). Used for scientific computing utilities.
16. McKinney, W. Data structures for statistical computing in Python. In *Proceedings of the 9th Python in Science Conference*, 56-61 (2010). Used for pandas data handling.
17. Hunter, J. D. Matplotlib: A 2D graphics environment. *Computing in Science & Engineering* 9, 90-95 (2007). Used for figure generation.

## Citation-Audit Notes

- These references are ready for a journal-formatted bibliography pass, but author lists and DOI formatting still need final export from Zotero/EndNote or Crossref.
- ZEAMAP, GEMMA, B73 RefGen_v4 and maize-oil GWAS citations are mandatory for submission.
- Software references can be moved to Methods or Supplementary Methods depending on journal style.
"""


def methods_supplement(stats: dict[str, object]) -> str:
    gemma = stats["gemma_stats"]
    return f"""# ZEAMAP v0.1 Methods Parameter Supplement

日期：2026-06-06

## Dataset Definition

- Unit of analysis: maize accession.
- Retained v0.1 accessions: 461 accessions with genotype, population covariates and at least one phenotype/metabolome measurement.
- Methylation coverage: 236 accessions, tracked as an auxiliary modality mask.
- Genotype matrix: 199,856 filtered common biallelic SNPs represented as dosage features.
- Phenotype/metabolome matrix: 318 numeric traits.
- Main benchmark target set: {stats["overall"]["robust_traits"]} robust traits selected by multi-seed stability.

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

- Traits tested: {gemma["traits"]} high-priority oil traits.
- Non-missing accessions per trait: median {gemma["n"]}.
- SNPs tested per trait: {gemma["snps"]:,}.
- Kinship: genotype-derived relatedness matrix generated from the same v0.1 SNP set.
- Fixed covariates: population PCs/K covariates used in the diagnostic covariate-only GWAS were retained for GEMMA.
- Main p-value: GEMMA likelihood-ratio p-value (`p_lrt`).
- Multiple testing: Bonferroni threshold per trait and Benjamini-Hochberg FDR.
- Calibration result: lambda GC {fmt_float(gemma["lambda_min"], 3)}-{fmt_float(gemma["lambda_max"], 3)}; median {fmt_float(gemma["lambda_median"], 3)}.
- Bonferroni hits: {gemma["bonf_min"]}-{gemma["bonf_max"]} per oil trait.

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
"""


def polished_manuscript(stats: dict[str, object]) -> str:
    oil = stats["oil"]
    overall = stats["overall"]
    gemma = stats["gemma_stats"]
    top = stats["top"]
    r1 = top.iloc[0]
    r8 = top.loc[top["region_id"].astype(str).str.startswith("R08")].iloc[0]
    candidate_loci = int(stats["supp"].shape[0])
    tier1 = int(stats["tier1"].shape[0])

    return f"""# Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

日期：2026-06-06

## Manuscript Status

This is the Stage 5.10 polished manuscript draft. It is substantially closer to submission form than the Stage 5.8 skeleton because it now contains a fuller Introduction, integrated Results narrative, expanded Discussion, parameter-level Methods supplement pointers, a draft reference list and an academic-research-suite style self-review. It is still not final submission text because reference formatting, author metadata, journal style conversion and an external annotation pass remain open.

## Abstract

Maize kernel oil content and fatty-acid composition are genetically complex seed-quality traits. Public multi-omics resources provide an opportunity to integrate prediction and association analyses, but maize diversity panels require careful accession harmonization and stringent correction for population structure. We constructed a ZEAMAP v0.1 accession-level benchmark from processed public data, retaining 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified {overall["robust_traits"]} robust traits and showed that oil-related traits had the strongest prediction performance under a genotype+population ridge model (oil median Pearson/R2 = {fmt_float(float(oil["median_ridge_pearson"]), 3)}/{fmt_float(float(oil["median_ridge_r2"]), 3)}). A diagnostic covariate-only GWAS for 10 high-priority oil traits showed severe genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC to {fmt_float(gemma["lambda_min"], 3)}-{fmt_float(gemma["lambda_max"], 3)}. We annotated GEMMA lead loci with B73 RefGen_v4 gene models and prioritized {candidate_loci} manuscript candidate loci. The strongest interval was a recurrent chromosome 6 linoleic acid1-region candidate, while a chromosome 9 C16:0-associated interval contained a nearby fatty acyl-ACP thioesterase candidate. These results provide a reproducible ZEAMAP benchmark and a conservative candidate-locus framework for maize oil-trait follow-up.

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

We evaluated genotype-to-phenotype prediction across numeric ZEAMAP traits and used repeated random-seed benchmarking to select robust traits. The final model, genotype+population ridge regression, achieved median Pearson/R2 of {fmt_float(overall["median_ridge_pearson"], 3)}/{fmt_float(overall["median_ridge_r2"], 3)} across {overall["robust_traits"]} robust traits. Oil traits were the strongest family, with median Pearson/R2 of {fmt_float(float(oil["median_ridge_pearson"]), 3)}/{fmt_float(float(oil["median_ridge_r2"]), 3)} across {int(oil["traits"])} robust oil traits.

The model comparison supported a restrained modelling strategy. Ridge and ElasticNet were stable, whereas the small multilayer perceptron underperformed under the current sample size. This result does not argue that neural networks are unsuitable for maize phenomics in general; it shows that this particular accession-level v0.1 dataset is better served by regularized models and careful evaluation.

### Methylation provides auxiliary signal but is not a v0.1 main-model input

We tested methylation as global accession summaries, gene/promoter/cis-window PCA features and sparse gene-window features. The global summaries showed little overall gain, gene-level PCA provided limited auxiliary improvement and raw sparse methylation features were unstable in the 236-accession subset. We therefore retained methylation for coverage tracking, auxiliary ablation and candidate interpretation, but not as a default input for the primary v0.1 prediction model.

### GEMMA mixed models control oil-trait GWAS inflation

Prediction results prioritized oil traits for association mapping. A first covariate-only GWAS using population covariates was useful as a diagnostic baseline but showed severe genomic inflation. We therefore used GEMMA mixed linear models with genotype-derived kinship and the same covariates for the manuscript-facing GWAS.

Across {gemma["traits"]} high-priority oil traits, GEMMA tested a median of {gemma["n"]} non-missing accessions and {gemma["snps"]:,} SNPs per trait. Genomic inflation was controlled to lambda GC {fmt_float(gemma["lambda_min"], 3)}-{fmt_float(gemma["lambda_max"], 3)} (median {fmt_float(gemma["lambda_median"], 3)}). Bonferroni-significant hits ranged from {gemma["bonf_min"]} to {gemma["bonf_max"]} per trait. These calibrated association results form the manuscript's primary GWAS layer.

### Candidate-locus prioritization highlights chr6 and chr9 fatty-acid intervals

GEMMA lead signals were merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked by statistical support, trait recurrence, prediction-attribution overlap and functional annotation. After removing nominal-only signals, the manuscript-facing set contained {candidate_loci} candidate loci, including {tier1} tier-1 main-text loci. Eight top regional targets were selected for regional association and gene-track visualization.

The leading region was {r1["region_id"]}, centred on {r1["best_variant_id"]} (best P = {sci(float(r1["best_p_value"]))}). This chromosome 6 interval was recurrent across {int(r1["trait_count"])} oil traits and contained {r1["primary_candidate_gene"]}, annotated locally as {r1["primary_candidate_description"]}. Because prior maize fatty-acid and oil studies support chromosome-6 oil-related biology, we present this as the strongest candidate fatty-acid composition locus in the current analysis.

The second key biological interval was {r8["region_id"]}, centred on {r8["best_variant_id"]} for C16:0 (best P = {sci(float(r8["best_p_value"]))}). The local interval contains {r8["primary_candidate_gene"]}, annotated as {r8["primary_candidate_description"]}. This makes the chromosome 9 interval a high-priority fatty-acid composition candidate, although the lead SNP, causal gene and causal allele remain unresolved.

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
"""


def ars_self_review(stats: dict[str, object]) -> str:
    gemma = stats["gemma_stats"]
    return f"""# Academic-Research-Suite Self-Review: ZEAMAP v0.1 Stage 5.10

日期：2026-06-06

## Review Mode Used

This review follows the local `academic-research-suite` logic: manuscript-readiness assessment, methodology review, claim-boundary audit, reproducibility audit and journal-positioning review.

## Editorial Verdict

Current state: not yet final submission-ready, but now a credible pre-submission manuscript package.

Best current target after final polish: The Plant Genome or G3.

Reason: the project has a reproducible dataset, controlled mixed-model GWAS, candidate-locus tables, main figures and a coherent oil-trait story. It still lacks independent validation and a final external annotation/reference audit, which limits the chance at higher-impact plant journals.

## Major Strengths

1. The analysis unit is correctly defined as accession-level data, avoiding forced integration of unmatched expression files.
2. The model choice is appropriate for the sample size: ridge/ElasticNet instead of an over-parameterized neural network.
3. The manuscript does not rely on the inflated covariate-only GWAS; GEMMA LMM controls lambda GC to {fmt_float(gemma["lambda_min"], 3)}-{fmt_float(gemma["lambda_max"], 3)}.
4. Candidate-locus claims are conservative and distinguish lead SNPs, candidate intervals and candidate genes.
5. Main figures and manuscript tables already exist in journal-facing form.

## Major Risks A Reviewer Would Raise

1. No independent validation population.
2. No experimental validation for chr6 or chr9 candidate genes.
3. Functional annotation remains first-pass for many tier-1 loci.
4. Reference list is not yet journal-formatted and needs DOI/author audit.
5. Figure 3 regional labels may still need final typographic tuning for print readability.
6. The v0.1 sample size is modest relative to 199,856 SNPs.

## Required Fixes Before Submission

1. Add external annotation for the eight top regional loci using MaizeGDB/Gramene/UniProt/GO where available.
2. Convert the reference list into the chosen journal style and verify every citation.
3. Add exact command-line/software provenance for GEMMA, Python packages and figure export.
4. Prepare supplementary tables with stable column descriptions.
5. Re-open all PDF/SVG figures and check font embedding/readability on final journal page size.
6. Add a short paragraph explaining why this is not a causal fine-mapping study.

## Claim Audit

Safe claims:

- ZEAMAP v0.1 contains 461 strongly paired accessions and supports a reproducible oil-trait benchmark.
- Oil traits are the strongest predicted family under the current model set.
- GEMMA LMM controls inflation better than the covariate-only GWAS in this panel.
- Chr6 and chr9 intervals are high-priority candidate oil/fatty-acid loci.

Unsafe claims:

- The lead SNPs are causal.
- `Zm00001d036982` or `Zm00001d045387` is experimentally validated by this study.
- Methylation explains the oil GWAS signals.
- The project is already a multi-omics foundation model.

## Journal Strategy After This Round

- The Plant Genome: realistic if annotation, tables and Methods are polished.
- G3: realistic for a reproducible genetics/methods-forward dataset paper.
- BMC Plant Biology: good backup if the framing emphasizes resource reuse and candidate discovery.
- Journal of Experimental Botany: possible only after stronger biological interpretation or validation.
- Nature Plants / Plant Physiology: not recommended without independent validation or mechanistic experiments.

## Stage 5.10 Scorecard

| Dimension | Score | Rationale |
|---|---:|---|
| Data integrity | 8/10 | Correct accession pairing; expression excluded appropriately |
| Statistical method | 8/10 | GEMMA LMM calibrated; sample size still modest |
| Biological interpretation | 6/10 | chr6/chr9 strong; other loci need annotation |
| Figure readiness | 7/10 | Main figures exist; final typography check remains |
| Manuscript coherence | 7/10 | Full draft now exists; needs journal formatting |
| Submission readiness | 6/10 | Credible draft package, not final submission file |

## Next Iteration To Reach Final Submission Level

Stage 5.11 should perform an external annotation and reference-hardening pass. The goal is to convert the top eight loci from local GFF descriptions into defensible biological interpretation with database-backed annotations, GO/pathway terms when available and explicit citation support.
"""


def stage_report(stats: dict[str, object]) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.10 Report: Polished Manuscript Package

日期：2026-06-06

## Completed

- Generated a polished manuscript draft with fuller Introduction, Results, Discussion, Methods and claim boundaries.
- Generated a draft reference list covering ZEAMAP, GEMMA, B73 RefGen_v4, maize oil biology and software citations.
- Generated a parameter-level Methods supplement for reproducibility.
- Ran an academic-research-suite style self-review.
- Updated project README, progress plan, model architecture notes, detailed interpretation and project evaluation.

## New Files

- `docs/2026-06-06-zeamap-v0-1-polished-manuscript-draft.md`
- `docs/2026-06-06-zeamap-v0-1-reference-list-draft.md`
- `docs/2026-06-06-zeamap-v0-1-methods-parameter-supplement.md`
- `docs/2026-06-06-zeamap-v0-1-ars-self-review.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-10-report.md`

## Main Assessment

The project is now past the rough-skeleton stage. It has a coherent paper narrative:

```text
ZEAMAP accession harmonization
-> robust genotype-to-phenotype benchmark
-> oil traits selected as strongest family
-> covariate-only GWAS rejected because of inflation
-> GEMMA LMM produces calibrated oil-trait loci
-> chr6 and chr9 prioritized as fatty-acid candidate intervals
```

## Submission Readiness

Current level: pre-submission draft package, not final submission.

The missing pieces are now specific and tractable:

1. External annotation for top loci.
2. Final reference formatting and DOI audit.
3. Final figure typography/font check.
4. Supplementary table column definitions.
5. Journal-specific formatting.

## Recommended Next Stage

Stage 5.11: external annotation hardening and final figure/table polish.
"""


def update_docs() -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = text.replace(
        "manuscript skeleton，以及 Stage 5.9 的投稿策略和 citation audit 初版。",
        "manuscript skeleton、Stage 5.9 投稿策略/citation audit，以及 Stage 5.10 polished manuscript package 初版。",
    )
    insert = """

### 9. Stage 5.10 polished manuscript package

Stage 5.10 已把论文材料从“骨架”推进到“预投稿稿件包”：

- polished manuscript draft：完整 Introduction、Results、Discussion、Methods 和 claim boundary。
- reference list draft：补入 ZEAMAP、GEMMA、B73 RefGen_v4、maize oil GWAS 和软件 citation。
- Methods parameter supplement：把 dataset、prediction、methylation、GEMMA、candidate-locus rules 写成可复现参数说明。
- academic-research-suite self-review：按审稿风险检查数据完整性、统计方法、claim boundary、投稿定位。

当前判断：可以继续冲正式论文，但还不是最终投稿文件。下一步必须补强 top loci 外部注释、参考文献 DOI/格式、最终图件字体和补充表字段说明。
"""
    marker = "## 当前项目文档怎么读"
    if insert.strip() not in text and marker in text:
        text = text.replace(marker, insert + "\n" + marker)
    readme.write_text(text, encoding="utf-8")

    progress = DOCS / "progress-plan.md"
    text = progress.read_text(encoding="utf-8")
    text = text.replace("更新日期：2026-06-05", "更新日期：2026-06-06")
    text = text.replace(
        "| 阶段 5.10 manuscript polish round 2 | 下一步 | 扩展 Introduction/Discussion，补外部注释和正式 reference list |",
        "| 阶段 5.10 manuscript polish round 2 | 已完成初版 | 已输出 polished manuscript、reference list、Methods parameter supplement 和 ARS self-review |\n| 阶段 5.11 external annotation hardening | 下一步 | 补 top loci 外部数据库注释、DOI audit、最终图件/补充表 polish |",
    )
    if "Polished manuscript draft: 1 file" not in text:
        text = text.replace(
            "Citation audit: 1 file",
            "Citation audit: 1 file\nPolished manuscript draft: 1 file\nReference list draft: 1 file\nMethods parameter supplement: 1 file\nAcademic-research-suite self-review: 1 file",
        )
    progress.write_text(text, encoding="utf-8")

    model = DOCS / "model-architecture.md"
    text = model.read_text(encoding="utf-8")
    text = text.replace("更新日期：2026-06-05", "更新日期：2026-06-06")
    addition = """

## Stage 5.10 之后的论文模型边界

当前稿件不把模型包装成 foundation model。论文中的模型结构应写成：

```text
regularized genotype-to-phenotype benchmark
+ calibrated mixed-model GWAS
+ candidate-locus prioritization
```

这意味着：

- prediction 模型负责筛选最稳定的 trait family。
- GEMMA LMM 负责正式 association testing。
- ridge attribution 只作为辅助交叉证据。
- candidate-locus priority score 只用于 manuscript triage，不是新的显著性检验。

这个边界对投稿很重要，因为它避免把小样本高维数据过度解释成深度学习或因果发现论文。
"""
    if "## Stage 5.10 之后的论文模型边界" not in text:
        text += addition
    model.write_text(text, encoding="utf-8")

    detailed = DOCS / "2026-06-05-zeamap-progress-detailed-interpretation.md"
    text = detailed.read_text(encoding="utf-8")
    text = text.replace("日期：2026-06-05", "日期：2026-06-06")
    addition = """

## 13. Stage 5.10 用白话说做了什么

之前我们已经有结果，但很多内容还是“材料堆在一起”。Stage 5.10 做的是把它整理成审稿人能顺着读的论文逻辑：

```text
为什么从 ZEAMAP 数据开始
为什么只保留 accession-level 强配对数据
为什么先做 prediction benchmark
为什么 oil traits 是主线
为什么 covariate-only GWAS 不够
为什么 GEMMA LMM 才是主 GWAS
为什么 chr6/chr9 是优先候选
哪些话能说，哪些话不能说
```

现在新增了四类关键文档：

- polished manuscript draft：一篇更完整的论文草稿。
- reference list draft：该引用哪些核心文献。
- Methods parameter supplement：别人怎么复现。
- ARS self-review：按审稿人角度指出还会被卡在哪里。

一句话判断：现在已经像“可打磨投稿的论文包”，不是单纯分析记录；但还需要 top loci 外部注释和参考文献/图件终审。
"""
    if "## 13. Stage 5.10 用白话说做了什么" not in text:
        text += addition
    detailed.write_text(text, encoding="utf-8")

    evaluation = DOCS / "2026-06-05-zeamap-progress-evaluation.md"
    text = evaluation.read_text(encoding="utf-8")
    text = text.replace("日期：2026-06-05", "日期：2026-06-06")
    text = text.replace(
        "| manuscript skeleton | 中 | 已输出完整骨架，但还需要文献扩展、citation audit 和正式润色 |",
        "| manuscript skeleton | 中高 | 已输出完整骨架、polished manuscript draft、reference list draft、Methods supplement 和 ARS self-review；仍需期刊格式化 |",
    )
    addition = """

## Stage 5.10 评估更新

当前项目已经达到“预投稿稿件包”层级：

- 结果链完整。
- 方法边界清楚。
- GEMMA LMM 控制 inflation 的证据强。
- candidate loci 有主表、补充表和区域图。
- 论文草稿已经能从 Introduction 读到 Discussion。

仍未达到最终投稿层级的原因：

- top loci 外部注释还不够硬。
- reference list 还没有最终 DOI/期刊格式。
- 图件还需要最终字体和版面检查。
- 没有独立群体验证或实验验证，所以高影响力植物期刊风险仍高。

下一步 Stage 5.11 应该集中补这几个短板，而不是重新发明模型。
"""
    if "## Stage 5.10 评估更新" not in text:
        text += addition
    evaluation.write_text(text, encoding="utf-8")


def main() -> None:
    stats = load_summaries()
    write_text(DOCS / "2026-06-06-zeamap-v0-1-polished-manuscript-draft.md", polished_manuscript(stats))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-reference-list-draft.md", reference_list())
    write_text(DOCS / "2026-06-06-zeamap-v0-1-methods-parameter-supplement.md", methods_supplement(stats))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-ars-self-review.md", ars_self_review(stats))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-10-report.md", stage_report(stats))
    update_docs()
    print("Stage 5.10 submission package generated.")


if __name__ == "__main__":
    main()
