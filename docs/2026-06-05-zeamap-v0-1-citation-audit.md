# ZEAMAP v0.1 Citation Audit

日期：2026-06-05

## Audit Status

This is a first-pass citation audit for the manuscript skeleton. It checks whether each current source supports the claim assigned to it and whether the source is ready for final bibliography formatting.

## Source-Level Audit

| Citation ID | Current Use | Status | Risk | Action |
|---|---|---|---|---|
| Li2013_NatGenet | Prior maize oil GWAS; oil concentration and fatty-acid composition loci | usable but needs final bibliographic details | medium | Convert to final reference format and verify exact title/authors/DOI |
| Alrefai1995_Genome | chr6 linoleic acid1-region QTL for 18:1/18:2 ratio | usable for chr6 prior | medium | Verify exact wording from abstract/full text if accessible |
| Cook2012_PlantPhysiol | DGAT1-2/NAM kernel composition context | usable as broader oil-composition context | low-medium | Keep as context, not as proof for `Zm00001d036982` |
| Zheng2012_PLoSGenet | QTL-Pal9 / Zmfatb / palmitic-acid candidate | strong for chr9 C16:0 prior | low | Use directly for chr9 FatB/acyl-ACP thioesterase interval |
| Khan2022_FrontNutr | fatb allelic variation and fatty-acid composition | usable support for chr9 fatty-acid biology | low-medium | Use as additional context, not primary mapping evidence |
| Liu2023_FrontPlantSci | recent maize oil QTL/candidate gene context | usable context | medium | Verify exact article scope and avoid overreliance |

## Claims That Are Currently Well Supported

- Maize oil traits have prior GWAS/QTL evidence.
- Mixed-model correction is necessary when population structure/relatedness are strong.
- chr9 palmitic-acid/FatB/acyl-ACP thioesterase biology is a plausible prior for a C16:0 candidate interval.
- The current study should use candidate-locus rather than causal-variant language.

## Claims That Need More Citation Support

- ZEAMAP resource description and data origin.
- Maize kernel oil biological importance.
- Why ridge/regularized models are appropriate for small-n high-dimensional genotype prediction.
- Why GEMMA LMM is standard for structured panels.
- Functional annotation details for all 8 top candidate regions.
- Journal-specific statement on data/code availability expectations.

## Citation Boundary Corrections Already Applied

- The chr6 `Zm00001d036982` region is now described as local B73 RefGen_v4 `linoleic acid1` annotation plus broader maize oil/fatty-acid prior.
- DGAT1-2 is not treated as the same gene as `Zm00001d036982` in the manuscript claim.
- chr9 `Zm00001d045387` is described as a nearby fatty acyl-ACP thioesterase candidate, not as a validated causal gene.

## Required Next Citation Work

1. Fetch final bibliographic metadata for all six current sources.
2. Add primary ZEAMAP database/publication citation.
3. Add GEMMA method citation.
4. Add genomic prediction/ridge baseline citation if needed.
5. Add B73 RefGen_v4 / Ensembl Plants / Gramene annotation citation.
6. Add maize oil biology review or seed oil metabolism citation.
7. Add MaizeGDB/UniProt/Gramene citations when external annotation is completed.

## Current Verdict

The current citation set is sufficient for an internal manuscript skeleton, but not sufficient for submission. Before journal submission, the manuscript needs a full citation audit with exact reference metadata and claim-by-claim alignment.
