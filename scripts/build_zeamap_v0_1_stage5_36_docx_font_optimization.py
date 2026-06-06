#!/usr/bin/env python3
"""Optimize DOCX fonts for Stage 5.35 revised manuscripts."""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
README = ROOT / "README.md"
PROGRESS = DOCS / "progress-plan.md"

EN_IN = DOCS / "2026-06-06-zeamap-v0-1-stage5-35-revised-submission-manuscript-en.docx"
ZH_IN = DOCS / "2026-06-06-zeamap-v0-1-stage5-35-revised-submission-manuscript-zh.docx"
EN_OUT = DOCS / "2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx"
ZH_OUT = DOCS / "2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx"
AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-36-docx-font-audit.tsv"
REPORT = DOCS / "2026-06-06-zeamap-v0-1-stage5-36-report.md"
FIGDIR = ROOT / "results" / "v0_1_baseline" / "gemma_lmm_v0_1" / "manuscript_figures_stage5_36"
FIGDIR.mkdir(parents=True, exist_ok=True)
WORKFLOW_PNG = FIGDIR / "figure5_overall_workflow_nature.png"
WORKFLOW_PDF = FIGDIR / "figure5_overall_workflow_nature.pdf"
WORKFLOW_SVG = FIGDIR / "figure5_overall_workflow_nature.svg"
MODEL_PNG = FIGDIR / "figure6_model_structure_nature.png"
MODEL_PDF = FIGDIR / "figure6_model_structure_nature.pdf"
MODEL_SVG = FIGDIR / "figure6_model_structure_nature.svg"
FIGURE_AUDIT = DOCS / "2026-06-06-zeamap-v0-1-stage5-36-workflow-model-figure-audit.tsv"

W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
NS = {"w": W_NS}
ET.register_namespace("w", W_NS)


