# yumi

ZEAMAP 玉米多性状预测模型项目。

## 当前重新定位

这个项目的目标需要改回来：不是写一篇以 GWAS 候选基因为主的文章，也不是只整理现有 benchmark，而是训练一个真正可以作为论文核心的**玉米基因型预测模型**。

更准确地说，我们要做的是：

```text
用 ZEAMAP 玉米公共数据构建 accession-level 多性状预测任务，
把 199,856 个 SNP 转成窗口 token，
训练 SNP window representation model，
再预测 phenotype/metabolome traits，
并与 ridge、ElasticNet、MLP 等强基线公平比较。
```

GWAS 和候选基因不是主线，只能作为模型结果的辅助解释。例如：如果模型发现 oil traits 最可预测，可以用 GWAS 或候选区间解释“为什么 oil traits 有强遗传信号”。但文章不能再写成“我们发现了 chr6/chr9 候选基因”的 GWAS 论文。

## 一句话说明

我们现在要做的是：

```text
ZEAMAP 数据整理
-> SNP window tokenizer
-> supervised SNPWindowFormer
-> masked-genotype self-supervised pretraining
-> multi-trait fine-tuning
-> ridge/ElasticNet/MLP 强基线比较
-> G2F/Panzea 外部数据扩展
-> trait family 和 ablation 分析
-> 写成真正的模型文章
```

## 为什么要改方向

之前工作走偏到了“油脂性状 GWAS + 候选基因投稿包”。这条路线不是完全没价值，但它不是当前项目最核心的目标。

现在重新判断后，模型文章更合适，原因是：

- 我们已经构建了一个干净的 ZEAMAP v0.1 accession-level 数据集。
- 已经完成了多性状 prediction benchmark。
- 已经比较了 ridge、ElasticNet、小 MLP、population-only 等模型。
- 已经做了 methylation 消融和多随机种子稳健性。
- 当前 ZEAMAP 样本量不适合单独训练大模型，但适合作为深度模型 fine-tuning/evaluation 数据。
- 2 张 A100 40G 可以支持 SNP window transformer，但需要窗口化 token，而不是直接把 199,856 个 SNP 当 199,856 个 token。
- GWAS 可以作为解释模型信号的辅助分析，而不是论文主线。

新的详细模型方案：

```text
docs/2026-06-06-good-model-paper-design.md
```

## 当前可用数据

核心数据集：

```text
data/processed/v0_1/
```

当前规模：

```text
461 accessions
199,856 SNPs
318 numeric phenotype/metabolome traits
236 accessions with methylation coverage
```

数据模态判断：

- `genotype`：主输入，当前最重要。
- `population`：重要协变量/基线特征。
- `phenotype/metabolome`：预测目标。
- `methylation`：辅助模态，只能在 236 个 accession 子集中评估。
- `expression`：当前不是 AMP accession-level expression，暂不作为主模型输入。
- `GWAS/candidate loci`：只作为模型解释和生物学解释的辅助模块。

## 已经完成的模型相关工作

### 0. 当前正在做的深度模型训练

现在已经不只是设计方案，深度模型训练已经启动。

已经完成的第一轮监督训练：

```text
模型：SNPWindowFormer
输入：199,856 个 SNP
做法：每 256 个 SNP 压成一个窗口 token
输出：66 个稳定 traits
训练方式：supervised multi-trait prediction
GPU：2 号 A100
结果目录：results/deep_model/windowformer_supervised_norm_v0_1/
日志：logs/windowformer_supervised_norm_gpu2_20260606_152101.log
```

为什么要先做这个模型：

```text
普通模型直接看 SNP PCA；
这个模型直接看接近 20 万个 SNP，但先把相邻 SNP 压成窗口。
这样既保留局部遗传信息，又不会把 199,856 个 SNP 当成 199,856 个超长 token。
```

已经修复的训练问题：

- 样本划分表改用 `pandas.read_csv` 读取，避免 accession/split 解析出错。
- 66 个 trait 已经按训练集均值/标准差做目标归一化，避免大数值性状支配 loss。

