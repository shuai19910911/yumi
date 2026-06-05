# Yumi progress plan

更新日期：2026-06-05

## 项目定位

本项目第一阶段只做 ZEAMAP/玉米，不扩展到油菜、茶树、大豆或水稻。当前样本量适合做 accession-level 可行性验证、baseline benchmark 和 trait 可预测性筛选；暂不把目标设为直接训练大规模多模态预训练模型。

阶段性判断：

- `v0.1` 有 461 个强配对 accession，适合训练和评估小模型 baseline。
- genotype 维度远大于样本数，必须先做降维、正则化或特征筛选。
- methylation 有 236 个 accession 覆盖，适合后续 missing-modality 或抽样实验，不作为 `v0.1` 主训练输入。
- 当前第一目标是证明 ZEAMAP processed data 支持 genotype/population 到 phenotype/metabolome 的可预测信号，而不是追求复杂模型结构。

## 阶段 0：数据下载清单确认

状态：已完成。

已经确认：

- CNGBdb `CNP0001565` 是 ZEAMAP database public download data。
- FTP 根目录下有 `01_Genomics`、`02_Variants`、`03_Genetics`、`04_Populations`、`05_Epigenetics`、`06_Pangenome`、`99_MaizegoResources`。
- 表达、表型/代谢物、群体结构和 SNP VCF 均有 processed 文件。
- 第一批 8 个目标文件已下载到 `/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/`。
- 表达矩阵和群体结构文本文件可读，行数与下载记录一致。
- 两个 `.xls` 文件经 `file` 检查为合法 `Composite Document File V2 Document`，不是 HTML 错误页。
- 已在 `bio3` 环境安装 `xlrd/openpyxl`，两个 `.xls` 文件内容级解析通过。

已完成产物：

- `docs/2026-06-04-zeamap-first-batch-download-check.md`
- `docs/2026-06-04-zeamap-sample-id-check.md`
- `data/metadata/zeamap_accession_index.tsv`
- `data/metadata/zeamap_table_id_summary.tsv`
- `data/metadata/zeamap_expression_sample_columns.tsv`
- `data/metadata/phenotype_sheets/*.tsv`

## 阶段 1：metadata-only 统一索引

状态：已完成第一批数据的样本 ID/列名检查和统一索引输出。

产出：

- `data/metadata/zeamap_file_manifest.tsv`
- `data/metadata/zeamap_accession_map.tsv`
- `data/metadata/zeamap_modality_coverage.tsv`
- 当前实际输出：
- `data/metadata/zeamap_accession_index.tsv`
- `data/metadata/zeamap_table_id_summary.tsv`
- `data/metadata/zeamap_expression_sample_columns.tsv`
- `data/metadata/phenotype_sheets/*.tsv`
- `docs/2026-06-04-zeamap-sample-id-check.md`

统一字段：

```text
database
crop
species
source_project
sample_id
accession_id
tissue
developmental_stage
treatment
omics_type
feature_space
genome_version
file_format
source_url
local_path
md5
raw_reads_flag
notes
```

关键检查：

- 表达矩阵列名是否直接是 accession。
- 表型/代谢物表中的材料名是否与表达矩阵一致。
- `amp_pca.txt`、`amp_str.txt` 的行名是否与 AMP phenotype 和 VCF samples 一致。
- SNP VCF header 中 sample names 是否覆盖 phenotype/metabolite accessions。

当前结论：

- `amp_pca.txt` 与 `amp_str.txt` 均有 507 个 accession，二者完全交集为 507。
- metabolite phenotype 有 339 个 accession，agri/AA/Oil phenotype 有 476 个 accession。
- population + 任一 phenotype/metabolome 的强配对 accession 为 461 个。
- 第一批 expression 文件是 B73/SK/HZS/Mo17 reference/tissue expression，不是 AMP accession-level expression。
- 第二批 VCF 有 507 个 samples、1,186,632 个 variants。
- VCF 与 accession index 交集为 507。
- genotype + population + 任一 phenotype/metabolome 的强配对 accession 为 461。
- genotype + population + phenotype/metabolome + 任一 DNA methylation 的强配对 accession 为 236。
- Chromatin accessibility 和 chromatin interaction 当前更适合作为 B73/reference regulatory prior。