def qn(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def ensure_child(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(f"w:{tag}", NS)
    if child is None:
        child = ET.SubElement(parent, qn(tag))
    return child


def set_attr(el: ET.Element, attr: str, value: str) -> None:
    el.set(qn(attr), value)


def set_rfonts(rpr: ET.Element, ascii_font: str, east_asia_font: str) -> None:
    rfonts = ensure_child(rpr, "rFonts")
    for attr, value in [
        ("ascii", ascii_font),
        ("hAnsi", ascii_font),
        ("cs", ascii_font),
        ("eastAsia", east_asia_font),
    ]:
        set_attr(rfonts, attr, value)


def optimize_styles(xml: bytes, ascii_font: str, east_asia_font: str) -> bytes:
    root = ET.fromstring(xml)

    doc_defaults = ensure_child(root, "docDefaults")
    rpr_default = ensure_child(doc_defaults, "rPrDefault")
    rpr = ensure_child(rpr_default, "rPr")
    set_rfonts(rpr, ascii_font, east_asia_font)

    for style in root.findall("w:style", NS):
        rpr = ensure_child(style, "rPr")
        set_rfonts(rpr, ascii_font, east_asia_font)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def optimize_document(xml: bytes, ascii_font: str, east_asia_font: str) -> bytes:
    root = ET.fromstring(xml)
    for run in root.findall(".//w:r", NS):
        rpr = run.find("w:rPr", NS)
        if rpr is None:
            rpr = ET.Element(qn("rPr"))
            run.insert(0, rpr)
        set_rfonts(rpr, ascii_font, east_asia_font)
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def optimize_docx(src: Path, dst: Path, ascii_font: str, east_asia_font: str) -> dict[str, object]:
    tmp = dst.with_suffix(".tmp.docx")
    with zipfile.ZipFile(src, "r") as zin, zipfile.ZipFile(tmp, "w", compression=zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)
            if item.filename == "word/styles.xml":
                data = optimize_styles(data, ascii_font, east_asia_font)
            elif item.filename == "word/document.xml":
                data = optimize_document(data, ascii_font, east_asia_font)
            zout.writestr(item, data)
    shutil.move(tmp, dst)

    with zipfile.ZipFile(dst, "r") as zf:
        styles = zf.read("word/styles.xml").decode("utf-8", errors="replace")
        document = zf.read("word/document.xml").decode("utf-8", errors="replace")
    return {
        "path": str(dst.relative_to(ROOT)),
        "status": "pass" if dst.exists() and dst.stat().st_size > 0 else "fail",
        "bytes": dst.stat().st_size if dst.exists() else 0,
        "ascii_font": ascii_font,
        "east_asia_font": east_asia_font,
        "styles_has_ascii_font": ascii_font in styles,
        "styles_has_east_asia_font": east_asia_font in styles,
        "document_has_east_asia_font": east_asia_font in document,
    }


def box(ax, xy, text, width=0.18, height=0.11, fc="#F4F4F4", ec="#2F2F2F", fontsize=8.5):
    x, y = xy
    patch = FancyBboxPatch(
        (x, y),
        width,
        height,
        boxstyle="round,pad=0.012,rounding_size=0.018",
        linewidth=1,
        edgecolor=ec,
        facecolor=fc,
    )
    ax.add_patch(patch)
    ax.text(x + width / 2, y + height / 2, text, ha="center", va="center", fontsize=fontsize, linespacing=1.15)
    return patch


def arrow(ax, start, end, color="#333333"):
    ax.add_patch(
        FancyArrowPatch(
            start,
            end,
            arrowstyle="-|>",
            mutation_scale=12,
            linewidth=1.1,
            color=color,
            shrinkA=3,
            shrinkB=3,
        )
    )


def make_workflow_figure() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(8.4, 5.0))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(0.03, 0.94, "Overall analysis workflow", fontsize=12.5, fontweight="bold", ha="left")
    ax.text(0.03, 0.90, "From public ZEAMAP processed data to calibrated maize oil-trait candidate intervals", fontsize=8.5, ha="left", color="#555555")

    colors = {
        "data": "#D9EAF7",
        "qc": "#E8E1F5",
        "model": "#DDEFD8",
        "gwas": "#FCE4D6",
        "output": "#F7F1C9",
    }
    boxes = {
        "raw": box(ax, (0.04, 0.70), "ZEAMAP\nprocessed data", fc=colors["data"]),
        "index": box(ax, (0.29, 0.70), "Accession\nharmonization", fc=colors["qc"]),
        "v01": box(ax, (0.54, 0.70), "v0.1 paired set\n461 accessions\n199,856 SNPs", width=0.20, fc=colors["qc"]),
        "pred": box(ax, (0.79, 0.70), "Prediction\nbenchmark", fc=colors["model"]),
        "traits": box(ax, (0.79, 0.48), "66 robust traits\n29 oil traits", fc=colors["model"]),
        "gwas": box(ax, (0.54, 0.48), "GEMMA LMM GWAS\n10 oil traits", width=0.20, fc=colors["gwas"]),
        "loci": box(ax, (0.29, 0.48), "Candidate-locus\nannotation", fc=colors["gwas"]),
        "rank": box(ax, (0.04, 0.48), "Prioritized\ncandidate intervals", fc=colors["output"]),
        "paper": box(ax, (0.29, 0.22), "Figures, tables\nand manuscript", width=0.20, fc=colors["output"]),
        "claim": box(ax, (0.54, 0.22), "Conservative\nclaim boundary", width=0.20, fc=colors["output"]),
    }

    arrow(ax, (0.22, 0.755), (0.29, 0.755))
    arrow(ax, (0.47, 0.755), (0.54, 0.755))
    arrow(ax, (0.74, 0.755), (0.79, 0.755))
    arrow(ax, (0.88, 0.70), (0.88, 0.59))
    arrow(ax, (0.79, 0.535), (0.74, 0.535))
    arrow(ax, (0.54, 0.535), (0.47, 0.535))
    arrow(ax, (0.29, 0.535), (0.22, 0.535))
    arrow(ax, (0.13, 0.48), (0.29, 0.31))
    arrow(ax, (0.49, 0.31), (0.54, 0.31))

    ax.text(0.04, 0.12, "Design principle: correct accession pairing and calibrated association before maximal feature count.", fontsize=8, color="#444444")
    for path in [WORKFLOW_PNG, WORKFLOW_PDF, WORKFLOW_SVG]:
        fig.savefig(path, dpi=450, bbox_inches="tight")
    plt.close(fig)


def make_model_figure() -> None:
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 9})
    fig, ax = plt.subplots(figsize=(8.4, 5.2))
    ax.set_axis_off()
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.text(0.03, 0.94, "Model and statistical structure", fontsize=12.5, fontweight="bold", ha="left")
    ax.text(0.03, 0.90, "Prediction triage feeds calibrated mixed-model GWAS and candidate-locus ranking", fontsize=8.5, ha="left", color="#555555")

    fc1, fc2, fc3, fc4 = "#D9EAF7", "#DDEFD8", "#FCE4D6", "#F7F1C9"
    box(ax, (0.05, 0.68), "Genotype matrix\n199,856 SNPs", width=0.19, fc=fc1)
    box(ax, (0.05, 0.48), "Population\ncovariates", width=0.19, fc=fc1)
    box(ax, (0.05, 0.28), "Phenotype /\nmetabolite traits", width=0.19, fc=fc1)
    box(ax, (0.33, 0.63), "Regularized\nprediction\nridge / ElasticNet", width=0.20, height=0.16, fc=fc2)
    box(ax, (0.33, 0.34), "Trait stability\nmulti-seed screen", width=0.20, height=0.14, fc=fc2)
    box(ax, (0.62, 0.62), "Oil-trait set\n10 GWAS traits", width=0.18, fc=fc3)
    box(ax, (0.62, 0.41), "GEMMA LMM\nK + covariates", width=0.18, fc=fc3)
    box(ax, (0.62, 0.20), "Inflation control\nlambda GC ≈ 1", width=0.18, fc=fc3)
    box(ax, (0.84, 0.55), "Lead loci\n+ gene models", width=0.13, fc=fc4)
    box(ax, (0.84, 0.29), "Evidence ranking\nrecurrence + ridge\n+ annotation", width=0.13, height=0.16, fc=fc4, fontsize=7.7)

    arrow(ax, (0.24, 0.735), (0.33, 0.72))
    arrow(ax, (0.24, 0.535), (0.33, 0.69))
    arrow(ax, (0.24, 0.335), (0.33, 0.40))
    arrow(ax, (0.43, 0.63), (0.43, 0.48))
    arrow(ax, (0.53, 0.41), (0.62, 0.67))
    arrow(ax, (0.71, 0.62), (0.71, 0.52))
    arrow(ax, (0.71, 0.41), (0.71, 0.31))
    arrow(ax, (0.80, 0.48), (0.84, 0.60))
    arrow(ax, (0.80, 0.27), (0.84, 0.36))
    arrow(ax, (0.905, 0.55), (0.905, 0.45))

    ax.text(0.05, 0.10, "Outputs: chr6 linoleic-acid interval, chr9 C16:0 acyl-ACP thioesterase interval and broader recurrent loci.", fontsize=8, color="#444444")
    for path in [MODEL_PNG, MODEL_PDF, MODEL_SVG]:
        fig.savefig(path, dpi=450, bbox_inches="tight")
    plt.close(fig)


