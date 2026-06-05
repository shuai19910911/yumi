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

## 13. lead loci 注释现在完成了什么

Stage 5.4 已经完成第一版。

做法：

- 把 GEMMA lead SNP 按 trait、染色体和物理距离合并成 locus。
- 从 B73 RefGen_v4 GFF3 里提取 gene description 和 biotype。
- 标注 Bonferroni、FDR、suggestive 和 nominal 等级。
- 输出完整 candidate loci 表，也输出排除 nominal-only 的 manuscript candidate loci 表。
- 检查 GEMMA candidate genes 是否和 ridge attribution screen 重叠。
- 自动标注 lipid/fatty-acid、seed、transport/membrane、hormone/regulatory 等功能关键词。
- 生成 Nature 风格 summary figure，包含 PDF、SVG、PNG。

结果：

```text
manuscript candidate loci = 184
manuscript candidate genes = 147
Bonferroni loci = 38
FDR loci = 131
suggestive loci = 15
ridge-supported manuscript loci = 63
lipid/fatty-acid keyword loci = 11
```

怎么理解：

- 这 184 个 loci 是下一步论文候选表的基础。
- 其中 11 个带 lipid/fatty-acid 关键词的 loci 应该优先查文献。
- 63 个同时有 ridge attribution 支持，说明它们不只是 GWAS 统计信号，也和预测模型解释性结果有交叉。
- 仍然不能写 causal claim，只能写 candidate locus/candidate gene。

下一步变成：

```text
从 184 个 manuscript candidate loci 中筛重点
-> 查文献
-> 画局部 locus/LD 图
-> 形成论文主表和补充表
```

## 14. top loci 排序和区域图现在完成了什么

Stage 5.5 已经完成初版。

这一步做的不是重新跑 GWAS，而是把 184 个 manuscript candidate loci 排出优先级。排序依据包括：

- GEMMA 显著性强不强。
- `P` 值有多小。
- 是否在多个 oil traits 里反复出现。
- 是否有 ridge attribution 交叉支持。
- candidate gene description 里是否有 lipid/fatty-acid 相关关键词。
- 一个区域里 candidate genes 是否太多。

结果：

```text
prioritized loci = 184
tier1 main-text loci = 18
tier2 strong loci = 22
top regional figures = 8
```

怎么理解：

- 184 个 loci 是补充表候选池。
- 18 个 tier1 loci 是论文主表优先候选。
- 8 个 regional figures 是主文/扩展数据图的初稿。
- 这个 priority score 只是排序工具，不是新的统计检验。

## 15. 当前最强候选为什么是 chr6 Zm00001d036982

chr6 `Zm00001d036982` / linoleic acid1 区域现在是最强主线。

原因：

```text
跨 7 个 oil traits 复现
最佳 P = 2.35e-25
Bonferroni significant
有 lipid/fatty-acid annotation
有 ridge attribution overlap
局部图显示清楚 association peak 和 LD context
```

通俗讲，这个区域同时满足：

- 统计很强。
- 多个油脂性状都指向它。
- gene function 和 oil/fatty-acid 方向能解释。
- prediction model 的解释性结果也支持。

所以它最适合做论文 Results 里的第一个重点 locus。

但仍然要注意：

```text
可以写 candidate locus / candidate gene。
不能写 causal variant 已证明。
```

## 16. 为什么 chr9 Zm00001d045383 区域也重要

chr9 `Zm00001d045383` 区域只有一个主要 trait：

```text
agri_aa_oil__Oil_C16_0
P = 7.76e-17
```

它不是多 trait 复现区域，所以排在 tier2。但这个区域局部包含：

```text
Zm00001d045387: fatty acyl-ACP thioesterase2
```

fatty acyl-ACP thioesterase 和脂肪酸链长/组成有直接生物学关联，所以它值得优先补 MaizeGDB、UniProt、Gramene 和文献证据。

这类区域的写法应该谨慎：

```text
The chr9 C16:0-associated region contains a fatty acyl-ACP thioesterase candidate gene.
```

不要写成：

```text
We proved this gene controls C16:0.
```

## 17. regional figure 能说明什么

现在的区域图包含三层信息：

1. 区域内 SNP 的 GEMMA association strength。
2. 每个 SNP 和 lead SNP 的 LD `r2`。
3. 区域内 candidate gene models 和重点 gene labels。

这类图能支持：

```text
这个 locus 的 association peak 在哪里。
lead SNP 附近有哪些 candidate genes。
候选 gene 是否落在同一 LD/物理区域中。
```

这类图不能支持：

```text
fine-mapped causal variant。
唯一 causal gene。
实验验证结论。
```

## 18. 下一步要补什么才更像正式论文

这一段原本对应 Stage 5.6 的目标；现在 Stage 5.6 已经完成初版，见第 19-22 节。

重点不是再跑模型，而是把 top loci 的证据链补完整：

```text
top region
-> candidate gene
-> external annotation
-> known oil/fatty-acid/QTL/GWAS evidence
-> main table
-> results paragraph
```

具体要做：