## 阶段 2：最小可行数据集

状态：v0.1 processed dataset 已完成构建和一致性检查。

目标：生成一个只包含强配对样本的 `v0.1` 数据集。当前 v0.1 以 `genotype + population + 任一 phenotype/metabolome` 为强配对标准，共 461 个 accession。

纳入模态：

- genotype：`AMP_SNP_anno.vcf.gz`，保留 biallelic SNP、`MAF >= 0.05`、`NS >= 450`，再抽稀到 199,856 个 variants。
- phenotype/metabolome：两个 AMP phenotype xls。
- population：PCA 和 structure。
- methylation：先作为 accession coverage/missing-modality mask，不在 v0.1 中展开区域特征。
- expression：当前 B73/SK/HZS/Mo17 文件是 reference/tissue expression，不是 AMP accession-level paired expression，因此不纳入 v0.1 paired matrix。

产出：

- `data/processed/v0_1/accessions.tsv`
- `data/processed/v0_1/phenotype.parquet`
- `data/processed/v0_1/population.parquet`
- `data/processed/v0_1/modality_mask.tsv`
- `data/processed/v0_1/genotype_samples.tsv`
- `data/processed/v0_1/genotype_variants.tsv`
- `data/processed/v0_1/genotype_dosage_int8.npz`
- `data/processed/v0_1/manifest.tsv`
- `docs/2026-06-04-zeamap-v0-1-build-report.md`

成功标准：

- 至少得到一批同时具有 genotype、phenotype/metabolome、population 的 accessions：已完成，461 个。
- 每个 accession 有 modality mask：已完成。
- genotype dosage matrix、sample order、variant table 一致性检查：已完成。
- 可以训练一个 baseline：用 genotype + population 预测部分 phenotype/metabolite：下一步。

## 阶段 3：v0.1 baseline benchmark

状态：已完成第一版 baseline benchmark。

目标：用 `v0.1` processed dataset 建立可复现 baseline，回答当前 461 个 accession 是否足以支持 genotype-to-phenotype/metabolome learning。

输入：

- `data/processed/v0_1/genotype_dosage_int8.npz`
- `data/processed/v0_1/genotype_samples.tsv`
- `data/processed/v0_1/genotype_variants.tsv`
- `data/processed/v0_1/phenotype.parquet`
- `data/processed/v0_1/population.parquet`
- `data/processed/v0_1/modality_mask.tsv`

训练策略：

- 固定 accession-level train/validation/test split，避免 accession 泄漏。
- genotype 先做低维表示，不直接把 199,856 SNP 全量喂给复杂模型。
- 优先 baseline：population-only、genotype PCA + ridge/elastic net、genotype PCA + population、轻量 MLP。
- 对 phenotype/metabolome 每个 trait 单独评估，保留缺失率、方差、有效样本数。
- population covariates 同时作为输入和对照，检查模型是否只是学习群体结构。

产出：

- `data/processed/v0_1/splits/`
- `data/processed/v0_1/genotype_pca.tsv`
- `data/processed/v0_1/genotype_pca_variance.tsv`
- `results/v0_1_baseline/trait_qc.tsv`
- `results/v0_1_baseline/trait_metrics.tsv`
- `results/v0_1_baseline/model_comparison.tsv`
- `results/v0_1_baseline/top_predictable_traits.tsv`
- `docs/2026-06-05-zeamap-v0-1-baseline-plan.md`
- `docs/2026-06-05-zeamap-v0-1-baseline-report.md`

成功标准：

