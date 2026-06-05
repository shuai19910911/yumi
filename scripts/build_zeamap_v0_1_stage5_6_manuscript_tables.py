#!/usr/bin/env python3
"""Build manuscript-facing top-locus tables and a results draft for Stage 5.6."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
GEMMA_DIR = ROOT / "results/v0_1_baseline/gemma_lmm_v0_1"
TOP_DIR = GEMMA_DIR / "top_loci"
OUT_DIR = GEMMA_DIR / "manuscript_tables"
REPORT = ROOT / "docs/2026-06-05-zeamap-v0-1-stage5-6-manuscript-tables-report.md"
DRAFT = ROOT / "docs/2026-06-05-zeamap-v0-1-results-draft.md"


LITERATURE = [
    {
        "citation_id": "Li2013_NatGenet",
        "short_citation": "Li et al., 2013, Nature Genetics",
        "url": "https://www.nature.com/articles/ng.2484",
        "evidence_type": "maize oil GWAS",
        "curated_summary": (
            "A maize kernel-oil GWAS using 1.03 million SNPs in 368 inbred lines identified "
            "74 loci associated with oil concentration and fatty-acid composition, with many "
            "candidate genes falling in oil-metabolic pathways."
        ),
    },
    {
        "citation_id": "Alrefai1995_Genome",
        "short_citation": "Alrefai et al., 1995, Genome",
        "url": "https://pubmed.ncbi.nlm.nih.gov/18470215/",
        "evidence_type": "maize fatty-acid QTL",
        "curated_summary": (
            "A chromosome 6 QTL near linoleic acid1 was reported for the 18:1/18:2 ratio "
            "in maize kernel oil, providing direct prior support for a chromosome 6 fatty-acid locus."
        ),
    },
    {
        "citation_id": "Cook2012_PlantPhysiol",
        "short_citation": "Cook et al., 2012, Plant Physiology",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3271770/",
        "evidence_type": "kernel composition NAM/GWAS",
        "curated_summary": (
            "NAM and association-panel analyses identified oil and starch associations in "
            "DGAT1-2, a gene implicated in maize oil composition and quantity."
        ),
    },
    {
        "citation_id": "Zheng2012_PLoSGenet",
        "short_citation": "Zheng et al., 2012, PLoS Genetics",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC3172307/",
        "evidence_type": "maize palmitic-acid gene mapping",
        "curated_summary": (
            "QTL-Pal9 was mapped to a narrow chromosome 9 interval containing Zmfatb, "
            "an acyl-ACP thioesterase gene affecting palmitic acid content in maize grain."
        ),
    },
    {
        "citation_id": "Khan2022_FrontNutr",
        "short_citation": "Khan et al., 2022, Frontiers in Nutrition",
        "url": "https://pmc.ncbi.nlm.nih.gov/articles/PMC9120846/",
        "evidence_type": "maize Zmfatb allelic variation",
        "curated_summary": (
            "Allelic variation in maize fatb was associated with fatty-acid composition; "
            "the gene encodes acyl-ACP thioesterase and is biologically linked to palmitic and oleic acid balance."
        ),
    },
    {
        "citation_id": "Liu2023_FrontPlantSci",
        "short_citation": "Liu et al., 2023, Frontiers in Plant Science",
        "url": "https://www.frontiersin.org/articles/10.3389/fpls.2023.1174985/full",
        "evidence_type": "maize oil QTL context",
        "curated_summary": (
            "A recent maize oil QTL study summarized oil accumulation in embryo and highlighted "
            "candidate genes including DGAT1-2 and fatty-acid metabolism genes in oil-related intervals."
        ),
    },
]


REGION_EVIDENCE = {
    "R01_Zm00001d036982": {
        "evidence_level": "A_direct_prior_lipid_locus",
        "evidence_label": "Direct chromosome-6 fatty-acid/oil prior plus local lipid gene annotation",
        "primary_candidate_gene": "Zm00001d036982",
        "primary_candidate_description": "linoleic acid1 in local B73 RefGen_v4 annotation",
        "external_annotation_summary": (
            "The chr6 peak is recurrent across seven oil traits and maps to a local gene annotated as linoleic acid1. "
            "Prior maize work reported a chromosome 6 linoleic acid1-region QTL for the 18:1/18:2 ratio, and "
            "kernel-composition studies provide broader support for oil-metabolism candidate biology in maize."
        ),
        "recommended_manuscript_claim": (
            "The chr6 locus should be presented as the strongest candidate fatty-acid composition locus, "
            "with Zm00001d036982 as the leading candidate gene."
        ),
        "claim_boundary": "Candidate locus; not fine-mapped causal variant or experimentally validated causal gene.",
        "citation_ids": "Alrefai1995_Genome;Cook2012_PlantPhysiol;Li2013_NatGenet;Liu2023_FrontPlantSci",
    },
    "R02_Zm00001d049511": {
        "evidence_level": "C_indirect_regulatory_candidate",
        "evidence_label": "Multi-trait association with regulatory/membrane annotation, but no direct oil-gene evidence yet",
        "primary_candidate_gene": "Zm00001d049511",
        "primary_candidate_description": "Putative MYB DNA-binding domain superfamily protein",
        "external_annotation_summary": (
            "The chr4 region is recurrent across five oil traits and is ridge-supported. Current annotation points to "
            "a putative MYB-domain gene and nearby membrane/P450 genes, which are plausible regulatory candidates "
            "but do not yet provide direct oil-pathway evidence."
        ),
        "recommended_manuscript_claim": (
            "The chr4 region should be included as a recurrent regulatory candidate requiring external annotation and validation."
        ),
        "claim_boundary": "Do not claim direct oil biosynthetic function without database or experimental support.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R03_Zm00001d031002": {
        "evidence_level": "C_indirect_recurrent_candidate",
        "evidence_label": "Multi-trait and ridge-supported, but current gene function is broad",
        "primary_candidate_gene": "Zm00001d031002",
        "primary_candidate_description": "Tetratricopeptide repeat-like superfamily protein",
        "external_annotation_summary": (
            "The chr1 region is recurrent across six oil traits and is ridge-supported, but the current GFF annotation "
            "is broad and not oil-specific. It is useful as a recurrent association locus rather than as a mechanistic claim."
        ),
        "recommended_manuscript_claim": "Report as a recurrent candidate locus with unresolved functional mechanism.",
        "claim_boundary": "Needs external annotation and independent support before gene-level mechanistic interpretation.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R04_Zm00001d009150": {
        "evidence_level": "C_indirect_transport_candidate",
        "evidence_label": "Strong recurrent region with protein-transport annotation",
        "primary_candidate_gene": "Zm00001d009150",
        "primary_candidate_description": "Sec23/Sec24 protein transport family protein",
        "external_annotation_summary": (
            "The chr8 region is recurrent across five oil traits and is ridge-supported. Sec23/Sec24 annotation suggests "
            "vesicle/protein transport biology, which may be relevant to seed cellular processes but is not direct oil-pathway evidence."
        ),
        "recommended_manuscript_claim": "Report as a recurrent transport-related candidate region.",
        "claim_boundary": "Avoid implying direct fatty-acid biosynthetic function.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R05_Zm00001d013603": {
        "evidence_level": "D_statistical_candidate",
        "evidence_label": "Statistical candidate with no direct oil annotation yet",
        "primary_candidate_gene": "Zm00001d013603",
        "primary_candidate_description": "Type IV inositol polyphosphate 5-phosphatase 7",
        "external_annotation_summary": (
            "The chr5 region is associated with four oil traits and is ridge-supported, but current candidate genes do not "
            "provide direct lipid or seed-oil evidence. It belongs in the supplementary/main extended candidate set."
        ),
        "recommended_manuscript_claim": "Report as a strong statistical candidate requiring functional follow-up.",
        "claim_boundary": "No direct oil-function claim at this stage.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R06_Zm00001d013849": {
        "evidence_level": "C_indirect_regulatory_candidate",
        "evidence_label": "Regulatory candidate with multi-trait support",
        "primary_candidate_gene": "Zm00001d013849",
        "primary_candidate_description": "Trihelix transcription factor GT-2",
        "external_annotation_summary": (
            "The chr5 region is associated with three oil traits and is ridge-supported. A trihelix transcription factor "
            "is a plausible regulatory candidate, but direct oil-pathway evidence is currently absent."
        ),
        "recommended_manuscript_claim": "Report as an oil-associated regulatory candidate locus.",
        "claim_boundary": "Regulatory plausibility is not proof of oil-trait causality.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R07_Zm00001d008881": {
        "evidence_level": "B_lipid_related_indirect",
        "evidence_label": "Lipid-related local annotation with recurrent oil-trait support",
        "primary_candidate_gene": "Zm00001d008881",
        "primary_candidate_description": "Protein RALF-like 33; nearby alkaline phytoceramidase",
        "external_annotation_summary": (
            "The chr8 region is associated with OIL and C18:2. The local interval includes alkaline phytoceramidase, "
            "a lipid-related annotation, but this is closer to sphingolipid metabolism than storage-oil biosynthesis."
        ),
        "recommended_manuscript_claim": "Report as a lipid-related candidate interval, with mechanism unresolved.",
        "claim_boundary": "Do not equate lipid-related annotation with direct kernel-oil biosynthesis.",
        "citation_ids": "Li2013_NatGenet",
    },
    "R08_Zm00001d045383": {
        "evidence_level": "A_direct_fatty_acid_candidate_interval",
        "evidence_label": "C16:0-associated chr9 interval containing fatty acyl-ACP thioesterase2",
        "primary_candidate_gene": "Zm00001d045387",
        "primary_candidate_description": "fatty acyl-ACP thioesterase2 near the lead region",
        "external_annotation_summary": (
            "The chr9 C16:0 peak is close to a fatty acyl-ACP thioesterase candidate. Prior maize studies mapped "
            "palmitic-acid QTL-Pal9 to Zmfatb/acyl-ACP thioesterase biology, supporting this as a high-priority "
            "fatty-acid composition candidate interval."
        ),
        "recommended_manuscript_claim": (
            "The chr9 C16:0 association should be highlighted as a candidate FatB/acyl-ACP-thioesterase interval."
        ),
        "claim_boundary": "Candidate interval; exact causal gene and allele require fine-mapping or validation.",
        "citation_ids": "Zheng2012_PLoSGenet;Khan2022_FrontNutr;Liu2023_FrontPlantSci",
    },
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--top-dir", type=Path, default=TOP_DIR)
    parser.add_argument("--out-dir", type=Path, default=OUT_DIR)
    parser.add_argument("--report", type=Path, default=REPORT)
    parser.add_argument("--draft", type=Path, default=DRAFT)
    return parser.parse_args()


def clean_trait_name(trait: str) -> str:
    return trait.replace("agri_aa_oil__Oil_", "Oil_")


def load_inputs(top_dir: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    priority = pd.read_csv(top_dir / "gemma_top_locus_priority.tsv", sep="\t")
    regions = pd.read_csv(top_dir / "gemma_top_region_targets.tsv", sep="\t")
    return priority, regions


def build_region_annotation(regions: pd.DataFrame) -> pd.DataFrame:
    evidence = pd.DataFrame.from_dict(REGION_EVIDENCE, orient="index").reset_index(names="region_id")
    merged = regions.merge(evidence, on="region_id", how="left")
    merged["trait_count"] = merged["traits"].fillna("").apply(lambda x: len([t for t in str(x).split(";") if t]))
    merged["top_traits_short"] = merged["traits"].fillna("").apply(
        lambda x: ";".join(clean_trait_name(t) for t in str(x).split(";") if t)
    )
    return merged


def build_main_locus_table(priority: pd.DataFrame, region_ann: pd.DataFrame) -> pd.DataFrame:
    tier1 = priority[priority["priority_tier"].eq("tier1_main_text")].copy()
    keep = [
        "locus_id",
        "trait",
        "chrom",
        "locus_start",
        "locus_end",
        "top_variant_id",
        "top_p_value",
        "top_minus_log10_p",
        "best_significance_class",
        "top_candidate_gene_id",
        "candidate_gene_descriptions",
        "recurrent_traits",
        "has_ridge_attribution_support",
        "functional_keyword_classes",
        "priority_score",
        "priority_tier",
    ]
    tier1 = tier1[keep].copy()
    tier1["trait_short"] = tier1["trait"].map(clean_trait_name)
    region_evidence = region_ann[["top_candidate_gene_id", "evidence_level", "evidence_label", "primary_candidate_gene", "citation_ids"]]
    tier1 = tier1.merge(region_evidence, on="top_candidate_gene_id", how="left")
    return tier1


def build_supplementary_table(priority: pd.DataFrame, region_ann: pd.DataFrame) -> pd.DataFrame:
    keep = [
        "locus_id",
        "trait",
        "chrom",
        "locus_start",
        "locus_end",
        "lead_snps_in_locus",
        "top_variant_id",
        "top_pos",
        "top_p_value",
        "top_q_value_bh",
        "best_significance_class",
        "top_candidate_gene_id",
        "top_gene_relation",
        "candidate_genes",
        "candidate_gene_count",
        "candidate_gene_descriptions",
        "has_ridge_attribution_support",
        "functional_keyword_classes",
        "recurrent_traits",
        "priority_score",
        "priority_tier",
    ]
    supp = priority[keep].copy()
    supp["trait_short"] = supp["trait"].map(clean_trait_name)
    region_evidence = region_ann[["top_candidate_gene_id", "evidence_level", "evidence_label"]]
    supp = supp.merge(region_evidence, on="top_candidate_gene_id", how="left")
    supp["evidence_level"] = supp["evidence_level"].fillna("E_not_yet_manually_curated")
    return supp


def write_results_draft(path: Path, region_ann: pd.DataFrame, main_loci: pd.DataFrame) -> None:
    r01 = region_ann.loc[region_ann["region_id"].eq("R01_Zm00001d036982")].iloc[0]
    r08 = region_ann.loc[region_ann["region_id"].eq("R08_Zm00001d045383")].iloc[0]
    tier1_count = len(main_loci)
    tier2_count = int(region_ann["priority_tier"].eq("tier2_strong").sum())
    text = f"""# ZEAMAP v0.1 Results Draft: Prediction-Guided Oil-Trait GWAS

