# Model architecture notes

更新日期：2026-06-06

## 当前模型定位

当前阶段不是做泛植物大模型，也不是直接做复杂多模态 transformer。

当前阶段要做的是：

```text
ZEAMAP maize accession-level benchmark
+ high-priority oil-trait GEMMA LMM GWAS
```

原因：

- v0.1 只有 461 个强配对 accession。
- methylation 只有 236 个 accession。
- expression 不是 AMP accession-level paired expression。
- genotype 特征有 199,856 个 SNP，远多于样本数。

所以当前最稳的路线是：

```text
小模型 + 严格 split + population 对照 + GEMMA LMM GWAS
```

## 当前数据接口

v0.1 processed dataset：

```text
data/processed/v0_1/accessions.tsv
data/processed/v0_1/modality_mask.tsv
data/processed/v0_1/population.parquet
data/processed/v0_1/phenotype.parquet
data/processed/v0_1/genotype_samples.tsv
data/processed/v0_1/genotype_variants.tsv
data/processed/v0_1/genotype_dosage_int8.npz
```

一个训练样本可以理解为：

```text
sample = {
  accession_id,
  genotype_features,
  population_covariates,
  phenotype_targets,
  modality_mask
}
```

当前不进入主模型的模态：

- expression：当前文件不是 AMP accession-level expression。
- raw methylation gene-window features：236 个 accession 上不稳定。
- open chromatin/chromatin interaction：当前更适合作为 reference regulatory prior。

## 当前主预测模型

最终 v0.1 benchmark 使用：

```text
genotype_population_ridge
```

输入：

- genotype representation
- population covariates

输出：

- 66 个 robust traits 的单 trait regression 结果。

当前结果：

```text
overall median Pearson/R2 = 0.498 / 0.204
oil median Pearson/R2 = 0.596 / 0.321
```

为什么用 ridge：

- 样本少，特征多。
- ridge 对高维 SNP 特征更稳。
- small MLP 已经测试过，表现不稳定。

## 当前模型比较结论

在 66 个 robust traits 上：

```text
genotype_population_ridge      median Pearson/R2 = 0.498 / 0.204
genotype_population_elasticnet median Pearson/R2 = 0.483 / 0.171
small MLP                      median Pearson/R2 = 0.351 / -0.191
```

结论：

- ridge 是当前默认主模型。
- ElasticNet 是有用对照。
- small MLP 暂不作为主模型。
- 当前不继续加深神经网络。

## Population covariates 的角色

population covariates 有两个用途：

1. 作为 prediction model 的输入，帮助模型解释 population structure。
2. 作为对照，判断 genotype 是否提供了 population 之外的预测信号。

因此 benchmark 里必须保留：

```text
population_only
genotype_only
genotype + population
```

如果 genotype + population 没有超过 population-only，就说明模型可能只是学到了群体结构。

当前结果显示 genotype + population 优于 population-only，所以 genotype 确实提供额外信号。

## Methylation 的当前角色

methylation 不作为 v0.1 主输入。

已经测试：

```text
global methylation summary: almost no overall gain
gene methylation PCA: small gain
sparse gene-window methylation: unstable
```

当前保留方式：

- modality coverage mask
- methylation PCA auxiliary ablation
- sparse selected features as candidate explanation only

暂不做：

- raw methylation gene-window features 直接并入主训练矩阵。
- methylation transformer。
- 用 236 个 accession 训练复杂 methylation 模型。

## GWAS 和 attribution 的角色

当前有三层解释性分析：

| 层级 | 作用 | 当前地位 |
|---|---|---|
| genotype attribution screen | 快速找候选 SNP/gene | 辅助证据 |
| covariate-only GWAS | 检查 GWAS 工具链和 inflation | 诊断 baseline |
| GEMMA LMM GWAS | 控制 kinship 后的 association | 论文主 GWAS baseline |

GEMMA LMM 当前结果：

```text
traits: 10 high-priority oil traits
n per trait: 440
SNPs: 199,856
lambda GC: 0.984-1.018
median lambda GC: 0.998
Bonferroni hits per trait: 1-21
```

当前解释性主线：

```text
GEMMA lead SNP
-> LD/locus grouping
-> candidate gene mapping
-> function annotation
-> oil/fatty-acid pathway literature
-> manuscript figure/table
```

Stage 5.4 已完成第一版 manuscript candidate locus layer：

```text
GEMMA lead SNPs
-> 1 Mb physical locus merge
-> B73 RefGen_v4 gene description
-> Bonferroni/FDR/suggestive class
-> ridge attribution overlap
-> functional keyword class
-> Nature-style summary figure
```

当前输出：

- manuscript candidate loci：184。
- manuscript candidate genes：147。
- lipid/fatty-acid keyword loci：11。
- ridge-supported manuscript loci：63。

Stage 5.5 已完成第一版 top locus priority layer：

```text
manuscript candidate loci
-> priority score
-> tier1/tier2 manuscript candidates
-> top regional targets
-> regional association + LD + gene-track figures
-> seed literature evidence
```

当前输出：

- prioritized loci：184。
- tier1 main-text loci：18。
- tier2 strong loci：22。
- top regional figures：8。
- 最强主线：chr6 `Zm00001d036982` / linoleic acid1。
- 重要补充候选：chr9 `Zm00001d045383` 区域，包含 `Zm00001d045387` fatty acyl-ACP thioesterase2。

