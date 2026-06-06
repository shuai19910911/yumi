# Yumi progress plan

更新日期：2026-06-06

## 当前项目一句话

这个项目现在只做一件事：

```text
训练一个能发表的玉米基因型到多性状预测模型。
```

通俗理解：

```text
先把 SNP 变成模型能学习的窗口 token，
训练 SNP 表征模型，
再预测 ZEAMAP 的 phenotype/metabolome traits，
并和 ridge/ElasticNet/MLP 做公平比较。
```

## 已经纠正的方向

之前项目走偏到了：

```text
油脂性状 GWAS -> 候选基因 -> 投稿包
```

这个方向已经降级。以后不再把它作为主线。

新的主线是：

```text
数据整理
-> SNP window tokenizer
-> self-supervised genotype representation learning
-> multi-trait fine-tuning
-> ridge/ElasticNet/MLP 强基线比较
-> trait family 可预测性分析
-> population/methylation 消融
-> 外部 G2F/Panzea 数据扩展
-> 少量生物学解释
-> 模型方向论文
```

GWAS 和候选基因只作为辅助解释。例如模型发现 oil traits 最好预测时，可以用 GWAS 结果说明这些性状确实有较强遗传信号。

## 当前保留的核心数据

核心 processed dataset：

```text
data/processed/v0_1/
```

当前数据规模：

```text
461 个 accession 有 genotype + population + phenotype/metabolome
236 个 accession 额外有 methylation
199,856 个 SNP
318 个 numeric traits
66 个 robust traits 进入最终 benchmark
```

这些数据足够做严谨的小样本模型微调和评估，但不适合单独训练大型深度模型。

因此当前新策略是：

```text
ZEAMAP 用于 fine-tuning/evaluation；
G2F/Panzea 用于扩大 genotype 预训练和外部验证。
```

详细模型方案见：

```text
docs/2026-06-06-good-model-paper-design.md
```

## 当前已经完成的模型工作

### 1. 样本和数据统一

已经完成：

- 检查 ZEAMAP 下载文件。
- 统一 phenotype、population、VCF、methylation 的 accession 名字。
- 建立统一样本索引。
- 构建 v0.1 processed dataset。

关键文件：

```text
data/metadata/zeamap_accession_index.tsv
data/processed/v0_1/
docs/2026-06-04-zeamap-v0-1-build-report.md
```

### 2. 基础预测 benchmark

已经比较：

- mean baseline
- population-only ridge
- genotype PCA ridge
- genotype PCA + population ridge

当前主模型：

```text
genotype_population_ridge
```

核心结果：

```text
66 个 robust traits
median Pearson = 0.498
median R2 = 0.204
positive R2 fraction = 0.979
```

关键文件：

```text
results/v0_1_baseline/model_comparison.tsv
results/v0_1_baseline/trait_metrics.tsv
results/v0_1_baseline/final_v0_1_trait_benchmark.tsv
```

### 3. 哪些性状更容易预测

当前最清楚的结果：

```text
oil traits 是最好预测的一类性状。
```

trait family 结果：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

这应该成为模型文章的一个主结果：不同性状家族的可预测性明显不同。

### 4. 多随机种子稳健性

已经做了 repeated seed evaluation。

目的：

```text
证明结果不是某一次 train/test 划分碰巧得到的。
```

关键文件：

```text
results/v0_1_baseline/robustness_metrics.tsv
results/v0_1_baseline/robustness_model_summary.tsv
results/v0_1_baseline/robust_selected_traits.tsv
```

### 5. 轻量模型比较

已经比较：

- ridge
- ElasticNet
- small MLP

当前结论：

```text
ridge/ElasticNet 比 small MLP 更稳。
```

原因很直接：

```text
样本只有 461 个，但 SNP 接近 20 万个。
在这种“小样本、高维特征”场景下，强正则化线性模型更稳。
```

关键文件：

```text
results/v0_1_baseline/lightweight_model_metrics.tsv
results/v0_1_baseline/lightweight_model_summary.tsv
```

### 6. methylation 消融

已经测试：

- global methylation summary
- gene/promoter/cis-window methylation PCA
- sparse gene-window methylation selection

当前结论：

```text
methylation 只能作为辅助模态，不能作为 v0.1 主模型输入。
```

主要原因：

```text
只有 236 个 accession 有 methylation，配对样本太少。
```

关键文件：

```text
results/v0_1_baseline/methylation_subset_metrics.tsv
results/v0_1_baseline/gene_methylation_pca_metrics.tsv
results/v0_1_baseline/sparse_methylation_selection_metrics.tsv
```

### 7. 可解释性辅助结果

已经有：

- genotype attribution
- oil traits GEMMA LMM GWAS
- candidate loci annotation

但这些只放在解释层，不再作为论文主线。

保留原因：

```text
模型发现 oil traits 好预测后，可以用这些结果辅助解释遗传信号。
```

