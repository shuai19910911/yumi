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

待完成：

- 检查每个表的样本列名和 accession 命名规则。
- 输出统一样本索引表。

## 阶段 1：metadata-only 统一索引

产出：

- `data/metadata/zeamap_file_manifest.tsv`
- `data/metadata/zeamap_accession_map.tsv`
- `data/metadata/zeamap_modality_coverage.tsv`

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

## 阶段 2：最小可行数据集

目标：生成一个只包含强配对样本的 `v0.1` 数据集。

纳入模态：

- genotype：`AMP_SNP_anno.vcf.gz`，先抽样或按 LD/MAF 过滤。
- expression：B73/SK 参考表达矩阵，先选一个 reference 作为主版本。
- phenotype/metabolome：两个 AMP phenotype xls。
- population：PCA 和 structure。

产出：

- `data/processed/v0_1/accessions.tsv`
- `data/processed/v0_1/expression.parquet`
- `data/processed/v0_1/phenotype.parquet`
- `data/processed/v0_1/population.parquet`
- `data/processed/v0_1/genotype.zarr` 或 `genotype.parquet`
- `data/processed/v0_1/coverage_report.md`

成功标准：

- 至少得到一批同时具有 genotype、expression、phenotype/metabolome、population 的 accessions。
- 每个模态都有缺失率统计。
- 可以训练一个 baseline：用 genotype + population 预测部分 phenotype/metabolite。

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