归一化后训练流程正常，最佳验证轮是 epoch 55：

```text
val median Pearson = 0.410
val median R2 = 0.137
test median Pearson = 0.351
test median R2 = 0.076
```

这个结果低于 ridge 强基线：

```text
ridge median Pearson = 0.498
ridge median R2 = 0.204
```

所以当前判断是：

```text
直接监督训练的深度模型还不够强。
下一步必须先做 masked-genotype self-supervised pretraining，
再把预训练权重 fine-tune 到 66 个 trait。
```

预训练已经完成：

```text
任务：masked-genotype pretraining
GPU：2 号 A100
结果目录：results/deep_model/windowformer_pretrain_v0_1/
日志：logs/windowformer_pretrain_gpu2_20260606_153859.log
test reconstruction loss = 0.621
best checkpoint = results/deep_model/windowformer_pretrain_v0_1/best.pt
```

这个预训练任务的意思是：

```text
随机遮住一部分 SNP 窗口，
让模型根据周围 SNP 信息猜回被遮住的 genotype。
它不使用 trait 标签，目的是先学会玉米基因型结构。
```

预训练后 fine-tuning 已经完成：

```text
任务：pretrained SNPWindowFormer fine-tuning
初始化权重：results/deep_model/windowformer_pretrain_v0_1/best.pt
GPU：2 号 A100
结果目录：results/deep_model/windowformer_finetune_v0_1/
日志：logs/windowformer_finetune_gpu2_20260606_155644.log
test median Pearson = 0.251
test median R2 = 0.021
```

这个结果比直接监督训练还低，说明：

```text
只用 ZEAMAP 461 个样本做 Transformer 预训练不够。
模型可以学到 genotype reconstruction，
但这个表征没有稳定转化为更好的 trait prediction。
```

更小、更强正则化的模型已经完成：

```text
任务：small regularized SNPWindowFormer
目的：减少过拟合
结果目录：results/deep_model/windowformer_small_regularized_v0_1/
日志：logs/windowformer_small_regularized_gpu2_20260606_161401.log
关键参数：d_model=96, layers=2, dropout=0.30, lr=5e-5, weight_decay=1e-3
test median Pearson = 0.325
test median R2 = 0.040
```

当前深度模型总评估：

```text
ridge baseline:                 Pearson 0.498 / R2 0.204
supervised SNPWindowFormer:      Pearson 0.351 / R2 0.076
pretrain + fine-tune:            Pearson 0.251 / R2 0.021
small regularized WindowFormer:  Pearson 0.325 / R2 0.040
```

结论：

```text
只用 ZEAMAP 461 个 accession，Transformer 还不能超过 ridge。
如果要写深度模型文章，下一步必须下载 G2F/Panzea 等外部 maize genotype 扩大预训练。
```

详细评估和下载清单：

```text
docs/2026-06-06-windowformer-training-validation-and-next-data.md
docs/2026-06-06-external-genotype-download-manifest.tsv
```

G2F 2014-2023 外部基因型下载入口已经解析到具体文件：

```text
inbreds_G2F_2014-2023_437k.vcf
key_inbreds_G2F_2014-2023.txt
readme.txt
```

它们会下载到：

```text
data/external/g2f/genotypic_2014_2023/
```

自动解析/下载脚本：

```bash
python scripts/fetch_g2f_genotype_resources.py --download
```

q08 作业模板：

```bash
sbatch -p q08 -c 2 jobs/2026-06-06_fetch_g2f_genotypes_q08.sh
```

注意：当前确认计算节点没有网络，真实下载只能在登录节点执行。登录节点访问 CyVerse 匿名下载链接时返回 IP verification 页面。脚本会把验证页自动改名为 `.blocked.html`，避免误当成 VCF/TXT。需要先在浏览器打开任一 `data.cyverse.org` 文件链接完成 CyVerse 验证后，再重新运行下载脚本。

Panzea 备用/补充外部基因型源已经定位：

