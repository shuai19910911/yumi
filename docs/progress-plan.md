# Yumi progress plan

更新日期：2026-06-04

## 项目定位

本项目第一阶段只做 ZEAMAP/玉米，不扩展到油菜、茶树、大豆或水稻。目标是证明同一批玉米自交系/accessions 可以在 processed data 层面对齐 variation、expression、metabolome/phenotype、population structure 和 epigenome，从而支撑 accession-level 多模态预训练。

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

## 阶段 3：epigenome 接入

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

## 阶段 4：预训练样本构建

训练样本形态：

- accession-level sample：一个 accession 对应多个模态向量。
- gene-level sample：一个 accession 的一个 gene token，包含 cis variants、expression、regulatory features。
- trait-level sample：一个 accession 的多个 phenotype/metabolite labels。

任务组合：

- masked expression prediction
- masked metabolite/phenotype prediction
- genotype-to-expression prediction
- modality contrastive learning
- gene-context reconstruction

## 阶段 5：GitHub 更新习惯

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
