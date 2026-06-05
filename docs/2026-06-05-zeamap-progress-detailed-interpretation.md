# ZEAMAP 当前进展详细解读

日期：2026-06-05

这份文件是给人读的解释版，不替代 `docs/progress-plan.md`。`progress-plan.md` 更像任务清单，这里解释每一步为什么做、结果代表什么、哪些结论可以相信。

## 一句话总结

我们已经把 ZEAMAP 玉米数据整理成一个可以建模的 `v0.1` accession-level 数据集，并完成了 baseline、trait 筛选、methylation 消融和 genotype 候选解释性分析。当前最可靠的主线不是大模型预训练，而是：

```text
461 个 accession
+ genotype
+ population structure
+ phenotype/metabolome labels
-> 用 ridge/ElasticNet 做 trait prediction benchmark
-> 选出 66 个稳定可预测 traits
-> 后续做 genotype 侧解释和更严格 association
```

## 当前数据到底是什么

当前 `v0.1` 数据集以玉米自交系/accession 为样本单位。

核心样本数：

- 461 个 accession 同时有 genotype、population、至少一种 phenotype/metabolome。
- 236 个 accession 还有 DNA methylation 覆盖。

核心输入：

- genotype：从 `AMP_SNP_anno.vcf.gz` 中筛出的 199,856 个 SNP dosage。
- population：群体结构 PCA 和 structure covariates。
- phenotype/metabolome：318 个数值 trait，其中 317 个能进入 baseline 评估。
- methylation：有 236 个 accession 覆盖，但目前不作为主模型输入。

为什么 expression 没进 `v0.1`：

- 目前下载的 expression 文件是 B73/SK/HZS/Mo17 reference/tissue expression。
- 它们不是 AMP accession-level expression。
- 如果强行把这些 expression 当成 461 个 accession 的表达，会造成错误配对。

## 阶段 0-2：数据整理完成了什么

这几步的重点不是建模，而是确认数据能不能对齐。

已经确认：

- phenotype/metabolome 表里的 accession 能和 population 对齐。
- VCF 里的样本名能和 accession index 对齐。
- genotype + population + phenotype/metabolome 的强配对集合是 461 个 accession。
- methylation 覆盖其中 236 个 accession。
- chromatin accessibility 和 chromatin interaction 目前更像 B73/reference regulatory prior，不适合作为 accession-level 主输入。

这一步的价值：

- 避免把不同 accession 或不同 reference 的数据错配。
- 明确当前能做的是 accession-level 小模型 benchmark，不是全模态预训练。

## 阶段 3：baseline 说明

baseline 的问题是：

```text
只用 genotype 和 population，能不能预测 phenotype/metabolome？
```

第一版 baseline 结果：

- 461 个 accession 被分成 train 322、validation 69、test 70。
- genotype 先做 PCA，100 个 PCs 解释约 50.45% genotype variation。
- 最佳第一版模型是 `genotype_pca_population_ridge`。
- 在 317 个 traits 上，test median Pearson 是 0.331，median R2 是 0.034。

这是什么意思：

- Pearson 0.331 表示模型预测值和真实值有中等偏弱相关。
- R2 0.034 表示整体解释方差很低，但这是所有 trait 混在一起的中位数。
- 有些 trait 很强，尤其 oil traits；有些 trait 很弱。

所以我们没有直接说“可以训练大模型”，而是继续筛 trait。

## 阶段 3.1-3.2：为什么要筛 66 个 robust traits

318 个 trait 不是都适合建模。原因：

- 有的缺失多。
- 有的方差小。
- 有的单次 split 看起来好，但换 split 后不稳定。
- 有的主要被 population structure 解释，不一定有额外 genotype signal。

筛选流程：

1. 从 317 个可评估 trait 中筛出 130 个 selected traits。
2. 用 5 个 random seeds 重复 split 和 baseline。
3. 只保留多次 split 下稳定的 traits，得到 66 个 robust traits。

66 个 robust traits 的组成：

- oil：29 个
- metabolite：16 个
- agronomic：15 个
- amino acid：6 个

重要解释：

- oil traits 最稳定，几乎是当前项目最强信号。
- metabolite traits 数量不少，但整体弱于 oil。
- 这 66 个 traits 是当前后续所有模型比较和消融实验的主评估集合。

## 阶段 3.3：为什么不继续上复杂模型

我们比较了 ridge、ElasticNet 和 small MLP。

结果：

```text
genotype_population_ridge      median Pearson/R2 = 0.498 / 0.204
genotype_population_elasticnet median Pearson/R2 = 0.483 / 0.171
small MLP                      median Pearson/R2 = 0.351 / -0.191
population_ridge               median Pearson/R2 = 0.332 / 0.085
```

解读：

- ridge 最稳，是当前主模型。
- ElasticNet 接近 ridge，但略低。
- small MLP 明显过拟合或不稳定，R2 甚至为负。
- genotype+population 明显强于 population-only，说明 genotype 确实提供额外信号。

结论：

当前样本量只有 461。对这种规模，线性正则模型比小神经网络更可靠。继续加深模型结构不划算。

## 阶段 4：methylation 为什么没有进入主模型

methylation 只有 236 个 accession，比主数据集小一半。我们做了三层测试。

### 4.1 全局 methylation summary

做法：

