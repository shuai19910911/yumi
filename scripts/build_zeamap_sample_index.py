#!/usr/bin/env python3
"""Build ZEAMAP first-batch sample/accession index tables."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


ROOT = Path("/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP")
OUT = Path("data/metadata")
DOC = Path("docs/2026-06-04-zeamap-sample-id-check.md")


FILES = {
    "b73_expression": ROOT / "expression/zmap_expression_ref_b73_exp.tsv",
    "sk_expression": ROOT / "expression/zmap_expression_ref_sk_exp.tsv",
    "hzs_expression": ROOT / "expression/HZS_genes.fmt_FPKM.results",
    "mo17_expression": ROOT / "expression/Mo1_only7_genes.fmt_FPKM.results",
    "pca": ROOT / "population/amp_pca.txt",
    "structure": ROOT / "population/amp_str.txt",
    "metabolite": ROOT / "phenotype/ZEAMAP_phenotype_AMP_183_known_Metabolites.xls",
    "agri_aa_oil": ROOT / "phenotype/ZEAMAP_phenotype_AMP_agri_AA_Oil.xls",
}


def norm_id(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).strip()
    if text.endswith(".0") and re.fullmatch(r"\d+\.0", text):
        text = text[:-2]
    return re.sub(r"\s+", "", text).upper()


def read_header(path: Path) -> list[str]:
    return pd.read_csv(path, sep="\t", nrows=0).columns.tolist()


def infer_expression_columns() -> pd.DataFrame:
    rows = []
    for source, path in [
        ("zmap_expression_ref_b73_exp.tsv", FILES["b73_expression"]),
        ("zmap_expression_ref_sk_exp.tsv", FILES["sk_expression"]),
        ("HZS_genes.fmt_FPKM.results", FILES["hzs_expression"]),
        ("Mo1_only7_genes.fmt_FPKM.results", FILES["mo17_expression"]),
    ]:
        cols = read_header(path)
        gene_col, sample_cols = cols[0], cols[1:]
        for col in sample_cols:
            inferred_line = col.split("_", 1)[0]
            tissue = col.split("_", 1)[1] if "_" in col else ""
            rows.append(
                {
                    "source_file": source,
                    "matrix_gene_id_column": gene_col,
                    "sample_column": col,
                    "sample_column_norm": norm_id(col),
                    "inferred_line": inferred_line,
                    "inferred_line_norm": norm_id(inferred_line),
                    "tissue_or_stage": tissue,
                    "sample_role": "reference_tissue_expression",
                    "accession_panel_sample": False,
                    "notes": "Column is a reference line plus tissue/stage label, not an AMP accession sample.",
                }
            )
    return pd.DataFrame(rows)


def read_population() -> tuple[pd.DataFrame, pd.DataFrame]:
    pca = pd.read_csv(FILES["pca"], sep="\t", dtype=str)
    struct = pd.read_csv(FILES["structure"], sep="\t", dtype=str)
    pca["accession_id_raw"] = pca["sample"]
    pca["accession_id_norm"] = pca["sample"].map(norm_id)
    struct["accession_id_raw"] = struct["Sample"]
    struct["accession_id_norm"] = struct["Sample"].map(norm_id)
    return pca, struct


def read_phenotype_book(path: Path, prefix: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    stock = pd.read_excel(path, sheet_name="stock", dtype=str)
    desc = pd.read_excel(path, sheet_name="descriptor", dtype=str)
    pheno = pd.read_excel(path, sheet_name="phenotype", dtype=str)

    stock = stock.rename(columns={"*stock_name": "stock_name", "alias": "alias"})
    pheno = pheno.rename(columns={"*stock_name": "stock_name", "*sample_id": "sample_id"})

    stock["stock_name_norm"] = stock["stock_name"].map(norm_id)
    stock["alias_norm"] = stock.get("alias", pd.Series(index=stock.index, dtype=str)).map(norm_id)
    pheno["stock_name_norm"] = pheno["stock_name"].map(norm_id)
    pheno["sample_id_norm"] = pheno["sample_id"].map(norm_id)

    stock["source_book"] = prefix
    desc["source_book"] = prefix
    pheno["source_book"] = prefix
    return stock, desc, pheno


def add_presence(rows: dict[str, dict[str, object]], ids: pd.Series, raw: pd.Series, column: str) -> None:
    for norm, raw_id in zip(ids, raw):
        if not norm:
            continue
        row = rows.setdefault(norm, {"accession_id_norm": norm, "raw_ids": set()})
        row["raw_ids"].add(str(raw_id))
        row[column] = True


def markdown_table(df: pd.DataFrame) -> str:
    cols = list(df.columns)
    lines = [
        "| " + " | ".join(cols) + " |",
        "| " + " | ".join(["---"] * len(cols)) + " |",
    ]
    for _, row in df.iterrows():
        lines.append("| " + " | ".join(str(row[col]) for col in cols) + " |")
    return "\n".join(lines)


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    DOC.parent.mkdir(parents=True, exist_ok=True)

    expression_cols = infer_expression_columns()
    pca, struct = read_population()
    met_stock, met_desc, met_pheno = read_phenotype_book(FILES["metabolite"], "metabolite_183_known")
    agri_stock, agri_desc, agri_pheno = read_phenotype_book(FILES["agri_aa_oil"], "agri_aa_oil")

    sources: dict[str, dict[str, object]] = {}
    add_presence(sources, pca["accession_id_norm"], pca["accession_id_raw"], "population_pca")
    add_presence(sources, struct["accession_id_norm"], struct["accession_id_raw"], "population_structure")
    add_presence(sources, met_stock["stock_name_norm"], met_stock["stock_name"], "metabolite_stock")
    add_presence(sources, met_pheno["stock_name_norm"], met_pheno["stock_name"], "metabolite_phenotype_stock_name")
    add_presence(sources, met_pheno["sample_id_norm"], met_pheno["sample_id"], "metabolite_phenotype_sample_id")
    add_presence(sources, agri_stock["stock_name_norm"], agri_stock["stock_name"], "agri_stock")
    add_presence(sources, agri_pheno["stock_name_norm"], agri_pheno["stock_name"], "agri_phenotype_stock_name")
    add_presence(sources, agri_pheno["sample_id_norm"], agri_pheno["sample_id"], "agri_phenotype_sample_id")

    bool_cols = [
        "population_pca",
        "population_structure",
        "metabolite_stock",
        "metabolite_phenotype_stock_name",
        "metabolite_phenotype_sample_id",
        "agri_stock",
        "agri_phenotype_stock_name",
        "agri_phenotype_sample_id",
    ]
    rows = []
    for norm, row in sorted(sources.items()):
        item = {k: False for k in bool_cols}
        item.update(row)
        item["raw_ids"] = "|".join(sorted(item["raw_ids"]))
        item["has_population"] = item["population_pca"] or item["population_structure"]
        item["has_metabolite"] = item["metabolite_phenotype_stock_name"] or item["metabolite_phenotype_sample_id"]
        item["has_agri_aa_oil"] = item["agri_phenotype_stock_name"] or item["agri_phenotype_sample_id"]
        item["has_any_phenotype"] = item["has_metabolite"] or item["has_agri_aa_oil"]
        item["strong_pair_population_phenotype"] = item["has_population"] and item["has_any_phenotype"]
        rows.append(item)
    accession_index = pd.DataFrame(rows)

    summary_rows = []
    for name, df, id_col in [
        ("population_pca", pca, "accession_id_norm"),
        ("population_structure", struct, "accession_id_norm"),
        ("metabolite_stock", met_stock, "stock_name_norm"),
        ("metabolite_phenotype_stock_name", met_pheno, "stock_name_norm"),
        ("metabolite_phenotype_sample_id", met_pheno, "sample_id_norm"),
        ("agri_stock", agri_stock, "stock_name_norm"),
        ("agri_phenotype_stock_name", agri_pheno, "stock_name_norm"),
        ("agri_phenotype_sample_id", agri_pheno, "sample_id_norm"),
    ]:
        summary_rows.append(
            {
                "table": name,
                "rows": len(df),
                "unique_normalized_ids": int(df[id_col].replace("", pd.NA).dropna().nunique()),
                "id_column": id_col,
            }
        )
    summary = pd.DataFrame(summary_rows)

    expression_cols.to_csv(OUT / "zeamap_expression_sample_columns.tsv", sep="\t", index=False)
    accession_index.to_csv(OUT / "zeamap_accession_index.tsv", sep="\t", index=False)
    summary.to_csv(OUT / "zeamap_table_id_summary.tsv", sep="\t", index=False)

    # Export phenotype metadata sheets for downstream joins.
    export_dir = OUT / "phenotype_sheets"
    export_dir.mkdir(parents=True, exist_ok=True)
    for name, df in [
        ("metabolite_stock.tsv", met_stock),
        ("metabolite_descriptor.tsv", met_desc),
        ("metabolite_phenotype.tsv", met_pheno),
        ("agri_aa_oil_stock.tsv", agri_stock),
        ("agri_aa_oil_descriptor.tsv", agri_desc),
        ("agri_aa_oil_phenotype.tsv", agri_pheno),
    ]:
        df.to_csv(export_dir / name, sep="\t", index=False)

    pca_ids = set(pca["accession_id_norm"])
    struct_ids = set(struct["accession_id_norm"])
    met_pheno_ids = set(met_pheno["stock_name_norm"]) | set(met_pheno["sample_id_norm"])
    agri_pheno_ids = set(agri_pheno["stock_name_norm"]) | set(agri_pheno["sample_id_norm"])
    met_stock_ids = set(met_stock["stock_name_norm"])
    agri_stock_ids = set(agri_stock["stock_name_norm"])

    pop_ids = pca_ids | struct_ids
    any_pheno_ids = met_pheno_ids | agri_pheno_ids
    pop_met_count = len(pop_ids & met_pheno_ids)
    pop_agri_count = len(pop_ids & agri_pheno_ids)
    pop_any_pheno_count = len(pop_ids & any_pheno_ids)
    pop_both_pheno_count = len(pop_ids & met_pheno_ids & agri_pheno_ids)

    report = f"""# ZEAMAP sample ID and accession naming check

