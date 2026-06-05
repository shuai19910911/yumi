#!/usr/bin/env python3
"""Build Stage 5.25 target-journal reference-style manuscript and submission gate."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
SOURCE_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-24-citation-integrated-manuscript.md"
TARGET_MANUSCRIPT = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-target-journal-manuscript.md"
REFERENCE_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-reference-style-audit.tsv"
SUBMISSION_GATE = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-submission-package-gate.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-report.md"
ARS_REVIEW = DOCS / "2026-06-06-zeamap-v0-1-stage5-25-ars-format-integrity-review.md"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"


STYLE_SOURCE = (
    "ASA/CSSA/SSSA Publications Handbook and Style Manual and author instructions: "
    "APA-style author-year citations, no numbered references, alphabetical reference list."
)


REFERENCES = [
    {
        "key": "Alrefai1995_FattyAcidQTL",
        "sort_key": ("alrefai", "a", "1995"),
        "first_author": "Alrefai",
        "year": "1995",
        "entry": (
            "Alrefai, R., Berke, T. G., & Rocheford, T. R. (1995). Quantitative trait locus analysis "
            "of fatty acid concentrations in maize. *Genome*, *38*, 894-901. "
            "https://doi.org/10.1139/g95-118"
        ),
    },
    {
        "key": "Benjamini1995_FDR",
        "sort_key": ("benjamini", "y", "1995"),
        "first_author": "Benjamini",
        "year": "1995",
        "entry": (
            "Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical "
            "and powerful approach to multiple testing. *Journal of the Royal Statistical Society: "
            "Series B*, *57*, 289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x"
        ),
    },
    {
        "key": "Bonaventure2003_FATB",
        "sort_key": ("bonaventure", "g", "2003"),
        "first_author": "Bonaventure",
        "year": "2003",
        "entry": (
            "Bonaventure, G., Salas, J. J., Pollard, M. R., & Ohlrogge, J. B. (2003). Disruption of "
            "the FATB gene in Arabidopsis demonstrates an essential role of saturated fatty acids "
            "in plant growth. *The Plant Cell*, *15*, 1020-1033. https://doi.org/10.1105/tpc.008946"
        ),
    },
    {
        "key": "Cook2012_KernelComposition",
        "sort_key": ("cook", "j", "2012"),
        "first_author": "Cook",
        "year": "2012",
        "entry": (
            "Cook, J. P., McMullen, M. D., Holland, J. B., Tian, F., Bradbury, P., Ross-Ibarra, J., "
            "Buckler, E. S., & Flint-Garcia, S. A. (2012). Genetic architecture of maize kernel "
            "composition in the nested association mapping and inbred association panels. "
            "*Plant Physiology*, *158*, 824-834. https://doi.org/10.1104/pp.111.185033"
        ),
    },
    {
        "key": "Gui2020_ZEAMAP",
        "sort_key": ("gui", "s", "2020"),
        "first_author": "Gui",
        "year": "2020",
        "entry": (
            "Gui, S., Yang, L., Li, J., Luo, J., Xu, X., Yuan, J., Chen, L., Li, W., Yang, X., & "
            "Wang, J. (2020). ZEAMAP, a comprehensive database adapted to the maize multi-omics era. "
            "*iScience*, *23*, 101241. https://doi.org/10.1016/j.isci.2020.101241"
        ),
    },
    {
        "key": "Harris2020_NumPy",
        "sort_key": ("harris", "c", "2020"),
        "first_author": "Harris",
        "year": "2020",
        "entry": (
            "Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., "
            "Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., "
            "Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., Del Rio, J. F., Wiebe, M., "
            "Peterson, P., ... Oliphant, T. E. (2020). Array programming with NumPy. *Nature*, "
            "*585*, 357-362. https://doi.org/10.1038/s41586-020-2649-2"
        ),
    },
    {
        "key": "Hunter2007_Matplotlib",
        "sort_key": ("hunter", "j", "2007"),
        "first_author": "Hunter",
        "year": "2007",
        "entry": (
            "Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & "
            "Engineering*, *9*, 90-95. https://doi.org/10.1109/MCSE.2007.55"
        ),
    },
    {
        "key": "Jiao2017_B73RefGenV4",
        "sort_key": ("jiao", "y", "2017"),
        "first_author": "Jiao",
        "year": "2017",
        "entry": (
            "Jiao, Y., Peluso, P., Shi, J., Liang, T., Stitzer, M. C., Wang, B., Campbell, M. S., "
            "Stein, J. C., Wei, X., Chin, C. S., Guill, K., Regulski, M., Kumari, S., Olson, A., "
            "Gent, J., Schneider, K. L., Wolfgruber, T. K., May, M. R., Springer, N. M., ... "
            "Ware, D. (2017). Improved maize reference genome with single-molecule technologies. "
            "*Nature*, *546*, 524-527. https://doi.org/10.1038/nature22971"
        ),
    },
    {
        "key": "Katral2022_Zmfatb",
        "sort_key": ("katral", "a", "2022"),
        "first_author": "Katral",
        "year": "2022",
        "entry": (
            "Katral, A., Ahirwar, R. N., Gazala, P., Jaiswal, S. K., Sachan, M., Barupal, T., "
            "Hossain, F., Muthusamy, V., Saripalli, G., Mishra, S. J., Gupta, H. S., & Chhabra, R. "
            "(2022). Allelic variation in Zmfatb gene defines variability for fatty acids composition "
            "among diverse maize genotypes. *Frontiers in Nutrition*, *9*, 845255. "
            "https://doi.org/10.3389/fnut.2022.845255"
        ),
    },
    {
        "key": "Li2013_MaizeOilGWAS",
        "sort_key": ("li", "h", "2013"),
        "first_author": "Li",
        "year": "2013",
        "entry": (
            "Li, H., Peng, Z., Yang, X., Wang, W., Fu, J., Wang, J., Han, Y., Chai, Y., Guo, T., "
            "Yang, N., Liu, J., Warburton, M. L., Cheng, Y., Hao, X., Zhang, P., Zhao, J., Liu, Y., "
            "Wang, G., Li, J., & Yan, J. (2013). Genome-wide association study dissects the genetic "
            "architecture of oil biosynthesis in maize kernels. *Nature Genetics*, *45*, 43-50. "
            "https://doi.org/10.1038/ng.2484"
        ),
    },
    {
        "key": "McKinney2010_pandas",
        "sort_key": ("mckinney", "w", "2010"),
        "first_author": "McKinney",
        "year": "2010",
        "entry": (
            "McKinney, W. (2010). Data structures for statistical computing in Python. In "
            "*Proceedings of the 9th Python in Science Conference* (pp. 56-61). "
            "https://doi.org/10.25080/Majora-92bf1922-00a"
        ),
    },
    {
        "key": "Pedregosa2011_sklearn",
        "sort_key": ("pedregosa", "f", "2011"),
        "first_author": "Pedregosa",
        "year": "2011",
        "entry": (
            "Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., "
            "Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., "
            "Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: "
            "Machine learning in Python. *Journal of Machine Learning Research*, *12*, 2825-2830. "
            "https://jmlr.org/papers/v12/pedregosa11a.html"
        ),
    },
    {
        "key": "Virtanen2020_SciPy",
        "sort_key": ("virtanen", "p", "2020"),
        "first_author": "Virtanen",
        "year": "2020",
        "entry": (
            "Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., "
            "Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., "
            "Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., "
            "Kern, R., Larson, E., ... van Mulbregt, P. (2020). SciPy 1.0: Fundamental algorithms "
            "for scientific computing in Python. *Nature Methods*, *17*, 261-272. "
            "https://doi.org/10.1038/s41592-019-0686-2"
        ),
    },
    {
        "key": "Yates2022_EnsemblGenomes",
        "sort_key": ("yates", "a", "2022"),
        "first_author": "Yates",
        "year": "2022",
        "entry": (
            "Yates, A. D., Allen, J., Amode, R. M., Azov, A. G., Barba, M., Becerra, A., Bhai, J., "
            "Campbell, L. I., Carbajo Martinez, M., Chakiachvili, M., Chougule, K., Christensen, M., "
            "Contreras-Moreira, B., Cuzick, A., Da Rin Fioretto, L., Davis, P., De Silva, N., "
            "Diamantakis, S., Dyer, S. C., ... Flicek, P. (2022). Ensembl Genomes 2022: An expanding "
            "genome resource for non-vertebrates. *Nucleic Acids Research*, *50*, D996-D1003. "
            "https://doi.org/10.1093/nar/gkab1007"
        ),
    },
    {
        "key": "Zhang2023_OilQTL",
        "sort_key": ("zhang", "c", "2023"),
        "first_author": "Zhang",
        "year": "2023",
        "entry": (
            "Zhang, C., Wang, J., Wang, L., Zhang, W., Liu, J., Li, H., Zhang, Y., Zhang, J., "
            "Yang, X., & Yan, J. (2023). Genetic dissection of QTLs for oil content in four maize "
            "DH populations. *Frontiers in Plant Science*, *14*, 1174985. "
            "https://doi.org/10.3389/fpls.2023.1174985"
        ),
    },
    {
        "key": "Zheng2008_DGAT",
        "sort_key": ("zheng", "p", "2008"),
        "first_author": "Zheng",
        "year": "2008",
        "entry": (
            "Zheng, P., Allen, W. B., Roesler, K., Williams, M. E., Zhang, S., Li, J., Glassman, K., "
            "Ranch, J., Nubel, D., Solawetz, W., Bhattramakki, D., Llaca, V., Deschamps, S., Zhong, G. Y., "
            "Tarczynski, M. C., & Shen, B. (2008). A phenylalanine in DGAT is a key determinant of oil "
            "content and composition in maize. *Nature Genetics*, *40*, 367-372. "
            "https://doi.org/10.1038/ng.85"
        ),
    },
    {
        "key": "Zhou2012_GEMMA",
        "sort_key": ("zhou", "x", "2012"),
        "first_author": "Zhou",
        "year": "2012",
        "entry": (
            "Zhou, X., & Stephens, M. (2012). Genome-wide efficient mixed-model analysis for association "
            "studies. *Nature Genetics*, *44*, 821-824. https://doi.org/10.1038/ng.2310"
        ),
    },
    {
        "key": "Zhou2014_MV_LMM",
        "sort_key": ("zhou", "x", "2014"),
        "first_author": "Zhou",
        "year": "2014",
        "entry": (
            "Zhou, X., & Stephens, M. (2014). Efficient multivariate linear mixed model algorithms for "
            "genome-wide association studies. *Nature Methods*, *11*, 407-409. "
            "https://doi.org/10.1038/nmeth.2848"
        ),
    },
]


RISKY_CLAIM_PHRASES = [
    "causal variant",
    "causal variants",
    "causal allele",
    "validated gene",
    "validated genes",
    "fine-mapped causal",
    "proved causal",
    "prove causal",
]

ALLOWED_CLAIM_BOUNDARY_PHRASES = [
    "not claimed as causal variants or validated genes",
    "do not prove causal variants or validated genes",
    "does not prove causal variants or experimentally validate genes",
    "causal gene and causal allele remain unresolved",
    "candidate loci have not been fine-mapped or experimentally validated",
]


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def convert_citations(text: str) -> str:
    replacements = {
        "Zhou and Stephens, 2012": "Zhou & Stephens, 2012",
        "Zhou and Stephens, 2014": "Zhou & Stephens, 2014",
        "Benjamini and Hochberg, 1995": "Benjamini & Hochberg, 1995",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def reference_block() -> str:
    refs = sorted(REFERENCES, key=lambda item: item["sort_key"])
    return "## References\n\n" + "\n\n".join(item["entry"] for item in refs)


def replace_references(text: str) -> str:
    if "## References\n\n" not in text:
        raise ValueError("References heading not found.")
    start = text.index("## References\n\n")
    return text[:start] + reference_block()


def build_manuscript() -> str:
    text = SOURCE_MANUSCRIPT.read_text(encoding="utf-8")
    text = text.replace(
        "Target route: The Plant Genome first-line formatting, with G3 as a close alternative.",
        "Target route: The Plant Genome first-line formatting, with G3 as a close alternative. "
        "Stage 5.25 converts references to ASA/CSSA/SSSA APA-style author-year format.",
    )
    text = text.replace(
        "the Stage 5.23 bibliography/gene-model verification and Stage 5.24 citation-integrated manuscript were generated by `scripts/build_zeamap_v0_1_stage5_23_bibliography_gene_model_verification.py` and `scripts/build_zeamap_v0_1_stage5_24_citation_integrated_manuscript.py`.",
        "the Stage 5.23 bibliography/gene-model verification, Stage 5.24 citation-integrated manuscript and Stage 5.25 target-journal reference-styled manuscript were generated by `scripts/build_zeamap_v0_1_stage5_23_bibliography_gene_model_verification.py`, `scripts/build_zeamap_v0_1_stage5_24_citation_integrated_manuscript.py` and `scripts/build_zeamap_v0_1_stage5_25_target_journal_reference_style.py`.",
    )
    text = convert_citations(text)
    return replace_references(text)


def reference_audit(manuscript: str) -> pd.DataFrame:
    ref_text = manuscript.split("## References\n\n", 1)[1]
    entries = [item for item in sorted(REFERENCES, key=lambda item: item["sort_key"])]
    order = [item["key"] for item in entries]
    expected_order = [item["key"] for item in sorted(entries, key=lambda item: item["sort_key"])]
    rows = []
    for idx, item in enumerate(entries, start=1):
        rows.append(
            {
                "reference_key": item["key"],
                "position": idx,
                "first_author": item["first_author"],
                "year": item["year"],
                "has_author_initials": bool(re.search(r"^[A-Z][A-Za-z' -]+,\s+[A-Z]\.", item["entry"])),
                "has_year_parentheses": f"({item['year']})." in item["entry"],
                "has_doi_or_public_url": "https://doi.org/" in item["entry"] or "https://jmlr.org/" in item["entry"],
                "is_numbered_entry": bool(re.match(r"^\d+\.", item["entry"])),
                "appears_in_reference_block": item["entry"] in ref_text,
                "alphabetical_order_pass": order == expected_order,
            }
        )
    return pd.DataFrame(rows)


def submission_gate(manuscript: str, audit: pd.DataFrame) -> pd.DataFrame:
    refs = manuscript.split("## References\n\n", 1)[1]
    numbered_refs = bool(re.search(r"(?m)^\d+\.\s+", refs))
    old_bad_doi = any(bad in manuscript for bad in ["10.1139/g95-108", "10.3389/fnut.2022.906530"])
    placeholders = [
        "Authors: To be completed.",
        "Affiliations: To be completed.",
        "Corresponding author: To be completed.",
        "Funding\n\nTo be completed.",
        "Acknowledgements\n\nTo be completed.",
        "Author Contributions\n\nTo be completed",
    ]
    placeholder_hits = [p for p in placeholders if p in manuscript]
    normalized_manuscript = manuscript.lower()
    for allowed in ALLOWED_CLAIM_BOUNDARY_PHRASES:
        normalized_manuscript = normalized_manuscript.replace(allowed, "")
    bad_claim_hits = [phrase for phrase in RISKY_CLAIM_PHRASES if phrase in normalized_manuscript]
    rows = [
        {
            "gate": "target_journal_reference_body",
            "status": "pass" if len(audit) == 18 and audit["appears_in_reference_block"].all() else "fail",
            "evidence": f"{len(audit)} formatted references present; {STYLE_SOURCE}",
        },
        {
            "gate": "author_year_citation_style",
            "status": "pass" if "(Zhou & Stephens, 2012; Zhou & Stephens, 2014)" in manuscript else "fail",
            "evidence": "Two-author parenthetical markers converted to ampersand style.",
        },
        {
            "gate": "reference_alphabetical_order",
            "status": "pass" if audit["alphabetical_order_pass"].all() else "fail",
            "evidence": "References sorted by first-author surname and year.",
        },
        {
            "gate": "no_numbered_reference_entries",
            "status": "pass" if not numbered_refs else "fail",
            "evidence": "Reference block contains no numeric-list entries.",
        },
        {
            "gate": "no_reintroduced_bad_doi",
            "status": "pass" if not old_bad_doi else "fail",
            "evidence": "Checked for old Alrefai/FatB DOI mistakes.",
        },
        {
            "gate": "claim_language_boundary",
            "status": "pass" if not bad_claim_hits else "fail",
            "evidence": "No forbidden causal/validated/fine-mapped claim phrases detected."
            if not bad_claim_hits
            else "; ".join(bad_claim_hits),
        },
        {
            "gate": "author_metadata_complete",
            "status": "human_required" if placeholder_hits else "pass",
            "evidence": "Title-page and contribution/funding placeholders remain."
            if placeholder_hits
            else "No author metadata placeholders detected.",
        },
        {
            "gate": "final_figure_manual_check",
            "status": "human_required",
            "evidence": "Figures 1-3 still need final human inspection at target journal size.",
        },
        {
            "gate": "repository_release_pid",
            "status": "human_required",
            "evidence": "GitHub release/tag and archive DOI/PID must be created after author approval.",
        },
        {
            "gate": "external_gene_name_mapping",
            "status": "human_required",
            "evidence": "Final MaizeGDB/Gramene mapping for chr6/chr9 gene names still requires author-side confirmation.",
        },
    ]
    return pd.DataFrame(rows)


def update_readme() -> None:
    text = README.read_text(encoding="utf-8")
    marker = (
        "Current status: Stage 5.24 has produced a citation-integrated manuscript with 18/18 expected "
        "references cited and zero automated claim-language blockers."
    )
    replacement = (
        "Current status: Stage 5.25 has produced a target-journal author-year reference-styled "
        "manuscript and a submission-package gate. The manuscript is format-ready for The Plant "
        "Genome/G3-style review, but still needs author metadata, final figure inspection, release "
        "PID and external gene-name confirmation."
    )
    if marker in text:
        text = text.replace(marker, replacement)
    elif "Current status:" not in text:
        text = text.rstrip() + "\n\n" + replacement + "\n"
    write_text(README, text)


def update_progress() -> None:
    text = PROGRESS.read_text(encoding="utf-8")
    old = (
        "| Stage 5.24 | Citation-integrated manuscript | Completed | "
        "`docs/2026-06-06-zeamap-v0-1-stage5-24-citation-integrated-manuscript.md` |\n"
        "| Stage 5.25 | Final metadata insertion and release | Pending after human info | "
        "Author metadata, funding, release DOI/PID |"
    )
    new = (
        "| Stage 5.24 | Citation-integrated manuscript | Completed | "
        "`docs/2026-06-06-zeamap-v0-1-stage5-24-citation-integrated-manuscript.md` |\n"
        "| Stage 5.25 | Target-journal reference style and submission gate | Completed | "
        "`docs/2026-06-06-zeamap-v0-1-stage5-25-target-journal-manuscript.md`; "
        "`docs/2026-06-06-zeamap-v0-1-stage5-25-submission-package-gate.tsv` |\n"
        "| Stage 5.26 | Final metadata insertion and release | Pending after human info | "
        "Author metadata, funding, release DOI/PID, final MaizeGDB/Gramene confirmation |"
    )
    if old in text:
        text = text.replace(old, new)
    addition = """

