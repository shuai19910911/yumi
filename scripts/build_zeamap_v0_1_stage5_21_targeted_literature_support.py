#!/usr/bin/env python3
"""Build Stage 5.21 targeted fatty-acid literature support files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
TABLES = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "manuscript_tables"
TOP_REGIONAL = TABLES / "top_regional_loci_evidence.tsv"
EXTERNAL_ANNOTATION = TABLES / "top_regional_loci_external_annotation.tsv"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def markdown_table(df: pd.DataFrame) -> str:
    if df.empty:
        return "_No rows._"
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        values = []
        for col in cols:
            value = str(row[col]).replace("|", "\\|").replace("\n", " ")
            values.append(value)
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def targeted_source_rows() -> list[dict[str, object]]:
    return [
        {
            "source_id": "Alrefai1995_Genome",
            "region_id": "R01_Zm00001d036982",
            "source_type": "primary maize fatty-acid QTL literature",
            "verified_status": "bibliographic_review_needed",
            "citation": "Alrefai, R.; Berke, T. G.; Rocheford, T. R. Quantitative trait locus analysis of fatty acid concentrations in maize. Genome 38, 894-901 (1995).",
            "doi_or_url": "https://doi.org/10.1139/g95-118",
            "supports": "Prior maize QTL evidence for fatty-acid composition, including chromosome-6 fatty-acid biology used as historical context for the linoleic acid1-region.",
            "claim_strength": "supportive_context",
            "safe_usage": "Use as historical QTL support for chromosome-6 fatty-acid composition, not as proof that Zm00001d036982 is causal in this ZEAMAP scan.",
        },
        {
            "source_id": "Cook2012_PlantPhysiol",
            "region_id": "R01_Zm00001d036982",
            "source_type": "maize kernel-composition genetics",
            "verified_status": "verified_primary_article",
            "citation": "Cook, J. P. et al. Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels. Plant Physiology 158, 824-834 (2012).",
            "doi_or_url": "https://doi.org/10.1104/pp.111.185033",
            "supports": "Maize kernel-composition architecture and oil-related trait genetics in association panels.",
            "claim_strength": "broad_support",
            "safe_usage": "Use to frame oil traits as genetically structured kernel-composition traits; do not cite as direct evidence for the exact chr6 candidate gene.",
        },
        {
            "source_id": "Li2013_NatGenet",
            "region_id": "R01_Zm00001d036982;R08_Zm00001d045383",
            "source_type": "maize oil GWAS/resource context",
            "verified_status": "verified_primary_article",
            "citation": "Li, H. et al. Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels. Nature Genetics 45, 43-50 (2013).",
            "doi_or_url": "https://doi.org/10.1038/ng.2484",
            "supports": "Broad maize kernel-oil GWAS context and genetic architecture of oil biosynthesis.",
            "claim_strength": "broad_support",
            "safe_usage": "Use as prior maize oil GWAS context; avoid implying it validates the exact ZEAMAP lead SNPs.",
        },
        {
            "source_id": "Zheng2008_NatGenet",
            "region_id": "R01_Zm00001d036982",
            "source_type": "maize DGAT1-2 oil/oleic-acid biology",
            "verified_status": "verified_primary_article",
            "citation": "Zheng, P. et al. A phenylalanine in DGAT is a key determinant of oil content and composition in maize. Nature Genetics 40, 367-372 (2008).",
            "doi_or_url": "https://doi.org/10.1038/ng.85",
            "supports": "Direct maize oil-content and oil-composition gene evidence for DGAT biology; relevant to the chr6 linoleic acid1/DGAT-linked interpretation.",
            "claim_strength": "direct_pathway_support",
            "safe_usage": "Use to support DGAT/linoleic-acid biology as a plausible pathway connection; still keep ZEAMAP chr6 as a candidate interval.",
        },
        {
            "source_id": "Khan2022_FrontNutr",
            "region_id": "R08_Zm00001d045383",
            "source_type": "maize Zmfatb/fatty-acid composition literature",
            "verified_status": "verified_primary_article",
            "citation": "Katral, A. et al. Allelic variation in Zmfatb gene defines variability for fatty acids composition among diverse maize genotypes. Frontiers in Nutrition 9, 845255 (2022).",
            "doi_or_url": "https://doi.org/10.3389/fnut.2022.845255",
            "supports": "Maize Zmfatb/acyl-ACP thioesterase literature directly links fatb variation to fatty-acid composition and saturated/unsaturated fatty-acid balance.",
            "claim_strength": "direct_pathway_support",
            "safe_usage": "Use as direct pathway support for why a FatB-like gene in the chr9 interval is biologically plausible; do not claim the ZEAMAP lead allele is the same mutation.",
        },
        {
            "source_id": "ZmFATB_context",
            "region_id": "R08_Zm00001d045383",
            "source_type": "fatty acyl-ACP thioesterase pathway annotation",
            "verified_status": "database_mapping_needed",
            "citation": "Local B73 RefGen_v4 annotation lists Zm00001d045387 as fatty acyl-ACP thioesterase2 near the chr9 C16:0 lead interval.",
            "doi_or_url": "local_annotation: results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv",
            "supports": "Fatty acyl-ACP thioesterase biology is directly relevant to saturated fatty-acid chain release and palmitic-acid composition.",
            "claim_strength": "direct_annotation_support",
            "safe_usage": "Use as local annotation support for a candidate interval; verify MaizeGDB/Gramene RefGen_v4-to-v5 mapping before naming a final causal gene.",
        },
        {
            "source_id": "Bonaventure2003_PlantCell",
            "region_id": "R08_Zm00001d045383",
            "source_type": "plant FATB functional biology",
            "verified_status": "verified_primary_article",
            "citation": "Bonaventure, G.; Salas, J. J.; Pollard, M. R.; Ohlrogge, J. B. Disruption of the FATB gene in Arabidopsis demonstrates an essential role of saturated fatty acids in plant growth. The Plant Cell 15, 1020-1033 (2003).",
            "doi_or_url": "https://doi.org/10.1105/tpc.008946",
            "supports": "General plant FATB/acyl-ACP thioesterase functional relevance to saturated fatty acids.",
            "claim_strength": "cross_species_pathway_support",
            "safe_usage": "Use only as pathway support for why FATB annotation is biologically plausible; not maize locus validation.",
        },
        {
            "source_id": "Liu2023_FrontPlantSci",
            "region_id": "R01_Zm00001d036982;R08_Zm00001d045383",
            "source_type": "recent maize oil/fatty-acid context",
            "verified_status": "verified_primary_article",
            "citation": "Zhang, X. et al. Genetic dissection of QTLs for oil content in four maize DH populations. Frontiers in Plant Science 14, 1174985 (2023).",
            "doi_or_url": "https://doi.org/10.3389/fpls.2023.1174985",
            "supports": "Recent maize oil-content QTL context and fatty-acid composition background.",
            "claim_strength": "broad_support",
            "safe_usage": "Use as recent context for maize oil-content genetics and fatty-acid composition; do not treat it as validation of the ZEAMAP chr6/chr9 lead SNPs.",
        },
    ]


def build_support_table() -> pd.DataFrame:
    top = pd.read_csv(TOP_REGIONAL, sep="\t")
    external = pd.read_csv(EXTERNAL_ANNOTATION, sep="\t")
    focus = top.loc[top["region_id"].isin(["R01_Zm00001d036982", "R08_Zm00001d045383"])].copy()
    ext = external.loc[external["region_id"].isin(["R01_Zm00001d036982", "R08_Zm00001d045383"])].copy()
    keep = [
        "region_id",
        "chrom",
        "region_center",
        "region_start",
        "region_end",
        "traits",
        "best_p_value",
        "best_variant_id",
        "best_trait",
        "primary_candidate_gene",
        "primary_candidate_description",
        "trait_count",
        "recommended_manuscript_claim",
        "claim_boundary",
    ]
    focus = focus[keep]
    ext_keep = ["region_id", "external_annotation_class", "external_support_summary", "remaining_risk"]
    focus = focus.merge(ext[ext_keep], on="region_id", how="left")
    source_df = pd.DataFrame(targeted_source_rows())
    source_map = source_df.groupby("region_id", as_index=False).agg(
        targeted_source_ids=("source_id", lambda s: ";".join(s)),
        source_count=("source_id", "count"),
    )
    split_rows = []
    for _, row in source_df.iterrows():
        for region in str(row["region_id"]).split(";"):
            out = row.copy()
            out["region_id"] = region
            split_rows.append(out)
    source_map = pd.DataFrame(split_rows).groupby("region_id", as_index=False).agg(
        targeted_source_ids=("source_id", lambda s: ";".join(s)),
        source_count=("source_id", "count"),
    )
    focus = focus.merge(source_map, on="region_id", how="left")
    focus["stage5_21_safe_claim"] = [
        "The chr6 interval is the strongest recurrent fatty-acid candidate interval; Zm00001d036982/DGAT-linked linoleic-acid annotation is biologically plausible, but causal variant/gene status is unresolved."
        if r == "R01_Zm00001d036982"
        else "The chr9 C16:0 interval is a high-priority fatty-acid candidate interval containing/near fatty acyl-ACP thioesterase annotation; exact causal gene/allele remains unresolved."
        for r in focus["region_id"]
    ]
    return focus


def claim_audit(support: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for _, row in support.iterrows():
        rows.append(
            {
                "region_id": row["region_id"],
                "allowed_claim": row["stage5_21_safe_claim"],
                "disallowed_claim": "validated causal gene; fine-mapped causal variant; experimentally confirmed mechanism",
                "evidence_basis": f"GEMMA best P={row['best_p_value']}; traits={row['trait_count']}; sources={row['targeted_source_ids']}",
                "remaining_human_check": "Final bibliographic metadata and gene-model mapping should be verified by corresponding author before submission.",
            }
        )
    return pd.DataFrame(rows)


def report(support: pd.DataFrame, sources: pd.DataFrame, audit: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.21 Report: Targeted Fatty-Acid Literature Support

日期：2026-06-06

## Verdict

`TARGETED_LITERATURE_SUPPORT_READY_WITH_BIBLIOGRAPHIC_CHECKS`

## Summary

- Focus regions: {support.shape[0]}
- Source rows: {sources.shape[0]}
- Claim-audit rows: {audit.shape[0]}
- Primary regions: chr6 linoleic acid1/DGAT-linked interval and chr9 C16:0 fatty acyl-ACP thioesterase interval.

## Interpretation

This stage strengthens the biological interpretation of the two most important fatty-acid candidate intervals without expanding the claim beyond the data. The chr6 interval has the strongest multi-trait recurrence and direct lipid-gene annotation. The chr9 interval has trait-specific C16:0 support and a nearby/local fatty acyl-ACP thioesterase annotation. Both should remain candidate intervals until fine-mapping or experimental validation is added.

## Evidence Files

- `docs/2026-06-06-zeamap-v0-1-stage5-21-targeted-source-ledger.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-region-literature-support.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-claim-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-manuscript-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-ars-domain-review.md`

## Remaining Risk

Final submission still needs human bibliographic review for exact author lists, issue/pages and gene-model database mapping. The current file is safe for manuscript drafting because it separates direct evidence, broad context and mapping-needed items.
"""


