# ZEAMAP v0.1 Stage 5.6 manuscript tables and Results draft

日期：2026-06-05

## Purpose

Stage 5.6 converts the Stage 5.5 top-locus ranking into manuscript-facing outputs: a top regional-locus table, tier-1 locus table, supplementary candidate-locus table, curated evidence table and a first Results draft.

## Outputs

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`
- `docs/2026-06-05-zeamap-v0-1-results-draft.md`

## Counts

- Top regional loci: 8
- Tier-1 locus rows: 18
- Supplementary manuscript candidate loci: 184
- Literature/source records: 6

## Evidence Level Counts

```text
C_indirect_regulatory_candidate           2
A_direct_prior_lipid_locus                1
C_indirect_recurrent_candidate            1
C_indirect_transport_candidate            1
D_statistical_candidate                   1
B_lipid_related_indirect                  1
A_direct_fatty_acid_candidate_interval    1
```

## Main Interpretation

- `R01_Zm00001d036982` is the strongest candidate interval because it combines recurrence across seven oil traits, Bonferroni significance, lipid annotation, ridge-attribution support and prior chromosome-6 fatty-acid/oil literature.
- `R08_Zm00001d045383` is a high-priority C16:0 interval because the local region includes `Zm00001d045387`, annotated as fatty acyl-ACP thioesterase2, and prior maize work links FatB/acyl-ACP thioesterase biology to palmitic acid.
- Regions R02-R07 remain useful manuscript candidates, but most should be written as recurrent/statistical or indirect regulatory/transport/lipid-related candidates until stronger external annotation or validation is available.

## Claim Boundary

The current evidence supports candidate loci and candidate genes. It does not prove causal variants, fine-mapped credible sets or experimentally validated genes.