1. 对 8 个 top regional loci 逐个查文献和数据库。
2. 把 18 个 tier1 loci 压缩成论文主表。
3. 把 184 个 manuscript candidate loci 放入补充表。
4. 继续打磨 Nature 风格 summary figure 和 regional panels。
5. 写 prediction benchmark 与 GEMMA GWAS 的 Results 初稿。

## 19. Stage 5.6 又完成了什么

Stage 5.6 已经把 top loci 变成论文写作材料。

这一步的产出可以理解成：

```text
8 个 top regional loci
-> evidence level
-> 推荐论文写法
-> 不能越界的 claim boundary
-> 主表
-> 补充表
-> Results 初稿
```

生成的核心表：

```text
top regional evidence table: 8 行
main tier1 locus table: 18 行
supplementary manuscript candidate loci: 184 行
literature/source records: 6 条
```

## 20. evidence level 怎么理解

Stage 5.6 不是简单写“这个 gene 有意思”，而是给每个 top region 分证据等级。

当前最重要的等级：

- A：有直接 fatty-acid/oil 先验或明确同通路候选。
- B：有 lipid-related annotation，但机制还偏间接。
- C：统计很强或多 trait 复现，但 gene function 还不够直接。
- D：统计候选，暂时没有明确 oil annotation。

这有两个好处：

1. 写论文时不会把弱证据写得太满。
2. 审稿人问“为什么挑这些 gene”时，我们有清楚规则。

## 21. 现在最适合写进主文的两个区域

第一个是 chr6 `Zm00001d036982`：

```text
证据等级: A_direct_prior_lipid_locus
最佳 P = 2.35e-25
跨 7 个 oil traits 复现
本地注释: linoleic acid1
```

这个区域适合做 Results 第一重点。

第二个是 chr9 C16:0 区域：

```text
证据等级: A_direct_fatty_acid_candidate_interval
最佳 P = 7.76e-17
附近候选: Zm00001d045387 fatty acyl-ACP thioesterase2
```

这个区域虽然只对应 C16:0 一个 trait，但 fatty acyl-ACP thioesterase 和脂肪酸组成非常相关，所以适合做第二重点区域。

## 22. 现在已经可以怎么写 Results

Results draft 已经写出四段主逻辑：

1. genotype-based prediction 说明 oil traits 是最强主线。
2. GEMMA LMM 说明 mixed model 控制了 GWAS inflation。
3. prioritized oil-trait loci 说明 184 loci、18 tier1、22 tier2 和 8 个区域图。
4. candidate-claim boundaries 明确不写 causal variant。

这已经是论文结果段落的雏形。下一步是把它扩展成完整 manuscript Results，并配 Figure 1-3。

## 23. Stage 5.7 又完成了什么

Stage 5.7 已经把论文骨架往前推进了一步。

现在不只是有 Results 初稿，还有：

```text
Methods 草稿
Figure 1 主图初版
Figure 2 主图计划
Figure 3 主图初版
Figure 1-3 captions 初稿
```

Figure 1 讲的是：

```text
数据怎么整理成 v0.1
样本/trait/SNP 规模
为什么 ridge 比 small MLP 更适合
为什么 oil traits 是主线
```

Figure 2 讲的是：

```text
covariate-only GWAS inflation 高
GEMMA LMM 把 lambda GC 控制到接近 1
GEMMA candidate loci 可以作为论文主 GWAS 结果
```

Figure 3 讲的是：

```text
chr6 Zm00001d036982 / linoleic acid1 是最强多 trait candidate interval
chr9 C16:0 区域包含 fatty acyl-ACP thioesterase2 候选
```

## 24. 下一步为什么是 manuscript skeleton

现在材料已经分散在几个文件里：

- Results draft
- Methods draft
- figure captions draft
- main/supp tables
- Figure 1-3

下一步 Stage 5.8 应该把这些合并成一个 manuscript skeleton。

也就是：

```text
Title
Abstract placeholder
Introduction draft
Results
Methods
Figure captions
Table captions
Discussion outline
Limitations
```

这样项目就从“分析结果”进入“论文草稿”阶段。

## 25. Stage 5.8 已经把 skeleton 做出来了

Stage 5.8 已完成初版 manuscript skeleton。

现在已有一个单独文件，把论文核心材料放在一起：

```text
docs/2026-06-05-zeamap-v0-1-manuscript-skeleton.md
```

里面包含：

- working title
- abstract draft
- keywords
- introduction draft
- results
- discussion outline
- methods
- figure captions
- table captions
- data/code availability draft
- references placeholder

这意味着项目已经从“分析报告很多”进入“论文骨架已成型”阶段。

## 26. 现在离投稿还差什么

还不能说已经是投稿稿。

主要差：

1. Introduction 还要补完整文献定位。
2. Results 要从结果报告风格改成正式论文叙事。
3. Discussion outline 要扩展成完整 Discussion。
4. Methods 要补软件版本、参数和命令细节。
5. 8 个 top loci 还要补 MaizeGDB、UniProt、Gramene 外部注释。
6. 所有引用要做 citation audit，并转成正式 reference list。
7. Figure 1-3 还要做最终字体、尺寸和 caption 一致性检查。

下一阶段 Stage 5.9 应该做 manuscript polish and citation audit。