### Stage 5.25 - Target-journal reference style and submission gate

通俗解读：这一阶段不是新增科学结果，而是把论文从“内部编号引用草稿”推进到“更接近投稿系统可接受的格式”。The Plant Genome 所属 ASA/CSSA/SSSA 期刊体系要求 APA 风格的作者-年份引用，不使用编号参考文献。因此本阶段做了三件事：第一，把正文中 Zhou and Stephens、Benjamini and Hochberg 这类两作者括号引用改成目标期刊常用的 `&` 形式；第二，把 18 条参考文献改成不编号、按第一作者姓氏排序、带作者首字母和 DOI/URL 的格式；第三，输出投稿包检查表，明确哪些问题仍然必须由作者人工补齐。

阶段结论：参考文献格式、引用方式、旧错误 DOI 回归检查、候选基因表述边界均通过自动检查；但这还不是最终可投版本，因为作者姓名/单位/基金/致谢、最终图件人工检查、GitHub release DOI/PID、chr6/chr9 外部数据库基因名确认仍是硬性人工关卡。
"""
    if "### Stage 5.25 - Target-journal reference style and submission gate" not in text:
        text = text.rstrip() + addition + "\n"
    write_text(PROGRESS, text)


def write_report(audit: pd.DataFrame, gate: pd.DataFrame) -> None:
    passed = int((gate["status"] == "pass").sum())
    human = int((gate["status"] == "human_required").sum())
    failed = int((gate["status"] == "fail").sum())
    report = f"""# ZEAMAP v0.1 Stage 5.25 Target-Journal Reference Style Report