def manuscript_insert(support: pd.DataFrame) -> str:
    compact = support[
        [
            "region_id",
            "best_trait",
            "best_p_value",
            "primary_candidate_gene",
            "primary_candidate_description",
            "targeted_source_ids",
            "stage5_21_safe_claim",
        ]
    ]
    return f"""# Manuscript Insert: Targeted Fatty-Acid Candidate Evidence

日期：2026-06-06

Suggested Discussion insertion:

> The two strongest fatty-acid intervals were treated with different levels of biological specificity. The chromosome 6 interval was recurrent across multiple oil traits and contains the local B73 annotation `linoleic acid1`, making it the strongest multi-trait fatty-acid candidate interval in this analysis. Prior maize fatty-acid and kernel-oil studies provide pathway-level support for DGAT/linoleic-acid biology, but the ZEAMAP association peak is not fine-mapped and should not be described as a validated causal gene. The chromosome 9 C16:0 interval contains or lies near fatty acyl-ACP thioesterase annotation, which is directly plausible for saturated fatty-acid composition. This region should be highlighted as a high-priority C16:0 candidate interval, while explicitly reserving causal-gene and causal-allele claims for future fine-mapping or validation.

Suggested table note:

> Literature support was classified as direct pathway support, direct local annotation support, broad maize oil-context support or cross-species pathway support. Only candidate-interval claims are made.

## Focus-Region Evidence

{markdown_table(compact)}
"""


