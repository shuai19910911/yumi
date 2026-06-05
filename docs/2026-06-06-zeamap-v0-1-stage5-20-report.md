# ZEAMAP v0.1 Stage 5.20 Report: GWAS Diagnostic Appendix

日期：2026-06-06

## Verdict

`GWAS_DIAGNOSTIC_APPENDIX_READY`

## Summary

- Oil traits checked: 10
- Diagnostic-ready traits: 10/10
- Lambda GC range: 0.984-1.018
- P-value column: `p_lrt`
- Bonferroni threshold: 0.05 / 199,856 = 2.502e-07
- Suggestive threshold used for candidate-locus triage: 1.0e-05

## Interpretation

All 10 oil-trait GEMMA LMM scans have lambda GC within the pre-specified well-controlled range of 0.95-1.05, use the likelihood-ratio p-value column and have matching QQ/Manhattan plot files. This directly addresses the Stage 5.18 statistical genetics reviewer risk.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-20-gwas-diagnostic-appendix.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-20-gwas-diagnostic-summary.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-20-methods-gwas-diagnostic-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-20-ars-statistical-review.md`

## Remaining Risk

The diagnostic appendix supports calibrated association testing, but it does not replace independent validation or fine-mapping. The manuscript should continue to use candidate-interval language.
