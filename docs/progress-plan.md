# Yumi progress plan

更新日期：2026-06-06

## 当前项目一句话

这个项目现在只做一件事：

```text
用 ZEAMAP 玉米数据，做一个 accession 水平的多性状预测模型文章。
```

通俗理解：

```text
给每个玉米材料一套基因型、群体结构、部分甲基化信息，
让模型预测它的表型和代谢性状，
然后系统比较哪些模型好、哪些性状好预测、哪些数据模态有帮助。
```

## 已经纠正的方向

之前项目走偏到了：

```text
油脂性状 GWAS -> 候选基因 -> 投稿包
```

这个方向已经降级。以后不再把它作为主线。

新的主线是：

```text
数据整理
-> 多性状预测模型
-> 模型比较
-> trait family 可预测性分析
-> methylation 消融
-> 稳健性评估
-> 少量生物学解释
-> 模型方向论文
```

GWAS 和候选基因只作为辅助解释。例如模型发现 oil traits 最好预测时，可以用 GWAS 结果说明这些性状确实有较强遗传信号。

## 当前保留的核心数据

核心 processed dataset：

```text
data/processed/v0_1/
```

当前数据规模：

```text
461 个 accession 有 genotype + population + phenotype/metabolome
236 个 accession 额外有 methylation
199,856 个 SNP
318 个 numeric traits
66 个 robust traits 进入最终 benchmark
```

这些数据足够做严谨的小样本模型 benchmark，但不适合现在直接做大模型预训练或复杂 transformer。

## 当前已经完成的模型工作

### 1. 样本和数据统一

已经完成：

- 检查 ZEAMAP 下载文件。
- 统一 phenotype、population、VCF、methylation 的 accession 名字。
- 建立统一样本索引。
- 构建 v0.1 processed dataset。

关键文件：

```text
data/metadata/zeamap_accession_index.tsv
data/processed/v0_1/
docs/2026-06-04-zeamap-v0-1-build-report.md
```

### 2. 基础预测 benchmark

已经比较：

- mean baseline
- population-only ridge
- genotype PCA ridge
- genotype PCA + population ridge

当前主模型：

```text
genotype_population_ridge
```

核心结果：

```text
66 个 robust traits
median Pearson = 0.498
median R2 = 0.204
positive R2 fraction = 0.979
```

关键文件：

```text
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
```

### 3. 哪些性状更容易预测

当前最清楚的结果：

```text
oil traits 是最好预测的一类性状。
```

trait family 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

这应该成为模型文章的一个主结果：不同性状家族的可预测性明显不同。

### 4. 多随机种子稳健性

已经做了 repeated seed evaluation。

目的：

```text
证明结果不是某一次 train/test 划分碰巧得到的。
```

关键文件：

```text
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_model_summary.tsv
results/v0_1_baseline/robust_selected_traits.tsv
```

### 5. 轻量模型比较

已经比较：

- ridge
- ElasticNet
- small MLP

当前结论：

```text
ridge/ElasticNet 比 small MLP 更稳。
```

原因很直接：

```text
样本只有 461 个，但 SNP 接近 20 万个。
在这种“小样本、高维特征”场景下，强正则化线性模型更稳。
```

关键文件：

```text
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/lightweight_model_summary.tsv
```

### 6. methylation 消融

已经测试：

- global methylation summary
- gene/promoter/cis-window methylation PCA
- sparse gene-window methylation selection

当前结论：

```text
methylation 只能作为辅助模态，不能作为 v0.1 主模型输入。
```

主要原因：

```text
只有 236 个 accession 有 methylation，配对样本太少。
```

关键文件：

```text
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
```

### 7. 可解释性辅助结果

已经有：

- genotype attribution
- oil traits GEMMA LMM GWAS
- candidate loci annotation

但这些只放在解释层，不再作为论文主线。

保留原因：

```text
模型发现 oil traits 好预测后，可以用这些结果辅助解释遗传信号。
```

## 已经清理的旧方向内容

已经从仓库清理：

- Stage 5.x 投稿包文档。
- cover letter、reviewer suggestion、release plan、Zenodo metadata。
- 作者、单位、基金、COI 模板。
- 以 GWAS 候选基因为主的 manuscript draft。
- Stage 5 投稿包装脚本。
- 旧投稿包装图表和 manuscript tables。
- 日志和 Python 缓存。

清理后，仓库入口不再围绕“GWAS 投稿包”，而是围绕“模型文章”。

## 后续只做这条主线

下一步任务按优先级：

1. 重新生成模型方向主图。
2. 写模型论文初稿。
3. 补充模型结果表。
4. 把 methylation 消融和 robustness 画成清楚的图。
5. 把 GWAS/candidate loci 缩成一个辅助解释小节。
6. 生成新的中文和英文模型文章版本。

## 论文建议标题

暂定英文标题：

```text
A conservative accession-level benchmark for maize multi-trait prediction using ZEAMAP
```

中文理解：

```text
基于 ZEAMAP 的玉米 accession 水平多性状预测模型基准研究
```

## 当前判断

当前项目不是“没做完”，而是要把已经完成的工作重新组织成正确故事。

最有论文价值的结果是：

```text
ZEAMAP 公共数据可以整理成干净的 accession-level 模型数据集；
genotype + population 对多类性状有稳定预测能力；
oil traits 最容易预测；
在当前样本量下，ridge/ElasticNet 比 small MLP 更可靠；
methylation 覆盖不足，暂时只能作为辅助模态；
GWAS 结果可作为 oil traits 可预测性的生物学解释。
```
