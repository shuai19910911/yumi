#!/usr/bin/env python3
"""Assemble a first manuscript skeleton from Stage 5.6-5.7 materials."""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUT = DOCS / "2026-06-05-zeamap-v0-1-manuscript-skeleton.md"
TABLE_CAPTIONS = DOCS / "2026-06-05-zeamap-v0-1-table-captions-draft.md"
CHECKLIST = DOCS / "2026-06-05-zeamap-v0-1-manuscript-readiness-checklist.md"
REPORT = DOCS / "2026-06-05-zeamap-v0-1-stage5-8-manuscript-skeleton-report.md"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=OUT)
    parser.add_argument("--table-captions", type=Path, default=TABLE_CAPTIONS)
    parser.add_argument("--checklist", type=Path, default=CHECKLIST)
    parser.add_argument("--report", type=Path, default=REPORT)
    return parser.parse_args()


def read_body(path: Path, skip_title: bool = True, heading_offset: int = 0) -> str:
    lines = path.read_text(encoding="utf-8").splitlines()
    if skip_title and lines and lines[0].startswith("# "):
        lines = lines[1:]
    while lines and (not lines[0].strip() or lines[0].startswith("日期：")):
        lines = lines[1:]
    if heading_offset:
        lines = [("#" * heading_offset + line) if line.startswith("#") else line for line in lines]
    return "\n".join(lines).strip()


def write_table_captions(path: Path) -> None:
    text = """# ZEAMAP v0.1 Table Captions Draft

日期：2026-06-05

## Table 1. Prioritized regional candidate loci for maize oil traits.

Eight top regional loci selected from GEMMA LMM manuscript candidate loci. Columns report the lead trait, lead SNP, genomic interval, best association P value, priority tier, recurrence across oil traits, ridge-attribution support, curated evidence level, primary candidate gene, recommended manuscript claim and claim boundary. Evidence levels are used for conservative manuscript triage and do not represent experimental validation.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv`

## Supplementary Table 1. Manuscript candidate loci from oil-trait GEMMA LMM GWAS.

Full manuscript-facing candidate-locus table after excluding nominal-only loci. Loci were derived from GEMMA LMM lead SNPs across 10 high-priority oil traits and annotated with B73 RefGen_v4 candidate genes, significance class, ridge-attribution overlap, functional keyword class, recurrence across traits and priority tier.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv`

## Supplementary Table 2. Tier-1 main-text candidate loci.

Subset of manuscript candidate loci assigned to the tier-1 main-text priority class. This table is intended to support main-text candidate-locus interpretation and figure selection. Candidate genes are reported as hypotheses, not experimentally validated causal genes.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv`

## Supplementary Table 3. Literature and database sources used for first-pass candidate-locus triage.

Curated source table used to support first-pass evidence labels for prioritized regional loci. This is not a systematic literature review and should be expanded before journal submission.

Source file:

- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`
"""
    path.write_text(text, encoding="utf-8")


def write_checklist(path: Path) -> None:
    text = """# ZEAMAP v0.1 Manuscript Readiness Checklist

日期：2026-06-05

## Completed

- v0.1 accession-level processed dataset built.
- Prediction benchmark completed on 66 robust traits.
- Oil traits identified as the strongest trait family.
- Methylation ablation completed; methylation kept auxiliary.
- Covariate-only GWAS diagnosed as inflated.
- GEMMA LMM GWAS completed with lambda GC near 1.
- Candidate loci and candidate genes annotated.
- Top regional loci prioritized.
- Figure 1, Figure 2 and Figure 3 initial manuscript figures available.
- Results draft, Methods draft, figure captions and table captions assembled.

## Required Before Submission

- Expand Introduction with full literature positioning.
- Convert Results skeleton into polished journal prose.
- Expand Methods with exact software versions and parameter values from scripts.
- Add Data Availability and Code Availability details.
- Complete external annotation for the 8 top regional loci using MaizeGDB, UniProt and Gramene.
- Add supplementary figure/table numbering after final journal format is chosen.
- Audit all citations and replace source placeholders with final bibliography entries.
- Verify PDF font embedding on a node with `pdffonts` or equivalent.
- Re-check Figure 1 and Figure 3 sizing after final caption text is fixed.

## Claim Boundaries To Preserve

- Say candidate locus, not causal locus.
- Say candidate gene, not validated causal gene.
- Say association interval, not fine-mapped variant.
- Keep methylation as auxiliary ablation, not a main predictive modality.
- Do not treat B73/SK/HZS/Mo17 reference expression as AMP accession-level expression.
"""
    path.write_text(text, encoding="utf-8")


