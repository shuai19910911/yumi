# ZEAMAP first batch download check

检查日期：2026-06-04

## 结论

第一阶段第一批 8 个目标文件已完整下载到：

```text
/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/
```

文件级校验通过：

- 8 个目标文件均存在。
- 未发现 0 字节文件。
- 当前 SHA256 与本地 `download_manifest_first_batch.md` 记录一致。
- 表达矩阵和群体结构文本文件可读。
- 两个 `.xls` 文件是合法旧版 Excel 文件，不是 HTML 错误页。
- 已在 `bio3` 环境安装 `xlrd/openpyxl`，两个 `.xls` 文件可用 pandas 读取。

## Excel 内容级解析

`ZEAMAP_phenotype_AMP_183_known_Metabolites.xls`：

- sheets: `cv`, `dataset`, `contact`, `site`, `stock`, `descriptor`, `phenotype`
- `stock`: 508 x 13
- `descriptor`: 388 x 7
- `phenotype`: 339 x 254
- phenotype key columns: `*dataset_name`, `*stock_name`, `genus`, `species`, `*sample_id`, `site_name`, `data_year`
- first phenotype traits include `#L_Tyrosine_E1`, `#Vanillin_E1`, `#N_Acetyl_L_glutamic_acid_E1`

`ZEAMAP_phenotype_AMP_agri_AA_Oil.xls`：

- sheets: `cv`, `dataset`, `contact`, `site`, `stock`, `descriptor`, `phenotype`
- `stock`: 508 x 13
- `descriptor`: 71 x 7
- `phenotype`: 476 x 78
- phenotype key columns: `*dataset_name`, `*stock_name`, `genus`, `species`, `*sample_id`, `site_name`, `data_year`
- first phenotype traits include `#AA_Asp`, `#AA_Thr`, `#AA_Ser`, `#AA_Glu`, `#AA_Gly`

## 文件清单

| 模态 | 文件 | 大小 bytes | 行数/状态 | SHA256 状态 |
|---|---|---:|---|---|
| expression | `expression/zmap_expression_ref_b73_exp.tsv` | 6705782 | 43782 行 | matched |
| expression | `expression/zmap_expression_ref_sk_exp.tsv` | 5424304 | 43271 行 | matched |
| expression | `expression/HZS_genes.fmt_FPKM.results` | 3683250 | 40894 行 | matched |
| expression | `expression/Mo1_only7_genes.fmt_FPKM.results` | 1436651 | 38621 行 | matched |
| phenotype/metabolome | `phenotype/ZEAMAP_phenotype_AMP_183_known_Metabolites.xls` | 731648 | Excel CDF V2 | matched |
| phenotype | `phenotype/ZEAMAP_phenotype_AMP_agri_AA_Oil.xls` | 803840 | Excel CDF V2 | matched |
| population | `population/amp_pca.txt` | 17016 | 507 行 | matched |
| population | `population/amp_str.txt` | 15426 | 508 行 | matched |

## 表头抽检

`amp_pca.txt`：

```text
sample PC1 PC2 PC3 POP
```

`amp_str.txt`：

```text
Group Sample K1 K2 K3
```

`zmap_expression_ref_b73_exp.tsv`：

```text
geneID B73_6-7_internode B73_7-8_internode ...
```

`zmap_expression_ref_sk_exp.tsv`：

```text
GeneID SK_15_DAP_Kernel SK_Immature_Ear ...
```

## 下一步

1. 导出两个 Excel 的 `stock`、`descriptor`、`phenotype` sheet 为 TSV。
2. 从 population、phenotype/metabolome、VCF header 里抽取 accession ID。
3. 判断 expression 文件是 accession-level expression 还是 reference/tissue expression；如果是 reference/tissue expression，需要作为 gene annotation/expression prior，而不是 accession-level 强配对模态。
