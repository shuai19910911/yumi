# WindowFormer 训练评估和下一阶段数据计划

日期：2026-06-06

## Material Passport

```text
Project: yumi / ZEAMAP maize multi-trait prediction
Mode: academic-research-suite experiment-agent validate
Status: ANALYZED
Data used: ZEAMAP v0.1 deep learning tensor package
Main files:
  data/deep_model/v0_1/
  results/deep_model/windowformer_supervised_norm_v0_1/
  results/deep_model/windowformer_pretrain_v0_1/
  results/deep_model/windowformer_finetune_v0_1/
  results/deep_model/windowformer_small_regularized_v0_1/
```

## 一句话结论

当前 ZEAMAP 461 个 accession 不足以让 SNP Transformer 超过 ridge。

更通俗地说：

```text
ridge 像一个很稳的传统统计模型，样本少的时候很占优势。
Transformer 参数更多，虽然能看 199,856 个 SNP，但 461 个样本太少，很容易记住训练集。
```

## 已完成的 GPU 训练

| 模型 | test median Pearson | test median R2 | 判断 |
|---|---:|---:|---|
| genotype + population ridge | 0.498 | 0.204 | 当前最强基线 |
| supervised SNPWindowFormer | 0.351 | 0.076 | 能跑通，但低于 ridge |
| masked-genotype pretrain + fine-tune | 0.251 | 0.021 | 预训练没有转化成更好 trait prediction |
| small regularized SNPWindowFormer | 0.325 | 0.040 | 过拟合稍轻，但仍低于 ridge |

## 这说明什么

1. 数据和训练脚本已经跑通。

我们已经证明：

```text
199,856 SNP -> window token -> Transformer -> 66 traits
```

这条技术路线可以运行，不是工程问题。

2. 当前问题是样本量和模型容量不匹配。

现在只有：

```text
461 个 accession
66 个 traits
199,856 个 SNP
```

这属于非常典型的“小样本、高维特征”问题。ridge/ElasticNet 这种强正则化模型天然适合这个场景，而 Transformer 更依赖更大的样本量或更大规模的 genotype-only 预训练。

3. 同数据预训练不够。

masked-genotype pretraining 的 reconstruction loss 能下降，说明模型学到了 SNP 局部结构；但 fine-tuning 到 trait prediction 后没有提升。这说明：

```text
只在 461 个 ZEAMAP accession 上预训练，信息量不够。
```

## ARS 风格风险检查

已检查的风险：

| 风险 | 当前判断 |
|---|---|
| 只看单次训练是否误判 | 有风险，后续需要多 seed |
| 只看验证集不看测试集 | 已避免，使用 test metrics 判断 |
| 数据泄漏 | 目标归一化只用训练集均值/标准差，当前无明显泄漏 |
| 模型比基线弱还硬写成深度模型优势 | 必须避免 |
| 用同一批样本预训练后声称泛化增强 | 必须避免 |
| 过拟合 | 已观察到，尤其 fine-tune 后训练集提升、验证/测试不稳定 |
| 外部数据引入后的 accession 重名/重复 | 下一阶段必须检查 |

当前严谨结论：

```text
ZEAMAP v0.1 已经足够做模型基准和小样本遗传预测文章；
但如果文章主打 Transformer/representation learning，需要外部 maize genotype 扩大预训练。
```

## 下一阶段应该下载的数据

### 必须优先下载 1：G2F 2014-2023 genotypic data

用途：

```text
扩大 maize genotype-only pretraining。
```

下载位置：

```text
Genomes to Fields Resources
https://www.genomes2fields.org/resources/
```

页面中列出的关键数据：

```text
2014-2023 G2F Genotypic Data
DOI: https://doi.org/10.25739/ragt-7213
```

为什么优先：

```text
G2F 是 maize genotype-by-environment 公共资源；
官网明确列出 2014-2023 的 G2F genotypic data；
它比 ZEAMAP 461 个样本更适合作为 genotype-only 预训练数据。
```

### 必须优先下载 2：Panzea / maize HapMap genotype flat files

用途：

```text
扩大 maize diversity genotype 预训练。
```

下载入口：

```text
Panzea Genotypes
https://www.panzea.org/genotypes
```

页面说明：

```text
Panzea 提供 public flat file genotype datasets；
包括 HapMap、GBS、MaizeSNP50 chip 等 maize genotype 数据。
```

优先目标：

```text
HapMap3 / 1210 maize lines genotype data
```

原因：

```text
MaizeSNPDB 文献说明 HapMap3 包含 1210 maize lines 和超过 83M variant sites；
这类数据非常适合做 masked-genotype pretraining。
```

### 可选下载 3：G2F phenotype/environment 数据

用途：

```text
后续做外部验证或 genotype-to-phenotype transfer。
```

可选年份：

```text
G2F 2014-2018: phenotypic, genotypic, environment data
G2F 2019-2023: phenotype/environment data
```

当前不是第一优先级。原因是我们现在最缺的是 genotype-only 预训练规模，不是马上做 GxE 预测。

## 暂时不建议下载

暂时不要下载：

```text
raw FASTQ / SRA
BAM
全量 genome assembly
全量 epigenome bigWig/BED
```

原因：

```text
当前瓶颈是 accession-level genotype 数量；
不是 read-level 重新比对，也不是重新做变异检测。
```

## 下一步执行路线

1. 下载 G2F 2014-2023 genotypic data。
2. 下载 Panzea HapMap/GBS genotype flat files。
3. 写外部 genotype ingestion 脚本。
4. 统一 marker 坐标、等位基因编码、accession 名。
5. 只保留和 ZEAMAP 可对齐或可映射到 B73 坐标的 SNP。
6. 做大规模 masked-genotype pretraining。
7. 回到 ZEAMAP v0.1 上 fine-tune/evaluate。
8. 如果仍低于 ridge，论文主线改为“强正则化 genomic prediction + 深度模型负结果/边界条件”，不要硬写 Transformer 优势。