日期：2026-06-05

## Genotype-based prediction prioritizes oil-related traits

After harmonizing ZEAMAP accessions across genotype, population and phenotype/metabolome tables, we constructed a v0.1 accession-level dataset containing 461 accessions, 199,856 common biallelic SNPs and 318 numeric traits. Multi-seed benchmarking identified 66 robust traits, among which oil-related traits showed the strongest prediction signal. The final `genotype_population_ridge` model achieved a median Pearson correlation of 0.498 and median R2 of 0.204 across robust traits, with the oil family reaching a median Pearson/R2 of 0.596/0.321. These results motivated a focused downstream GWAS analysis of high-priority oil traits rather than immediate expansion to a high-capacity deep model.

## Mixed linear modelling controls oil-trait GWAS inflation

A covariate-only GWAS using PC1-PC3 and K1-K3 showed severe genomic inflation (lambda GC 2.41-3.97), indicating that population covariates alone were insufficient for association testing in this maize panel. We therefore used GEMMA mixed linear models with a genotype-derived kinship matrix and the same covariates. Across 10 high-priority oil traits, GEMMA reduced lambda GC to 0.984-1.018 (median 0.998), supporting these results as the main GWAS baseline. Lead SNPs were then merged into physical loci, mapped to B73 RefGen_v4 candidate genes and ranked for manuscript interpretation.

