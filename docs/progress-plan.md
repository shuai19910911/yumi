# Yumi progress plan

更新日期：2026-06-07

## 项目当前定位

当前主线已经改回模型文章：

```text
用玉米 SNP 基因型预测多个 phenotype/metabolome traits。
重点不是 GWAS 候选基因，而是模型、数据、基线比较和泛化能力评估。
```

GWAS、候选基因和功能注释只作为结果解释，不能再作为主线。

## 已完成

### 1. ZEAMAP v0.1 数据集

已经完成：

```text
461 个 accession
199,856 个 SNP
318 个数值型 traits
66 个稳定 traits 用于核心模型评估
```

已有样本索引、trait 矩阵、population 协变量和模型输入包。

### 2. 传统模型基线

已经完成 ridge、ElasticNet、MLP、population-only 等基线。

当前最强基线仍是 ridge / ElasticNet：

```text
median Pearson 约 0.498
median R2 约 0.204
```

这也是深度模型必须超过的主线门槛。

### 3. ZEAMAP-only SNPWindowFormer

已经完成监督训练：

```text
输入：199,856 SNP
窗口：256 SNP/window
模型：SNPWindowFormer
目标：66 stable traits
结果目录：results/deep_model/windowformer_supervised_norm_v0_1/
```

测试结果：

```text
median Pearson = 0.351
median R2 = 0.076
```

判断：

```text
模型跑通了，但没有超过 ridge / ElasticNet。
```

### 4. ZEAMAP-only masked-genotype 预训练

已经完成：

```text
结果目录：results/deep_model/windowformer_pretrain_v0_1/
test reconstruction loss = 0.621
```

预训练后 fine-tuning 测试结果：

```text
median Pearson = 0.251
median R2 = 0.021
```

判断：

```text
在 ZEAMAP 自己的小样本数据上做 genotype-only 预训练，没有提升 trait prediction。
```

### 5. G2F 外部基因型数据

已经完成 G2F 2014-2023 genotype 数据检查和转换：

```text
VCF: data/external/g2f/genotypic_2014_2023/inbreds_G2F_2014-2023_437k.vcf
样本数：2,193
SNP 数：437,214
输出目录：data/deep_model/external_pretrain_v0/g2f_native_b73v5/
```

G2F 和 ZEAMAP 坐标体系不同：

```text
ZEAMAP SNP: 199,856
G2F SNP: 437,214
可直接共用 SNP: 9
```

所以不能直接拼接两个 SNP 表。当前采用 G2F native genotype-only pretraining，然后把 shape 一致的 encoder 权重迁移到 ZEAMAP。

### 6. G2F native masked-genotype pretraining

已经在 GPU 节点完成：

```text
结果目录：results/deep_model/windowformer_g2f_native_pretrain_v0/
test reconstruction loss = 0.420
```

判断：

```text
G2F 预训练任务本身成功，模型能较好学习基因型重构。
```

### 7. G2F pretrained -> ZEAMAP fine-tuning

第一轮 fine-tuning：

```text
结果目录：results/deep_model/windowformer_g2f_native_finetune_v0_1/
median Pearson = 0.277
median R2 = 0.041
```

第二轮补救实验，降低学习率、增加 dropout 和 weight decay：

```text
结果目录：results/deep_model/windowformer_g2f_native_finetune_lr1e5_do30_v0_1/
median Pearson = 0.227
median R2 = 0.020
```

判断：

```text
G2F 预训练没有提升 ZEAMAP trait prediction。
第二轮更强正则化也没有解决问题。
```

## 当前总体结论

当前最关键结论：

```text
深度模型可以跑通，也能学到 genotype reconstruction；
但在当前 ZEAMAP 461 个带标签样本上，trait prediction 没有超过 ridge / ElasticNet。
```

这说明如果文章一定要写“新深度模型显著优于传统模型”，当前证据还不够。

更稳的论文定位是：

```text
小样本 maize multi-trait genomic prediction benchmark：
比较线性模型、浅层模型、Transformer、genotype-only pretraining、外部 G2F 迁移；
证明当前数据条件下强线性基线仍然最稳，并分析深度模型失败边界。
```

## 下一步执行计划

### A. 必须先做的整理

1. 固化当前所有模型结果表。
2. 生成一张清晰的模型比较图。
3. 生成一张工作流程图。
4. 生成一张模型结构图。
5. 把论文目标从“深度模型超过所有方法”改为“严格基准和失败边界分析”。

### B. 如果继续冲深度模型提升

只有下面几条路还有意义：

```text
1. 找更多带 trait 标签的玉米材料，而不只是 genotype。
2. 找与 ZEAMAP 同一 genome build 或可 liftover 的外部 SNP 数据。
3. 换成更小、更强正则化、更接近 ridge inductive bias 的模型。
4. 做 trait-family-specific 模型，而不是一次预测 66 个 trait。
```

不建议继续盲目堆大 Transformer，因为当前主要瓶颈是标签样本量，不是 GPU 算力。

## 当前需要人工协助的问题

见：

```text
docs/2026-06-07-g2f-pretrain-finetune-monitoring-report.md
```
