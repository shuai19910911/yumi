# yumi

ZEAMAP 玉米多性状预测模型项目。

## 当前重新定位

这个项目的目标需要改回来：不是写一篇以 GWAS 候选基因为主的文章，而是写一篇**模型方向文章**。

更准确地说，我们要做的是：

```text
用 ZEAMAP 玉米公共数据，构建一个 accession-level 多性状预测数据集，
比较不同模型和不同数据模态对玉米 phenotype/metabolome 的预测能力，
分析哪些性状最可预测、哪些模态有用、模型为什么有效，
最后形成一篇以 genotype-to-phenotype prediction / multi-trait modelling 为主线的论文。
```

GWAS 和候选基因不是主线，只能作为模型结果的辅助解释。例如：如果模型发现 oil traits 最可预测，可以用 GWAS 或候选区间解释“为什么 oil traits 有强遗传信号”。但文章不能再写成“我们发现了 chr6/chr9 候选基因”的 GWAS 论文。

## 一句话说明

我们现在要做的是：

```text
ZEAMAP 数据整理
-> 构建 v0.1 模型数据集
-> 设计 genotype/population/methylation 等输入模态
-> 比较 ridge、ElasticNet、MLP 等模型
-> 做多随机种子稳健性评估
-> 分析哪些性状、哪些模态、哪些模型最有效
-> 用可解释性和少量 GWAS 结果辅助说明模型学到了什么
-> 写成模型方法/模型应用文章
```

## 为什么要改方向

之前工作走偏到了“油脂性状 GWAS + 候选基因投稿包”。这条路线不是完全没价值，但它不是当前项目最核心的目标。

现在重新判断后，模型文章更合适，原因是：

- 我们已经构建了一个干净的 ZEAMAP v0.1 accession-level 数据集。
- 已经完成了多性状 prediction benchmark。
- 已经比较了 ridge、ElasticNet、小 MLP、population-only 等模型。
- 已经做了 methylation 消融和多随机种子稳健性。
- 当前样本量不适合大模型预训练，但适合做一个严谨的小样本多性状预测模型研究。
- GWAS 可以作为解释模型信号的辅助分析，而不是论文主线。

## 当前可用数据

核心数据集：

```text
data/processed/v0_1/
```

当前规模：

```text
461 accessions
199,856 SNPs
318 numeric phenotype/metabolome traits
236 accessions with methylation coverage
```

数据模态判断：

- `genotype`：主输入，当前最重要。
- `population`：重要协变量/基线特征。
- `phenotype/metabolome`：预测目标。
- `methylation`：辅助模态，只能在 236 个 accession 子集中评估。
- `expression`：当前不是 AMP accession-level expression，暂不作为主模型输入。
- `GWAS/candidate loci`：只作为模型解释和生物学解释的辅助模块。

## 已经完成的模型相关工作

### 1. 数据整理

已经完成：

- 检查 ZEAMAP 下载文件是否可读。
- 统一 phenotype、population、VCF、methylation 等表的 accession 命名。
- 构建统一样本索引。
- 构建 v0.1 processed dataset。

主要产出：

```text
data/metadata/zeamap_accession_index.tsv
data/processed/v0_1/
docs/2026-06-04-zeamap-v0-1-build-report.md
```

### 2. 基础预测模型

已经比较过：

- mean baseline
- population-only ridge
- genotype PCA ridge
- genotype PCA + population ridge

核心结论：

```text
genotype + population 的 ridge 模型最稳。
```

当前整体结果：

```text
66 robust traits
median Pearson = 0.498
median R2 = 0.204
positive R2 fraction = 0.979
```

主要结果文件：

```text
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
```

### 3. 性状家族分析

已经发现：

```text
oil traits 是最容易预测的性状家族。
```

trait family 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

这在模型文章里很重要，因为它说明：

```text
不同类型性状的可预测性不同，模型对 oil/fatty-acid traits 最有效。
```

主要结果文件：

```text
results/v0_1_baseline/selected_trait_family_summary.tsv
results/v0_1_baseline/robustness_trait_summary.tsv
results/v0_1_baseline/top_predictable_traits.tsv
```

### 4. 多随机种子稳健性

已经做了 repeated seed evaluation。

目的：

```text
不是只看一次 train/test split，而是看模型表现是否稳定。
```

这对模型文章很关键，因为审稿人会关心结果是不是偶然划分造成的。

主要结果文件：

```text
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_model_summary.tsv
results/v0_1_baseline/robust_selected_traits.tsv
```

### 5. 轻量模型比较

已经比较过 ridge、ElasticNet 和 small MLP。

当前结论：