## Prioritized oil-trait loci

The GEMMA candidate-locus layer contained 184 manuscript candidate loci after removing nominal-only signals. We ranked these loci using GEMMA significance, association strength, recurrence across oil traits, ridge-attribution overlap and lipid/fatty-acid annotations. This yielded {tier1_count} tier-1 main-text loci and 22 tier-2 strong loci. Eight representative regional association figures were generated to show local association peaks, LD to the lead SNP and nearby gene models.

The strongest region was chr6 {r01.primary_candidate_gene}, centred on {r01.best_variant_id} (best P = {r01.best_p_value:.2e}). This region was recurrent across {int(r01.trait_count)} oil traits and included a local gene annotated as {r01.primary_candidate_description}. Prior maize studies reported chromosome 6 linoleic-acid/oil-related QTL evidence and broader maize oil GWAS support for lipid-metabolism loci. We therefore treat this chr6 interval as the leading candidate fatty-acid composition locus, while maintaining the conservative interpretation that the lead SNP marks a candidate interval rather than a proven causal variant.

The chr9 C16:0-associated region around {r08.best_variant_id} (best P = {r08.best_p_value:.2e}) is also biologically notable. Although it is not recurrent across multiple oil traits, the interval contains {r08.primary_candidate_gene}, annotated as {r08.primary_candidate_description}. Previous maize studies mapped palmitic-acid variation to FatB/acyl-ACP thioesterase biology on chromosome 9, making this a high-priority candidate interval for fatty-acid composition follow-up.