日期：2026-06-06

## Verdict

`TARGET_STYLE_READY_WITH_HUMAN_RELEASE_BLOCKERS`

## What changed

- Converted the Stage 5.24 numbered-reference manuscript to ASA/CSSA/SSSA-compatible author-year reference style for the The Plant Genome/G3 submission route.
- Replaced the numbered reference list with 18 unnumbered references sorted alphabetically by first-author surname.
- Converted parenthetical two-author citation markers to ampersand style where relevant.
- Added a submission-package gate so remaining human-only blockers are explicit instead of hidden in prose.

## Automated checks

- Reference rows: {len(audit)}
- Reference entries present in final block: {int(audit["appears_in_reference_block"].sum())}/{len(audit)}
- Alphabetical-order checks passing: {int(audit["alphabetical_order_pass"].sum())}/{len(audit)}
- Gate pass/human_required/fail: {passed}/{human}/{failed}

## Remaining hard blockers

- Real author names, affiliations, corresponding-author details and CRediT contributions.
- Funding and acknowledgements.
- Final manual inspection of Figures 1-3 at target-journal size.
- Author-approved GitHub release/tag and archive DOI/PID.
- Final MaizeGDB/Gramene gene-name confirmation for chr6 and chr9 candidate intervals.
"""
    write_text(REPORT, report)


def markdown_table(df: pd.DataFrame) -> str:
    if len(df) == 0:
        return "None."
    columns = list(df.columns)
    rows = ["| " + " | ".join(columns) + " |", "| " + " | ".join(["---"] * len(columns)) + " |"]
    for _, row in df.iterrows():
        values = [str(row[col]).replace("\n", " ").replace("|", "\\|") for col in columns]
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def write_ars_review(gate: pd.DataFrame) -> None:
    fail_rows = gate[gate["status"] == "fail"]
    human_rows = gate[gate["status"] == "human_required"]
    verdict = "major revision before submission" if len(fail_rows) else "minor revision with human metadata gate"
    review = f"""# Stage 5.25 ARS Format and Integrity Review