```text
在 461 个 accession 的样本量下，ridge/ElasticNet 比 small MLP 更稳。
```

这不是说神经网络没用，而是说明：

```text
当前数据规模更适合正则化线性模型。
复杂模型需要更多 accession、更完整的多模态配对数据。
```

主要结果文件：

```text
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/lightweight_model_summary.tsv
```

### 6. methylation 消融

已经评估过 methylation 的几种用法：

- global methylation summary
- gene/promoter/cis-window methylation PCA
- sparse gene-window methylation selection

当前结论：

```text
methylation 在当前数据里只能作为辅助模态。
236 个 accession 的覆盖不足以支撑强多模态主模型。
```

主要结果文件：

```text
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
```

### 7. 可解释性与生物学辅助分析

已经做过：

- genotype attribution
- oil traits GEMMA LMM GWAS
- candidate loci annotation

这些不再作为主线，而是作为模型文章中的解释模块：

```text
模型发现 oil traits 最可预测。
GWAS/候选区间可以辅助说明这些性状确实有强遗传信号。
```

保留但降级的结果：

```text
results/v0_1_baseline/genotype_attribution_gene_summary.tsv
results/v0_1_baseline/genotype_attribution_snp_summary.tsv
results/v0_1_baseline/gemma_lmm_v0_1/
```

## 新论文目标

建议新文章方向：

```text
A conservative accession-level genotype-to-phenotype prediction benchmark for maize traits using ZEAMAP
```

中文理解：

```text
基于 ZEAMAP 的玉米 accession 水平多性状预测基准研究
```

文章核心问题：

1. ZEAMAP 公共数据能不能整理成可靠的 accession-level 模型数据集？
2. genotype + population 能不能预测 phenotype/metabolome？
3. 哪些性状最容易被预测？
4. ridge、ElasticNet、小 MLP 谁更适合当前样本量？
5. methylation 在当前配对样本不足的情况下有没有增益？
6. 模型预测最好的 oil traits 是否能通过遗传信号得到辅助解释？

## 新文章结构

建议主线：

```text
Introduction
  为什么公共多组学数据不能直接拿来建模
  为什么需要 accession-level harmonization
  为什么小样本下要先做稳健 benchmark

Results
  1. ZEAMAP v0.1 accession-level dataset
  2. Genotype + population prediction benchmark
  3. Trait family predictability differences
  4. Model comparison: ridge / ElasticNet / MLP
  5. Methylation ablation under partial coverage
  6. Model interpretation: oil traits and genetic signal

Discussion
  当前模型路线适合什么
  为什么不是大模型
  为什么 oil traits 最强
  methylation 为什么暂时不能作为主模态
  后续如何扩展到更大 accession、多模态和预训练模型
```

## 需要保留的核心文件

这些是模型文章主线需要保留的：

```text
data/metadata/
data/processed/v0_1/
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
results/v0_1_baseline/selected_trait_family_summary.tsv
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_trait_summary.tsv
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
scripts/build_zeamap_sample_index.py
scripts/build_zeamap_v0_1_dataset.py
scripts/run_zeamap_v0_1_baseline.py
scripts/run_zeamap_v0_1_robustness.py
scripts/run_zeamap_v0_1_lightweight_models.py
scripts/run_zeamap_v0_1_methylation_subset.py
scripts/run_zeamap_v0_1_gene_methylation_pca.py
scripts/run_zeamap_v0_1_sparse_methylation_selection.py
```

## 已经清理或降级的信息

下面这些内容已经从主线中清理或降级：

- 大量 `Stage 5.x` 投稿包文件。
- cover letter、journal route、reviewer suggestion、Zenodo release draft。
- 以 chr6/chr9 候选基因为主的论文版本。
- 最终投稿 gate、人类作者信息模板、release checklist。
- 把 GEMMA GWAS 写成主结果的图表和段落。

当前保留少量 GWAS 结果，只用于解释模型为什么对 oil traits 更有效。

## 下一步计划

下一步应该做三件事：

1. 重画模型方向图表

重点画清楚：数据怎么进入模型、模型怎么比较、robust traits 怎么筛出来、methylation 怎么做消融。

2. 重写模型论文稿

围绕 prediction benchmark、model comparison、trait family predictability、methylation ablation 和 interpretation 写新稿。

3. 补模型结果表

把 final benchmark、trait family、model comparison、methylation ablation、robustness 组织成模型文章主表和补充表。

## 当前注意事项

当前最重要的是不要再继续往“GWAS 候选基因投稿包”方向扩展。

正确方向是：

```text
模型数据集 + 多性状预测 + 模型比较 + 模态消融 + 稳健性 + 可解释性
```

GWAS 只作为解释模型结果的一小部分。