- 对 mCG/mCHG/mCHH 做 accession-level 全局 summary。

结果：

```text
genotype+population+methylation median Pearson/R2 = 0.496 / 0.173
genotype+population             median Pearson/R2 = 0.490 / 0.173
```

解释：

- Pearson 只涨了 0.006。
- R2 几乎不变。
- 全局 methylation summary 太粗，不值得作为主输入。

### 4.2 gene/promoter/cis-window methylation PCA

做法：

- 用 B73 RefGen_v4 annotation 定义 gene body、promoter 2kb、cis +/-10kb。
- 对 mCG/mCHG/mCHH 做 gene-level 聚合。
- 再用 PCA 压成 90 个 methylation PCs。

结果：

```text
genotype+population+gene methylation PCA median Pearson/R2 = 0.496 / 0.199
genotype+population                      median Pearson/R2 = 0.490 / 0.173
```

解释：

- R2 有小幅提升。
- 说明 gene-level methylation 比全局 summary 更合理。
- 但提升仍然小，不足以让 methylation 成为主输入。

### 4.3 sparse gene-window methylation

做法：

- 只针对 methylation PCA 增益较高的 10 个 traits。
- 构建 4500 个 gene-window methylation 候选特征。
- 每个 seed 只在 train split 中筛选特征，再用 ElasticNet 评估 test。

结果：

```text
gene methylation PCA ridge      median Pearson/R2 = 0.449 / 0.160
genotype+population ridge       median Pearson/R2 = 0.414 / 0.106
sparse methylation ElasticNet   median Pearson/R2 = 0.338 / 0.025
```

解释：

- raw gene-window methylation 稀疏模型反而最差。
- 这通常说明样本量太小、特征太多、选择不稳定。
- sparse feature 表可以当候选解释表，但不能当性能提升证据。

最终 methylation 决策：

- 不进入 v0.1 主模型。
- 保留 coverage mask。
- 保留 methylation PCA 作为辅助消融。
- sparse selected features 只作为候选 gene/window 解释材料。

## v0.1 final benchmark 代表什么

final benchmark 是当前项目最重要的稳定结论。

最终主模型：

```text
genotype_population_ridge
```

主评估集合：

```text
66 个 robust traits
```

整体结果：

```text
median Pearson = 0.498
median R2      = 0.204
positive R2 fraction = 0.979
```

family 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

解读：

- oil traits 是最强、最稳定的主线。
- agronomic traits 有一定信号。
- metabolite 和 amino acid 可做辅助，但不要作为第一优先。
- 当前数据适合做小模型 benchmark 和解释性分析，不适合直接上大规模预训练。

## genotype attribution screen 说明

我们做了一个轻量的候选解释性 screen。

目的：

```text
找出 top traits 中哪些 SNP 和 trait 在 train split 内稳定相关，
并把 SNP 映射到附近基因。
```

做法：

- 选 final benchmark 中 ridge median Pearson 最高的 15 个 traits。
- 每个 seed 只用 train split，不用 test split 算相关。
- 每个 trait/seed 取 top 200 SNP。
- 跨 5 个 seeds 聚合。
- 每个 trait 输出 top 50 SNP。
- 用 B73 RefGen_v4 映射到 gene body、promoter、10kb cis-window 或 nearest gene。

结果：

- SNP-trait candidates：750 行。
- 674 个 SNP 在 5 个 seeds 都入选。
- 745 个 SNP 至少 4 个 seeds 入选。
- gene relation：gene body 488、cis-window 147、promoter 59、nearest 56。
- gene-level candidates：587 行。

怎么理解：

- 这是候选解释性 screen，不是正式 GWAS。
- 它能告诉我们“哪些位点/基因值得优先看”。
- 它不能直接证明这些 SNP 是 causal variant。

下一步若做正式解释：

- 加 population covariate residualization。
- 做 LD clumping。
- 做 permutation 或 FDR 控制。
- 加 gene function annotation。
- 对 oil traits 优先做 trait family-specific validation。

## 当前可以相信的结论

可以较放心使用：

- `v0.1` 数据集有 461 个强配对 accession。
- 66 个 robust traits 是当前主评估集合。
- `genotype_population_ridge` 是当前最稳主模型。
- oil traits 是当前最适合深入分析的 trait family。
- methylation 不应作为 v0.1 主输入。

需要谨慎使用：

- methylation sparse selected features 只能作为候选解释表。
- genotype attribution SNP/gene candidates 不是正式 GWAS 结果。
- metabolite/amino acid family 的结论弱于 oil family。

不应该现在做：

- 直接训练大型多模态 transformer。
- 把 B73/SK/HZS/Mo17 reference expression 当成 AMP accession expression。
- 把 raw methylation gene-window features 加进主模型。
- 宣称 genotype attribution candidates 是 causal genes。

## 建议下一步

优先级 1：

- 做 oil traits 的严格 genotype association/attribution。
- 加 population covariate correction、LD clumping 和候选基因注释。

优先级 2：

- 构建 gene-window genotype burden features。
- 比较 SNP-level、gene-window-level 和 PCA-level genotype representation。

优先级 3：

- 准备结果汇报图表：trait family performance、top traits、methylation ablation、候选 gene table。

暂缓：

- 大模型预训练。
- 全量 epigenome raw feature 进入主模型。
- raw SRA/FASTQ 处理。