检查日期：2026-06-04

## 结论

- population 表使用材料名作为 accession ID：`amp_pca.txt` 字段为 `sample`，`amp_str.txt` 字段为 `Sample`。
- 两个 phenotype Excel 使用 `*stock_name` / `*sample_id` 作为样本 ID；ID 类型是混合型，既有数字样 ID，也有材料名样 ID，例如 `150`、`05W002`、`CIMBL47`。
- phenotype 的 `stock` sheet 与 `phenotype` sheet 使用同一套 `*stock_name` 命名规则，可直接在 Excel 内部对齐。
- population 与 phenotype 在 normalized exact ID 层面存在大量交集：population + metabolite 为 {pop_met_count} 个，population + agri/AA/Oil 为 {pop_agri_count} 个，population + 任一 phenotype/metabolome 为 {pop_any_pheno_count} 个。
- 当前第一批 expression 文件不是 AMP accession 面板表达矩阵，而是 B73/SK/HZS/Mo17 参考基因型的组织/时期表达矩阵。它们应作为 gene-level reference expression prior 或 annotation，不应计入 accession-level 强配对模态。
- 第一批数据已经可以形成 accession-level `population + phenotype/metabolome` 的强配对索引，但 expression 仍不是 accession-level 强配对模态。

## 输出文件