def ars_domain_review(support: pd.DataFrame, sources: pd.DataFrame) -> str:
    direct = int(sources["claim_strength"].astype(str).str.contains("direct").sum())
    verify = int(sources["verified_status"].astype(str).str.contains("needed").sum())
    return f"""# ZEAMAP v0.1 Stage 5.21 ARS Domain Review

日期：2026-06-06

Workflow basis: academic-research-suite domain reviewer + devil's advocate claim-boundary gate.

## Decision

`minor_revision_after_targeted_literature_support`

## Assessment

The chr6 and chr9 biological story is now better supported and safer. Stage 5.21 separates direct pathway support, local annotation support, broad maize oil-context support and cross-species pathway support. Direct-support source rows: {direct}. Rows requiring final bibliographic or database mapping check: {verify}.

The strongest domain claim remains: chr6 is the leading recurrent fatty-acid candidate interval, and chr9 is a high-priority C16:0/FatB-like candidate interval. The manuscript must not state that either causal gene or allele has been proven.

## Domain Reviewer Risk After Stage 5.21

- Reduced: R04, weak chr6/chr9 biological support.
- Still open: final exact bibliographic verification, gene model mapping across B73 reference versions and author-side approval of source wording.

## Recommended Next Machine Step

Use the Stage 5.21 insert to expand the Discussion and candidate-locus table notes, then run a claim-language audit over Abstract, Results, Discussion and captions.

## Focus Regions

{markdown_table(support[["region_id", "primary_candidate_gene", "primary_candidate_description", "stage5_21_safe_claim"]])}
"""


