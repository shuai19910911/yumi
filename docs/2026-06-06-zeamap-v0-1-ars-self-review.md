# Academic-Research-Suite Self-Review: ZEAMAP v0.1 Stage 5.10

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
3. The manuscript does not rely on the inflated covariate-only GWAS; GEMMA LMM controls lambda GC to 0.984-1.018.
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
