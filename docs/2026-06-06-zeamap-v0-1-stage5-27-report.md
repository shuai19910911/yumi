# ZEAMAP v0.1 Stage 5.27 External Gene-Name Confirmation Report

日期：2026-06-06

## Verdict

`EXTERNAL_GENE_NAME_EVIDENCE_COLLECTED_WITH_BOUNDED_CLAIMS`

## What this stage confirmed

- MaizeGDB B73v4-to-B73v5 cross-reference gives one current B73 v5 gene ID for each of the three target RefGen_v4 genes.
- chr6 `Zm00001d036982` maps to `Zm00001eb277490`; Ensembl xrefs include DGAT/O-acyltransferase/triglyceride/lipid-process evidence.
- chr9 lead-host `Zm00001d045383` maps to `Zm00001eb377300`; xrefs support a DXS/isoprenoid-related protein-coding gene, so it should not be renamed as FatB.
- chr9 nearby `Zm00001d045387` maps to `Zm00001eb377350`; xrefs include acyl-ACP hydrolase, palmitoyl-ACP thioesterase and fatty-acid biosynthesis evidence.

## Final submission gate status

- pass/human_required/fail: 3/4/0
- External gene-name confirmation is now machine-pass with source evidence.
- Remaining blockers are author-only: figure approval, author metadata, funding/acknowledgements/COI and repository release PID.

## Source URLs

- MaizeGDB B73v4-to-B73v5 xref: https://download.maizegdb.org/Pan-genes/B73_gene_xref/B73v4_to_B73v5.tsv
- Ensembl REST lookup/xrefs were queried for `Zm00001eb277490`, `Zm00001eb377300` and `Zm00001eb377350`.

## Claim boundary

This closes the external gene-name evidence gap, but it does not create causal evidence. The manuscript should continue to say chr6 is the strongest recurrent fatty-acid candidate interval and chr9 is a C16:0 interval with a nearby fatty-acid thioesterase candidate. It should not claim a causal gene, causal allele or experimental validation.

## Evidence files

- `docs/2026-06-06-zeamap-v0-1-stage5-27-external-gene-name-confirmation.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-27-ensembl-xref-functional-evidence.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-27-final-submission-gate.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-27-gene-name-hardened-manuscript.md`