- `data/metadata/zeamap_accession_index.tsv`
- `data/metadata/zeamap_table_id_summary.tsv`
- `data/metadata/zeamap_expression_sample_columns.tsv`
- `data/metadata/phenotype_sheets/*.tsv`

## 表级 ID 摘要

{markdown_table(summary)}

## 关键交集

- `amp_pca` vs `amp_str`: {len(pca_ids & struct_ids)}
- metabolite phenotype IDs vs metabolite stock IDs: {len(met_pheno_ids & met_stock_ids)}
- agri/AA/Oil phenotype IDs vs agri stock IDs: {len(agri_pheno_ids & agri_stock_ids)}
- population IDs vs metabolite phenotype IDs: {pop_met_count}
- population IDs vs agri/AA/Oil phenotype IDs: {pop_agri_count}
- population IDs vs any phenotype/metabolome IDs: {pop_any_pheno_count}
- population IDs vs both phenotype/metabolome groups: {pop_both_pheno_count}
- metabolite phenotype IDs vs agri/AA/Oil phenotype IDs: {len(met_pheno_ids & agri_pheno_ids)}

## Expression 列命名规则

Expression 矩阵首列为 gene ID，后续列为 `line_tissue/stage`：

- B73: {int((expression_cols["inferred_line"] == "B73").sum())} columns
- SK: {int((expression_cols["inferred_line"] == "SK").sum())} columns
- HZS: {int((expression_cols["inferred_line"] == "HZS").sum())} columns
- Mo17: {int((expression_cols["inferred_line"] == "Mo17").sum())} columns

## 下一步

1. 以 `data/metadata/zeamap_accession_index.tsv` 中 `strong_pair_population_phenotype == True` 的 {pop_any_pheno_count} 个 accession 作为第一版 phenotype/population 配对集合。
2. 第二批下载 VCF 后，用 VCF sample header 与该索引做交集，确定 genotype 可配对样本数。
3. Expression 当前只作为 B73/SK/HZS/Mo17 reference/tissue expression，不进入 accession-level 强配对集合。
4. 继续核验是否存在 AMP accession-level expression matrix；如果没有，第一版模型应定位为 genotype/population/phenotype/metabolome + reference-expression-prior。
"""
    DOC.write_text(report, encoding="utf-8")


if __name__ == "__main__":
    main()
