# Release Execution Commands Draft

日期：2026-06-06

Current checked commit when this draft was generated:

```text
3817c62
```

## Preconditions

Do not execute the release until:

- author list, affiliations, funding and competing interests are finalized;
- final target journal is selected;
- Figure 1-3 have passed manual visual inspection;
- final reference list has been exported in journal style;
- repository visibility has been confirmed.

## Local Tag Commands

```bash
git status --short
git tag -a zeamap-oil-v0.1-submission -m "ZEAMAP maize oil-trait manuscript submission package"
git push origin zeamap-oil-v0.1-submission
```

## GitHub Release Notes Draft

Title:

```text
ZEAMAP maize oil-trait manuscript submission package v0.1
```

Description:

```text
Submission package for "Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP". Includes manuscript-facing documentation, summary tables, candidate-locus annotation, figure outputs and scripts. Large raw ZEAMAP inputs and large intermediate matrices are not included and should be retrieved from the public ZEAMAP/CNGBdb source documented in the repository.
```

## DOI Archive

After creating the GitHub release, archive it with Zenodo or Figshare if required by the target journal. Record the archive DOI in:

- `docs/2026-06-06-zeamap-v0-1-data-code-availability-draft.md`
- final manuscript Data Availability statement
- cover letter, if journal requests repository/DOI detail
