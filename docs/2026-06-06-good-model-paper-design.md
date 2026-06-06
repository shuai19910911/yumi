# 2026-06-06 好模型论文重新设计

## 结论先说

当前真正值得继续做的方向不是继续整理 GWAS 投稿包，也不是只把 ridge benchmark 写成论文。

更合适的目标是：

```text
训练一个玉米基因型表征模型，让它从 SNP 中学习 accession 的遗传表示，
再用这个表示预测 ZEAMAP 的多性状 phenotype/metabolome。
```

建议论文主线：

```text
SNP window tokenizer
-> self-supervised genotype representation learning
-> multi-trait phenotype/metabolome fine-tuning
-> comparison with ridge/ElasticNet/MLP
-> trait-family transfer and methylation/population ablation
-> external genotype/phenotype data validation
```

## 为什么之前又走歪了

前一轮主要在做“文档、图表、终稿导出”。这对投稿包装有用，但没有解决最关键问题：

```text
我们到底训练了什么更好的模型？
```

现在必须把工作重心改成模型本身。

## 当前数据能做什么

本仓库已有 ZEAMAP v0.1：

```text
461 accessions
199,856 SNPs
318 numeric traits
66 robust traits
236 accessions with methylation
```

这批数据适合做模型微调和严格评估，但不适合单独训练大型深度模型。原因是样本数太少。

因此，深度模型路线必须是：

```text
先用更多未标注/弱标注玉米 genotype 数据预训练，
再在 ZEAMAP 多性状上微调。
```

## 推荐文章题目

英文暂定：

```text
Self-supervised SNP window representation learning improves maize multi-trait prediction from public genotype resources
```

中文理解：

```text
基于自监督 SNP 窗口表征学习的玉米多性状预测模型
```

## 核心模型设计

### 1. SNP window tokenizer

不能把 199,856 个 SNP 直接当 199,856 个 transformer token。

原因：

```text
普通 transformer 的计算量和 token 数平方相关。
199,856 个 token 会爆显存。
```

所以采用窗口化：

```text
每 256 个连续 SNP 作为一个 window token
199,856 SNP -> 约 781 个 window tokens
```

这样 2 张 A100 40G 可以训练。

### 2. 自监督预训练

预训练任务：

```text
随机遮住一部分 SNP windows，
让模型根据其他 windows 还原被遮住窗口里的 genotype dosage。
```

类似语言模型的 masked token prediction，但对象是 SNP dosage。

### 3. 多性状微调

微调任务：

```text
输入：SNP window 表示 + population covariates
输出：66 个 robust phenotype/metabolome traits
```

loss 使用 masked MSE，因为不同 trait 有不同缺失情况。

### 4. 对照模型

必须比较：

- ridge
- ElasticNet
- small MLP
- supervised SNPWindowFormer
- self-supervised pretrain + SNPWindowFormer fine-tune
- population-only
- genotype-only
- genotype + population

## 当前已经生成的脚本

CPU 数据准备脚本：

```text
scripts/prepare_zeamap_deep_learning_inputs.py
```

GPU 训练脚本：

```text
scripts/train_snp_window_transformer_multitask.py
```

CPU q08 提交脚本：

```text
jobs/2026-06-06_prepare_deep_inputs_q08.sh
```

## 当前 GPU 训练命令

如果 PyTorch CUDA 还没装，先在 `yumi` 环境安装：

```bash
mamba run -n yumi python -m pip install torch --index-url https://download.pytorch.org/whl/cu121
```

监督训练第一版：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_supervised_v0_1 \
  --mode supervised \
  --epochs 300 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6
```

自监督预训练：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_pretrain_v0_1 \
  --mode pretrain \
  --epochs 500 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6
```

预训练后微调：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_finetune_v0_1 \
  --mode finetune \
  --pretrained-checkpoint results/deep_model/windowformer_pretrain_v0_1/best.pt \
  --epochs 300 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6
