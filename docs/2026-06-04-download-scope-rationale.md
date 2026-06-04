# ZEAMAP download scope rationale

更新日期：2026-06-04

## 原则

第一阶段的核心目标不是“把 ZEAMAP 所有数据都下载下来”，而是先证明同一批玉米 accessions 可以在 processed data 层面形成可训练的多模态样本表。下载优先级按下面顺序决定：

1. 能直接暴露 accession/sample ID。
2. 能直接用于 phenotype、metabolome、population、genotype 的配对检查。
3. 已处理过，格式接近 matrix、VCF、trait table、metadata。
4. 体量可控，失败后重试和验证成本低。

## 原始 SRA/FASTQ

暂缓全量下载。

原因：

- 体量通常远大于 processed matrix，下载、校验和备份成本高。
- 需要完整重跑 QC、adapter trimming、alignment 或 pseudoalignment、quantification、normalization 和 batch correction。
- 同一项目内 raw reads 的组织、时期、处理、重复和 accession 命名不一定直接可对齐，metadata 整理成本高。
- 第一阶段的主要风险是 ID 对齐和模态覆盖，不是 reads-level 信号提取；processed matrix 已足够验证 feasibility。

什么时候再下载：

- processed matrix 缺失关键 accession 或关键模态。
- 需要统一 pipeline 消除不同来源 processed data 的批次差异。
- 要训练 read/coverage-level、isoform-level 或 allele-specific expression 模型。
- 需要从 raw reads 重新生成特定 reference genome 版本下的表达或表观组信号。

## 全部 genome assembly/pangenome

暂缓全量下载。

原因：

- 当前阶段只需要 gene ID、annotation、reference FASTA index 和少量参考序列来做特征对齐。
- 全量 assembly/pangenome 会带来 assembly 版本、gene ID 映射、pan-gene cluster、orthology 和 liftover 问题。
- 如果不训练序列 tokenizer 或 pan-gene 模型，全量 assembly 对 accession-level phenotype/population 配对帮助有限。
- 大规模 genome 文件下载后还需要建立索引、压缩和版本管理，会推迟最小可行数据集构建。

当前只需要：

- B73/SK/HZS/Mo17 的 annotation。
- 对应 gene ID 列表和必要的 FASTA index。
- 后续 genotype/epigenome 聚合到 gene/promoter/cis-window 时所需的坐标文件。

什么时候再下载：

- 做 sequence tokenizer、gene sequence encoder 或 promoter sequence model。
- 做 pan-gene/presence-absence variation 模型。
- 需要 SV、PAV、gene family 或 cross-assembly liftover。
- 需要把不同参考基因组上的表达和表观组信号统一到同一坐标系。

## 全量 epigenome bigWig/BED

暂缓全量下载。

原因：

- epigenome 文件通常按 accession、tissue、developmental stage、treatment 和 assay type 拆分。
- 如果不先核验 metadata，容易下载大量不能与 phenotype/metabolome/population 配对的样本。
- bigWig/BED 虽然比 raw reads 小，但全量下载后仍需要 peak/region/gene-level 聚合和坐标版本检查。
- 第一阶段只需要判断 epigenome 是否能补充 accession-level 或 gene-level regulatory features，不需要全量覆盖。

当前策略：

- 先下载目录清单、metadata、md5 和少量代表性 processed files。
- 按模态分批：DNA methylation、open chromatin、chromatin interaction、histone modification。
- 优先选择能聚合到 gene body、promoter、distal cis-window 的 processed summary、matrix、BED 或 bigWig。
- 先确认 accession、tissue、developmental_stage、treatment，再决定是否扩大下载。

什么时候再下载：

- 已确认 epigenome 样本与当前 461 个 phenotype/population accession 有足够交集。
- 已确定坐标版本和 gene annotation 可以稳定对齐。
- 模型进入 regulatory feature pretraining 或 missing-modality training 阶段。
- 需要为特定组织/时期建立 gene-level methylation/accessibility/interactome feature matrix。
