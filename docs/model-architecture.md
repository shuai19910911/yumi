# Model architecture notes

更新日期：2026-06-06

## 当前模型定位

当前模型不再停留在 ridge benchmark。新的目标是训练一个可以作为论文核心的 SNP window deep model。

当前最合适的模型定位是：

```text
SNP window representation learning for maize multi-trait prediction
```

通俗理解：

```text
把每个玉米材料看成一个样本。
输入是它的 199,856 个 SNP、群体结构和可选甲基化特征。
先把连续 SNP 切成 window tokens。
模型学习每个 accession 的遗传表示。
输出是多个 phenotype/metabolome traits。
```

## 为什么不用复杂大模型

当前数据规模：

```text
461 个 accession 有 genotype + population + phenotype/metabolome
236 个 accession 有 methylation
199,856 个 SNP
318 个 numeric traits
```

这里的问题是：

```text
样本数少，特征数非常多。
```

这种情况下，复杂神经网络很容易过拟合。当前更合理的路线是先做严谨、稳健、可复现的小模型 benchmark。

## 一个训练样本是什么

一个 accession 可以理解成：

```text
sample = {
  accession_id,
  genotype_features,
  population_covariates,
  optional_methylation_features,
  phenotype_or_metabolome_targets
}
```

也就是说，模型学的是：

```text
玉米材料的基因型/群体结构/甲基化信息
-> 这个材料的性状数值
```

## 当前主模型

当前深度模型候选是：

```text
SNPWindowFormer
```

输入：

- SNP window tokens
- population covariates

输出：

- 66 个 robust traits 的 multi-task regression

强基线仍然是：

```text
genotype_population_ridge
```

当前整体表现：

```text
median Pearson = 0.498
median R2 = 0.204
```

oil traits 表现最好：

```text
oil median Pearson/R2 = 0.596 / 0.321
```

## 为什么 ridge 仍然必须保留为强基线

ridge 的优点：

- 适合小样本、高维特征。
- 对 SNP 这种强相关特征更稳。
- 参数少，不容易过拟合。
- 结果容易解释和复现。

当前模型比较也支持这个判断：

```text
genotype_population_ridge      median Pearson/R2 = 0.498 / 0.204
genotype_population_elasticnet median Pearson/R2 = 0.483 / 0.171
small MLP                      median Pearson/R2 = 0.351 / -0.191
```

结论：

```text
ridge 是当前必须击败的强基线。
ElasticNet 是重要对照。
small MLP 说明普通浅层神经网络不够。
新模型必须证明 SNP window tokenizer + Transformer 表征学习确实带来增益。
```

## 模型比较应该怎么组织

论文里需要保留这些模型层级：

```text
mean baseline
population-only ridge
genotype-only ridge
genotype + population ridge
genotype + population ElasticNet
small MLP
```

每一层回答一个问题：

```text
mean baseline:
  不看任何输入，只猜平均值，作为最低基线。

population-only:
  只看群体结构，判断是否只是 population structure 在起作用。

genotype-only:
  只看基因型，判断 SNP 是否有预测信号。

genotype + population:
  当前主模型，判断联合输入是否最稳。

ElasticNet:
  检查稀疏线性模型是否能接近 ridge。

small MLP:
  检查简单神经网络在当前样本量下是否有优势。
```

## methylation 的模型角色

methylation 当前不是主输入。

原因：

```text
只有 236 个 accession 有 methylation，样本覆盖不完整。
```

已经测试的 methylation 用法：

```text
global methylation summary
gene/promoter/cis-window methylation PCA
sparse gene-window methylation selection
```

当前结论：

```text
methylation 在 v0.1 中只能做辅助消融。
不能把它写成强多模态主模型。
```

## GWAS 和 candidate loci 的角色

GWAS 不再是模型结构的一部分。

它只回答一个辅助问题：

```text
为什么 oil traits 比其他性状更容易预测？
```

如果 oil traits 的 GWAS 信号更清楚，说明这些性状有较强遗传基础，可以辅助解释模型表现。

论文里应该这样放：

```text
主线：模型预测和模型比较
辅助：GWAS/candidate loci 解释 oil traits 的遗传信号
```

不能再写成：

```text
主线：我们发现了 chr6/chr9 候选基因
```

## 推荐论文图表

模型文章应该优先做这些图：

1. 数据集构建流程图
2. 模型输入和预测任务图
3. 不同模型的预测性能比较图
4. 不同性状家族的可预测性图
5. 多随机种子的稳健性图
6. methylation 消融图
7. oil traits 的辅助 GWAS/解释图

## 当前模型文章的核心结论

可以围绕这几句话组织全文：

```text
ZEAMAP 公共数据可以整理为 accession-level 多性状预测数据集。
genotype + population ridge 对 66 个 robust traits 有稳定预测能力。
oil traits 是当前最可预测的性状家族。
在 461 个 accession 的规模下，ridge/ElasticNet 比 small MLP 更可靠。
methylation 因覆盖不足暂时只能作为辅助模态。
GWAS/candidate loci 可用于解释 oil traits 的强遗传信号，但不是主线。
```