```

## 需要补充下载的数据

为了让文章真正像“好模型论文”，建议补充至少一种外部数据。

已核实的数据入口：

- G2F Resources: <https://www.genomes2fields.org/resources/>
- Panzea: <https://www.panzea.org/>
- MaizeGDB: <https://www.maizegdb.org/>

### 优先级 1：G2F Genomes to Fields

用途：

```text
外部 genotype/phenotype 数据，用于预训练、外部验证、GxE 扩展。
```

需要下载：

- G2F 2014 field season release。
- G2F 2015 field season release。
- G2F 2016 field season release。
- G2F 2017 field season release。
- G2F 2018 field season release。
- G2F 2019 field season release。
- G2F 2020 field season release。
- G2F 2021 field season release。
- G2F 2022 field season release。
- G2F 2023 field season release。
- G2F 2014-2023 genotypic data release。
- 可选：G2F 2024 Maize Genotype by Environment Prediction Competition Data。

文章价值：

```text
ZEAMAP 证明模型能预测 metabolome/oil traits；
G2F 证明模型不只在一个数据库里有效，还能迁移到农艺产量/GxE 数据。
```

### 优先级 2：Panzea

用途：

```text
补充 maize diversity genotype/phenotype flat files，
增加 accession 数量和遗传多样性。
```

需要下载：

- Panzea Data -> Genotypes。
- Panzea Data -> Phenotypes。
- Panzea Data -> Genome Annotations。
- 可选：Panzea RNAseq Data，只作为后续功能解释，不作为当前主模型输入。

文章价值：

```text
作为 genotype-only 自监督预训练数据，
也可以作为部分 phenotype 外部验证数据。
```

### 优先级 3：MaizeGDB / reference annotation

用途：

```text
给 SNP windows 加基因密度、功能区间、染色体位置注释。
```

需要下载：

- MaizeGDB Downloads。
- B73 representative genome annotation。
- NAM parents / genome assembly collections。
- SNPversity 2.0 或 variation-related resources。
- 可选 pathway/gene functional annotation。

文章价值：

```text
用于解释模型关注的 windows 是否富集在基因区、调控区或 oil/fatty-acid 相关区域。
```

## 论文实验设计

### Experiment 1：ZEAMAP 内部模型评估

问题：

```text
SNPWindowFormer 能不能超过 ridge/ElasticNet？
```

指标：

- median Pearson
- median R2
- positive R2 fraction
- trait-family median performance
- seeds across 5 splits

### Experiment 2：自监督预训练是否有用

比较：

```text
supervised SNPWindowFormer
vs
masked-genotype pretraining + fine-tuning
```

如果外部 genotype 数据下载完成，还要比较：

```text
ZEAMAP-only pretraining
vs
Panzea/G2F+ZEAMAP pretraining
```

### Experiment 3：多性状学习是否有用

比较：

```text
single-trait training
vs
multi-trait training
```

预期：

```text
相关 trait family，尤其 oil/fatty-acid traits，会从 multi-trait learning 中获益。
```

### Experiment 4：population/methylation ablation

比较：

```text
genotype only
genotype + population
genotype + population + methylation PCA
```

当前判断：

```text
population 应该保留；
methylation 只能作为辅助消融，不能作为主模型卖点。
```

### Experiment 5：模型解释

做法：

```text
对预测最好的 oil traits，计算 window-level attribution。
检查高贡献 windows 是否与 GEMMA lead loci、gene annotation 或 fatty-acid biology 有交叉。
```

注意：

```text
这只是解释模型，不是重新写成 GWAS 文章。
```

## 文章卖点

1. 不是普通 ridge benchmark，而是训练了 SNP window 深度表征模型。
2. 不是盲目深度学习，而是针对 SNP 超长序列设计 window tokenizer。
3. 不是只看单个性状，而是多性状、多 family、跨 seed 稳健评估。
4. 不是只在一个 split 上报最高分，而是和 ridge/ElasticNet/MLP 做公平比较。
5. 如果补充 G2F/Panzea，可形成跨数据集预训练和迁移验证。

## 当前风险

最大风险：

```text
ZEAMAP 只有 461 个 accession，深度模型可能打不过 ridge。
```

解决方案：

```text
必须做外部 genotype 数据预训练；
必须把 ridge 作为强基线；
必须报告失败的 deep model ablation；
如果 transformer 不赢，改写成“什么时候深度模型不能超过正则化模型”的方法学论文。
```

## 下一步

1. q08 生成 `data/deep_model/v0_1/` 输入包。
2. 你在 GPU 上跑 supervised SNPWindowFormer。
3. 如果 supervised 不超过 ridge，马上跑 masked pretraining + fine-tuning。
4. 同时下载 G2F/Panzea，扩展预训练数据。
5. 根据 GPU 结果决定论文定位：
   - 如果显著超过 ridge：写深度模型提升论文。
   - 如果接近 ridge：写稳健 benchmark + 深度模型边界论文。
   - 如果明显低于 ridge：必须引入外部预训练，否则不建议投稿高水平模型文章。