- 至少完成 population-only 与 genotype+population 两类 baseline。
- 输出每个 trait 的 R2、Pearson、Spearman、MAE/RMSE、有效样本数和缺失率。
- 找出一批稳定可预测 trait，用作后续多模态模型的主评估集合。
- 如果大多数 trait 信号弱，仍保留结果作为样本量和模态覆盖不足的证据。

当前结果：

- split：train 322、validation 69、test 70。
- genotype PCA：100 PCs，累计解释方差 0.504527。
- 318 个 trait 中 317 个通过 baseline 过滤。
- test median Pearson：`genotype_pca_population_ridge` 0.331，`genotype_pca_ridge` 0.298，`population_ridge` 0.237。
- `genotype_pca_population_ridge` 有 204 个 trait 的 test R2 为正，226 个 trait 的 test Pearson 大于 0.2。
- 最强可预测 trait 主要是 oil 相关性状，最高 test Pearson 约 0.92。

### 阶段 3.1：selected traits

状态：已完成。

筛选标准：

- `genotype_pca_population_ridge` test Pearson >= 0.3。
- `genotype_pca_population_ridge` test R2 > 0。
- 相比 `population_ridge` 至少满足 Pearson gain >= 0.02 或 R2 gain > 0。
- trait 通过 baseline QC。

产出：

- `scripts/select_zeamap_v0_1_traits.py`
- `results/v0_1_baseline/selected_traits.tsv`
- `results/v0_1_baseline/selected_trait_family_summary.tsv`
- `results/v0_1_baseline/selected_trait_tier_summary.tsv`
- `docs/2026-06-05-zeamap-v0-1-selected-traits.md`

结果：

- selected traits：130 / 317。
- high-priority traits：11。
- medium-priority traits：28。
- watch traits：91。
- family 分布：metabolite 76、oil 29、agronomic 16、amino acid 9。
- oil traits 最强，最高 test Pearson 约 0.92；metabolite traits 数量最多，但需要 multi-seed robustness 确认稳定性。

### 阶段 3.2：multi-seed robustness

状态：已完成。

目标：只对 130 个 selected traits 重复多个 random seed 的 split 和 baseline，评估 trait ranking 与 test performance 是否稳定。

产出：

- `results/v0_1_baseline/robustness_metrics.tsv`
- `results/v0_1_baseline/robustness_model_summary.tsv`
- `results/v0_1_baseline/robustness_trait_summary.tsv`
- `results/v0_1_baseline/robust_selected_traits.tsv`
- `docs/2026-06-05-zeamap-v0-1-robustness-report.md`

结果：

- seeds：20260605、20260606、20260607、20260608、20260609。
- `genotype_pca_population_ridge` 在 selected traits 上的 5-seed test median Pearson 为 0.396，median R2 为 0.109。
- robust selected traits：66 / 130。
- robust family 分布：oil 29、metabolite 16、agronomic 15、amino acid 6。
- oil traits 全部通过 robust 规则，是当前最稳定目标集合。
- 这 66 个 robust traits 是后续 lightweight MLP、ElasticNet comparison 和 methylation subset experiment 的优先目标。

### 阶段 3.3：lightweight model comparison

状态：已完成。

目标：在 66 个 robust traits 上比较 ridge、ElasticNet 和轻量 MLP，确认是否值得引入非线性模型。

建议约束：

- 仍然使用 accession-level split，避免泄漏。
- 只在 robust traits 上做，不再使用全部 318 个 traits。
- MLP 只做小模型和强正则，不上 GPU，不做大 transformer。

产出：

- `results/v0_1_baseline/lightweight_model_metrics.tsv`
- `results/v0_1_baseline/lightweight_model_summary.tsv`
- `results/v0_1_baseline/lightweight_trait_summary.tsv`
- `docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md`

结果：

