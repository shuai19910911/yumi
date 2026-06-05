# Repository Release And Data DOI Plan

日期：2026-06-06

## Current Repository

GitHub remote:

```text
git@github.com:shuai19910911/yumi.git
```

Current manuscript package is tracked through staged Git commits. Before journal submission, create a stable public release or archive.

## Recommended Release Steps

1. Ensure the repository is public or accessible to reviewers.
2. Add a release tag such as `zeamap-oil-v0.1-submission`.
3. Archive the release in Zenodo or Figshare if the target journal requires a persistent DOI.
4. Record the release DOI in the Data/Code Availability statement.
5. Keep large raw files outside GitHub; document public ZEAMAP source URLs and local regeneration scripts.

## Minimum Release Contents

- `README.md`
- `docs/progress-plan.md`
- target-journal manuscript draft
- reference DOI audit
- data/code availability statement
- figure quality audit
- manuscript-facing tables
- candidate-locus annotation tables
- scripts used to generate current manuscript package

## Not To Release In GitHub

- raw VCF/matrix files too large for GitHub,
- raw SRA/FASTQ,
- large intermediate GEMMA association outputs unless compressed and explicitly needed,
- private author notes or conflict-of-interest files.