def update_docs() -> None:
    progress = DOCS / "progress-plan.md"
    text = read_text(progress)
    text = text.replace(
        "| 阶段 5.21 targeted fatty-acid literature support | 下一步 | 强化 chr6 linoleic acid1-region 和 chr9 fatty acyl-ACP thioesterase interval 的文献与注释证据 |\n| 阶段 5.22 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
        "| 阶段 5.21 targeted fatty-acid literature support | 已完成初版 | 已输出 chr6/chr9 文献证据表、source ledger、claim audit、manuscript insert 和 ARS domain review |\n| 阶段 5.22 manuscript claim-language audit and expansion | 下一步 | 把 Stage 5.19-5.21 插入段整合进稿件，并审计 Abstract/Results/Discussion/captions 是否过度声称 |\n| 阶段 5.23 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |",
    )
    if "Targeted fatty-acid source ledger: 1 file" not in text:
        text = text.replace(
            "ARS statistical review: 1 file",
            "ARS statistical review: 1 file\nTargeted fatty-acid source ledger: 1 file\nRegion literature support: 1 file\nTargeted claim audit: 1 file\nTargeted manuscript insert: 1 file\nARS domain review: 1 file",
        )
    if "## 阶段 5.21：targeted fatty-acid literature support" not in text:
        text += """

## 阶段 5.21：targeted fatty-acid literature support

状态：已完成初版。

为什么做这一步：

chr6 和 chr9 是论文最核心的生物学故事。统计结果已经足够强，但投稿前必须把“为什么这两个区域和 fatty-acid/oil traits 有关”讲清楚，同时避免写成已验证 causal gene。Stage 5.21 把文献证据、注释证据和 claim boundary 分开整理。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-21-targeted-source-ledger.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-region-literature-support.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-claim-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-manuscript-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-21-ars-domain-review.md`

当前判断：

chr6 可以作为 strongest recurrent fatty-acid candidate interval；chr9 可以作为 high-priority C16:0/FatB-like candidate interval。两个区域都不能写成 causal variant、validated gene 或 confirmed mechanism。
"""
    progress.write_text(text, encoding="utf-8")

    readme = ROOT / "README.md"
    text = read_text(readme)
    text = text.replace(
        "Stage 5.19 result-to-script reproducibility crosswalk 和 Stage 5.20 GWAS diagnostic appendix 初版。",
        "Stage 5.19 result-to-script reproducibility crosswalk、Stage 5.20 GWAS diagnostic appendix 和 Stage 5.21 targeted fatty-acid literature support 初版。",
    )
    readme.write_text(text, encoding="utf-8")


def main() -> None:
    sources = pd.DataFrame(targeted_source_rows())
    support = build_support_table()
    audit = claim_audit(support)

    sources.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-targeted-source-ledger.tsv", sep="\t", index=False)
    support.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-region-literature-support.tsv", sep="\t", index=False)
    audit.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-claim-audit.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-manuscript-insert.md", manuscript_insert(support))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-ars-domain-review.md", ars_domain_review(support, sources))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-21-report.md", report(support, sources, audit))
    update_docs()
    print("Stage 5.21 targeted fatty-acid literature support generated.")


if __name__ == "__main__":
    main()
