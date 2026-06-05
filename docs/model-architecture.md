# Model architecture notes

更新日期：2026-06-05

## 建模对象

第一阶段模型不是泛植物大模型，也不是直接上复杂多模态 transformer。当前 461 个强配对 accession 更适合先做 ZEAMAP 玉米 accession-level baseline benchmark，证明 genotype/population 对 phenotype/metabolome 是否有稳定可预测信号。

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

## v0.1 baseline 优先级

当前推荐模型顺序：

1. population-only baseline：只用 PCA/structure 预测 trait，作为群体结构对照。
2. genotype PCA baseline：从 dosage matrix 提取低维 genotype PCs，再用 ridge/elastic net 预测 trait。
3. genotype PCA + population：检查 genotype 是否在 population covariates 之外提供增益。
4. 轻量 MLP：仅在正则化 baseline 有信号后使用，避免样本量不足导致过拟合。

暂不推荐：

- 直接用 199,856 SNP 训练深层模型。
- 直接做大规模 contrastive pretraining。
- 把 236 个 methylation-covered accession 作为主训练全集。
- 把 B73/SK/HZS/Mo17 reference/tissue expression 当成 AMP accession-level expression。

当前 baseline 结果：

- `genotype_pca_population_ridge` 是第一版最优 baseline，test median Pearson 为 0.331，test median R2 为 0.034。
- `genotype_pca_ridge` 优于 `population_ridge`，说明 genotype PCs 提供了 population covariates 之外的信号。
- 最强可预测 trait 主要是 oil 相关性状，适合作为下一阶段主评估 trait 集合的候选。
- 大量 trait 的 R2 仍然较低或不稳定，下一步应做 trait subset selection，而不是直接扩大模型复杂度。
- 第一版 selected traits 共 130 个：oil 29、agronomic 16、amino acid 9、metabolite 76。后续小模型和多模态实验应优先在这个 trait 集合上做，再用 multi-seed robustness 收紧。
- Multi-seed robustness 后保留 66 个 robust traits：oil 29、metabolite 16、agronomic 15、amino acid 6。后续模型主目标应优先使用这 66 个 traits。

### Genotype encoder

输入：

- VCF genotype dosage：0/1/2 或 missing。
- 位点注释：染色体、位置、影响基因、功能注释。

第一版做法：

- SNP 先按 MAF、missing rate、LD pruning 过滤。
- 对每个 accession 形成 sparse genotype vector。
- 可选 gene-level 聚合：promoter/gene body/cis-window 内 ALT dosage sum、deleterious count、variant category count。

模型：

- baseline：PCA/SVD + ridge/elastic net。
- 小模型：MLP 或 linear projection。
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

baseline 完成前，第一版不做复杂融合。先比较以下输入组合：

```text
population_only -> trait heads
genotype_pca -> trait heads
genotype_pca + population -> trait heads
```

baseline 有明确增益后，再进入 late fusion：

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

当前优先顺序：

1. genotype/population to phenotype/metabolome baseline。
2. trait 可预测性筛选。
3. masked phenotype/metabolite prediction。
4. modality dropout reconstruction。
5. gene-context prediction。
6. cross-modal contrastive learning。

暂缓任务：

- masked expression prediction：等待 accession-level expression 或明确的 reference prior 设计。
- genotype-to-expression prediction：当前没有 AMP accession-level expression 配对。

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
