# ZEAMAP v0.1 Methods Software Versions

日期：2026-06-05

## Runtime Environment

Primary conda/mamba environment:

```text
yumi
```

Python stack checked on 2026-06-05:

```text
python      3.10.20
pandas      2.3.3
numpy       2.2.6
scipy       1.15.2
scikit-learn 1.7.2
matplotlib  3.10.9
```

GEMMA:

```text
GEMMA 0.98.5 (2021-08-25)
```

## Methods Text To Add Later

Suggested software sentence:

```text
Analyses were performed in Python 3.10.20 using pandas 2.3.3, NumPy 2.2.6, SciPy 1.15.2, scikit-learn 1.7.2 and matplotlib 3.10.9. Mixed-linear-model GWAS was performed with GEMMA 0.98.5 using likelihood-ratio test P values.
```

## Known Environment Notes

- `pdffonts` is not installed on the current login node, so PDF font embedding could not be independently audited here.
- Figure scripts set `pdf.fonttype = 42` and `ps.fonttype = 42` before export.
- `gemma` is available through the `yumi` mamba environment, not the default login-shell PATH.

## Still Needed

- Exact command lines for final Methods supplement.
- Full package list export from `mamba env export -n yumi` if required by the target journal.
- Version information for any command-line tools used during the earlier raw preprocessing steps.
