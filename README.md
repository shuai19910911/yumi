# yumi

ZEAMAP 玉米 oil-trait prediction + GWAS 项目。

当前项目只做 `/home/user/zhangzhishuai/data/plantDB/pretraining_dataset_assessment.md` 里的第一条玉米路线。现在的目标不是先做大模型，而是先把 ZEAMAP 这批数据做成能写论文的结果：

```text
数据对齐 -> v0.1 processed dataset -> trait prediction benchmark
-> oil traits GEMMA LMM GWAS -> lead loci / candidate genes / figures
```

## 当前一句话结论

我们已经完成 ZEAMAP v0.1 数据集、稳定 trait 筛选、小模型预测基准、methylation 消融、10 个 high-priority oil traits 的 GEMMA LMM GWAS、candidate loci 注释、top loci 优先级排序、区域图初版、论文主表/补充表、Results/Methods 草稿、Figure 1/3 主图初版、manuscript skeleton、Stage 5.9 投稿策略/citation audit、Stage 5.10 polished manuscript package、Stage 5.11 top loci external annotation hardening、Stage 5.12 final manuscript assembly、Stage 5.13 final submission gate、Stage 5.14 human metadata/release templates、Stage 5.15 preflight validation、Stage 5.16 metadata ingestion dry-run、Stage 5.17 single human-input package、Stage 5.18 reviewer-risk register、Stage 5.19 result-to-script reproducibility crosswalk、Stage 5.20 GWAS diagnostic appendix、Stage 5.21 targeted fatty-acid literature support、Stage 5.22 integrated manuscript/claim audit、Stage 5.23 final bibliography/gene-model verification、Stage 5.24 citation-integrated manuscript 和 Stage 5.25 target-journal reference-styled manuscript/submission gate、Stage 5.26 final figure technical QA、Stage 5.27 external gene-name confirmation、Stage 5.28 final submission package、Stage 5.29 DOCX/HTML export package、Stage 5.30 author metadata ingestion pipeline、Stage 5.31 figure/release readiness pipeline、Stage 5.32 single human action packet 和 Stage 5.33 submission artifact integrity manifest。

最可靠的主线是：

- 用 461 个 accession 做 genotype + population 到 phenotype/metabolome 的预测基准。
- 用 66 个 robust traits 做主评估集合。
- 用 `genotype_population_ridge` 作为当前主预测模型。
- 用 GEMMA LMM 作为 oil traits 的论文主 GWAS，而不是用简单相关或 covariate-only GWAS。

## 当前数据规模

已构建的 v0.1 processed dataset 在本地：

```text
data/processed/v0_1/
```

核心数据：

- 461 个 accession：同时有 genotype、population、至少一种 phenotype/metabolome。
- 236 个 accession：额外有 DNA methylation 覆盖。
- 199,856 个 SNP：从 ZEAMAP `AMP_SNP_anno.vcf.gz` 过滤得到。
- 318 个数值 phenotype/metabolome traits。
- 317 个 traits 进入第一版 baseline 评估。

重要限制：

- 当前 expression 文件是 B73/SK/HZS/Mo17 reference/tissue expression，不是 AMP accession-level expression，所以没有放进 v0.1 主数据集。
- methylation 覆盖样本只有 236 个，所以暂时不作为主模型输入。
- chromatin accessibility 和 chromatin interaction 目前更适合作为 B73/reference regulatory prior。

## 数据来源和下载记录

主数据来自 ZEAMAP database public download data：

```text
CNGBdb project: CNP0001565
FTP root: https://ftp.cngb.org/pub/CNSA/data3/CNP0001565/zeamap/
local data: /home/user/zhangzhishuai/data/plantDB/maize_ZEAMAP/
```

下载和检查记录不在 README 展开，避免入口文档太长。需要回看下载依据时读：

- `docs/2026-06-04-zeamap-first-batch-download-check.md`
- `docs/2026-06-04-zeamap-second-batch-check.md`
- `docs/2026-06-04-download-scope-rationale.md`

## 当前主要结果

### 1. 预测模型 benchmark

最终主模型：

```text
genotype_population_ridge
```

主评估集合：

```text
66 个 robust traits
```

整体结果：

```text
median Pearson = 0.498
median R2      = 0.204
positive R2 fraction = 0.979
```

trait family 表现：

```text
oil        median Pearson/R2 = 0.596 / 0.321
agronomic  median Pearson/R2 = 0.498 / 0.190
metabolite median Pearson/R2 = 0.389 / 0.116
amino acid median Pearson/R2 = 0.367 / 0.131
```

解释：