Other recurrent tier-1 regions on chromosomes 4, 1 and 8 were strongly supported statistically and by ridge-attribution overlap, but their current annotations are regulatory, transport-related or broad protein-family descriptions rather than direct oil-biosynthetic genes. These loci should be presented as recurrent candidate regions and prioritized for external database annotation and experimental follow-up.

## Candidate-claim boundaries

All loci in the current manuscript table should be described as candidate loci or candidate genes. The current analysis does not perform fine-mapping, allele-specific validation or transgenic/biochemical experiments. Therefore, no lead SNP should be described as causal, and no candidate gene should be described as experimentally validated by this study.

## Draft Figure And Table Calls

- Figure 1: v0.1 dataset construction and prediction benchmark summary.
- Figure 2: GEMMA LMM GWAS calibration and candidate-locus summary.
- Figure 3: Regional association panels for chr6 `Zm00001d036982` and chr9 `Zm00001d045387` candidate intervals.
- Table 1: Eight top regional loci with evidence levels and cautious manuscript claims.
- Supplementary Table 1: 184 manuscript candidate loci.
- Supplementary Table 2: Tier-1 locus-level candidate table.

## References For This Draft

"""
    for item in LITERATURE:
        text += f"- {item['citation_id']}: {item['short_citation']}. {item['url']}\n"
    path.write_text(text, encoding="utf-8")


def write_report(path: Path, region_ann: pd.DataFrame, main_loci: pd.DataFrame, supp: pd.DataFrame) -> None:
    evidence_counts = region_ann["evidence_level"].value_counts().to_dict()
    text = f"""# ZEAMAP v0.1 Stage 5.6 manuscript tables and Results draft

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

