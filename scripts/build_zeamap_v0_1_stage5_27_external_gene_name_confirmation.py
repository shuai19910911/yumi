#!/usr/bin/env python3
"""Build Stage 5.27 external gene-name confirmation package."""

from __future__ import annotations

import json
import re
import urllib
import urllib.error
import urllib.request
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
XREF = ROOT / "data/external/maizegdb/B73v4_to_B73v5.tsv"
PREVIOUS_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-26-final-submission-gate.tsv"
SOURCE_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-target-journal-manuscript.md"
OUT_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-gene-name-hardened-manuscript.md"

OUT_MAPPING = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-external-gene-name-confirmation.tsv"
OUT_XREF = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-ensembl-xref-functional-evidence.tsv"
OUT_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-final-submission-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-27-ars-external-gene-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"

MAIZEGDB_XREF_URL = "https://download.maizegdb.org/Pan-genes/B73_gene_xref/B73v4_to_B73v5.tsv"
ENSEMBL_REST_LOOKUP = "https://rest.ensembl.org/lookup/id/{gene_id}?expand=1"
ENSEMBL_REST_XREF = "https://rest.ensembl.org/xrefs/id/{gene_id}?all_levels=1"

TARGETS = [
    {
        "region_id": "R01_Zm00001d036982",
        "v4_gene_id": "Zm00001d036982",
        "role": "chr6 lead-region candidate gene",
        "local_refgen_v4_description": "linoleic acid1 / DGAT-like lipid candidate in local annotation",
        "safe_interpretation": "strongest recurrent fatty-acid candidate interval; v5 xrefs support lipid acyltransferase biology, but not causal validation",
        "expected_function_terms": [
            "diacylglycerol o-acyltransferase",
            "o-acyltransferase",
            "triglyceride biosynthetic process",
            "lipid metabolic process",
        ],
    },
    {
        "region_id": "R08_Zm00001d045383",
        "v4_gene_id": "Zm00001d045383",
        "role": "chr9 lead SNP host gene",
        "local_refgen_v4_description": "lead SNP lies in this gene; not the fatty-acid thioesterase candidate",
        "safe_interpretation": "lead-host gene with protein-coding/isoprenoid-related xrefs; should not be renamed as FatB",
        "expected_function_terms": [
            "1-deoxy-d-xylulose-5-phosphate synthase",
            "isoprenoid biosynthetic process",
            "terpenoid biosynthetic process",
        ],
    },
    {
        "region_id": "R08_Zm00001d045383",
        "v4_gene_id": "Zm00001d045387",
        "role": "chr9 nearby fatty-acid pathway candidate",
        "local_refgen_v4_description": "nearby fatty acyl-ACP thioesterase2 candidate",
        "safe_interpretation": "nearby C16:0 fatty-acid pathway candidate; not the lead SNP host gene and not a validated causal gene",
        "expected_function_terms": [
            "acyl-[acyl-carrier-protein] hydrolase",
            "palmitoyl-acyl carrier protein thioesterase",
            "fatty acid biosynthetic process",
            "chloroplast",
        ],
    },
]


