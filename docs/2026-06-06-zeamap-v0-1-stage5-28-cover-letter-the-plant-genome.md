# Cover Letter Draft: The Plant Genome Route

日期：2026-06-06

Dear Editor,

We are pleased to submit the manuscript entitled "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP" for consideration as a research article in *The Plant Genome*.

This manuscript presents a reproducible accession-level reanalysis of public ZEAMAP processed data focused on maize kernel oil and fatty-acid traits. We constructed a conservative v0.1 benchmark containing 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified oil-related traits as the most robustly predictable trait family under a genotype+population ridge model.

We then used prediction as a triage step for focused oil-trait association mapping. A diagnostic covariate-only GWAS showed strong genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC near one across 10 high-priority oil traits. We annotated candidate intervals using B73 RefGen_v4 gene models, MaizeGDB B73v4-to-B73v5 cross-references, Ensembl/Gramene xrefs, prediction-attribution overlap and targeted fatty-acid literature. The strongest intervals include a recurrent chromosome 6 lipid acyltransferase/DGAT-like candidate interval and a chromosome 9 C16:0 interval with a nearby acyl-ACP hydrolase/palmitoyl-ACP thioesterase candidate.

The paper is intentionally conservative. We do not claim causal variants, causal alleles or experimentally validated genes. Instead, we provide a transparent benchmark, calibrated mixed-model GWAS results, current-ID annotation evidence and prioritized candidate intervals for follow-up maize oil-trait genetics.

We believe the manuscript will interest readers of *The Plant Genome* because it combines public crop-genomics resource reuse, genotype-to-phenotype prediction, mixed-model GWAS calibration and candidate-locus prioritization for seed-quality traits. The repository includes scripts, manuscript-facing summary tables, reproducibility documentation and figure outputs. Large raw inputs and large intermediate matrices are not committed to GitHub, but their public sources and regeneration paths are documented.

The corresponding author should confirm before submission that the manuscript is original, is not under consideration elsewhere, has been approved by all authors and has complete funding, acknowledgements and competing-interest statements.

Sincerely,

[Corresponding author name]