- Top regional loci: {len(region_ann)}
- Tier-1 locus rows: {len(main_loci)}
- Supplementary manuscript candidate loci: {len(supp)}
- Literature/source records: {len(LITERATURE)}

## Evidence Level Counts

```text
{pd.Series(evidence_counts).to_string()}
```

## Main Interpretation

- `R01_Zm00001d036982` is the strongest candidate interval because it combines recurrence across seven oil traits, Bonferroni significance, lipid annotation, ridge-attribution support and prior chromosome-6 fatty-acid/oil literature.
- `R08_Zm00001d045383` is a high-priority C16:0 interval because the local region includes `Zm00001d045387`, annotated as fatty acyl-ACP thioesterase2, and prior maize work links FatB/acyl-ACP thioesterase biology to palmitic acid.
- Regions R02-R07 remain useful manuscript candidates, but most should be written as recurrent/statistical or indirect regulatory/transport/lipid-related candidates until stronger external annotation or validation is available.

## Claim Boundary

The current evidence supports candidate loci and candidate genes. It does not prove causal variants, fine-mapped credible sets or experimentally validated genes.
"""
    path.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.out_dir.mkdir(parents=True, exist_ok=True)
    priority, regions = load_inputs(args.top_dir)
    region_ann = build_region_annotation(regions)
    main_loci = build_main_locus_table(priority, region_ann)
    supp = build_supplementary_table(priority, region_ann)
    literature = pd.DataFrame(LITERATURE)

    region_ann.to_csv(args.out_dir / "top_regional_loci_evidence.tsv", sep="\t", index=False)
    main_loci.to_csv(args.out_dir / "main_tier1_locus_table.tsv", sep="\t", index=False)
    supp.to_csv(args.out_dir / "supplementary_manuscript_candidate_loci.tsv", sep="\t", index=False)
    literature.to_csv(args.out_dir / "literature_sources.tsv", sep="\t", index=False)
    write_results_draft(args.draft, region_ann, main_loci)
    write_report(args.report, region_ann, main_loci, supp)


if __name__ == "__main__":
    main()