```text
/iplant/home/shared/panzea/hapmap3/hmp321/unimputed/uplifted_APGv4
```

需要下载 `hmp321_agpv4_chr1.vcf.gz` 到 `hmp321_agpv4_chr10.vcf.gz`：

```text
data/external/panzea/hapmap3/hmp321_agpv4/
```

自动下载脚本：

```bash
python scripts/fetch_panzea_hapmap321_agpv4.py --download
```

q08 作业模板：

```bash
sbatch -p q08 -c 2 jobs/2026-06-06_fetch_panzea_hapmap321_q08.sh
```

注意：由于计算节点没有网络，Panzea 实际下载也应在登录节点直接运行脚本；q08 作业只保留为集群环境改变后的模板。

下载后检查命令：

```bash
python scripts/inspect_external_genotype_downloads.py --root data/external
```

如果在登录节点不想直接跑，也可以提交 q08：

```bash
sbatch -p q08 -c 2 jobs/2026-06-06_inspect_external_genotypes_q08.sh
```

下载完成后，外部预训练输入准备脚本是：

```bash
python scripts/prepare_external_genotype_pretrain_inputs.py
```

当前这个脚本已经能检查 inventory 和 ZEAMAP SNP 参考表；因为 G2F/Panzea genotype 还没下载，所以目前会明确提示：

```text
No usable external genotype files found yet.
```

### 1. 数据整理

已经完成：

- 检查 ZEAMAP 下载文件是否可读。
- 统一 phenotype、population、VCF、methylation 等表的 accession 命名。
- 构建统一样本索引。
- 构建 v0.1 processed dataset。

主要产出：

```text
data/metadata/zeamap_accession_index.tsv
data/processed/v0_1/
docs/2026-06-04-zeamap-v0-1-build-report.md
```

### 2. 基础预测模型

已经比较过：

- mean baseline
- population-only ridge
- genotype PCA ridge
- genotype PCA + population ridge

核心结论：

```text
genotype + population 的 ridge 模型最稳。
```

当前整体结果：

```text
66 robust traits
median Pearson = 0.498
median R2 = 0.204
positive R2 fraction = 0.979
```

主要结果文件：

```text
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
```

### 3. 性状家族分析

已经发现：

```text
oil traits 是最容易预测的性状家族。
```

trait family 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

这在模型文章里很重要，因为它说明：

```text
不同类型性状的可预测性不同，模型对 oil/fatty-acid traits 最有效。
```

主要结果文件：

```text
results/v0_1_baseline/selected_trait_family_summary.tsv
results/v0_1_baseline/robustness_trait_summary.tsv
results/v0_1_baseline/top_predictable_traits.tsv
```

### 4. 多随机种子稳健性

已经做了 repeated seed evaluation。

目的：

```text
不是只看一次 train/test split，而是看模型表现是否稳定。
```

这对模型文章很关键，因为审稿人会关心结果是不是偶然划分造成的。

主要结果文件：

```text
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_model_summary.tsv
results/v0_1_baseline/robust_selected_traits.tsv
```

### 5. 轻量模型比较

已经比较过 ridge、ElasticNet 和 small MLP。

当前结论：

```text
在 461 个 accession 的样本量下，ridge/ElasticNet 比 small MLP 更稳。
```

这不是说神经网络没用，而是说明：

```text
当前数据规模更适合正则化线性模型。
复杂模型需要更多 accession、更完整的多模态配对数据。
```

主要结果文件：

```text
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/lightweight_model_summary.tsv
```

### 6. methylation 消融

已经评估过 methylation 的几种用法：

- global methylation summary
- gene/promoter/cis-window methylation PCA
- sparse gene-window methylation selection

当前结论：

```text
methylation 在当前数据里只能作为辅助模态。
236 个 accession 的覆盖不足以支撑强多模态主模型。
```

主要结果文件：

```text
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
```

### 7. 可解释性与生物学辅助分析

已经做过：

- genotype attribution
- oil traits GEMMA LMM GWAS
- candidate loci annotation

