# yumi

玉米基因型到多性状预测模型项目。

## 现在到底在做什么

这个项目不是单纯做 GWAS，也不是只整理数据。当前主线是：

```text
给定一个玉米材料的 SNP 基因型，
预测它的多个表型和代谢性状。
```

通俗地说，就是想训练一个模型，让它看到玉米的 DNA 变异模式后，尽量准确地判断这个材料在油脂、脂肪酸、农艺性状等指标上会是什么表现。

## 当前数据

主数据来自 ZEAMAP：

```text
461 个玉米材料
199,856 个 SNP
318 个数值型 phenotype/metabolome traits
66 个通过稳定性筛选的核心 traits
```

外部预训练数据来自 G2F：

```text
2,193 个玉米自交系
437,214 个 SNP
只用于 genotype-only 自监督预训练
```

G2F 和 ZEAMAP 不是同一套基因组坐标：

```text
ZEAMAP: AGPv4 / B73 RefGen_v4
G2F: B73 v5 / G2F PHG marker space
```

两者直接可共用的 SNP 只有 9 个，所以不能硬拼成一个大 SNP 表。现在的做法是：G2F 保持自己的 SNP 顺序预训练模型，ZEAMAP 保持自己的 SNP 顺序做性状预测，只迁移模型中形状一致的通用权重。

## 已经完成什么

1. 整理出 ZEAMAP v0.1 processed dataset。
2. 建立 accession-level 样本索引和 trait 矩阵。
3. 筛选出 66 个更稳定、更适合建模的 traits。
4. 完成 ridge、ElasticNet、MLP、population-only 等传统基线。
5. 完成 ZEAMAP-only SNPWindowFormer 监督训练。
6. 完成 ZEAMAP-only masked-genotype 预训练和微调。
7. 完成 G2F native genotype matrix 构建。
8. 完成 G2F genotype-only masked pretraining。
9. 完成两轮 G2F 预训练权重迁移到 ZEAMAP 的 fine-tuning。

## 当前最重要结果

目前最强、最稳的还是传统线性模型：

```text
ridge / ElasticNet robust benchmark:
median Pearson 约 0.498
median R2 约 0.204
```

深度模型结果如下：

```text
ZEAMAP-only SNPWindowFormer:
median Pearson = 0.351
median R2 = 0.076

G2F pretrained -> ZEAMAP fine-tune:
median Pearson = 0.277
median R2 = 0.041

G2F pretrained -> ZEAMAP fine-tune, lower LR / stronger regularization:
median Pearson = 0.227
median R2 = 0.020
```

结论很直接：

```text
G2F 预训练成功学到了基因型重构任务，
但目前没有提升 ZEAMAP 性状预测。
深度模型还没有超过 ridge / ElasticNet 强基线。
```

## 这说明什么

当前 461 个带标签的 ZEAMAP 样本，对训练大深度模型太少。模型能跑通，但很容易过拟合，预测效果不如传统线性模型稳定。

这不是代码没跑完的问题，而是当前数据规模和任务设计限制。要把文章写成“深度模型明显优于传统方法”，还需要更多同类标签数据，或者重新设计成更适合小样本的模型。

## 下一步方向

优先做两件事：

1. 把论文目标改成诚实的模型基准文章：系统比较线性模型、浅层模型、深度模型、预训练迁移，说明在小样本玉米多性状预测中什么有效、什么无效。
2. 如果仍然要冲“深度模型优于基线”，需要补充更多带 phenotype/metabolome 标签的外部材料，或者拿到与 ZEAMAP 同坐标体系的外部 genotype 数据。

详细进展见：

```text
docs/progress-plan.md
docs/2026-06-07-g2f-pretrain-finetune-monitoring-report.md
docs/model-architecture.md
```
