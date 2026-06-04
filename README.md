# yumi

玉米 ZEAMAP 多组学预训练项目。

当前目标是完成 `/home/user/zhangzhishuai/data/plantDB/pretraining_dataset_assessment.md` 中第一条“ZEAMAP/玉米”路线：以玉米自交系/accession 为样本单位，构建 variation、expression、epigenome、metabolome、phenotype、population structure 等模态的统一索引和预训练数据集。

## 数据源

主数据源：

- ZEAMAP database public download data, CNGBdb project `CNP0001565`
- 入口：`https://db.cngb.org/data_resources/project/CNP0001565`
- FTP 根目录：`https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/`
- 项目页标注数据类型：Assembly, Epigenomics, Phenotype or Genotype, Transcriptome or Gene expression, Variation, Targeted Locus
- 项目页标注总量：264.87GB

## 第一批建议下载

先下载小文件和中等体量 processed data，用来做 accession ID 对齐和可行性验证。

状态：已下载到 `/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/`，文件级校验通过。详情见 `docs/2026-06-04-zeamap-first-batch-download-check.md`。

```text
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/01_Genomics/Transcriptions/Sample_gene_expression/zmap_expression_ref_b73_exp.tsv
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/01_Genomics/Transcriptions/Sample_gene_expression/zmap_expression_ref_sk_exp.tsv
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/01_Genomics/Transcriptions/Sample_gene_expression/HZS_genes.fmt_FPKM.results
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/01_Genomics/Transcriptions/Sample_gene_expression/Mo1_only7_genes.fmt_FPKM.results
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/03_Genetics/Phenotype/ZEAMAP_phenotype_AMP_183_known_Metabolites.xls
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/03_Genetics/Phenotype/ZEAMAP_phenotype_AMP_agri_AA_Oil.xls
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/04_Populations/amp_pca.txt
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/04_Populations/amp_str.txt
```

用途：

- 表达矩阵：验证 gene expression matrix 中列名/样本名是否能和 AMP phenotype、population structure 对齐。
- 表型/代谢物：作为第一阶段监督标签和 masked modality 目标。
- PCA/structure：作为群体结构协变量，避免模型只学习群体分层。

## 第二批建议下载

第一批 ID 对齐成功后再下载较大文件。

```text
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/02_Variants/SNPs/AMP_SNP_anno.vcf.gz
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/02_Variants/SNPs/AMP_SNP_anno.vcf.gz.tbi
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/05_Epigenetics/DNA_Methylation/
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/05_Epigenetics/Chromatin_Accessibility/
https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/05_Epigenetics/Chromatin_Interaction/
```

用途：

- SNP VCF：建立 accession-level genotype embedding，也可聚合成 gene/cis-window burden。
- DNA methylation/open chromatin/chromatin interaction：补充调控模态，先做区域到基因的聚合特征。

## 暂缓下载

这些数据有价值，但不建议在可行性验证前下载全量。

- 原始 SRA/FASTQ：暂缓下载。原始 reads 体量大，质控、比对、定量和批次校正成本高；第一阶段的目标是先验证 accession ID 能否跨模态对齐，所以优先使用 ZEAMAP 已处理好的 matrix、trait table 和 VCF。只有当 processed data 缺少关键模态、需要统一重跑 pipeline，或要训练 read/coverage-level 模型时，才进入原始 reads 下载。
- 全部 genome assembly/pangenome：暂缓全量下载。当前只需要 B73/SK/HZS/Mo17 的 annotation、gene ID、FASTA index 或少量参考序列来做 gene-level 特征对齐；全量 assembly/pangenome 会引入版本映射、pan-gene 聚类和大规模存储问题。只有在做 sequence tokenizer、pan-gene model、SV/presence-absence 建模或跨 assembly liftover 时，才下载全量。
- 全量 epigenome bigWig/BED：暂缓全量下载。epigenome 文件通常按 accession、组织、时期和实验类型拆分，直接全量下载容易拿到大量无法和 AMP phenotype 配对的样本。第一阶段先确认 accession、tissue、developmental_stage 和 treatment，再按 DNA methylation、open chromatin、chromatin interaction 等模态抽样下载，并优先选择 processed summary、matrix 或可聚合到 gene/promoter/cis-window 的文件。

详细理由见 `docs/2026-06-04-download-scope-rationale.md`。

## 当前建模思路

样本单位以 `accession_id` 为主，必要时扩展到 `accession_id + tissue + developmental_stage + treatment`。

第一批样本索引检查结果：

- 统一 accession 索引：`data/metadata/zeamap_accession_index.tsv`
- 表级 ID 摘要：`data/metadata/zeamap_table_id_summary.tsv`
- expression 列命名表：`data/metadata/zeamap_expression_sample_columns.tsv`
- 检查报告：`docs/2026-06-04-zeamap-sample-id-check.md`
- 可作为第一版 phenotype/population 配对集合的 accession 数：461
- 当前 expression 文件是 B73/SK/HZS/Mo17 reference/tissue expression，不是 AMP accession-level expression。

核心任务：

- masked modality modeling：用 genotype、population、regulatory features 预测 expression、metabolite、phenotype。
- cross-modal contrastive learning：同一 accession 的不同模态 embedding 拉近，不同 accession 拉远。
- gene-context prediction：把 gene annotation、cis variants、methylation/open chromatin、expression 聚合到 gene-level token。
- phenotype-aware pretraining：把农艺性状、油分/氨基酸、已知代谢物作为弱监督目标。

更多细节见：

- `docs/progress-plan.md`
- `docs/model-architecture.md`
