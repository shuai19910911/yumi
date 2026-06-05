# ZEAMAP v0.1 Stage 5.19 Report: Result-To-Script Reproducibility Crosswalk

日期：2026-06-06

## Verdict

`REPRODUCIBILITY_CROSSWALK_READY`

## Summary

- Crosswalk rows: 21
- Reviewer-ready rows: 21/21
- Inventory paths checked: 74
- Missing paths: 0
- Existing but not Git-tracked paths: 5

## Interpretation

This stage turns the manuscript's main claims into a reviewer-facing provenance map. Each row links one claim/result to a generating script or source document, primary inputs, primary outputs, key parameter decisions and the reviewer risk it addresses.

The crosswalk is not a substitute for rerunning every analysis. It is a submission-support artifact: reviewers and coauthors can see where each number, figure and table comes from, and which large local inputs are intentionally outside GitHub.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-methods-reproducibility-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-ars-reproducibility-review.md`

## Remaining Risk

Some existing paths point to local processed matrices or large outputs that are not intended for GitHub release. Before final submission, the release package should state which files are public-source inputs, which files are committed derivatives and which large files must be regenerated locally from ZEAMAP.
