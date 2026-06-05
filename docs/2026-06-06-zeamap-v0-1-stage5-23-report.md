# ZEAMAP v0.1 Stage 5.23 Report: Bibliography And Gene-Model Verification

日期：2026-06-06

## Verdict

`BIBLIOGRAPHY_AND_LOCAL_GENE_MAPPING_READY_WITH_STYLE_AND_DATABASE_FINAL_CHECK`

## Summary

- Crossref DOI records queried: 17
- Verified DOI metadata rows: 17
- URL/no-standard-DOI rows: 1
- Not verified rows: 0
- Metadata mismatch rows: 0
- Stale/corrected reference issues documented: 3
- Blocking stale issues if left in final references: 2
- Local RefGen_v4 gene mapping rows checked: 3
- Local gene mapping rows passing: 3

## Interpretation

Stage 5.23 closes the biggest bibliography risk found after Stage 5.22. The previous Alrefai DOI `10.1139/g95-108` resolves to an unrelated Brassica erratum, so the final reference list now uses `10.1139/g95-118` for the maize fatty-acid QTL paper. The previous Khan/FatB draft DOI `10.3389/fnut.2022.906530` did not resolve in Crossref during this audit; the chr9 FatB support now uses Katral et al. 2022, DOI `10.3389/fnut.2022.845255`, matching the Stage 5.21 source ledger.

The local B73 RefGen_v4 mapping supports the manuscript's bounded language: chr6 `Zm00001d036982` is the strongest recurrent fatty-acid candidate interval, and chr9 has a lead SNP in/at `Zm00001d045383` with nearby `Zm00001d045387` fatty acyl-ACP thioesterase2 annotation. This supports candidate-interval wording only; it does not establish a causal gene or allele.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-23-reference-crossref-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-23-stale-reference-corrections.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-23-gene-model-mapping-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-23-ars-integrity-review.md`
- `docs/2026-06-06-zeamap-v0-1-reference-list-draft.md`

## Remaining Risk

Target-journal bibliography style, author initials, final issue formatting and MaizeGDB/Gramene cross-database RefGen_v4-to-v5 gene-name mapping still need a final human-facing submission pass. This is a style/database finalization risk, not a current claim-language blocker.