这些不再作为主线，而是作为模型文章中的解释模块：

```text
模型发现 oil traits 最可预测。
GWAS/候选区间可以辅助说明这些性状确实有强遗传信号。
```

保留但降级的结果：

```text
results/v0_1_baseline/genotype_attribution_gene_summary.tsv
results/v0_1_baseline/genotype_attribution_snp_summary.tsv
results/v0_1_baseline/gemma_lmm_v0_1/
```

## 新论文目标

建议新文章方向：

```text
Self-supervised SNP window representation learning improves maize multi-trait prediction from public genotype resources
```

中文理解：

```text
基于自监督 SNP 窗口表征学习的玉米多性状预测模型
```

文章核心问题：

1. 199,856 个 SNP 能不能通过 window tokenizer 压缩成可训练的遗传表示？
2. SNPWindowFormer 能不能超过 ridge/ElasticNet/MLP 强基线？
3. masked-genotype 自监督预训练能不能提高 ZEAMAP 多性状预测？
4. 多性状学习是否比单性状训练更适合 oil/metabolome traits？
5. population 和 methylation 在深度模型中到底提供多少增益？
6. 外部 G2F/Panzea genotype 数据能否提升预训练和迁移验证？

## 新文章结构

建议主线：

```text
Introduction
  为什么公共多组学数据不能直接拿来建模
  为什么需要 accession-level harmonization
  为什么小样本下要先做稳健 benchmark

Results
  1. ZEAMAP v0.1 accession-level dataset and deep-learning tensor package
  2. SNP window tokenizer and SNPWindowFormer architecture
  3. Supervised deep model versus ridge / ElasticNet / MLP
  4. Masked-genotype pretraining and fine-tuning
  5. Trait-family performance and multi-trait learning
  6. Population/methylation ablation and model interpretation

Discussion
  当前模型路线适合什么
  为什么不是大模型
  为什么 oil traits 最强
  methylation 为什么暂时不能作为主模态
  后续如何扩展到更大 accession、多模态和预训练模型
```

## 需要保留的核心文件

这些是模型文章主线需要保留的：

```text
data/metadata/
data/processed/v0_1/
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
results/v0_1_baseline/selected_trait_family_summary.tsv
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_trait_summary.tsv
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
scripts/build_zeamap_sample_index.py
scripts/build_zeamap_v0_1_dataset.py
scripts/run_zeamap_v0_1_baseline.py
scripts/run_zeamap_v0_1_robustness.py
scripts/run_zeamap_v0_1_lightweight_models.py
scripts/run_zeamap_v0_1_methylation_subset.py
scripts/run_zeamap_v0_1_gene_methylation_pca.py
scripts/run_zeamap_v0_1_sparse_methylation_selection.py
```

## 已经清理或降级的信息

下面这些内容已经从主线中清理或降级：

- 大量 `Stage 5.x` 投稿包文件。
- cover letter、journal route、reviewer suggestion、Zenodo release draft。
- 以 chr6/chr9 候选基因为主的论文版本。
- 最终投稿 gate、人类作者信息模板、release checklist。
- 把 GEMMA GWAS 写成主结果的图表和段落。

当前保留少量 GWAS 结果，只用于解释模型为什么对 oil traits 更有效。

## 下一步计划

下一步应该做三件事：

1. 重画模型方向图表

重点画清楚：数据怎么进入模型、模型怎么比较、robust traits 怎么筛出来、methylation 怎么做消融。

2. 重写模型论文稿

围绕 prediction benchmark、model comparison、trait family predictability、methylation ablation 和 interpretation 写新稿。

3. 补模型结果表

把 final benchmark、trait family、model comparison、methylation ablation、robustness 组织成模型文章主表和补充表。

## 当前注意事项

当前最重要的是不要再继续往“GWAS 候选基因投稿包”方向扩展。

正确方向是：

```text
模型数据集 + 多性状预测 + 模型比较 + 模态消融 + 稳健性 + 可解释性
```

GWAS 只作为解释模型结果的一小部分。