- oil traits 是目前最强、最稳定的结果。
- ridge/ElasticNet 比 small MLP 更可靠。
- 当前样本量不适合直接训练复杂 deep learning 或大规模多模态 transformer。

### 2. methylation 结论

我们测试了三种 methylation 接入方式：

- accession-level global methylation summary
- gene/promoter/cis-window methylation PCA
- sparse gene-window methylation feature selection

结论：

- global methylation summary 几乎没有整体增益。
- gene-level methylation PCA 有小幅增益。
- raw sparse gene-window methylation 在 236 个 accession 上不稳定。

所以 v0.1 主模型不接入 raw methylation features。methylation 只保留为辅助消融、coverage mask 和候选解释材料。

### 3. GWAS 结论

我们做了两层 GWAS。

第一层：covariate-only GWAS

- 输入：10 个 high-priority oil traits，440 个非缺失 accession，199,856 个 SNP。
- 方法：PC1-PC3 + K1-K3 residualization。
- 结果：lambda GC = 2.41-3.97。
- 判断：统计膨胀明显，只能作为 diagnostic baseline，不能作为论文主 GWAS。

第二层：GEMMA LMM GWAS

- 输入：同样 10 个 oil traits，440 个 accession，199,856 个 SNP。
- 方法：GEMMA mixed linear model + genotype-derived kinship + PC1-PC3/K1-K3 covariates。
- 主 p-value：`p_lrt`。
- 结果：lambda GC = 0.984-1.018，median = 0.998。
- Bonferroni hits：每个 trait 1-21 个。

判断：

- GEMMA LMM 有效控制了群体结构和亲缘关系导致的 inflation。
- GEMMA LMM 是当前可面向论文的 GWAS 主结果。
- lead SNP/gene 可以进入 candidate table 初稿，但还不能直接写成 causal variant。

### 4. GEMMA candidate loci 注释

已把 GEMMA lead SNP 整理成论文候选 locus/gene 表：

- manuscript candidate loci：184 个，不含 nominal-only loci。
- manuscript candidate genes：147 个。
- Bonferroni loci：38 个。
- FDR loci：131 个。
- suggestive loci：15 个。
- 有 ridge attribution 交叉支持的 manuscript loci：63 个。
- 有 lipid/fatty-acid keyword 的 manuscript loci：11 个。
- 功能注释来源：B73 RefGen_v4 Ensembl/Gramene GFF3 gene description。
- 图：已生成 Nature 风格 PDF/SVG/PNG summary figure。

输出目录：

```text
results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/
results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/
```

### 5. top loci 和区域图初版

已把 184 个 manuscript candidate loci 进一步排序，得到论文主结果优先候选：

- Tier 1 main-text loci：18 个。
- Tier 2 strong loci：22 个。
- 已生成 8 个 top regional association/LD/gene-track figures。
- 最强主线：chr6 `Zm00001d036982` / linoleic acid1 区域，跨 7 个 oil traits 复现，Bonferroni significant，有 lipid/fatty-acid 注释，并且有 ridge attribution 交叉支持。
- 重要补充候选：chr9 `Zm00001d045383` 区域，C16:0 强信号，局部包含 `Zm00001d045387` fatty acyl-ACP thioesterase2。

输出目录：

```text
results/v0_1_baseline/gemma_lmm_v0_1/top_loci/
results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/
```

注意：当前文献证据是 seed evidence，用来指导 top loci triage；还不是完整系统文献综述。

### 6. 论文主表和 Results 初稿

Stage 5.6 已把 top loci 推进到论文写作材料：

- top regional loci evidence table：8 行。
- main tier1 locus table：18 行。
- supplementary manuscript candidate loci：184 行。
- literature/source records：6 条。
- Results draft：已写 prediction benchmark、GEMMA LMM inflation control、prioritized oil-trait loci 和 claim boundary。

输出目录：

```text
results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/
docs/2026-06-05-zeamap-v0-1-results-draft.md
```

### 7. Methods 和主图初版

Stage 5.7 已完成论文骨架初版：

- Methods draft：dataset harmonization、prediction benchmark、methylation ablation、GEMMA LMM GWAS、candidate-locus annotation、top-locus prioritization、regional figures。
- Figure 1：dataset construction + prediction benchmark，Nature double-column PDF/SVG/PNG。
- Figure 2：沿用 GEMMA LMM summary figure。
- Figure 3：chr6 linoleic acid1 candidate interval + chr9 C16:0 fatty acyl-ACP thioesterase interval，Nature double-column PDF/SVG/PNG。
- Figure captions draft：Figure 1-3 captions 初版。

输出目录：