def audit_figures() -> pd.DataFrame:
    rows = []
    for label, files in [
        ("overall_workflow", [WORKFLOW_PNG, WORKFLOW_PDF, WORKFLOW_SVG]),
        ("model_structure", [MODEL_PNG, MODEL_PDF, MODEL_SVG]),
    ]:
        rows.append(
            {
                "figure": label,
                "png": str(files[0].relative_to(ROOT)),
                "pdf": str(files[1].relative_to(ROOT)),
                "svg": str(files[2].relative_to(ROOT)),
                "status": "pass" if all(p.exists() and p.stat().st_size > 0 for p in files) else "fail",
                "purpose": "Make the analysis and model structure understandable at a glance.",
            }
        )
    return pd.DataFrame(rows)


def write_report(audit: pd.DataFrame, figure_audit: pd.DataFrame) -> None:
    rows = []
    cols = list(audit.columns)
    rows.append("| " + " | ".join(cols) + " |")
    rows.append("| " + " | ".join(["---"] * len(cols)) + " |")
    for _, row in audit.iterrows():
        rows.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    table = "\n".join(rows)
    text = f"""# ZEAMAP v0.1 Stage 5.36 DOCX Font Optimization Report

日期：2026-06-06

## Verdict

`DOCX_FONT_OPTIMIZED`

## What changed

- Created new optimized Word files instead of overwriting the Stage 5.35 exports.
- Set Latin text to `Times New Roman`.
- Set East Asian text to `宋体`.
- Applied fonts both at style/default level and at run level in `word/document.xml`.

## Outputs

- `{EN_OUT.relative_to(ROOT)}`
- `{ZH_OUT.relative_to(ROOT)}`
- `{WORKFLOW_PNG.relative_to(ROOT)}`
- `{MODEL_PNG.relative_to(ROOT)}`

## Audit

{table}

## Workflow/model figure audit

{figure_audit.to_csv(sep='	', index=False)}
"""
    REPORT.write_text(text.rstrip() + "\n", encoding="utf-8")


