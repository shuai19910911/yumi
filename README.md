# yumi

玉米 ZEAMAP 多组学预训练项目。

当前目标是完成 `/home/user/zhangzhishuai/data/plantDB/pretraining_dataset_assessment.md` 中第一条“ZEAMAP/玉米”路线：以玉米自交系/accession 为样本单位，先构建 variation、metabolome/phenotype、population structure 和 epigenome coverage 的统一索引与 `v0.1` processed dataset，再做 baseline benchmark 判断是否有足够信号进入多模态建模。

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

状态：已下载到 `/home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/`，完整性检查通过。详情见 `docs/2026-06-04-zeamap-second-batch-check.md`。

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

第二批 genotype/epigenome 检查结果：

- VCF 样本数：507
- VCF variants：1,186,632
- `genotype + population + 任一 phenotype/metabolome` 强配对 accession 数：461
- 任一 DNA methylation 文件覆盖 accession 数：263
- `genotype + population + phenotype/metabolome + 任一 methylation` 强配对 accession 数：236
- Chromatin accessibility 和 chromatin interaction 当前更适合作为 B73/reference regulatory prior。
- 检查报告：`docs/2026-06-04-zeamap-second-batch-check.md`

v0.1 processed dataset：

- 构建脚本：`scripts/build_zeamap_v0_1_dataset.py`
- 本地输出目录：`data/processed/v0_1/`
- 构建报告：`docs/2026-06-04-zeamap-v0-1-build-report.md`
- accession 数：461
- genotype：199,856 个常见、高样本数 biallelic SNP，dosage 矩阵 shape 为 `[199856, 461]`
- phenotype/metabolome：318 个数值 trait columns
- population：PCA + structure covariates
- DNA methylation：当前作为 coverage/missing-modality 标记，v0.1 中有 236 个 accession 覆盖任一 methylation 文件
- `data/processed/` 已加入 `.gitignore`，大矩阵只保留在本地，不提交到 GitHub。

v0.1 baseline benchmark：

- 运行环境：mamba `yumi`，Slurm `q07` CPU 作业
- 运行脚本：`scripts/run_zeamap_v0_1_baseline.py`
- Slurm 脚本：`scripts/slurm/run_zeamap_v0_1_baseline.sh`
- 结果目录：`results/v0_1_baseline/`
- 报告：`docs/2026-06-05-zeamap-v0-1-baseline-report.md`
- split：train 322、validation 69、test 70
- genotype PCA：100 PCs，累计解释方差 0.504527
- 最佳 baseline：`genotype_pca_population_ridge`，test median Pearson 0.331，test median R2 0.034
- 结论：当前样本量可以继续做 trait 筛选和小模型 baseline；复杂多模态预训练仍需谨慎。

v0.1 selected traits：

- 筛选脚本：`scripts/select_zeamap_v0_1_traits.py`
- 结果：`results/v0_1_baseline/selected_traits.tsv`
- 报告：`docs/2026-06-05-zeamap-v0-1-selected-traits.md`
- selected traits：130 / 317 evaluated traits
- high-priority traits：11
- medium-priority traits：28
- family 分布：metabolite 76、oil 29、agronomic 16、amino acid 9
- 下一步：对 selected traits 做 multi-seed robustness，避免单次 split 偶然性。

v0.1 multi-seed robustness：

- 运行脚本：`scripts/run_zeamap_v0_1_robustness.py`
- Slurm 脚本：`scripts/slurm/run_zeamap_v0_1_robustness.sh`
- 报告：`docs/2026-06-05-zeamap-v0-1-robustness-report.md`
- seeds：20260605, 20260606, 20260607, 20260608, 20260609
- robust selected traits：66 / 130 selected traits
- robust family 分布：oil 29、metabolite 16、agronomic 15、amino acid 6
- 结论：后续 lightweight MLP、ElasticNet comparison 和 methylation subset experiment 应优先使用这 66 个 robust traits。

v0.1 lightweight model comparison：

- 运行脚本：`scripts/run_zeamap_v0_1_lightweight_models.py`
- 报告：`docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md`
- 输入：66 个 robust traits，5 个 random seeds
- 最佳整体模型：`genotype_population_ridge`
- median Pearson / R2：ridge 0.498 / 0.204，ElasticNet 0.483 / 0.171，small MLP 0.351 / -0.191
- 结论：当前样本量下 ridge/ElasticNet 足够强，小 MLP 不稳定；下一步优先做 methylation subset features，而不是继续加深模型。

v0.1 methylation subset experiment：

- 运行脚本：`scripts/run_zeamap_v0_1_methylation_subset.py`
- 报告：`docs/2026-06-05-zeamap-v0-1-methylation-subset-report.md`
- 输入：236 个 methylation-covered v0.1 accessions，66 个 robust traits，5 个 seeds
- methylation features：mCG/mCHG/mCHH region-level 全局 summary
- 整体结果：genotype+population+methylation median Pearson/R2 为 0.496/0.173，genotype+population 为 0.490/0.173
- 结论：全局 methylation summary 只带来极小整体增益；如果继续 epigenome，应做 gene/promoter/cis-window 聚合，而不是继续加模型复杂度。

v0.1 gene/promoter/cis-window methylation PCA：

- annotation：Ensembl Plants release 47 `B73_RefGen_v4`
- 运行脚本：`scripts/run_zeamap_v0_1_gene_methylation_pca.py`
- 报告：`docs/2026-06-05-zeamap-v0-1-gene-methylation-pca-report.md`
- genes：39,005
- region types：gene body、promoter upstream 2kb、cis-window +/-10kb
- methylation PCs：mCG/mCHG/mCHH x 3 region types x 10 PCs = 90 features
- 结果：genotype+population+gene methylation PCA median Pearson/R2 为 0.496/0.199，genotype+population 为 0.490/0.173
- 结论：gene-level methylation PCA 比全局 summary 稍好，但整体增益仍小；下一步应做 trait-specific sparse gene/window feature selection。

核心任务：

- v0.1 baseline benchmark：用 genotype PCA/regularized models + population covariates 预测 phenotype/metabolome。
- trait 可预测性筛选：按 R2、Pearson、Spearman、缺失率和有效样本数筛出稳定 trait。
- 小模型优先：当前 461 个 accession 适合 ridge/elastic net、population-only 对照、轻量 MLP，不适合直接训练大型多模态 transformer。
- epigenome 后置：236 个 methylation-covered accession 先作为 missing-modality/coverage mask，baseline 完成后再接入区域聚合特征。
- phenotype-aware pretraining：仅在 baseline 证明有足够信号后，作为下一阶段弱监督或多任务学习目标。

更多细节见：

- `docs/progress-plan.md`
- `docs/model-architecture.md`
