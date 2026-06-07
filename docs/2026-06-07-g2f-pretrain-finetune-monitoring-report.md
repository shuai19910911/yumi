# 2026-06-07 G2F pretraining and ZEAMAP fine-tuning monitoring report

## 简短结论

训练已经结束。

G2F 外部 genotype-only 预训练成功完成，但迁移到 ZEAMAP 预测 phenotype/metabolome traits 后，没有超过现有 ridge / ElasticNet 基线，也没有超过 ZEAMAP-only 的监督 SNPWindowFormer。

这说明当前问题不是“训练没跑完”，而是“当前数据量和预训练方式不足以让深度模型超过强基线”。

## 已完成任务

### 1. G2F 数据转换

输入数据：

```text
data/external/g2f/genotypic_2014_2023/inbreds_G2F_2014-2023_437k.vcf
```

转换结果：

```text
data/deep_model/external_pretrain_v0/g2f_native_b73v5/
```

内容：

```text
2,193 个 accessions
437,214 个 SNP
train / val / test = 1,754 / 219 / 220
```

### 2. G2F native masked-genotype pretraining

输出目录：

```text
results/deep_model/windowformer_g2f_native_pretrain_v0/
```

测试结果：

```text
test reconstruction loss = 0.420
```

通俗解释：

```text
模型看见一部分 SNP 被遮住后，能根据周围 SNP 猜回被遮住的信息。
所以预训练任务本身是成功的。
```

### 3. G2F pretrained -> ZEAMAP fine-tuning

第一轮：

```text
results/deep_model/windowformer_g2f_native_finetune_v0_1/
median Pearson = 0.277
median R2 = 0.041
```

第二轮补救实验：

```text
results/deep_model/windowformer_g2f_native_finetune_lr1e5_do30_v0_1/
median Pearson = 0.227
median R2 = 0.020
```

第二轮做了什么：

```text
降低学习率
增加 dropout
增加 weight decay
```

目的：

```text
减少小样本 fine-tuning 过拟合。
```

结果：

```text
没有改善，反而更差。
```

## 与已有模型比较

| 方法 | 测试 median Pearson | 测试 median R2 | 判断 |
|---|---:|---:|---|
| ridge / ElasticNet robust benchmark | 约 0.498 | 约 0.204 | 当前最强 |
| ZEAMAP-only SNPWindowFormer | 0.351 | 0.076 | 深度模型可用，但不够强 |
| G2F pretrained -> ZEAMAP fine-tune | 0.277 | 0.041 | 迁移没有带来提升 |
| G2F pretrained -> ZEAMAP fine-tune, stronger regularization | 0.227 | 0.020 | 补救失败 |
| ZEAMAP-only pretrain -> fine-tune | 0.251 | 0.021 | 小样本预训练没有帮助 |

## 为什么会这样

### 原因 1：ZEAMAP 有标签样本太少

ZEAMAP 只有 461 个带标签 accession。对于 199,856 个 SNP 输入和 66 个 traits 输出，这个样本量很小。

线性模型在小样本高维 SNP 预测里有天然优势：参数形式简单、正则化强、不容易过拟合。

深度模型虽然表达能力更强，但在标签样本太少时，容易学到训练集噪声。

### 原因 2：G2F 只提供 genotype 预训练，没有 trait 标签

G2F 预训练学到的是：

```text
玉米 SNP 之间的结构关系
```

它没有学到：

```text
SNP 如何影响 oil traits、fatty acid traits 或其他 phenotype/metabolome traits
```

所以它能降低 genotype reconstruction loss，但不一定能提高 trait prediction。

### 原因 3：G2F 和 ZEAMAP 不是同一套 SNP 坐标

直接检查后，两者只有 9 个 SNP 可以直接共用。

所以只能迁移通用 encoder 权重，不能把同一个 SNP token 的知识直接对齐迁移。

### 原因 4：当前任务可能更适合强线性基线

很多性状可能主要由可加遗传效应解释。ridge / ElasticNet 对这类任务很强。

如果深度模型没有更多样本、环境信息、表达信息或更强先验，很难稳定超过它。

## 我多次尝试后仍没有解决的问题

### 问题 1：深度模型没有超过 ridge / ElasticNet

已经尝试：

```text
ZEAMAP-only supervised SNPWindowFormer
ZEAMAP-only masked-genotype pretrain + fine-tune
G2F native masked-genotype pretrain + fine-tune
G2F fine-tune lower LR / higher dropout / stronger weight decay
```

仍未解决：

```text
测试集 median Pearson 仍低于 ridge / ElasticNet。
```

需要你做的事：

```text
决定文章是否接受“严格 benchmark + 深度模型失败边界”这个定位。
如果不接受，就需要提供或允许继续下载更多带 trait 标签的玉米数据。
```

### 问题 2：G2F 和 ZEAMAP SNP 坐标不一致

已经尝试：

```text
按 chrom + pos + ref + alt 做直接重叠检查。
```

结果：

```text
可直接共用 SNP 只有 9 个。
```

需要你做的事：

```text
如果要做真正 SNP-level 对齐迁移，需要提供同 genome build 的外部 genotype，或提供可靠 liftover 方案。
```

可参考链接：

```text
G2F resources: https://www.genomes2fields.org/resources/
Panzea genotypes: https://www.panzea.org/genotypes
```

### 问题 3：外部 genotype-only 预训练不等于外部 trait 监督

已经证明：

```text
G2F genotype reconstruction 能训练好，但 trait prediction 没提升。
```

需要你做的事：

```text
如果要继续冲模型性能，需要寻找带 phenotype/metabolome 标签的外部 accession-level 数据。
只增加 genotype-only 数据，收益可能有限。
```

### 问题 4：GPU 登录自动化不能用明文密码写日志

我可以继续手动或交互式登录 GPU 节点运行任务，但不能把 SSH 密码写进日志或脚本。

需要你做的事：

```text
建议配置 SSH key 登录 GPU 节点。
这样后续训练监控和自动提交会稳定很多。
```

## 当前建议

最稳的投稿方向：

```text
写成 maize multi-trait genomic prediction benchmark / model evaluation paper。
核心卖点是严谨比较，而不是夸大深度模型。
```

更冒险的方向：

```text
继续找更多有标签外部数据，重新设计更小、更有先验约束的模型，目标是超过 ridge / ElasticNet。
```

当前不建议：

```text
继续盲目加大 Transformer。
```

理由：

```text
瓶颈不是 A100 算力，而是 461 个有标签样本太少。
```

## 关键本地文件

```text
results/deep_model/windowformer_g2f_native_pretrain_v0/test_metrics.json
results/deep_model/windowformer_g2f_native_finetune_v0_1/test_metrics.json
results/deep_model/windowformer_g2f_native_finetune_lr1e5_do30_v0_1/test_metrics.json
results/deep_model/windowformer_supervised_norm_v0_1/test_metrics.json
docs/progress-plan.md
docs/model-architecture.md
README.md
```