## 已经清理的旧方向内容

已经从仓库清理：

- Stage 5.x 投稿包文档。
- cover letter、reviewer suggestion、release plan、Zenodo metadata。
- 作者、单位、基金、COI 模板。
- 以 GWAS 候选基因为主的 manuscript draft。
- Stage 5 投稿包装脚本。
- 旧投稿包装图表和 manuscript tables。
- 日志和 Python 缓存。

清理后，仓库入口不再围绕“GWAS 投稿包”，而是围绕“模型文章”。

## 当前新增的深度模型任务

已经新增：

- `scripts/prepare_zeamap_deep_learning_inputs.py`
- `scripts/train_snp_window_transformer_multitask.py`
- `jobs/2026-06-06_prepare_deep_inputs_q08.sh`
- `jobs/gpu_run_windowformer_supervised.sh`
- `jobs/gpu_run_windowformer_pretrain.sh`
- `jobs/gpu_run_windowformer_finetune.sh`
- `docs/2026-06-06-good-model-paper-design.md`
- `docs/2026-06-06-gpu-run-guide.md`
- `docs/2026-06-06-windowformer-resource-estimate.md`

已经完成 q08 输入准备：

```text
job 8459940: prepare ZEAMAP deep learning input tensors
```

已经生成：

```text
data/deep_model/v0_1/
```

内容包括：

```text
461 个 accession
199,856 个 SNP
66 个 robust traits
train/val/test = 323/69/69
```

也就是说，深度模型现在已经可以直接读取 numpy tensor 训练，不再需要每次重新解析 VCF 或大表。

## 2026-06-06 GPU 训练进展

已经在 GPU 节点启动了第一个正式深度模型试验。

已经完成的监督训练：

```text
模型：SNPWindowFormer
输入：199,856 个 SNP，按 256 个 SNP 一个窗口切成 window token
输出：66 个 robust traits
训练方式：supervised multi-trait prediction
GPU：2 号 A100
输出目录：results/deep_model/windowformer_supervised_norm_v0_1/
日志：logs/windowformer_supervised_norm_gpu2_20260606_152101.log
```

中间发现并修复了两个关键问题：

1. `splits.tsv` 读取方式不稳。

原来用 `np.genfromtxt` 读取样本划分表，GPU 训练时把空字符串也读进来了，导致脚本报错。现在改成 `pandas.read_csv`，并且增加了检查：如果某个 accession 没有 train/val/test 标签，会直接报出样本名。

2. 不能直接用性状原始数值做 MSE。

第一次监督训练能跑，但 loss 到了 1e13 量级，R2 很差。原因是不同性状单位不同、数值范围差异很大，模型会被大数值性状主导。现在改为只用训练集计算每个 trait 的均值和标准差，训练时预测标准化后的 trait，评估时再还原到原始单位计算 Pearson/R2。

归一化后训练流程正常，最佳验证轮为 epoch 55：

```text
val median Pearson = 0.410
val median R2 = 0.137
test median Pearson = 0.351
test median R2 = 0.076
```

这个结果低于当前 ridge 强基线：

```text
ridge test median Pearson = 0.498
ridge test median R2 = 0.204
```

所以结论很明确：

```text
直接监督训练 SNPWindowFormer 还不够。
下一步必须做 masked-genotype self-supervised pretraining，或者引入更多外部 genotype 数据扩大预训练。
```

已经完成的下一步：

```text
任务：masked-genotype pretraining
GPU：2 号 A100
输出目录：results/deep_model/windowformer_pretrain_v0_1/
日志：logs/windowformer_pretrain_gpu2_20260606_153859.log
test reconstruction loss = 0.621
best checkpoint = results/deep_model/windowformer_pretrain_v0_1/best.pt
```

预训练任务的含义：

```text
随机遮住一部分 SNP 窗口，
让模型根据上下文恢复被遮住位置的 SNP genotype 类别。
这一步不使用 trait 标签，目的是先学习玉米 genotype 的结构。
```

已经完成 fine-tuning：

```text
任务：pretrained SNPWindowFormer fine-tuning
初始化权重：results/deep_model/windowformer_pretrain_v0_1/best.pt
GPU：2 号 A100
输出目录：results/deep_model/windowformer_finetune_v0_1/
日志：logs/windowformer_finetune_gpu2_20260606_155644.log
test median Pearson = 0.251
test median R2 = 0.021
```

这个结果比直接监督训练还低，也明显低于 ridge。当前判断：

```text
只用 ZEAMAP 461 个样本做 Transformer 预训练和 fine-tuning 不够。
模型会很快记住训练集，但验证集和测试集提升不稳定。
```

已经完成的改进试验：

