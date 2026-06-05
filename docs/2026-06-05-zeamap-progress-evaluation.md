# ZEAMAP 当前进展评估

日期：2026-06-05

## 总评

当前项目进展是好的，而且方向应该继续冲论文。

现在已经不是“刚把数据跑通”的阶段，而是已经有了一个可以写成论文结果雏形的 v0.1：

```text
v0.1 processed dataset
+ prediction benchmark
+ robust trait selection
+ methylation ablation
+ GEMMA LMM oil-trait GWAS
```

当前最适合的论文定位是：

```text
ZEAMAP maize accession-level genotype-to-phenotype benchmark
and mixed-linear-model GWAS for oil-related traits
```

不是：

```text
large-scale plant multi-omics foundation model
```

后者现在样本量和模态配对都不够。

## 当前能写进论文的内容

### 可以写

1. 数据集构建

我们可以写 ZEAMAP processed data 被整理成 accession-level v0.1 数据集，包含 461 个强配对 accession、199,856 个 SNP、318 个数值 traits 和 population covariates。

2. 预测 benchmark

我们可以写 ridge/ElasticNet 在 66 个 robust traits 上建立了稳定预测基准，其中 oil traits 表现最好。

3. 模型选择

我们可以写在当前样本量下，正则线性模型优于 small MLP，说明复杂模型会有过拟合风险。

4. methylation 消融

我们可以写 methylation PCA 有小幅增益，但 raw gene-window methylation features 在 236 个 accession 上不稳定，所以 methylation 不作为 v0.1 主输入。

5. GWAS 方法升级

我们可以写 covariate-only GWAS 出现明显 inflation，而 GEMMA LMM 通过 kinship correction 把 lambda GC 控制到接近 1。

6. oil-trait candidate loci

我们可以写 GEMMA LMM 为 10 个 high-priority oil traits 产生了 candidate loci 初稿。

### 不能写

1. 不能说当前模型是大规模预训练模型。
2. 不能说 small MLP 或 transformer 优于线性模型。
3. 不能把 B73/SK/HZS/Mo17 expression 当成 AMP accession expression。
4. 不能把 attribution screen 的 SNP 当成 GWAS lead SNP。
5. 不能把 covariate-only GWAS 的 hits 当成最终论文 loci。
6. 不能把 GEMMA lead SNP 直接写成 causal variant。

## 各部分完成度

| 模块 | 完成度 | 评价 |
|---|---|---|
| 数据下载检查 | 高 | 文件完整，可读性检查完成 |
| accession ID 对齐 | 高 | phenotype、population、VCF 已对齐 |
| v0.1 processed dataset | 高 | 461 个强配对 accession 已构建 |
| prediction benchmark | 高 | ridge/ElasticNet baseline 完成 |
| robust trait selection | 高 | 66 个 robust traits 已确定 |
| methylation ablation | 中高 | 已证明不适合作为主输入 |
| genotype attribution screen | 中 | 可作为候选解释，不能作为正式 GWAS |
| covariate-only GWAS | 中 | 工具链完成，但 inflation 高 |
| GEMMA LMM GWAS | 中高 | 当前论文主 GWAS baseline 已完成 |
| candidate gene annotation | 低 | 下一步要做 |
| manuscript figures | 低到中 | Manhattan/QQ 有了，locus 图和汇总图还缺 |

## 当前最大优势

### 1. oil traits 信号强

oil family 的 benchmark 表现最好：

```text
oil median Pearson/R2 = 0.596 / 0.321
```

这说明 oil traits 是最适合继续深入的论文主线。

### 2. GWAS inflation 已经被处理

covariate-only GWAS：

```text
lambda GC = 2.41-3.97
```

GEMMA LMM：

```text
lambda GC = 0.984-1.018
median = 0.998
```

这是一条很清楚的方法学故事：

```text
简单协变量校正不够 -> mixed linear model 必要 -> GEMMA 后 inflation 得到控制
```

### 3. 当前模型选择稳健

ridge/ElasticNet 优于 small MLP，这和样本量、特征维度关系一致。这个结果虽然不花哨，但可信。

## 当前最大风险

### 风险 1：样本量仍然偏小

461 个 accession 对 199,856 SNP 是小样本高维问题。236 个 methylation accession 更小。

应对：

- 继续使用 ridge/ElasticNet。
- 保持 multi-seed robustness。
- 不上复杂深度模型。

### 风险 2：群体结构很强

玉米 accession 存在明显 population structure。如果控制不够，GWAS 和 prediction 都可能虚高。

应对：

- prediction 里保留 population-only baseline。
- GWAS 主结果使用 GEMMA LMM。
- covariate-only GWAS 只作为 diagnostic baseline。

### 风险 3：candidate locus 还没有生物学解释

GEMMA 已经给出 lead SNP，但还缺：

- candidate gene function
- oil/fatty-acid pathway support
- 已知 maize QTL/GWAS 文献对照
- locus/LD 图

应对：

- 下一阶段优先做 GEMMA lead loci 注释。

### 风险 4：模态配对不完整

expression 不是 AMP accession-level，methylation 只有 236 个 accession。

应对：

- v0.1 主模型只用 genotype + population。
- methylation 只做辅助消融。
- expression 暂不进入主数据集。

## 对当前结果的可信度分级

高可信：

- 461 个强配对 accession。
- 66 个 robust traits。
- oil traits 是最强 trait family。
- ridge/ElasticNet 是当前最稳模型。
- methylation raw features 不适合作为 v0.1 主输入。
- GEMMA LMM 后 lambda GC 接近 1。

中等可信：

- methylation PCA 的小幅增益。
- genotype attribution screen 的候选 SNP/gene。
- metabolite 和 amino acid traits 的可预测性。

低可信或不能声称：

- causal SNP。
- causal gene。
- methylation sparse selected genes 是真实调控因子。
- 当前数据足够做大规模多模态预训练。

## 是否适合继续

适合继续，但方向要明确。

适合继续做：

- GEMMA lead loci 注释。
- candidate gene 功能解释。
- oil/fatty-acid pathway 文献核查。
- locus/LD 图。
- final benchmark 图表整理。
- ridge attribution 和 GEMMA lead loci overlap。

不适合继续做：

- 直接上 transformer。
- 扩大 neural network。
- 处理 raw FASTQ。
- 把 methylation raw features 强行加进主模型。
- 把 expression 文件强行配到 AMP accession。

## 下一阶段目标

下一阶段建议命名为：

```text
Stage 5.4: GEMMA lead loci annotation and paper figure preparation
```

目标：

把 GEMMA GWAS 的统计结果整理成论文可用的候选基因和图表。

具体任务：

1. 从 `gemma_lmm_lead_snps.tsv` 提取每个 trait 的 lead SNP。
2. 按 LD 或物理距离合并成 locus。
3. 给每个 locus 匹配 candidate gene。
4. 补充 gene annotation、GO/pathway、known maize ortholog/function。
5. 查 oil/fatty-acid/seed metabolism 文献。
6. 画每个重点 trait 的 Manhattan/QQ/locus panel。
7. 输出 manuscript-facing candidate loci table。

成功标准：

- 每个 oil trait 有清楚的 candidate locus 表。
- 每个重点 locus 有 candidate gene 和功能解释。
- 图表能进入论文结果草稿。
- 所有表述保持 candidate 口径，不夸大成 causal。

## 当前一句话判断

项目已经有论文级雏形，但还没到可以写完整 GWAS 结果段落的程度。下一步不是再堆模型，而是把 GEMMA lead loci 做成 candidate gene、locus figure 和文献支持。