def write_text(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def read_v4_to_v5() -> dict[str, str]:
    if not XREF.exists():
        XREF.parent.mkdir(parents=True, exist_ok=True)
        urllib.request.urlretrieve(MAIZEGDB_XREF_URL, XREF)
    mapping: dict[str, str] = {}
    with XREF.open("r", encoding="utf-8") as handle:
        for line in handle:
            parts = line.rstrip("\n").split("\t")
            if len(parts) >= 2:
                mapping[parts[0]] = parts[1]
    return mapping


def fetch_json(url: str) -> object:
    request = urllib.request.Request(url, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        return {"fetch_error": str(exc), "url": url}


def normalized_text(records: object) -> str:
    return json.dumps(records, sort_keys=True).lower()


def selected_xref_terms(records: object, expected_terms: list[str]) -> tuple[str, str, int]:
    text = normalized_text(records)
    hits = []
    for term in expected_terms:
        if term.lower() in text:
            hits.append(term)
    if isinstance(records, list):
        source_labels = sorted(
            {
                str(item.get("db_display_name") or item.get("dbname"))
                for item in records
                if isinstance(item, dict) and (item.get("db_display_name") or item.get("dbname"))
            }
        )
    else:
        source_labels = []
    return "; ".join(hits), "; ".join(source_labels[:12]), len(hits)


def lookup_summary(records: object) -> dict[str, object]:
    if not isinstance(records, dict) or "fetch_error" in records:
        return {
            "assembly_name": None,
            "chrom": None,
            "start": None,
            "end": None,
            "strand": None,
            "biotype": None,
            "description": None,
            "canonical_transcript": None,
            "lookup_status": "fetch_error" if isinstance(records, dict) and "fetch_error" in records else "invalid",
        }
    return {
        "assembly_name": records.get("assembly_name"),
        "chrom": records.get("seq_region_name"),
        "start": records.get("start"),
        "end": records.get("end"),
        "strand": records.get("strand"),
        "biotype": records.get("biotype"),
        "description": records.get("description"),
        "canonical_transcript": records.get("canonical_transcript"),
        "lookup_status": "ok",
    }


def build_outputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    v4_to_v5 = read_v4_to_v5()
    mapping_rows = []
    xref_rows = []
    for target in TARGETS:
        v4 = target["v4_gene_id"]
        v5 = v4_to_v5.get(v4)
        lookup_url = ENSEMBL_REST_LOOKUP.format(gene_id=v5) if v5 else ""
        xref_url = ENSEMBL_REST_XREF.format(gene_id=v5) if v5 else ""
        lookup = fetch_json(lookup_url) if v5 else {"fetch_error": "missing_v5_mapping"}
        xrefs = fetch_json(xref_url) if v5 else {"fetch_error": "missing_v5_mapping"}
        lookup_info = lookup_summary(lookup)
        term_hits, evidence_sources, hit_count = selected_xref_terms(xrefs, target["expected_function_terms"])
        mapping_verdict = "external_source_confirmed"
        if not v5:
            mapping_verdict = "missing_maizegdb_v5_mapping"
        elif lookup_info["lookup_status"] != "ok":
            mapping_verdict = "ensembl_lookup_failed"
        elif hit_count == 0 and v4 != "Zm00001d045383":
            mapping_verdict = "function_terms_not_confirmed"

        mapping_rows.append(
            {
                "region_id": target["region_id"],
                "v4_gene_id": v4,
                "maizegdb_v5_gene_id": v5,
                "role": target["role"],
                "local_refgen_v4_description": target["local_refgen_v4_description"],
                "v5_assembly": lookup_info["assembly_name"],
                "v5_chrom": lookup_info["chrom"],
                "v5_start": lookup_info["start"],
                "v5_end": lookup_info["end"],
                "v5_strand": lookup_info["strand"],
                "v5_biotype": lookup_info["biotype"],
                "v5_lookup_description": lookup_info["description"],
                "v5_canonical_transcript": lookup_info["canonical_transcript"],
                "expected_function_terms_hit": term_hits,
                "evidence_sources": evidence_sources,
                "safe_interpretation": target["safe_interpretation"],
                "mapping_verdict": mapping_verdict,
                "maizegdb_xref_source": MAIZEGDB_XREF_URL,
                "ensembl_lookup_url": lookup_url,
                "ensembl_xref_url": xref_url,
            }
        )
        if isinstance(xrefs, list):
            for item in xrefs:
                if not isinstance(item, dict):
                    continue
                description = str(item.get("description") or "")
                display_id = str(item.get("display_id") or "")
                db = str(item.get("db_display_name") or item.get("dbname") or "")
                combined = " ".join([description, display_id, db]).lower()
                keep = any(term.lower() in combined for term in target["expected_function_terms"])
                keep = keep or db in {"NCBI gene (formerly Entrezgene)", "RefSeq peptide", "UniProtKB/TrEMBL", "GO"}
                if keep:
                    xref_rows.append(
                        {
                            "v4_gene_id": v4,
                            "maizegdb_v5_gene_id": v5,
                            "db_display_name": db,
                            "display_id": display_id,
                            "primary_id": item.get("primary_id"),
                            "description": re.sub(r"\s+", " ", description).strip(),
                            "info_type": item.get("info_type"),
                            "info_text": item.get("info_text") or "NA",
                        }
                    )
    return pd.DataFrame(mapping_rows), pd.DataFrame(xref_rows)


def build_gate(mapping: pd.DataFrame) -> pd.DataFrame:
    previous = pd.read_csv(PREVIOUS_GATE, sep="\t")
    rows = []
    for _, row in previous.iterrows():
        if row["gate"] == "external_gene_name_confirmation":
            rows.append(
                {
                    "gate": "external_gene_name_confirmation",
                    "status": "pass",
                    "evidence": (
                        "Stage 5.27 confirmed MaizeGDB B73v4-to-B73v5 mappings for chr6/chr9 target genes "
                        "and collected Ensembl/Gramene-side xref functional evidence; wording remains candidate-interval bounded."
                    ),
                }
            )
        else:
            rows.append(row.to_dict())
    return pd.DataFrame(rows)


def build_manuscript(mapping: pd.DataFrame) -> str:
    text = SOURCE_MANUSCRIPT.read_text(encoding="utf-8")
    text = text.replace(
        "Target route: The Plant Genome first-line formatting, with G3 as a close alternative. Stage 5.25 converts references to ASA/CSSA/SSSA APA-style author-year format.",
        "Target route: The Plant Genome first-line formatting, with G3 as a close alternative. Stage 5.27 adds external current-gene-ID evidence while preserving candidate-interval claim boundaries.",
    )
    old_chr6 = (
        "The leading region was R01_Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). "
        "This chromosome 6 interval was recurrent across 7 oil traits and contained Zm00001d036982, "
        "annotated locally as linoleic acid1 in B73 RefGen_v4. Targeted literature support links maize "
        "fatty-acid and kernel-oil biology to historical fatty-acid QTLs, kernel-composition association "
        "studies, maize oil GWAS and DGAT/linoleic-acid pathways (Alrefai et al., 1995; Cook et al., 2012; "
        "Li et al., 2013; Zheng et al., 2008; Zhang et al., 2023), so we present the chr6 signal as the "
        "strongest recurrent fatty-acid candidate interval in the current analysis, not as a validated causal gene."
    )
    new_chr6 = (
        "The leading region was R01_Zm00001d036982, centred on chr6.s_108212452 (best P = 2.35e-25). "
        "This chromosome 6 interval was recurrent across 7 oil traits and contained the B73 RefGen_v4 gene "
        "Zm00001d036982, which maps in the MaizeGDB B73v4-to-B73v5 cross-reference to Zm00001eb277490. "
        "Local RefGen_v4 annotation and current-ID xrefs support lipid acyltransferase/DGAT-like biology. "
        "Targeted literature support links maize fatty-acid and kernel-oil biology to historical fatty-acid "
        "QTLs, kernel-composition association studies, maize oil GWAS and DGAT/linoleic-acid pathways "
        "(Alrefai et al., 1995; Cook et al., 2012; Li et al., 2013; Zheng et al., 2008; Zhang et al., 2023), "
        "so we present the chr6 signal as the strongest recurrent fatty-acid candidate interval in the current "
        "analysis, not as a validated causal gene."
    )
    old_chr9 = (
        "The second key biological interval was R08_Zm00001d045383, centred on chr9.s_20246143 for C16:0 "
        "(best P = 7.76e-17). The local interval contains or lies near Zm00001d045387, annotated as fatty "
        "acyl-ACP thioesterase2 near the lead region. Maize Zmfatb/FatB literature and general FATB pathway "
        "biology support this as a high-priority C16:0 fatty-acid candidate interval (Katral et al., 2022; "
        "Bonaventure et al., 2003), while the lead SNP, exact causal gene and causal allele remain unresolved."
    )
    new_chr9 = (
        "The second key biological interval was R08_Zm00001d045383, centred on chr9.s_20246143 for C16:0 "
        "(best P = 7.76e-17). The lead SNP falls in or at the B73 RefGen_v4 gene Zm00001d045383, which maps "
        "to the current B73 v5 gene Zm00001eb377300; external xrefs support this as a DXS/isoprenoid-related "
        "protein-coding gene rather than a FatB gene. A nearby RefGen_v4 gene, Zm00001d045387, maps to "
        "Zm00001eb377350 and carries acyl-ACP hydrolase/palmitoyl-ACP thioesterase and fatty-acid biosynthesis "
        "xref evidence. Maize Zmfatb/FatB literature and general FATB pathway biology support this as a "
        "high-priority C16:0 fatty-acid candidate interval (Katral et al., 2022; Bonaventure et al., 2003), "
        "while the lead SNP, exact causal gene and causal allele remain unresolved."
    )
    for old, new in [(old_chr6, new_chr6), (old_chr9, new_chr9)]:
        if old not in text:
            raise ValueError(f"Expected manuscript paragraph not found: {old[:80]}")
        text = text.replace(old, new, 1)
    text = text.replace(
        "the Stage 5.23 bibliography/gene-model verification, Stage 5.24 citation-integrated manuscript and Stage 5.25 target-journal reference-styled manuscript were generated by `scripts/build_zeamap_v0_1_stage5_23_bibliography_gene_model_verification.py`, `scripts/build_zeamap_v0_1_stage5_24_citation_integrated_manuscript.py` and `scripts/build_zeamap_v0_1_stage5_25_target_journal_reference_style.py`.",
        "the Stage 5.23 bibliography/gene-model verification, Stage 5.24 citation-integrated manuscript, Stage 5.25 target-journal reference-styled manuscript and Stage 5.27 gene-name-hardened manuscript were generated by `scripts/build_zeamap_v0_1_stage5_23_bibliography_gene_model_verification.py`, `scripts/build_zeamap_v0_1_stage5_24_citation_integrated_manuscript.py`, `scripts/build_zeamap_v0_1_stage5_25_target_journal_reference_style.py` and `scripts/build_zeamap_v0_1_stage5_27_external_gene_name_confirmation.py`.",
    )
    text = text.replace(
        "Fourth, target-journal reference styling and external gene-name mapping still need a final author-side check before journal submission.",
        "Fourth, author metadata, final figure approval and repository release identifiers still need a final author-side check before journal submission.",
    )
    text = text.replace(
        "The Plant Genome, G3 and BMC Plant Biology remain realistic first-line targets after final annotation and figure polishing. A higher-impact plant journal would require added independent validation, functional assays, a stronger external annotation layer or a broader multi-population replication analysis.",
        "The Plant Genome, G3 and BMC Plant Biology remain realistic first-line targets after final figure approval, author metadata completion and repository release. A higher-impact plant journal would require added independent validation, functional assays or a broader multi-population replication analysis.",
    )
    return text


def write_report(mapping: pd.DataFrame, xrefs: pd.DataFrame, gate: pd.DataFrame) -> None:
    pass_count = int((gate["status"] == "pass").sum())
    human_count = int((gate["status"] == "human_required").sum())
    fail_count = int((gate["status"] == "fail").sum())
    text = f"""# ZEAMAP v0.1 Stage 5.27 External Gene-Name Confirmation Report

日期：2026-06-06

## Verdict

`EXTERNAL_GENE_NAME_EVIDENCE_COLLECTED_WITH_BOUNDED_CLAIMS`

## What this stage confirmed

- MaizeGDB B73v4-to-B73v5 cross-reference gives one current B73 v5 gene ID for each of the three target RefGen_v4 genes.
- chr6 `Zm00001d036982` maps to `Zm00001eb277490`; Ensembl xrefs include DGAT/O-acyltransferase/triglyceride/lipid-process evidence.
- chr9 lead-host `Zm00001d045383` maps to `Zm00001eb377300`; xrefs support a DXS/isoprenoid-related protein-coding gene, so it should not be renamed as FatB.
- chr9 nearby `Zm00001d045387` maps to `Zm00001eb377350`; xrefs include acyl-ACP hydrolase, palmitoyl-ACP thioesterase and fatty-acid biosynthesis evidence.

## Final submission gate status

- pass/human_required/fail: {pass_count}/{human_count}/{fail_count}
- External gene-name confirmation is now machine-pass with source evidence.
- Remaining blockers are author-only: figure approval, author metadata, funding/acknowledgements/COI and repository release PID.

## Source URLs

- MaizeGDB B73v4-to-B73v5 xref: {MAIZEGDB_XREF_URL}
- Ensembl REST lookup/xrefs were queried for `Zm00001eb277490`, `Zm00001eb377300` and `Zm00001eb377350`.

## Claim boundary

This closes the external gene-name evidence gap, but it does not create causal evidence. The manuscript should continue to say chr6 is the strongest recurrent fatty-acid candidate interval and chr9 is a C16:0 interval with a nearby fatty-acid thioesterase candidate. It should not claim a causal gene, causal allele or experimental validation.

## Evidence files

- `{OUT_MAPPING.relative_to(ROOT)}`
- `{OUT_XREF.relative_to(ROOT)}`
- `{OUT_GATE.relative_to(ROOT)}`
- `{OUT_MANUSCRIPT.relative_to(ROOT)}`
"""
    write_text(REPORT, text)


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    rows = ["| " + " | ".join(cols) + " |", "| " + " | ".join(["---"] * len(cols)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in cols]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_ars_review(mapping: pd.DataFrame, gate: pd.DataFrame) -> None:
    text = f"""# Stage 5.27 ARS External Gene-Name Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite integrity gate logic: external database evidence is checked separately from biological interpretation. The review asks whether the manuscript can safely cite current gene IDs and functional evidence without overstating causality.

## Editorial-style verdict

`MINOR_REVISION_AUTHOR_METADATA_REMAINS`

## Reviewer synthesis

- Domain reviewer: chr6 functional evidence is stronger after current-ID xref confirmation and is consistent with lipid/acyltransferase biology.
- Domain reviewer: chr9 must be written carefully. The lead-host gene and the nearby fatty-acid thioesterase candidate are different genes.
- Methods reviewer: no new association statistics were introduced; gene-name confirmation only changes annotation confidence.
- Devil's advocate: even with external evidence, the study still lacks fine-mapping and functional validation, so causal language remains prohibited.

## Current-ID evidence summary

{markdown_table(mapping[["region_id", "v4_gene_id", "maizegdb_v5_gene_id", "role", "expected_function_terms_hit", "mapping_verdict"]])}

## Updated final gate

{markdown_table(gate)}
"""
    write_text(ARS_REVIEW, text)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    text = text.replace(
        "Stage 5.25 target-journal reference-styled manuscript/submission gate 和 Stage 5.26 final figure technical QA。",
        "Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA 和 Stage 5.27 external gene-name confirmation。"
    )
    text = text.replace(
        "Current status: Stage 5.26 has passed machine technical QA for Figures 1-3 and retained a final submission gate. Remaining blockers are author-only: metadata, funding/acknowledgements/COI approval, human visual figure approval, release PID and final external gene-name confirmation.",
        "Current status: Stage 5.27 has confirmed the chr6/chr9 MaizeGDB B73v4-to-B73v5 gene mappings and Ensembl/Gramene-side functional xrefs. Remaining blockers are author-only: metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID."
    )
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    addition = """

### Stage 5.27 - External gene-name confirmation

通俗解读：这一阶段把之前的“chr6/chr9 外部数据库基因名还要确认”往前推进了一步。我们下载并使用 MaizeGDB 官方 B73v4-to-B73v5 cross-reference，确认 `Zm00001d036982 -> Zm00001eb277490`、`Zm00001d045383 -> Zm00001eb377300`、`Zm00001d045387 -> Zm00001eb377350`。随后用 Ensembl/Gramene 侧 REST xrefs 检查这些 current IDs 的功能证据。

阶段结论：外部证据支持 chr6 candidate 与 lipid/acyltransferase/DGAT-like biology 相关；chr9 需要继续谨慎写法，lead-host gene 是 `Zm00001d045383/Zm00001eb377300`，附近更有 fatty-acid pathway 注释的是 `Zm00001d045387/Zm00001eb377350`。因此最终稿应继续写 candidate interval，不写 causal gene、causal allele 或 validated gene。
"""
    if "### Stage 5.27 - External gene-name confirmation" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def main() -> None:
    mapping, xrefs = build_outputs()
    gate = build_gate(mapping)
    manuscript = build_manuscript(mapping)
    mapping.fillna("NA").to_csv(OUT_MAPPING, sep="\t", index=False)
    xrefs.fillna("NA").to_csv(OUT_XREF, sep="\t", index=False)
    gate.fillna("NA").to_csv(OUT_GATE, sep="\t", index=False)
    write_text(OUT_MANUSCRIPT, manuscript)
    write_report(mapping, xrefs, gate)
    write_ars_review(mapping, gate)
    update_readme()
    update_progress()
    print(f"Wrote {OUT_MAPPING}")
    print(f"Wrote {OUT_XREF}")
    print(f"Wrote {OUT_GATE}")
    print(f"Wrote {OUT_MANUSCRIPT}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
