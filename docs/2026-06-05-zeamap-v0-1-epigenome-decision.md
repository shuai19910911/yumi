# ZEAMAP v0.1 epigenome decision

日期：2026-06-05

## Decision

v0.1 主模型不接入 raw gene-window methylation features。后续主线继续使用 `genotype+population ridge` 和 66 个 robust traits；methylation 保留为辅助 PCA 特征、coverage/missing-modality mask、消融实验和候选 gene/window 解释表。

## Evidence

阶段 4.1 global methylation summary:

- 236 个 methylation-covered accessions。
- `genotype_population_methylation_ridge` median Pearson/R2：0.496 / 0.173。
- `genotype_population_ridge` median Pearson/R2：0.490 / 0.173。
- 结论：全局 summary 几乎没有整体增益。

阶段 4.2 gene/promoter/cis-window methylation PCA:

- 39,005 genes，mCG/mCHG/mCHH x gene/promoter/cis-window，共 90 PCA features。
- `genotype_population_gene_methylation_pca_ridge` median Pearson/R2：0.496 / 0.199。
- `genotype_population_ridge` median Pearson/R2：0.490 / 0.173。
- 结论：PCA methylation 有小幅 R2 增益，但不是决定性信号。

阶段 4.3 sparse gene-window methylation:

- 10 个 methylation gain 较高 traits，4500 个候选 gene-window features。
- `genotype_population_gene_methylation_pca_ridge` median Pearson/R2：0.449 / 0.160。
- `genotype_population_ridge` median Pearson/R2：0.414 / 0.106。
- `genotype_population_sparse_methylation_elasticnet` median Pearson/R2：0.338 / 0.025。
- 结论：raw gene-window methylation 稀疏模型整体低于 PCA methylation 和 genotype+population baseline。

## Practical Rule

- 默认主模型输入：genotype PCA/full regularized genotype representation + population covariates。
- 默认评估集合：66 个 robust traits。
- methylation 默认不作为主输入；只在 ablation 中使用 `methylation_gene_region_pca.tsv`。
- `sparse_methylation_selected_features.tsv` 只作为候选解释表，不作为性能结论。
- open chromatin 和 chromatin interaction 暂作为 B73/reference regulatory prior，不做 accession-level 主输入，除非后续拿到更完整的 accession-paired matrix。

## Next Work

1. 固化 v0.1 main benchmark：以 `genotype_population_ridge` 为主线，输出 trait family 层面的 final table。
2. 做 genotype 侧可解释性：按 trait family 建立 SNP/gene-window burden 或 ElasticNet feature attribution。
3. 只在需要写论文/报告时，把 methylation PCA 作为辅助消融结果呈现。
