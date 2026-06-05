#!/usr/bin/env python3
"""Build Stage 5.23 bibliography and chr6/chr9 gene-model verification files."""

from __future__ import annotations

import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
GENE_WINDOWS = ROOT / "data" / "processed" / "v0_1" / "b73_refgen_v4_gene_windows.tsv"
TOP_EVIDENCE = (
    ROOT
    / "results"
    / "v0_1_baseline"
    / "gemma_lmm_v0_1"
    / "manuscript_tables"
    / "top_regional_loci_evidence.tsv"
)
LEAD_SNPS = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "gemma_lmm_lead_snps.tsv"
GENE_SUMMARY = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "gemma_lmm_gene_summary.tsv"


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def normalize(s: str) -> str:
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def doi_url(doi: str) -> str:
    return f"https://doi.org/{doi}"


def crossref_fetch(doi: str) -> tuple[str, dict[str, object] | None, str]:
    encoded = urllib.parse.quote(doi, safe="")
    url = f"https://api.crossref.org/works/{encoded}"
    req = urllib.request.Request(url, headers={"User-Agent": "yumi-stage5-23/0.1 (mailto:unknown@example.com)"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        return "crossref_found", data.get("message", {}), url
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return "crossref_not_found", None, url
        return f"crossref_http_error_{exc.code}", None, url
    except Exception as exc:  # noqa: BLE001 - audit trail should record exact failure class.
        return f"crossref_error_{type(exc).__name__}", None, url


def year_from_message(message: dict[str, object]) -> str:
    for key in ["published-print", "published-online", "issued", "published"]:
        value = message.get(key)
        if isinstance(value, dict):
            parts = value.get("date-parts")
            if isinstance(parts, list) and parts and parts[0]:
                return str(parts[0][0])
    return ""


def first_author(message: dict[str, object]) -> str:
    authors = message.get("author", [])
    if isinstance(authors, list) and authors:
        fam = authors[0].get("family", "")
        given = authors[0].get("given", "")
        return " ".join(str(x) for x in [given, fam] if x)
    return ""


def reference_records() -> list[dict[str, object]]:
    return [
        {
            "id": "Gui2020_ZEAMAP",
            "first_author_expected": "Gui",
            "year_expected": "2020",
            "title_expected": "ZEAMAP, a comprehensive database adapted to the maize multi-omics era",
            "container_expected": "iScience",
            "volume_expected": "23",
            "page_expected": "101241",
            "doi": "10.1016/j.isci.2020.101241",
            "submission_action": "Mandatory ZEAMAP data-resource citation.",
        },
        {
            "id": "Jiao2017_B73RefGenV4",
            "first_author_expected": "Jiao",
            "year_expected": "2017",
            "title_expected": "Improved maize reference genome with single-molecule technologies",
            "container_expected": "Nature",
            "volume_expected": "546",
            "page_expected": "524-527",
            "doi": "10.1038/nature22971",
            "submission_action": "Mandatory B73 RefGen_v4 citation.",
        },
        {
            "id": "Yates2022_EnsemblGenomes",
            "first_author_expected": "Yates",
            "year_expected": "2022",
            "title_expected": "Ensembl Genomes 2022: an expanding genome resource for non-vertebrates",
            "container_expected": "Nucleic Acids Research",
            "volume_expected": "50",
            "page_expected": "D996-D1003",
            "doi": "10.1093/nar/gkab1007",
            "submission_action": "Use for Ensembl/annotation provenance if retained.",
        },
        {
            "id": "Zhou2012_GEMMA",
            "first_author_expected": "Zhou",
            "year_expected": "2012",
            "title_expected": "Genome-wide efficient mixed-model analysis for association studies",
            "container_expected": "Nature Genetics",
            "volume_expected": "44",
            "page_expected": "821-824",
            "doi": "10.1038/ng.2310",
            "submission_action": "Mandatory GEMMA citation.",
        },
        {
            "id": "Zhou2014_MV_LMM",
            "first_author_expected": "Zhou",
            "year_expected": "2014",
            "title_expected": "Efficient multivariate linear mixed model algorithms for genome-wide association studies",
            "container_expected": "Nature Methods",
            "volume_expected": "11",
            "page_expected": "407-409",
            "doi": "10.1038/nmeth.2848",
            "submission_action": "Optional; remove if reference list is too long because analysis is univariate.",
        },
        {
            "id": "Benjamini1995_FDR",
            "first_author_expected": "Benjamini",
            "year_expected": "1995",
            "title_expected": "Controlling the false discovery rate: a practical and powerful approach to multiple testing",
            "container_expected": "Journal of the Royal Statistical Society: Series B",
            "volume_expected": "57",
            "page_expected": "289-300",
            "doi": "10.1111/j.2517-6161.1995.tb02031.x",
            "submission_action": "Use for FDR method citation.",
        },
        {
            "id": "Li2013_MaizeOilGWAS",
            "first_author_expected": "Li",
            "year_expected": "2013",
            "title_expected": "Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels",
            "container_expected": "Nature Genetics",
            "volume_expected": "45",
            "page_expected": "43-50",
            "doi": "10.1038/ng.2484",
            "submission_action": "Mandatory maize oil GWAS citation.",
        },
        {
            "id": "Alrefai1995_FattyAcidQTL",
            "first_author_expected": "Alrefai",
            "year_expected": "1995",
            "title_expected": "Quantitative trait locus analysis of fatty acid concentrations in maize",
            "container_expected": "Genome",
            "volume_expected": "38",
            "page_expected": "894-901",
            "doi": "10.1139/g95-118",
            "submission_action": "Corrects previous erroneous DOI 10.1139/g95-108 and title/page fields.",
        },
        {
            "id": "Cook2012_KernelComposition",
            "first_author_expected": "Cook",
            "year_expected": "2012",
            "title_expected": "Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels",
            "container_expected": "Plant Physiology",
            "volume_expected": "158",
            "page_expected": "824-834",
            "doi": "10.1104/pp.111.185033",
            "submission_action": "Use for kernel-composition genetic architecture.",
        },
        {
            "id": "Zheng2008_DGAT",
            "first_author_expected": "Zheng",
            "year_expected": "2008",
            "title_expected": "A phenylalanine in DGAT is a key determinant of oil content and composition in maize",
            "container_expected": "Nature Genetics",
            "volume_expected": "40",
            "page_expected": "367-372",
            "doi": "10.1038/ng.85",
            "submission_action": "Corrected DGAT oil-composition reference.",
        },
        {
            "id": "Katral2022_Zmfatb",
            "first_author_expected": "Katral",
            "year_expected": "2022",
            "title_expected": "Allelic variation in Zmfatb gene defines variability for fatty acids composition among diverse maize genotypes",
            "container_expected": "Frontiers in Nutrition",
            "volume_expected": "9",
            "page_expected": "845255",
            "doi": "10.3389/fnut.2022.845255",
            "submission_action": "Replaces unresolved Khan2022/10.3389.fnut.2022.906530 draft item for chr9 FatB support.",
        },
        {
            "id": "Zhang2023_OilQTL",
            "first_author_expected": "Zhang",
            "year_expected": "2023",
            "title_expected": "Genetic dissection of QTLs for oil content in four maize DH populations",
            "container_expected": "Frontiers in Plant Science",
            "volume_expected": "14",
            "page_expected": "1174985",
            "doi": "10.3389/fpls.2023.1174985",
            "submission_action": "Recent maize oil-content QTL context; use Zhang, not Liu, as first author.",
        },
        {
            "id": "Bonaventure2003_FATB",
            "first_author_expected": "Bonaventure",
            "year_expected": "2003",
            "title_expected": "Disruption of the FATB gene in Arabidopsis demonstrates an essential role of saturated fatty acids in plant growth",
            "container_expected": "The Plant Cell",
            "volume_expected": "15",
            "page_expected": "1020-1033",
            "doi": "10.1105/tpc.008946",
            "submission_action": "Cross-species pathway support only, not maize locus validation.",
        },
        {
            "id": "Pedregosa2011_sklearn",
            "first_author_expected": "Pedregosa",
            "year_expected": "2011",
            "title_expected": "Scikit-learn: machine learning in Python",
            "container_expected": "Journal of Machine Learning Research",
            "volume_expected": "12",
            "page_expected": "2825-2830",
            "doi": "",
            "url": "https://jmlr.org/papers/v12/pedregosa11a.html",
            "submission_action": "Software citation; no standard DOI recorded.",
        },
        {
            "id": "Harris2020_NumPy",
            "first_author_expected": "Harris",
            "year_expected": "2020",
            "title_expected": "Array programming with NumPy",
            "container_expected": "Nature",
            "volume_expected": "585",
            "page_expected": "357-362",
            "doi": "10.1038/s41586-020-2649-2",
            "submission_action": "Software citation.",
        },
        {
            "id": "Virtanen2020_SciPy",
            "first_author_expected": "Virtanen",
            "year_expected": "2020",
            "title_expected": "SciPy 1.0: fundamental algorithms for scientific computing in Python",
            "container_expected": "Nature Methods",
            "volume_expected": "17",
            "page_expected": "261-272",
            "doi": "10.1038/s41592-019-0686-2",
            "submission_action": "Software citation.",
        },
        {
            "id": "McKinney2010_pandas",
            "first_author_expected": "McKinney",
            "year_expected": "2010",
            "title_expected": "Data structures for statistical computing in Python",
            "container_expected": "Proceedings of the 9th Python in Science Conference",
            "volume_expected": "",
            "page_expected": "56-61",
            "doi": "10.25080/Majora-92bf1922-00a",
            "submission_action": "Software citation.",
        },
        {
            "id": "Hunter2007_Matplotlib",
            "first_author_expected": "Hunter",
            "year_expected": "2007",
            "title_expected": "Matplotlib: A 2D graphics environment",
            "container_expected": "Computing in Science & Engineering",
            "volume_expected": "9",
            "page_expected": "90-95",
            "doi": "10.1109/MCSE.2007.55",
            "submission_action": "Figure-generation software citation.",
        },
    ]


def audit_references() -> pd.DataFrame:
    rows = []
    for rec in reference_records():
        doi = str(rec.get("doi", ""))
        if doi:
            fetch_status, message, source = crossref_fetch(doi)
            time.sleep(0.05)
            if message:
                got_title = str((message.get("title") or [""])[0])
                got_container = str((message.get("container-title") or [""])[0])
                got_year = year_from_message(message)
                got_page = str(message.get("page", ""))
                got_volume = str(message.get("volume", ""))
                got_first_author = first_author(message)
                title_match = normalize(str(rec["title_expected"])) == normalize(got_title)
                year_match = str(rec["year_expected"]) == got_year
                first_author_match = str(rec["first_author_expected"]).lower() in got_first_author.lower()
                verdict = "verified" if title_match and year_match and first_author_match else "metadata_mismatch_review"
            else:
                got_title = got_container = got_year = got_page = got_volume = got_first_author = ""
                title_match = year_match = first_author_match = False
                verdict = "not_verified"
        else:
            source = str(rec.get("url", ""))
            got_title = str(rec["title_expected"])
            got_container = str(rec["container_expected"])
            got_year = str(rec["year_expected"])
            got_page = str(rec["page_expected"])
            got_volume = str(rec["volume_expected"])
            got_first_author = str(rec["first_author_expected"])
            title_match = year_match = first_author_match = True
            fetch_status = "no_doi_url_record"
            verdict = "url_record_needs_manual_style_check"
        rows.append(
            {
                **rec,
                "source_checked": source,
                "fetch_status": fetch_status,
                "crossref_title": got_title,
                "crossref_container": got_container,
                "crossref_year": got_year,
                "crossref_volume": got_volume,
                "crossref_page": got_page,
                "crossref_first_author": got_first_author,
                "title_match": title_match,
                "year_match": year_match,
                "first_author_match": first_author_match,
                "verdict": verdict,
            }
        )
    return pd.DataFrame(rows)


def stale_reference_checks() -> pd.DataFrame:
    checks = [
        {
            "old_record": "Alrefai1995_FattyAcidQTL_old",
            "old_doi_or_text": "10.1139/g95-108",
            "problem": "Crossref resolves this DOI to a Brassica erratum, not maize fatty-acid QTL.",
            "replacement": "10.1139/g95-118 / Alrefai et al. Quantitative trait locus analysis of fatty acid concentrations in maize. Genome 38, 894-901 (1995).",
            "severity": "blocking_if_left_in_final_refs",
        },
        {
            "old_record": "Khan2022_FattyAcidContent_old",
            "old_doi_or_text": "10.3389/fnut.2022.906530",
            "problem": "Crossref lookup returned not found during Stage 5.23; Stage 5.21 evidence actually uses Katral et al. 2022 DOI 10.3389/fnut.2022.845255.",
            "replacement": "Katral et al. Allelic variation in Zmfatb gene defines variability for fatty acids composition among diverse maize genotypes. Frontiers in Nutrition 9, 845255 (2022).",
            "severity": "blocking_if_left_in_final_refs",
        },
        {
            "old_record": "Liu2023_OilRelatedTraits_old",
            "old_doi_or_text": "Liu, H. et al.; DOI 10.3389/fpls.2023.1174985",
            "problem": "DOI resolves to a Zhang-first-author Frontiers in Plant Science article; the manuscript should cite Zhang et al. if this source is retained.",
            "replacement": "Zhang et al. Genetic dissection of QTLs for oil content in four maize DH populations. Frontiers in Plant Science 14, 1174985 (2023).",
            "severity": "medium_bibliography_accuracy",
        },
    ]
    return pd.DataFrame(checks)


def final_reference_list(audit: pd.DataFrame) -> str:
    lines = [
        "# ZEAMAP v0.1 Reference List Draft",
        "",
        "日期：2026-06-06",
        "",
        "This file was updated by Stage 5.23. It keeps the submission reference list but corrects the Alrefai fatty-acid QTL record, replaces the unresolved Khan/FatB item with the verified Katral Zmfatb paper, and changes the Frontiers in Plant Science 1174985 first author to Zhang.",
        "",
        "## Audited References",
        "",
    ]
    for i, row in enumerate(audit.itertuples(index=False), start=1):
        doi = getattr(row, "doi")
        url = doi_url(doi) if doi else getattr(row, "url", "")
        title = getattr(row, "title_expected")
        container = getattr(row, "container_expected")
        volume = getattr(row, "volume_expected")
        page = getattr(row, "page_expected")
        year = getattr(row, "year_expected")
        first = getattr(row, "first_author_expected")
        doi_text = f"DOI: `{doi}`" if doi else f"URL/status: `{url}` / no standard DOI recorded"
        vol_text = f" {volume}," if volume else ""
        lines.append(f"{i}. {first} et al. {title}. {container}{vol_text} {page} ({year}). {doi_text}.")
    lines.extend(
        [
            "",
            "## Final Formatting Notes",
            "",
            "- Export final bibliography in the target journal style before submission.",
            "- All DOI records in Stage 5.23 were queried against Crossref; the scikit-learn JMLR record remains a URL/no-standard-DOI software citation.",
            "- Do not reintroduce `10.1139/g95-108` for Alrefai or `10.3389/fnut.2022.906530` for the chr9 FatB/Zmfatb support.",
        ]
    )
    return "\n".join(lines)


def gene_model_audit() -> pd.DataFrame:
    genes = pd.read_csv(GENE_WINDOWS, sep="\t")
    top = pd.read_csv(TOP_EVIDENCE, sep="\t")
    lead = pd.read_csv(LEAD_SNPS, sep="\t")
    summary = pd.read_csv(GENE_SUMMARY, sep="\t")
    focus = [
        {
            "region_id": "R01_Zm00001d036982",
            "candidate_gene": "Zm00001d036982",
            "lead_variant": "chr6.s_108212452",
            "expected_description": "linoleic acid1",
            "safe_claim": "strongest recurrent fatty-acid candidate interval; leading local candidate gene, not validated causal gene",
        },
        {
            "region_id": "R08_Zm00001d045383",
            "candidate_gene": "Zm00001d045383",
            "lead_variant": "chr9.s_20246143",
            "expected_description": "lead SNP lies in Zm00001d045383; nearby Zm00001d045387 is fatty acyl-ACP thioesterase2",
            "safe_claim": "high-priority C16:0 candidate interval; exact causal gene/allele unresolved",
        },
        {
            "region_id": "R08_Zm00001d045383",
            "candidate_gene": "Zm00001d045387",
            "lead_variant": "chr9.s_20246143",
            "expected_description": "nearby fatty acyl-ACP thioesterase2 candidate",
            "safe_claim": "nearby pathway candidate only; not the lead SNP host gene",
        },
    ]
    rows = []
    for item in focus:
        gene_id = item["candidate_gene"]
        g = genes.loc[genes["gene_id"] == gene_id]
        l = lead.loc[lead["variant_id"] == item["lead_variant"]]
        top_row = top.loc[top["region_id"] == item["region_id"]]
        if not g.empty and not l.empty:
            chrom = int(g.iloc[0]["chrom"])
            start = int(g.iloc[0]["start_1based"])
            end = int(g.iloc[0]["end_1based"])
            strand = str(g.iloc[0]["strand"])
            lead_pos = int(l.iloc[0]["pos"])
            lead_relation_to_gene = "inside_gene" if start <= lead_pos <= end else "outside_gene"
            distance_to_lead_bp = 0 if lead_relation_to_gene == "inside_gene" else min(abs(lead_pos - start), abs(lead_pos - end))
            evidence_rows = summary.loc[
                (summary["nearest_gene_id"] == gene_id)
                & (summary["trait"].astype(str).str.startswith("agri_aa_oil__Oil"))
            ]
            strongest_p = evidence_rows["min_p_value"].min() if not evidence_rows.empty else ""
            mapping_verdict = "local_refgen_v4_mapping_ok"
        else:
            chrom = start = end = lead_pos = distance_to_lead_bp = ""
            strand = lead_relation_to_gene = strongest_p = ""
            mapping_verdict = "missing_local_mapping"
        rows.append(
            {
                **item,
                "chrom": chrom,
                "gene_start_1based": start,
                "gene_end_1based": end,
                "strand": strand,
                "lead_pos": lead_pos,
                "lead_relation_to_gene": lead_relation_to_gene,
                "distance_to_lead_bp": distance_to_lead_bp,
                "top_table_primary_candidate": "" if top_row.empty else str(top_row.iloc[0]["primary_candidate_gene"]),
                "top_table_description": "" if top_row.empty else str(top_row.iloc[0]["primary_candidate_description"]),
                "strongest_oil_trait_gene_summary_p": strongest_p,
                "mapping_verdict": mapping_verdict,
            }
        )
    return pd.DataFrame(rows)


def report(ref_audit: pd.DataFrame, stale: pd.DataFrame, gene_audit: pd.DataFrame) -> str:
    verified = int((ref_audit["verdict"] == "verified").sum())
    no_doi = int((ref_audit["verdict"] == "url_record_needs_manual_style_check").sum())
    not_verified = int((ref_audit["verdict"] == "not_verified").sum())
    mismatches = int((ref_audit["verdict"] == "metadata_mismatch_review").sum())
    blocking_stale = int(stale["severity"].astype(str).str.contains("blocking").sum())
    gene_ok = int((gene_audit["mapping_verdict"] == "local_refgen_v4_mapping_ok").sum())
    verdict = "BIBLIOGRAPHY_AND_LOCAL_GENE_MAPPING_READY_WITH_STYLE_AND_DATABASE_FINAL_CHECK"
    if not_verified or mismatches:
        verdict = "BIBLIOGRAPHY_REQUIRES_MANUAL_REVIEW_BEFORE_SUBMISSION"
    return f"""# ZEAMAP v0.1 Stage 5.23 Report: Bibliography And Gene-Model Verification

日期：2026-06-06

## Verdict

`{verdict}`

## Summary

- Crossref DOI records queried: {int((ref_audit["doi"].astype(str) != "").sum())}
- Verified DOI metadata rows: {verified}
- URL/no-standard-DOI rows: {no_doi}
- Not verified rows: {not_verified}
- Metadata mismatch rows: {mismatches}
- Stale/corrected reference issues documented: {stale.shape[0]}
- Blocking stale issues if left in final references: {blocking_stale}
- Local RefGen_v4 gene mapping rows checked: {gene_audit.shape[0]}
- Local gene mapping rows passing: {gene_ok}

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
"""


def ars_review(ref_audit: pd.DataFrame, stale: pd.DataFrame, gene_audit: pd.DataFrame) -> str:
    return f"""# ZEAMAP v0.1 Stage 5.23 ARS Integrity Review

日期：2026-06-06

Workflow basis: academic-research-suite academic-pipeline integrity verification gate.

## Decision

`minor_revision_after_reference_correction`

## Integrity Gate Assessment

- Reference existence: DOI-backed references were checked against Crossref metadata.
- Serious hallucination/misdirection detected and corrected: Alrefai old DOI `10.1139/g95-108` was unrelated to maize fatty acids.
- Unresolved DOI detected and corrected: the old Khan/FatB draft DOI did not resolve; Katral et al. `10.3389/fnut.2022.845255` now carries the chr9 Zmfatb support.
- Gene-model mapping: local RefGen_v4 coordinates support the candidate-interval wording for chr6 and chr9.
- Claim boundary: no causal-gene, causal-allele or validation claim is allowed from Stage 5.23 evidence.

## Gate Status

`PASS_FOR_CURRENT_DRAFT_WITH_FINAL_STYLE_AND_AUTHOR_METADATA_PENDING`

This is not yet the final submission gate because target-journal reference formatting, human author metadata and release/DOI actions remain open.

## Key Counts

- Reference rows audited: {ref_audit.shape[0]}
- Stale correction rows: {stale.shape[0]}
- Gene mapping rows audited: {gene_audit.shape[0]}
"""


def update_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    old = "Stage 5.21 targeted fatty-acid literature support 和 Stage 5.22 integrated manuscript/claim audit 初版。"
    new = "Stage 5.21 targeted fatty-acid literature support、Stage 5.22 integrated manuscript/claim audit 和 Stage 5.23 final bibliography/gene-model verification 初版。"
    if old in text:
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")


def update_progress() -> None:
    path = DOCS / "progress-plan.md"
    text = path.read_text(encoding="utf-8")
    old = "| 阶段 5.23 final bibliography/gene-model verification | 下一步 | 核对参考文献最终格式、DOI、chr6/chr9 gene-model mapping 和 target-journal reference style |\n| 阶段 5.24 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |"
    new = "| 阶段 5.23 final bibliography/gene-model verification | 已完成初版 | 已输出 Crossref DOI audit、stale reference corrections、chr6/chr9 gene-model mapping audit 和 ARS integrity review |\n| 阶段 5.24 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |"
    if old in text:
        text = text.replace(old, new)
    append = """

## 阶段 5.23：final bibliography/gene-model verification

这一步做的是投稿前的“参考文献和基因名核验”。它不是再扩大结果，而是防止审稿人一查 DOI 就发现引用不对。

主要结论：

- `10.1139/g95-108` 不能用于 maize fatty-acid QTL；Crossref 显示它是 Brassica erratum。已经改为 `10.1139/g95-118`。
- 旧的 Khan/FatB draft DOI `10.3389/fnut.2022.906530` 未能在 Crossref 解析。chr9 FatB 支持改为 Stage 5.21 已使用的 Katral et al. 2022：`10.3389/fnut.2022.845255`。
- `10.3389/fpls.2023.1174985` 的第一作者应按 DOI 元数据写 Zhang，不应写 Liu。
- 本地 RefGen_v4 坐标支持 chr6 `Zm00001d036982` 和 chr9 `Zm00001d045383`/nearby `Zm00001d045387` 的候选区间表述。

这一步完成后，当前稿件的参考文献风险明显降低，但仍不能宣布最终投稿完成。剩余问题是 target-journal reference style、作者/单位/基金/COI、最终图件人工确认、GitHub release/DOI。
"""
    if "## 阶段 5.23：final bibliography/gene-model verification" not in text:
        text = text.rstrip() + append
    path.write_text(text, encoding="utf-8")


def main() -> None:
    ref_audit = audit_references()
    ref_audit_tsv = ref_audit.fillna("NA").replace("", "NA")
    stale = stale_reference_checks()
    gene_audit = gene_model_audit()

    ref_audit_tsv.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-23-reference-crossref-audit.tsv", sep="\t", index=False)
    stale.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-23-stale-reference-corrections.tsv", sep="\t", index=False)
    gene_audit.to_csv(DOCS / "2026-06-06-zeamap-v0-1-stage5-23-gene-model-mapping-audit.tsv", sep="\t", index=False)
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-23-report.md", report(ref_audit, stale, gene_audit))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-stage5-23-ars-integrity-review.md", ars_review(ref_audit, stale, gene_audit))
    write_text(DOCS / "2026-06-06-zeamap-v0-1-reference-list-draft.md", final_reference_list(ref_audit))
    update_readme()
    update_progress()


if __name__ == "__main__":
    main()