```text
任务：small regularized SNPWindowFormer
目的：减少参数、增加 dropout、降低学习率，先控制过拟合
输出目录：results/deep_model/windowformer_small_regularized_v0_1/
日志：logs/windowformer_small_regularized_gpu2_20260606_161401.log
关键参数：d_model=96, layers=2, dropout=0.30, lr=5e-5, weight_decay=1e-3
test median Pearson = 0.325
test median R2 = 0.040
```

阶段评估文档：

```text
docs/2026-06-06-windowformer-training-validation-and-next-data.md
docs/2026-06-06-external-genotype-download-manifest.tsv
```

当前模型训练结论：

```text
ridge 仍然是当前最强模型；
三个 WindowFormer 版本都没有超过 ridge；
如果论文主打深度表征学习，必须引入外部 maize genotype 做更大规模预训练。
```

资源估算：

```text
当前先用 1 x A100 40G
batch size 16
AMP on
实际占用约 6.6 GB
```

自动选卡脚本：

```bash
bash jobs/gpu_run_windowformer_supervised.sh
```

## 后续只做这条主线

下一步任务按优先级：

1. 下载 G2F 2014-2023 genotypic data。

现在已经确认 G2F 2014-2023 不是一个模糊目录，而是 3 个明确文件：

```text
inbreds_G2F_2014-2023_437k.vcf
key_inbreds_G2F_2014-2023.txt
readme.txt
```

这 3 个文件来自 CyVerse Data Commons / G2F DOI：

```text
10.25739/ragt-7213
```

当前登录节点访问 `data.cyverse.org` 时返回的是 CyVerse 的 IP verification 页面，不是真实数据文件。因此下载入口已经解决，但当前网络出口需要先完成 CyVerse 网页验证，或者换一个没有被拦截的计算节点下载。

已经新增自动解析和下载脚本：

```text
scripts/fetch_g2f_genotype_resources.py
jobs/2026-06-06_fetch_g2f_genotypes_q08.sh
```

可以提交：

```bash
sbatch -p q08 -c 2 jobs/2026-06-06_fetch_g2f_genotypes_q08.sh
```

如果 q08 节点也被 CyVerse 验证页拦截，脚本会明确报：

```text
blocked_by_cyverse_ip_verification
```

这时不要继续训练模型，要先解决 G2F 文件下载。

2. 下载 Panzea HapMap/GBS genotype flat files。

Panzea 也已经定位到一个可执行的 VCF 目录：

```text
CyVerse path:
/iplant/home/shared/panzea/hapmap3/hmp321/unimputed/uplifted_APGv4

Files:
hmp321_agpv4_chr1.vcf.gz
...
hmp321_agpv4_chr10.vcf.gz
```

目标下载目录：

```text
data/external/panzea/hapmap3/hmp321_agpv4/
```

已经新增自动下载脚本：

```text
scripts/fetch_panzea_hapmap321_agpv4.py
jobs/2026-06-06_fetch_panzea_hapmap321_q08.sh
```

这个数据可以作为 G2F 的补充，或者在 G2F 暂时被 CyVerse IP 验证拦截时作为备用外部预训练来源。

3. 下载后运行外部 genotype 完整性检查：

```bash
python scripts/inspect_external_genotype_downloads.py --root data/external
```

也可以提交 q08：

```bash
sbatch -p q08 -c 2 jobs/2026-06-06_inspect_external_genotypes_q08.sh
```

当前已经新增下载后检查脚本：

```text
scripts/inspect_external_genotype_downloads.py
jobs/2026-06-06_inspect_external_genotypes_q08.sh
```

当前已经新增外部预训练输入准备骨架：

```text
scripts/prepare_external_genotype_pretrain_inputs.py
```

目前运行结果是：

```text
No usable external genotype files found yet.
```

这是预期结果，因为 G2F/Panzea genotype 还没有下载到 `data/external/`。

4. 下载完成后运行 inventory 检查。
5. 根据实际文件格式补全 VCF/HapMap/table parser。
6. 扩大 masked-genotype pretraining。
7. 回到 ZEAMAP v0.1 做 fine-tuning/evaluation。
8. 做多 seed、trait family、population/methylation 消融。
9. 根据深度模型结果重写模型论文。

## 论文建议标题

暂定英文标题：

```text
Self-supervised SNP window representation learning improves maize multi-trait prediction from public genotype resources
```

中文理解：

```text
基于自监督 SNP 窗口表征学习的玉米多性状预测模型
```

## 当前判断

当前项目不是“没做完”，而是要把已经完成的工作重新组织成正确故事。

最有论文价值的结果是：

```text
ZEAMAP 公共数据可以整理成干净的 accession-level 模型数据集；
genotype + population 对多类性状有稳定预测能力；
oil traits 最容易预测；
在当前样本量下，ridge/ElasticNet 比 small MLP 更可靠；
methylation 覆盖不足，暂时只能作为辅助模态；
GWAS 结果可作为 oil traits 可预测性的生物学解释。
```