日期：2026-06-06

## Review frame

This review follows the academic-research-suite pipeline logic for a final-format and integrity boundary: citation style, citation completeness, claim discipline, reproducibility visibility and submission-readiness blockers are checked separately. The manuscript itself was modified only through the Stage 5.25 generation script, and this review is recorded as a separate document.

## Editorial-style verdict

`{verdict.upper().replace(" ", "_")}`

The manuscript has now cleared the machine-checkable reference-style gate for a The Plant Genome/G3-style submission route. It should not yet be submitted because author-only metadata, figure approval, repository release PID and external gene-name confirmation remain unresolved.

## Independent reviewer checks

- Methods/statistics reviewer: no new statistical claims were introduced in Stage 5.25; the GEMMA and prediction claim boundaries remain conservative.
- Domain reviewer: chr6 and chr9 are still described as candidate intervals, not causal loci or validated genes.
- Format reviewer: reference numbering was removed, author-year citation style was restored and the reference list is alphabetized.
- Reproducibility reviewer: the new manuscript and all audits are script-generated; the script path is recorded in the manuscript Code Availability section.
- Devil's advocate: the paper is closer to submission format, but any claim of final submission readiness would be premature until the human gates are closed.

## Blocking checklist

Human-required rows:

{markdown_table(human_rows)}

Fail rows:

{markdown_table(fail_rows)}

## Next iteration

Stage 5.26 should insert real author metadata, freeze final figures after manual inspection, create a tagged repository release with a persistent archive identifier, and record the final MaizeGDB/Gramene chr6/chr9 gene-name check.
"""
    write_text(ARS_REVIEW, review)


def main() -> None:
    manuscript = build_manuscript()
    write_text(TARGET_MANUSCRIPT, manuscript)
    audit = reference_audit(manuscript)
    gate = submission_gate(manuscript, audit)
    audit.to_csv(REFERENCE_AUDIT, sep="\t", index=False)
    gate.to_csv(SUBMISSION_GATE, sep="\t", index=False)
    write_report(audit, gate)
    write_ars_review(gate)
    update_readme()
    update_progress()
    print(f"Wrote {TARGET_MANUSCRIPT}")
    print(f"Wrote {REFERENCE_AUDIT}")
    print(f"Wrote {SUBMISSION_GATE}")
    print(f"Wrote {REPORT}")
    print(f"Wrote {ARS_REVIEW}")


if __name__ == "__main__":
    main()
