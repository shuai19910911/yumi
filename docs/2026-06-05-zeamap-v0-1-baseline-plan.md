# ZEAMAP v0.1 baseline benchmark plan

日期：2026-06-05

## 目标

当前 `v0.1` 只有 461 个强配对 accession，不适合直接训练大型多模态模型。阶段 3 的目标是先建立可复现 baseline，判断 genotype 和 population 是否能稳定预测 phenotype/metabolome。

## 输入

- `data/processed/v0_1/genotype_dosage_int8.npz`
- `data/processed/v0_1/genotype_samples.tsv`
- `data/processed/v0_1/genotype_variants.tsv`
- `data/processed/v0_1/phenotype.tsv`
- `data/processed/v0_1/population.tsv`
- `data/processed/v0_1/modality_mask.tsv`

## 方法

1. 固定 accession-level train/validation/test split。
2. 对 genotype dosage matrix 做标准化和 PCA，默认输出 100 个 genotype PCs。
3. 对每个 phenotype/metabolome trait 做缺失率、有效样本数和方差过滤。
4. 训练并比较四类模型：
   - `mean_baseline`
   - `population_ridge`
   - `genotype_pca_ridge`
   - `genotype_pca_population_ridge`
5. 在 validation/test split 上输出 trait-level R2、Pearson、Spearman、MAE 和 RMSE。

## 计算环境

CPU 作业提交到 Slurm `q07` 分区：

```bash
sbatch -p q07 -c 8 scripts/slurm/run_zeamap_v0_1_baseline.sh
```

脚本内部使用：

```bash
mamba run -n yumi python scripts/run_zeamap_v0_1_baseline.py --n-pcs 100
```

## 产出

- `data/processed/v0_1/splits/split_assignments.tsv`
- `data/processed/v0_1/genotype_pca.tsv`
- `data/processed/v0_1/genotype_pca_variance.tsv`
- `results/v0_1_baseline/trait_qc.tsv`
- `results/v0_1_baseline/trait_metrics.tsv`
- `results/v0_1_baseline/model_comparison.tsv`
- `results/v0_1_baseline/top_predictable_traits.tsv`
- `docs/2026-06-05-zeamap-v0-1-baseline-report.md`

## 判断标准

- 如果 `genotype_pca_population_ridge` 相比 `population_ridge` 在多个 trait 上有正向增益，说明 genotype 提供了 population covariates 之外的预测信号。
- 如果多数 trait 的 test R2 接近或低于 0，则当前样本量或 trait 噪声不足以支撑复杂模型。
- 后续多模态建模只优先使用 baseline 中稳定可预测的 trait。
