# Model architecture notes

更新日期：2026-06-04

## 建模对象

第一阶段模型不是泛植物大模型，而是 ZEAMAP 玉米 accession-level 多模态预训练模型。

主要实体：

- `accession_id`：核心样本单位。
- `gene_id`：基因级 token 和特征聚合单位。
- `variant_id`：VCF 中的 SNP/INDEL/SV 位点。
- `trait_id`：农艺性状、油分/氨基酸、代谢物。
- `modality`：genotype、expression、epigenome、metabolome、phenotype、population。

## 数据接口

v0.1 已把强配对 accession 写成本地 processed dataset：

```text
data/processed/v0_1/accessions.tsv
data/processed/v0_1/modality_mask.tsv
data/processed/v0_1/population.parquet
data/processed/v0_1/phenotype.parquet
data/processed/v0_1/genotype_samples.tsv
data/processed/v0_1/genotype_variants.tsv
data/processed/v0_1/genotype_dosage_int8.npz
```

当前 batch 先使用 genotype、phenotype/metabolome、population 和 methylation coverage mask。第一批 expression 文件是 B73/SK/HZS/Mo17 reference/tissue expression，不是 AMP accession-level paired expression，因此暂不作为 v0.1 accession-level 输入。

建议先把可配对模态变成统一 batch：

```text
batch = {
  accession_id,
  modality_mask,
  genotype_features,
  regulatory_features,
  metabolite_features,
  phenotype_targets,
  population_covariates
}
```

其中：

- `modality_mask` 表示该 accession 哪些模态可用。
- `genotype_features` 在 v0.1 中来自 `genotype_dosage_int8.npz`，矩阵 shape 为 `[variants, samples]`，sample 顺序以 `genotype_samples.tsv` 为准。
- `population_covariates` 默认不作为预测目标，而作为协变量或 adversarial/confounder control。
- `phenotype_targets` 和 `metabolite_features` 在不同任务中可以互换为输入或目标。

## 编码器设计

### Genotype encoder

输入：

- VCF genotype dosage：0/1/2 或 missing。
- 位点注释：染色体、位置、影响基因、功能注释。

第一版做法：

- SNP 先按 MAF、missing rate、LD pruning 过滤。
- 对每个 accession 形成 sparse genotype vector。
- 可选 gene-level 聚合：promoter/gene body/cis-window 内 ALT dosage sum、deleterious count、variant category count。

模型：

- baseline：MLP 或 linear projection。
- 后续：variant set transformer 或 gene-window attention。

### Expression encoder

输入：

- gene expression matrix，行是 gene，列是 sample/accession。

第一版做法：

- log1p 或 rank-normalization。
- 选择高变基因或 pathway/gene-family 聚合。
- 输出 accession expression embedding。

模型：

- MLP over selected genes。
- gene token transformer：每个 gene 一个 token，token feature 是 expression value + gene embedding。

### Regulatory encoder

输入：

- DNA methylation、open chromatin、chromatin interaction、histone modification。

第一版做法：

- 暂不处理原始 reads。
- 把 BED/bigWig/matrix 聚合到 gene promoter、gene body、distal cis-window。
- 允许样本缺失，依赖 `modality_mask`。

模型：

- region-to-gene pooling + MLP。
- 后续接 graph attention，把 chromatin interaction 作为 gene-gene 或 enhancer-gene edge。

### Metabolome/phenotype encoder

输入：

- `ZEAMAP_phenotype_AMP_183_known_Metabolites.xls`
- `ZEAMAP_phenotype_AMP_agri_AA_Oil.xls`

第一版做法：

- 数值列标准化。
- 分类/环境字段作为 metadata，不直接混入 target。
- 缺失值用 mask，而不是简单填 0。

模型：

- MLP encoder。
- 多任务 regression head。

### Population encoder

输入：

- `amp_pca.txt`
- `amp_str.txt`

用途：

- 作为协变量输入。
- 用于评估模型是否过度依赖群体结构。
- 可在 phenotype prediction 中做 residualization 或 covariate adjustment。

## 融合结构

第一版推荐 late fusion：

```text
genotype_embedding   \
expression_embedding  \
regulatory_embedding   -> fusion transformer/MLP -> accession_embedding -> task heads
metabolite_embedding  /
population_embedding /
```

原因：

- ZEAMAP 各模态覆盖不一定完全一致。
- late fusion 容易支持缺失模态。
- 第一阶段更容易调试 ID 对齐和数据泄漏问题。

第二版可以扩展为 gene-centric fusion：

```text
gene token = {
  gene_id_embedding,
  cis_variant_features,
  expression_value,
  methylation_features,
  chromatin_accessibility_features,
  interaction_edges
}
```

然后对每个 accession 训练 gene token transformer，得到 accession embedding 和 gene embedding。

## 预训练任务

优先顺序：

1. masked phenotype/metabolite prediction：遮掉部分 phenotype/metabolite，用 genotype、expression、population 预测。
2. masked expression prediction：遮掉部分 genes，用 genotype/regulatory/population 预测表达。
3. cross-modal contrastive learning：同一 accession 的不同模态为正样本。
4. modality dropout reconstruction：随机丢掉 expression 或 phenotype，让模型从剩余模态恢复。
5. gene-context prediction：预测 gene-level expression/regulatory state。

## 评估

内部评估：

- 按 accession split，避免同一 accession 泄漏。
- trait-level R2/Pearson/Spearman。
- metabolite-level masked reconstruction error。
- modality ablation：去掉 genotype/expression/population 后性能变化。

关键风险：

- 样本 ID 不一致导致错误配对。
- 群体结构泄漏导致 phenotype prediction 虚高。
- reference genome 版本不一致导致 gene ID 无法稳定对齐。
- epigenome 样本可能和 AMP accessions 弱配对或不完全配对。

第一版目标是先做对齐和 baseline，不追求复杂模型。
