# ZEAMAP 当前进展白话解读

日期：2026-06-05

这份文件只回答四个问题：

1. 我们现在做到哪了？
2. 每个结果是什么意思？
3. 哪些结论可以写论文？
4. 下一步为什么要这样做？

## 1. 现在做到哪了

我们已经完成了一个从数据到论文候选结果的 v0.1 闭环：

```text
下载 ZEAMAP processed data
-> 检查 accession ID
-> 构建 v0.1 processed dataset
-> 做 trait prediction benchmark
-> 筛出稳定 traits
-> 测试 methylation 是否有用
-> 做 oil traits GEMMA LMM GWAS
```

当前最重要的结论是：

```text
这个项目现在应该主攻 oil traits。
预测模型用 ridge/ElasticNet 做扎实。
GWAS 用 GEMMA LMM 做论文主结果。
不要现在直接上大模型。
```

## 2. 当前数据是什么

v0.1 数据集的样本单位是 `accession`，可以理解成一份玉米材料。

核心数据规模：

```text
461 个 accession: 有 genotype + population + phenotype/metabolome
236 个 accession: 额外有 methylation 覆盖
199,856 个 SNP
318 个数值 phenotype/metabolome traits
```

为什么只有 461 个 accession？

因为我们只保留能在多个表之间对齐的材料。比如一个 accession 只有 phenotype、没有 genotype，或者只有 population、没有 trait，就不能进入主数据集。

为什么 expression 没用？

当前下载的 expression 是 B73/SK/HZS/Mo17 reference/tissue expression，不是这 461 个 AMP accession 的 expression。如果强行用，会把样本配错，论文里这是严重问题。

为什么 methylation 没直接进主模型？

methylation 只有 236 个 accession，比 461 少接近一半。样本变少以后，高维 methylation 特征很容易过拟合。所以先做消融测试，只有证明有明显增益才进主模型。结果显示增益有限。

## 3. prediction benchmark 说明

benchmark 的问题很简单：

```text
只看 genotype 和 population，能不能预测 phenotype/metabolome？
```

第一版结果：

```text
317 个 traits 可评估
best baseline: genotype_pca_population_ridge
test median Pearson = 0.331
test median R2 = 0.034
```

这个结果不能简单理解成“所有 trait 都预测得好”。更准确地说：

- 所有 traits 混在一起，中位数一般。
- oil traits 很强。
- 有些 metabolite 和 agronomic traits 也有信号。
- 有些 traits 不稳定，不适合作为主结果。

所以我们继续做 trait 筛选。

## 4. 为什么筛出 66 个 robust traits

一个 trait 单次 split 表现好，不一定真的稳定。可能只是这次 train/test 划分比较幸运。

所以我们做了：

```text
317 个可评估 traits
-> 130 个 selected traits
-> 5 个 random seeds 重复评估
-> 66 个 robust traits
```

66 个 robust traits 的组成：

```text
oil: 29
metabolite: 16
agronomic: 15
amino acid: 6
```

这说明：

- oil traits 是当前最稳的主线。
- 66 个 robust traits 是后面模型比较的主评估集合。
- 论文里可以说我们先做了 multi-seed robustness，而不是只报告一次 split 的结果。

## 5. 为什么不用复杂神经网络

我们比较了 ridge、ElasticNet 和 small MLP。

结果：

```text
ridge      median Pearson/R2 = 0.498 / 0.204
ElasticNet median Pearson/R2 = 0.483 / 0.171
small MLP  median Pearson/R2 = 0.351 / -0.191
```

解释：

- ridge 最稳。
- ElasticNet 接近 ridge。
- small MLP 的 R2 为负，说明测试集表现比简单均值预测还差。

为什么会这样？

因为样本只有 461，而 SNP 有 199,856 个。特征远多于样本时，复杂模型很容易记住训练集，但泛化差。

所以当前论文路线应该是：

```text
小模型 + 严格评估 + 清楚解释
```

而不是：

```text
复杂模型 + 样本不足 + 结果不稳定
```

## 6. final benchmark 代表什么

最终 benchmark 固化为：

```text
model: genotype_population_ridge
traits: 66 robust traits
```

结果：

```text
overall median Pearson = 0.498
overall median R2 = 0.204
positive R2 fraction = 0.979
```

family-level 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

这可以写成论文结果：

- ZEAMAP v0.1 中，genotype + population 对一批 traits 有稳定预测能力。
- oil traits 的预测表现最强。
- ridge/ElasticNet 在当前样本量下优于 small MLP。

但不能写成：

- 当前数据足够训练大规模预训练模型。
- 模型已经能解释所有 phenotype variation。

## 7. methylation 结果怎么理解

我们不是凭感觉决定不用 methylation，而是做了三次测试。

### global methylation summary

结果：

```text
加 methylation:  median Pearson/R2 = 0.496 / 0.173
不加 methylation: median Pearson/R2 = 0.490 / 0.173
```