- 输入 traits：66 个 robust selected traits。
- seeds：5 个。
- `genotype_population_ridge` 最佳：median Pearson 0.498，median R2 0.204。
- `genotype_population_elasticnet` 接近 ridge：median Pearson 0.483，median R2 0.171。
- `genotype_population_small_mlp` 明显不稳定：median Pearson 0.351，median R2 -0.191。
- 当前样本量下不应继续增加模型复杂度；下一步优先做 methylation subset feature experiment。

## 阶段 4：epigenome 接入

目标：在不下载全量原始 reads 的前提下，接入 DNA methylation、open chromatin、chromatin interaction。

策略：

- 先下载目录清单和 md5。
- 优先 processed matrix、BED、bigWig summary，不处理 FASTQ。
- 把 epigenome features 聚合到 gene body、promoter、cis-window。
- 如果 epigenome 样本不是 AMP 全覆盖，允许作为 missing-modality 训练数据。

产出：

- `data/processed/v0_2/regulatory_gene_features.parquet`
- `data/processed/v0_2/modality_mask.parquet`
- `docs/epigenome-alignment-report.md`

进入条件：

- `v0.1 baseline` 确认至少部分 phenotype/metabolome trait 有可预测信号。
- 明确 methylation 文件的 accession、组织、时期和区域类型。
- 优先从 236 个 methylation-covered accession 做小规模 missing-modality 实验。

### 阶段 4.1：methylation subset global summary

状态：已完成。

目标：先用 DNA methylation `01_regions` bedgraph 文件构建 accession-level 全局 summary features，测试是否能在 236 个 methylation-covered accession 子集上提升 66 个 robust traits 的预测。

产出：

- `scripts/run_zeamap_v0_1_methylation_subset.py`
- `scripts/slurm/run_zeamap_v0_1_methylation_subset.sh`
- `data/processed/v0_1/methylation_region_summary.tsv`
- `results/v0_1_baseline/methylation_subset_metrics.tsv`
- `results/v0_1_baseline/methylation_subset_model_summary.tsv`
- `results/v0_1_baseline/methylation_subset_trait_summary.tsv`
- `docs/2026-06-05-zeamap-v0-1-methylation-subset-report.md`

结果：

- methylation-covered v0.1 accession：236。
- `genotype_population_methylation_ridge` median Pearson/R2：0.496 / 0.173。
- `genotype_population_ridge` median Pearson/R2：0.490 / 0.173。
- 全局 methylation summary 整体增益很小，但少数 traits 有稳定增益，例如 `metabolite__Feruloyltryptamine_E1` 和 `metabolite__N_Coumaroyltryptamine_E1`。

结论：

- accession-level global methylation summary 不足以明显提升整体预测。
- 下一步如果继续 epigenome，应做 gene/promoter/cis-window methylation aggregation，而不是继续加深模型。

## 阶段 5：预训练样本构建

进入条件：

- baseline benchmark 已建立，并筛出主评估 trait。
- 确认 accession-level 样本量不足以支撑大模型后，转向小模型、多任务学习、gene-level token 扩样或跨数据源扩展。

训练样本形态：

- accession-level sample：一个 accession 对应多个模态向量。
- gene-level sample：一个 accession 的一个 gene token，包含 cis variants、expression、regulatory features。
- trait-level sample：一个 accession 的多个 phenotype/metabolite labels。

任务组合：

- masked metabolite/phenotype prediction
- modality contrastive learning
- gene-context reconstruction
- masked expression prediction：仅在拿到 accession-level expression 或明确使用 reference expression prior 后启用。
- genotype-to-expression prediction：当前暂缓，因为现有 expression 文件不是 AMP accession-level paired expression。

## 阶段 6：GitHub 更新习惯

后续每完成一个小阶段，更新：

- `README.md`：当前项目入口、下载清单和状态。
- `docs/progress-plan.md`：阶段状态。
- `docs/model-architecture.md`：模型结构和数据接口变化。
- 新增阶段报告放在 `docs/`。

提交信息建议：

```text
docs: update ZEAMAP data manifest plan
data: add ZEAMAP metadata manifest
model: document v0.1 pretraining architecture
```