注意：

- GEMMA lead SNP 是 candidate locus，不是 causal variant。
- attribution screen 只能作为与 GEMMA 交叉支持的辅助结果。
- covariate-only GWAS 因为 lambda GC 过高，不作为主结果。
- priority score 是候选排序工具，不是新的统计检验。
- regional figures 是 association/LD context，不是 fine-mapping。

Stage 5.6 已完成第一版 manuscript evidence layer：

```text
top regional targets
-> evidence level
-> recommended manuscript claim
-> claim boundary
-> main tier1 locus table
-> supplementary candidate-locus table
-> Results draft
```

当前输出：

- top regional evidence table：8 行。
- main tier1 locus table：18 行。
- supplementary manuscript candidate loci：184 行。
- literature/source records：6 条。
- Results draft：1 份。

这一层不是模型训练层，而是论文解释层。它的核心作用是把统计结果转换成可写、可审稿、不过度声称的 manuscript material。

Stage 5.7 已完成第一版 manuscript assembly layer：

```text
Results draft + manuscript tables
-> Methods draft
-> Figure 1 dataset/prediction figure
-> Figure 2 GEMMA summary figure
-> Figure 3 top regional loci figure
-> figure captions draft
```

当前输出：

- Methods draft：1 份。
- Figure 1：PDF/SVG/PNG。
- Figure 3：PDF/SVG/PNG。
- Figure plan：1 份。
- Figure captions draft：1 份。

这一层仍然不是模型升级，而是把已经完成的 benchmark/GWAS/candidate-locus 结果组织成论文骨架。

Stage 5.8 已完成第一版 manuscript skeleton layer：

```text
Results draft + Methods draft + figure/table captions
-> manuscript skeleton
-> readiness checklist
-> next polish/audit task list
```

当前输出：

- manuscript skeleton：1 份。
- table captions draft：1 份。
- manuscript readiness checklist：1 份。
- Stage 5.8 report：1 份。

这一层的作用是把项目从“结果材料集合”推进到“可继续润色的论文草稿骨架”。

Stage 5.9 已完成第一版 journal/citation strategy layer：

```text
manuscript skeleton
-> citation audit
-> software/version supplement
-> journal strategy
-> acceptance probability estimate
```

当前输出：

- journal strategy and acceptance estimate：1 份。
- citation audit：1 份。
- methods software versions：1 份。
- Stage 5.9 report：1 份。

这一层用于决定投稿路线和下一步补强优先级，不改变模型或 GWAS 结果。

## 以后如果扩展模型，怎么做

只有在当前论文级 benchmark/GWAS 主线稳定后，才考虑扩展模型。

建议扩展顺序：

1. gene-window genotype representation

把 SNP 聚合到 gene body、promoter、cis-window，减少维度，增加可解释性。

2. multi-task ridge/ElasticNet

利用 oil traits 之间的相关性，做 trait family-level multi-task model。

3. methylation PCA 辅助输入

只在明确增益 trait 上使用，不作为默认全局输入。

4. gene-centric fusion

如果后续拿到 accession-level expression 或更完整 epigenome，再考虑：

```text
gene token = {
  gene_id,
  cis_variant_features,
  expression_value,
  methylation_features,
  chromatin_features
}
```

5. transformer or contrastive pretraining

只有在样本量和模态配对显著扩大后再做。

## 当前不建议的结构

不建议：

- 直接用 199,856 SNP 训练深层模型。
- 用 236 个 methylation accession 训练复杂多模态模型。
- 把 reference/tissue expression 当作 accession expression。
- 用 transformer 替代当前 ridge baseline。
- 在没有独立验证的情况下强化 causal gene 结论。

## 当前论文级模型图可以怎么画

推荐画成三块，而不是画成大模型：

```text
ZEAMAP processed data
  |
  |-- accession ID harmonization
  |
v0.1 dataset
  |-- genotype
  |-- population covariates
  |-- phenotype/metabolome traits
  |-- methylation coverage mask
  |
  |-- prediction benchmark: ridge / ElasticNet / MLP comparison
  |
  |-- oil-trait GWAS: GEMMA LMM + kinship
  |
  |-- interpretation: lead loci + candidate genes
  |
  |-- manuscript triage: top loci + regional figures + literature evidence
  |
  |-- manuscript writing layer: evidence table + main/supp tables + Results draft
  |
  |-- manuscript assembly: Methods draft + Figure 1-3 plan/captions
  |
  |-- manuscript skeleton: title + abstract + introduction + results + methods + discussion outline
  |
  |-- journal strategy: citation audit + software versions + submission target ranking
```

这个图更符合当前真实进展，也更适合论文方法部分。


## Stage 5.10 之后的论文模型边界

当前稿件不把模型包装成 foundation model。论文中的模型结构应写成：

```text
regularized genotype-to-phenotype benchmark
+ calibrated mixed-model GWAS
+ candidate-locus prioritization
```

这意味着：

- prediction 模型负责筛选最稳定的 trait family。
- GEMMA LMM 负责正式 association testing。
- ridge attribution 只作为辅助交叉证据。
- candidate-locus priority score 只用于 manuscript triage，不是新的显著性检验。

这个边界对投稿很重要，因为它避免把小样本高维数据过度解释成深度学习或因果发现论文。