def write_skeleton(path: Path) -> None:
    results = read_body(DOCS / "2026-06-05-zeamap-v0-1-results-draft.md", heading_offset=1)
    methods = read_body(DOCS / "2026-06-05-zeamap-v0-1-methods-draft.md", heading_offset=1)
    fig_caps = read_body(DOCS / "2026-06-05-zeamap-v0-1-figure-captions-draft.md", heading_offset=1)
    table_caps = read_body(TABLE_CAPTIONS, heading_offset=1)

    text = f"""# Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

日期：2026-06-05

## Manuscript Status

This is a Stage 5.8 manuscript skeleton. It assembles the current Results, Methods, figure captions, table captions and claim boundaries into a single paper-facing document. It is not yet a submission-ready manuscript.

## Working Title

Prediction-guided mixed-model GWAS prioritizes maize oil-trait candidate loci in ZEAMAP

## Abstract Draft

Maize kernel oil traits are genetically complex and strongly shaped by population structure, making prediction and association analyses vulnerable to overfitting and inflated test statistics. We harmonized public ZEAMAP processed data into an accession-level v0.1 benchmark containing 461 strongly paired accessions, 199,856 filtered SNPs and 318 numeric phenotype/metabolome traits. Multi-seed genotype-to-phenotype benchmarking identified 66 robust traits and showed that oil-related traits had the strongest prediction performance under a genotype+population ridge model. A diagnostic covariate-only GWAS for 10 high-priority oil traits showed severe genomic inflation, whereas GEMMA mixed linear models with genotype-derived kinship controlled lambda GC near 1. We annotated GEMMA lead loci using B73 RefGen_v4 gene models, prioritized 184 manuscript candidate loci and generated regional association figures for top candidates. The strongest interval was a recurrent chr6 `Zm00001d036982` / linoleic acid1 candidate region, while a chr9 C16:0-associated interval contained a nearby fatty acyl-ACP thioesterase candidate gene. These results provide a reproducible ZEAMAP benchmark and a conservative candidate-locus framework for maize oil-trait follow-up.

## Keywords

maize; ZEAMAP; oil traits; genotype-to-phenotype prediction; GEMMA; GWAS; fatty acid composition; candidate loci

## Introduction Draft

Maize kernel oil content and fatty-acid composition are important seed-quality traits with direct relevance to nutrition, feed, industrial use and breeding. These traits are influenced by many loci and by the genetic structure of maize diversity panels, making both prediction and association mapping technically challenging. Public ZEAMAP resources provide a valuable foundation for accession-level genotype, population and phenotype integration, but their utility depends on careful sample harmonization and conservative interpretation of partially paired omics modalities.

In this study, we first constructed a ZEAMAP v0.1 accession-level benchmark rather than immediately training a high-capacity multi-omics model. This choice was motivated by the available sample scale: 461 strongly paired accessions for genotype, population and phenotype/metabolome data, but only 236 accessions with methylation coverage and no AMP accession-level expression matrix. We therefore used regularized prediction models and multi-seed trait screening to identify robustly predictable trait families.

Oil traits emerged as the most stable and predictable family, motivating focused oil-trait GWAS. Because maize diversity panels have strong population structure and relatedness, we compared a diagnostic covariate-only GWAS against GEMMA mixed linear models. This design allowed us to separate inflated association signals from kinship-controlled candidate loci. We then mapped GEMMA lead loci to B73 RefGen_v4 candidate genes, integrated prediction-attribution overlap and curated the strongest regional candidates with explicit claim boundaries.

## Results

{results}

## Discussion Outline

### Main Interpretation

The current ZEAMAP v0.1 analysis supports a pragmatic manuscript narrative: robust genotype-based prediction identifies oil traits as the strongest target family, and GEMMA LMM provides a calibrated GWAS framework for candidate-locus discovery in those traits. The chr6 `Zm00001d036982` / linoleic acid1 region is the strongest main-text candidate because it combines multi-trait recurrence, Bonferroni significance, lipid annotation, ridge-attribution overlap and prior fatty-acid/oil evidence. The chr9 C16:0 interval is biologically focused because of the nearby fatty acyl-ACP thioesterase candidate.

### Biological Implications

The top candidates are consistent with a model in which oil-trait variation reflects both direct fatty-acid metabolism and broader regulatory or transport-related processes. Direct lipid/fatty-acid candidates should be emphasized first, while recurrent regulatory or transport candidates should be framed as hypotheses for follow-up.

### Methodological Implications

The contrast between covariate-only GWAS inflation and GEMMA LMM calibration is central. It shows that population covariates alone were not sufficient in this panel and that mixed-model correction is necessary before making candidate-locus claims.

### Limitations

The v0.1 dataset is still small relative to the SNP feature space. Methylation coverage is incomplete, and expression files currently available for this project are reference/tissue expression rather than accession-level AMP expression. Candidate loci have not been fine-mapped or experimentally validated. External functional annotation is still a first pass and must be expanded before submission.

### Next Experiments Or Analyses

The strongest next analyses are external database annotation for the eight top regional loci, polishing Figure 1-3, expanding the literature review, and preparing a final manuscript version with full references and software versions. Experimental validation, allele-specific tests or independent population replication would be required to move from candidate loci to causal claims.

## Methods

{methods}

## Figure Captions

{fig_caps}

## Table Captions

{table_caps}

## Data Availability Draft

The analysis used publicly available ZEAMAP processed data from CNGBdb project CNP0001565. Local processed derivatives, scripts, summary tables and manuscript-facing figures are organized in the `yumi` project repository. Large raw or intermediate association files are not committed to GitHub and remain in the local analysis workspace.

## Code Availability Draft

All project scripts used to build the v0.1 dataset, run prediction benchmarks, perform GEMMA summary processing, annotate candidate loci, generate figures and assemble manuscript tables are stored under `scripts/` in the project repository. The current manuscript skeleton was assembled by `scripts/build_zeamap_v0_1_stage5_8_manuscript_skeleton.py`.

## Acknowledgements Placeholder

To be completed.

## Author Contributions Placeholder

To be completed.

## Competing Interests Placeholder

The authors declare no competing interests. This statement should be confirmed before submission.

## References Placeholder

Initial literature/source records are stored in `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`. These entries must be converted into final journal-formatted references before submission.
"""
    path.write_text(text, encoding="utf-8")


def write_report(path: Path) -> None:
    text = """# ZEAMAP v0.1 Stage 5.8 manuscript skeleton report

日期：2026-06-05

## Purpose

Stage 5.8 assembled the current manuscript-facing materials into a single skeleton document.

## Outputs

- `docs/2026-06-05-zeamap-v0-1-manuscript-skeleton.md`
- `docs/2026-06-05-zeamap-v0-1-table-captions-draft.md`
- `docs/2026-06-05-zeamap-v0-1-manuscript-readiness-checklist.md`
- `scripts/build_zeamap_v0_1_stage5_8_manuscript_skeleton.py`

## Status

The project now has a first manuscript skeleton containing working title, abstract draft, keywords, introduction draft, Results, Discussion outline, Methods, figure captions, table captions and availability placeholders.

## Remaining Work

- Expand and polish Introduction.
- Convert Results and Methods into final journal prose.
- Complete citation audit and reference formatting.
- Add exact software versions and parameter details.
- Continue external annotation for top loci.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    write_table_captions(args.table_captions)
    write_checklist(args.checklist)
    write_skeleton(args.out)
    write_report(args.report)


if __name__ == "__main__":
    main()
