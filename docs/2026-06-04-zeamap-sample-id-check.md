# ZEAMAP sample ID and accession naming check

检查日期：2026-06-04

## 结论

- population 表使用材料名作为 accession ID：`amp_pca.txt` 字段为 `sample`，`amp_str.txt` 字段为 `Sample`。
- 两个 phenotype Excel 使用 `*stock_name` / `*sample_id` 作为样本 ID；ID 类型是混合型，既有数字样 ID，也有材料名样 ID，例如 `150`、`05W002`、`CIMBL47`。
- phenotype 的 `stock` sheet 与 `phenotype` sheet 使用同一套 `*stock_name` 命名规则，可直接在 Excel 内部对齐。
- population 与 phenotype 在 normalized exact ID 层面存在大量交集：population + metabolite 为 320 个，population + agri/AA/Oil 为 459 个，population + 任一 phenotype/metabolome 为 461 个。
- 当前第一批 expression 文件不是 AMP accession 面板表达矩阵，而是 B73/SK/HZS/Mo17 参考基因型的组织/时期表达矩阵。它们应作为 gene-level reference expression prior 或 annotation，不应计入 accession-level 强配对模态。
- 第一批数据已经可以形成 accession-level `population + phenotype/metabolome` 的强配对索引，但 expression 仍不是 accession-level 强配对模态。

## 输出文件

- `data/metadata/zeamap_accession_index.tsv`
- `data/metadata/zeamap_table_id_summary.tsv`
- `data/metadata/zeamap_expression_sample_columns.tsv`
- `data/metadata/phenotype_sheets/*.tsv`

## 表级 ID 摘要

| table | rows | unique_normalized_ids | id_column |
| --- | --- | --- | --- |
| population_pca | 507 | 507 | accession_id_norm |
| population_structure | 507 | 507 | accession_id_norm |
| metabolite_stock | 508 | 508 | stock_name_norm |
| metabolite_phenotype_stock_name | 339 | 339 | stock_name_norm |
| metabolite_phenotype_sample_id | 339 | 339 | sample_id_norm |
| agri_stock | 508 | 508 | stock_name_norm |
| agri_phenotype_stock_name | 476 | 476 | stock_name_norm |
| agri_phenotype_sample_id | 476 | 476 | sample_id_norm |

## 关键交集

- `amp_pca` vs `amp_str`: 507
- metabolite phenotype IDs vs metabolite stock IDs: 339
- agri/AA/Oil phenotype IDs vs agri stock IDs: 476
- population IDs vs metabolite phenotype IDs: 320
- population IDs vs agri/AA/Oil phenotype IDs: 459
- population IDs vs any phenotype/metabolome IDs: 461
- population IDs vs both phenotype/metabolome groups: 318
- metabolite phenotype IDs vs agri/AA/Oil phenotype IDs: 326

## Expression 列命名规则

Expression 矩阵首列为 gene ID，后续列为 `line_tissue/stage`：

- B73: 23 columns
- SK: 9 columns
- HZS: 12 columns
- Mo17: 5 columns

## 下一步

1. 以 `data/metadata/zeamap_accession_index.tsv` 中 `strong_pair_population_phenotype == True` 的 461 个 accession 作为第一版 phenotype/population 配对集合。
2. 第二批下载 VCF 后，用 VCF sample header 与该索引做交集，确定 genotype 可配对样本数。
3. Expression 当前只作为 B73/SK/HZS/Mo17 reference/tissue expression，不进入 accession-level 强配对集合。
4. 继续核验是否存在 AMP accession-level expression matrix；如果没有，第一版模型应定位为 genotype/population/phenotype/metabolome + reference-expression-prior。