解释：几乎没提升。

### gene/promoter/cis-window methylation PCA

结果：

```text
加 methylation PCA: median Pearson/R2 = 0.496 / 0.199
不加 methylation:   median Pearson/R2 = 0.490 / 0.173
```

解释：有小幅 R2 提升，但不大。

### sparse gene-window methylation

结果：

```text
sparse methylation ElasticNet median Pearson/R2 = 0.338 / 0.025
```

解释：高维 gene-window methylation 在 236 个 accession 上不稳定。

所以最终决定：

```text
methylation 不进入 v0.1 主模型。
methylation PCA 可以作为辅助消融。
raw sparse methylation features 只作为候选解释材料。
```

## 8. attribution screen 和 GWAS 的区别

我们做过一个 genotype attribution screen。它的作用是找候选 SNP/gene。

但它不是正式 GWAS。

区别：

| 分析 | 用途 | 能不能作为论文主 GWAS |
|---|---|---|
| train-split SNP correlation screen | 快速找候选解释位点 | 不能 |
| covariate-only GWAS | 可复现 GWAS 工具链和 inflation 诊断 | 不能作为最终主结果 |
| GEMMA LMM GWAS | 控制 kinship 后的正式 GWAS baseline | 当前可以作为主 GWAS baseline |

## 9. covariate-only GWAS 为什么不够

covariate-only GWAS 用了 PC1-PC3 和 K1-K3 作为协变量。

结果：

```text
lambda GC = 2.41-3.97
```

lambda GC 可以理解成 GWAS 统计量有没有整体膨胀：

- 接近 1：比较健康。
- 明显大于 1：可能有群体结构、亲缘关系、LD 或其他混杂。

这里 2.41-3.97 太高。所以 covariate-only GWAS 的大量显著 SNP 不能直接当成真实 loci。

它的价值是：

```text
证明简单 covariate correction 不够，必须上 mixed linear model。
```

## 10. GEMMA LMM GWAS 说明

GEMMA LMM 加入了 genotype-derived kinship matrix。通俗讲，它会考虑 accession 之间的亲缘关系，避免把“亲缘相近导致的相似表型”误判成某个 SNP 的真实效应。

输入：

```text
10 个 high-priority oil traits
440 个有 oil phenotype 的 accession
199,856 个 SNP
PC1-PC3 + K1-K3 covariates
genotype-derived kinship
```

结果：

```text
GEMMA LMM lambda GC range = 0.984-1.018
GEMMA LMM median lambda GC = 0.998
Bonferroni hits per trait = 1-21
```

和 covariate-only 对比：

```text
covariate-only lambda GC = 2.41-3.97
GEMMA LMM lambda GC       = 0.984-1.018
```

这说明：

- GEMMA LMM 基本消除了统计膨胀。
- lead SNP 数量从 covariate-only 的大量 hits 收敛到更合理的范围。
- GEMMA LMM 是当前能面向论文的 GWAS 主结果。

能写：

```text
GEMMA LMM identified candidate loci for oil-related traits with well-controlled genomic inflation.
```

不能写：

```text
这些 lead SNP 已经被证明是 causal variants。
```

## 11. 当前哪些结论可信

高可信：

- v0.1 有 461 个强配对 accession。
- 66 个 robust traits 是稳定评估集合。
- oil traits 是当前最强 family。
- ridge/ElasticNet 比 small MLP 更适合当前样本量。
- methylation 不适合作为 v0.1 主输入。
- covariate-only GWAS 有明显 inflation。
- GEMMA LMM GWAS 的 lambda GC 接近 1。

中等可信：

- methylation PCA 有小幅增益。
- attribution screen 的候选 SNP/gene 有参考价值。
- metabolite/amino acid traits 有一定可预测性，但弱于 oil。

不能声称：

- 某个 SNP 是 causal variant。
- 某个 gene 已经被证明控制 oil trait。
- 当前样本量适合大规模多模态预训练。
- 当前 expression 能代表 AMP accession expression。

## 12. 下一步为什么做 lead loci 注释

现在 GEMMA 已经给出了可作为论文主线的 GWAS 结果，但还只是统计结果。

论文里还需要把统计结果变成生物学解释：

```text
lead SNP
-> locus
-> candidate gene
-> gene function
-> oil/fatty-acid pathway or literature support
-> figure/table
```

下一步优先任务：

1. 合并 GEMMA lead SNP 成 locus。
2. 给每个 locus 找 nearest gene、gene body/promoter/cis-window gene。
3. 查候选 gene 的功能注释。
4. 查 maize oil、fatty acid、seed metabolism 相关文献。
5. 画重点 locus 的局部图。
6. 检查 GEMMA lead loci 和 ridge attribution candidates 是否重叠。

这样才能从“我们跑了 GWAS”变成“我们有论文候选位点和候选基因”。
