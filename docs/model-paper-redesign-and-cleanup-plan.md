# Model-paper redesign and cleanup plan

日期：2026-06-06

## 新目标

项目重新定位为 ZEAMAP 玉米多性状预测模型文章。

新的论文主线是：

```text
accession-level data harmonization
-> genotype/population/methylation feature design
-> multi-trait prediction benchmark
-> model comparison
-> trait-family predictability analysis
-> methylation ablation
-> robustness evaluation
-> model interpretation
```

GWAS 不再是论文主线。GWAS 和 candidate loci 只作为解释模型发现的辅助分析。

## 保留内容

必须保留：

- `data/metadata/`
- `data/processed/v0_1/`
- `results/v0_1_baseline/model_comparison.tsv`
- `results/v0_1_baseline/trait_metrics.tsv`
- `results/v0_1_baseline/final_v0_1_trait_benchmark.tsv`
- `results/v0_1_baseline/selected_trait_family_summary.tsv`
- `results/v0_1_baseline/robustness_metrics.tsv`
- `results/v0_1_baseline/robustness_trait_summary.tsv`
- `results/v0_1_baseline/lightweight_model_metrics.tsv`
- `results/v0_1_baseline/methylation_subset_metrics.tsv`
- `results/v0_1_baseline/gene_methylation_pca_metrics.tsv`
- `results/v0_1_baseline/sparse_methylation_selection_metrics.tsv`
- `results/v0_1_baseline/genotype_attribution_gene_summary.tsv`
- `results/v0_1_baseline/genotype_attribution_snp_summary.tsv`
- 核心模型脚本：dataset build、baseline、robustness、lightweight models、methylation ablation、final benchmark。

可保留为辅助解释：

- `results/v0_1_baseline/gemma_lmm_v0_1/`
- `scripts/prepare_zeamap_v0_1_gemma_inputs.py`
- `scripts/summarize_zeamap_v0_1_gemma_lmm.py`
- `scripts/build_zeamap_v0_1_gemma_candidate_loci.py`
- `scripts/build_zeamap_v0_1_top_locus_priority.py`

## 已删除或归档内容

已经清理：

- `docs/2026-06-06-zeamap-v0-1-stage5-*`
- 投稿包文件：cover letter、reviewer suggestion、release plan、Zenodo metadata、submission gate。
- 作者/单位/基金/COI 模板。
- 以 GWAS 候选基因为主的 manuscript draft、polished manuscript、target-journal manuscript。
- Stage 5 论文包装脚本：`scripts/build_zeamap_v0_1_stage5_*.py`
- `scripts/__pycache__/`
- `logs/`
- 旧投稿包装图件：`manuscript_figures_stage5_*`
- 旧 GWAS 投稿表格：`manuscript_tables/`

## 为什么要清理

这些文件会让项目看起来像一篇 GWAS 候选基因论文，而不是模型文章。

保留它们会造成三个问题：

1. README 和文档入口难读。
2. 项目目标被误解为投稿包整理，而不是模型研究。
3. 后续继续工作时容易沿着错误方向扩展。

## 清理后项目应该长什么样

清理后，仓库应该只突出四类内容：

```text
1. 数据构建
2. 模型训练与评估
3. 模态消融与稳健性
4. 模型文章草稿与模型方向图表
```

## 下一步模型文章任务

清理后应继续做：

1. 重画模型方向主图。
2. 重写模型论文初稿。
3. 补充模型结果表。
4. 重新组织 `docs/progress-plan.md`。
5. 重新生成 Word/PDF，但不要再做 GWAS 投稿包。

## 清理后的判断

当前仓库应该这样理解：

```text
保留模型数据、模型脚本、模型结果、methylation 消融和稳健性结果。
保留少量 GWAS 结果作为解释材料。
删除围绕 GWAS 候选基因投稿的包装材料。
```

后续新增文件必须服务于模型文章，不能再新增 Stage 5.x 投稿包流水账。