```text
results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/
docs/2026-06-05-zeamap-v0-1-methods-draft.md
docs/2026-06-05-zeamap-v0-1-main-figure-plan.md
docs/2026-06-05-zeamap-v0-1-figure-captions-draft.md
```

### 8. manuscript skeleton

Stage 5.8 已把分散材料合并成论文骨架：

- working title
- abstract draft
- keywords
- introduction draft
- results
- discussion outline
- methods
- figure captions
- table captions
- data/code availability draft
- manuscript readiness checklist

入口文件：

```text
docs/2026-06-05-zeamap-v0-1-manuscript-skeleton.md
docs/2026-06-05-zeamap-v0-1-manuscript-readiness-checklist.md
docs/2026-06-05-zeamap-v0-1-table-captions-draft.md
```

### 9. 投稿策略和 citation audit

Stage 5.9 已完成初版：

- 投稿策略和中稿率估计。
- Citation audit 初版。
- Methods software versions 初版。

推荐投稿路线：

```text
平衡路线：The Plant Genome -> G3 -> BMC Plant Biology
保守高概率路线：G3 or BMC Plant Biology
冲刺路线：Journal of Experimental Botany presubmission enquiry
暂不建议首投：Nature Plants / Plant Physiology
```

当前中稿率判断：

```text
当前 skeleton 直接投：合理期刊 eventually accepted 约 35-55%
Stage 5.9-5.10 打磨后：约 55-75%
有独立验证/更强多组学支持后：约 70-85%
```

## 重要文件入口

适合先读：

- `docs/progress-plan.md`：按阶段看的项目计划和状态。
- `docs/2026-06-05-zeamap-progress-detailed-interpretation.md`：白话版进展解释。
- `docs/2026-06-05-zeamap-progress-evaluation.md`：当前结果能不能写论文、还缺什么。
- `docs/model-architecture.md`：模型和数据接口说明。

关键结果报告：

- `docs/2026-06-04-zeamap-v0-1-build-report.md`
- `docs/2026-06-05-zeamap-v0-1-final-benchmark.md`
- `docs/2026-06-05-zeamap-v0-1-gemma-lmm-report.md`
- `docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md`
- `docs/2026-06-05-zeamap-v0-1-top-locus-priority-report.md`
- `docs/2026-06-05-zeamap-v0-1-stage5-6-manuscript-tables-report.md`
- `docs/2026-06-05-zeamap-v0-1-results-draft.md`
- `docs/2026-06-05-zeamap-v0-1-methods-draft.md`
- `docs/2026-06-05-zeamap-v0-1-main-figure-plan.md`
- `docs/2026-06-05-zeamap-v0-1-figure-captions-draft.md`
- `docs/2026-06-05-zeamap-v0-1-manuscript-skeleton.md`
- `docs/2026-06-05-zeamap-v0-1-manuscript-readiness-checklist.md`
- `docs/2026-06-05-zeamap-v0-1-journal-strategy-and-acceptance-estimate.md`
- `docs/2026-06-05-zeamap-v0-1-citation-audit.md`
- `docs/2026-06-05-zeamap-v0-1-methods-software-versions.md`
- `docs/2026-06-05-zeamap-v0-1-epigenome-decision.md`

## 下一步

下一步不应该继续加模型复杂度，而应该继续 manuscript polish：

1. 扩展 Introduction 文献定位。
2. 把 Results 和 Discussion 从骨架改成流畅论文段落。
3. 把 Methods software versions 和关键参数并入 skeleton。
4. 继续补 8 个 top regional loci 的 MaizeGDB/UniProt/Gramene 注释。
5. 做 citation audit 第二轮和最终 figure polish。

## 暂不做的事

- 不下载和处理原始 SRA/FASTQ。
- 不把 B73/SK/HZS/Mo17 expression 当成 AMP accession expression。
- 不把 methylation raw gene-window features 放进 v0.1 主模型。
- 不直接训练大型多模态 transformer。
- 不把 GEMMA lead SNP 直接声称为 causal variant。

Current status: Stage 5.32 has compiled all remaining author-only blockers into one human action packet with exact files, commands and completion evidence. Remaining blockers are still author-only: real metadata, funding/acknowledgements/COI approval, human visual figure approval and release PID.


## Stage 5.33 submission integrity manifest

已新增最终投稿包校验清单：

- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-manifest.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-artifact-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-submission-package-readme.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-33-ars-submission-integrity-review.md`

这一步记录核心 manuscript、figure、table、result 和 script 文件的 SHA256 指纹，方便最终 GitHub release、Zenodo/Figshare 归档和投稿后复核。它不替代作者信息、基金/COI、图件人工审核和 DOI/PID 创建。