def update_docs() -> None:
    readme = README.read_text(encoding="utf-8")
    old = "Stage 5.35 revised bilingual manuscript/figure enrichment。"
    new = "Stage 5.35 revised bilingual manuscript/figure enrichment 和 Stage 5.36 DOCX font optimization。"
    if old in readme:
        readme = readme.replace(old, new)
    if "Stage 5.36 DOCX font optimization" not in readme:
        readme += """

## Stage 5.36 DOCX font optimization

已新增 Word 字体优化版：

- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx`
- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.png`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.png`

优化规则：拉丁文字 `Times New Roman`，中文/东亚文字 `宋体`，同时写入 DOCX styles 和正文 run-level 字体设置。
"""
    README.write_text(readme.rstrip() + "\n", encoding="utf-8")

    progress = PROGRESS.read_text(encoding="utf-8")
    if "阶段 5.36 DOCX font optimization" not in progress:
        progress += """

## 阶段 5.36 DOCX font optimization

状态：已完成。

这一步解决的问题：

- Word 文档打开后字体不稳定或中英文字体混乱。
- 新生成一版字体优化 DOCX，不覆盖上一版，便于比较。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx`
- `docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx`
- `docs/2026-06-06-zeamap-v0-1-stage5-36-docx-font-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-36-workflow-model-figure-audit.tsv`

字体设置：

- 英文/数字：Times New Roman
- 中文/东亚字符：宋体
"""
    PROGRESS.write_text(progress.rstrip() + "\n", encoding="utf-8")


def main() -> None:
    rows = [
        optimize_docx(EN_IN, EN_OUT, "Times New Roman", "宋体"),
        optimize_docx(ZH_IN, ZH_OUT, "Times New Roman", "宋体"),
    ]
    audit = pd.DataFrame(rows)
    audit.to_csv(AUDIT, sep="\t", index=False)
    make_workflow_figure()
    make_model_figure()
    figure_audit = audit_figures()
    figure_audit.to_csv(FIGURE_AUDIT, sep="\t", index=False)
    write_report(audit, figure_audit)
    update_docs()
    print(f"Wrote {EN_OUT}")
    print(f"Wrote {ZH_OUT}")
    print(f"Wrote {AUDIT}")
    print(f"Wrote {FIGURE_AUDIT}")
    print(f"Wrote {WORKFLOW_PNG}")
    print(f"Wrote {MODEL_PNG}")
    print(f"Wrote {REPORT}")


if __name__ == "__main__":
    main()
