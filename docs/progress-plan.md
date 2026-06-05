# Yumi progress plan

更新日期：2026-06-06

## 项目现在要做什么

当前项目只聚焦 ZEAMAP 玉米数据。目标是按正式论文标准完成两条主线：

1. `genotype + population -> phenotype/metabolome` 的预测 benchmark。
2. high-priority oil traits 的 GEMMA mixed-linear-model GWAS。

当前不把“大规模多模态预训练”作为近期目标。原因很直接：v0.1 只有 461 个强配对 accession，methylation 只有 236 个 accession，样本量不足以支撑复杂 transformer。现在最有论文价值的是把 oil-trait prediction 和 oil-trait GWAS 做扎实。

## 总体状态表

| 阶段 | 状态 | 结论 |
|---|---|---|
| 阶段 0 数据下载与检查 | 已完成 | 第一批、第二批 ZEAMAP 文件可读，核心文件完整 |
| 阶段 1 样本 ID 统一 | 已完成 | phenotype、population、VCF 可以对齐到 accession |
| 阶段 2 v0.1 processed dataset | 已完成 | 得到 461 个强配对 accession |
| 阶段 3 baseline benchmark | 已完成 | genotype+population ridge 有稳定预测信号 |
| 阶段 3.1 trait 筛选 | 已完成 | 317 个可评估 trait 中筛出 130 个 selected traits |
| 阶段 3.2 multi-seed 稳定性 | 已完成 | 得到 66 个 robust traits |
| 阶段 3.3 lightweight model comparison | 已完成 | ridge/ElasticNet 优于 small MLP |
| 阶段 4 methylation 消融 | 已完成 | methylation 不进入 v0.1 主模型 |
| 阶段 4.5 final benchmark | 已完成 | 固化 `genotype_population_ridge` 主模型 |
| 阶段 5.1 genotype attribution screen | 已完成 | 得到候选 SNP/gene，但不是正式 GWAS |
| 阶段 5.2 covariate-only GWAS | 已完成 | lambda GC 过高，只作诊断 |
| 阶段 5.3 GEMMA LMM GWAS | 已完成 | lambda GC 接近 1，可作为论文主 GWAS baseline |
| 阶段 5.4 GEMMA lead loci 注释 | 已完成初版 | 已输出 manuscript candidate loci/gene 表和 Nature 风格 summary figure |
| 阶段 5.5 top locus 优先级和局部图 | 已完成初版 | 已输出 top loci 排序、seed literature evidence 和 8 个 regional locus/LD/gene-track figures |
| 阶段 5.6 论文主表和 Results 初稿 | 已完成初版 | 已输出 top regional evidence table、tier1 主表、184 loci 补充表和 Results draft |
| 阶段 5.7 Methods 草稿和主图整合 | 已完成初版 | 已输出 Methods draft、Figure 1、Figure 3、figure plan 和 captions draft |
| 阶段 5.8 manuscript skeleton | 已完成初版 | 已输出完整论文骨架、table captions、readiness checklist |
| 阶段 5.9 manuscript polish and citation audit | 已完成初版 | 已输出投稿策略/中稿率、citation audit 和软件版本文件 |
| 阶段 5.10 manuscript polish round 2 | 已完成初版 | 已输出 polished manuscript、reference list、Methods parameter supplement 和 ARS self-review |
| 阶段 5.11 external annotation hardening | 已完成初版 | 已输出 top regional loci 外部注释硬化表和投稿就绪度评估 |
| 阶段 5.12 final manuscript assembly | 已完成初版 | 已输出目标期刊稿件组装、supplement column dictionary、figure audit 和 data/code availability |
| 阶段 5.13 final submission gate | 已完成初版 | 已输出 DOI/reference audit、cover letter、reviewer profiles、release plan 和 final gate audit |
| 阶段 5.14 human metadata and release finalization templates | 已完成模板包 | 已输出作者/单位/基金/COI、命名审稿人、图件人工检查和 release 命令模板 |
| 阶段 5.15 preflight validation | 已完成校验器 | 已输出文件 manifest、placeholder audit、gate status 和 action items；真实 release 仍需作者填表后执行 |
| 阶段 5.16 metadata ingestion dry-run | 已完成 dry-run | 已输出 metadata ingestion audit、title-page preview 和 contribution preview；真实元数据仍未填 |
| 阶段 5.17 single human-input package | 已完成初版 | 已输出单一人工信息总表、同步 dry-run、填写说明和 ARS 投稿闸门自评；真实元数据仍未填 |
| 阶段 5.18 reviewer-risk register | 已完成初版 | 已输出模拟审稿风险表、修订路线图、submission gate matrix 和 ARS reviewer synthesis |
| 阶段 5.19 result-to-script reproducibility crosswalk | 已完成初版 | 已输出主结果到脚本/输入/输出/参数的 crosswalk、文件 inventory、Methods 插入段和 ARS 可复现性审查 |
| 阶段 5.20 GWAS diagnostic appendix | 下一步 | 输出每个 oil trait 的 lambda、样本数、SNP 数、Bonferroni/FDR/suggestive 阈值和图件路径 |
| 阶段 5.21 final metadata insertion and release | 待人工信息后执行 | 单表填完并同步后，重跑 preflight/dry-run，通过后创建 release/tag/DOI |

## 当前最重要的数字

数据规模：

```text
461 accessions: genotype + population + phenotype/metabolome
236 accessions: additional methylation coverage
199,856 SNPs
318 numeric traits
66 robust traits for final benchmark
10 high-priority oil traits for GEMMA GWAS
```

预测 benchmark：

```text
final model: genotype_population_ridge
final traits: 66 robust traits
median Pearson: 0.498
median R2: 0.204
oil traits median Pearson/R2: 0.596 / 0.321
```

GWAS：

```text
covariate-only GWAS lambda GC: 2.41-3.97
GEMMA LMM GWAS lambda GC: 0.984-1.018
GEMMA LMM median lambda GC: 0.998
GEMMA Bonferroni hits per oil trait: 1-21
manuscript candidate loci: 184
manuscript candidate genes: 147
lipid/fatty-acid keyword loci: 11
ridge-supported manuscript loci: 63
top prioritized loci: 184
tier1 main-text loci: 18
tier2 strong loci: 22
top regional figures: 8
strongest region: chr6 Zm00001d036982 / linoleic acid1
top regional evidence table: 8 rows
main tier1 locus table: 18 rows
supplementary manuscript candidate loci: 184 rows
literature/source records: 6
Figure 1/3 main figures: PDF/SVG/PNG generated
Methods draft: 1 file
Figure captions draft: 1 file
Manuscript skeleton: 1 file
Readiness checklist: 1 file
Journal strategy: 1 file
Citation audit: 1 file
Polished manuscript draft: 1 file
Reference list draft: 1 file
Methods parameter supplement: 1 file
Academic-research-suite self-review: 1 file
Methods software versions: 1 file
External annotation hardening table: 1 file
Target-journal manuscript assembly: 1 file
Supplementary column dictionary: 1 file
Figure quality audit: 1 file
Data/code availability draft: 1 file
Reference DOI audit: 1 file
Cover letter draft: 1 file
Reviewer suggestion draft: 1 file
Repository release plan: 1 file
Final submission gate audit: 1 file
Author metadata template: 1 file
Affiliation template: 1 file
Reviewer worksheet: 1 file
Figure manual checklist: 1 file
Release command draft: 1 file
Preflight manifest: 1 file
Placeholder audit: 1 file
Gate status table: 1 file
Action-item table: 1 file
Metadata ingestion dry-run: 1 file
Title-page preview: 1 file
Contribution preview: 1 file
Single human-input form: 1 file
Single-form sync audit: 1 file
Single-form filling guide: 1 file
Stage 5.17 ARS self-review: 1 file
Reviewer-risk register: 1 file
Revision roadmap: 1 file
Submission gate matrix: 1 file
ARS reviewer synthesis: 1 file
Result-to-script crosswalk: 1 file
Reproducibility file inventory: 1 file
Methods reproducibility insert: 1 file
ARS reproducibility review: 1 file
```

## 阶段 0：数据下载与检查

状态：已完成。

做了什么：

- 确认 ZEAMAP 数据来自 CNGBdb project `CNP0001565`。
- 下载第一批 processed expression、phenotype/metabolome、population 文件。
- 下载第二批 SNP VCF 和 epigenome 相关文件。
- 检查文本、VCF、xls 文件都能读取，不是错误页或空文件。

主要报告：

- `docs/2026-06-04-zeamap-first-batch-download-check.md`
- `docs/2026-06-04-zeamap-second-batch-check.md`

## 阶段 1：样本 ID 统一

状态：已完成。

做了什么：

- 检查每个表的样本列名和 accession 命名规则。
- 输出统一样本索引表。
- 确认 phenotype、population、VCF 三者能对齐。

主要结果：

- population 文件有 507 个 accession。
- metabolite phenotype 有 339 个 accession。
- agri/AA/Oil phenotype 有 476 个 accession。
- population + 任一 phenotype/metabolome 的强配对 accession 为 461 个。
- VCF 有 507 个 samples，和 population accession 对齐。

重要判断：

- 当前 expression 文件不是 AMP accession-level expression，不能放进 v0.1 主数据。

主要产出：

- `data/metadata/zeamap_accession_index.tsv`
- `data/metadata/zeamap_table_id_summary.tsv`
- `data/metadata/zeamap_expression_sample_columns.tsv`
- `docs/2026-06-04-zeamap-sample-id-check.md`

## 阶段 2：v0.1 processed dataset

状态：已完成。

做了什么：

- 以 accession 为单位构建最小可行数据集。
- 纳入 genotype、population、phenotype/metabolome。
- methylation 先只作为 coverage/missing-modality 标记。
- expression 暂不纳入。

主要结果：

- accessions：461。
- SNP：199,856 个常见、高样本数 biallelic SNP。
- phenotype/metabolome：318 个数值 trait columns。
- methylation coverage：236 个 accession。

主要产出：

- `data/processed/v0_1/accessions.tsv`
- `data/processed/v0_1/phenotype.parquet`
- `data/processed/v0_1/population.parquet`
- `data/processed/v0_1/modality_mask.tsv`
- `data/processed/v0_1/genotype_dosage_int8.npz`
- `docs/2026-06-04-zeamap-v0-1-build-report.md`

## 阶段 3：prediction benchmark

状态：已完成。

这一步回答的问题：

```text
只用 genotype 和 population，能不能预测 phenotype/metabolome？
```

第一版 baseline：

- train/validation/test = 322/69/70。
- genotype 先做 PCA。
- 最佳第一版模型是 `genotype_pca_population_ridge`。
- 在 317 个 traits 上 test median Pearson = 0.331，median R2 = 0.034。

为什么还要继续筛 trait：

- 所有 trait 混在一起看，中位数不高。
- 但 oil traits 信号很强。
- 需要找出稳定、可重复预测的 trait 集合。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-baseline-report.md`

## 阶段 3.1-3.2：trait 筛选和稳定性

状态：已完成。

流程：

1. 从 317 个可评估 traits 中筛出 130 个 selected traits。
2. 用 5 个 random seeds 重复训练和测试。
3. 保留多次 split 下稳定的 traits，得到 66 个 robust traits。

66 个 robust traits 组成：

```text
oil: 29
metabolite: 16
agronomic: 15
amino acid: 6
```

结论：

- oil traits 是当前最强主线。
- 这 66 个 robust traits 是后续模型比较和消融实验的主评估集合。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-selected-traits.md`
- `docs/2026-06-05-zeamap-v0-1-robustness-report.md`

## 阶段 3.3：lightweight model comparison

状态：已完成。

比较模型：

- ridge
- ElasticNet
- small MLP

结果：

```text
genotype_population_ridge      median Pearson/R2 = 0.498 / 0.204
genotype_population_elasticnet median Pearson/R2 = 0.483 / 0.171
small MLP                      median Pearson/R2 = 0.351 / -0.191
```

结论：

- ridge 是当前最稳主模型。
- ElasticNet 接近 ridge。
- small MLP 不稳定，暂时不继续加深神经网络。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-lightweight-model-report.md`

## 阶段 4：methylation 消融

状态：已完成。

我们测试了三种 methylation 用法。

### 4.1 global methylation summary

结果：

```text
genotype+population+methylation median Pearson/R2 = 0.496 / 0.173
genotype+population             median Pearson/R2 = 0.490 / 0.173
```

结论：整体增益很小。

### 4.2 gene/promoter/cis-window methylation PCA

结果：

```text
genotype+population+gene methylation PCA median Pearson/R2 = 0.496 / 0.199
genotype+population                      median Pearson/R2 = 0.490 / 0.173
```

结论：比 global summary 好一些，但提升仍有限。

### 4.3 sparse gene-window methylation

结果：

```text
gene methylation PCA ridge      median Pearson/R2 = 0.449 / 0.160
genotype+population ridge       median Pearson/R2 = 0.414 / 0.106
sparse methylation ElasticNet   median Pearson/R2 = 0.338 / 0.025
```

结论：raw gene-window methylation 稀疏模型不稳定，不适合做主输入。

最终决策：

- v0.1 主模型不接入 raw methylation features。
- methylation 保留为 coverage mask、辅助 PCA 消融和候选解释材料。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-methylation-subset-report.md`
- `docs/2026-06-05-zeamap-v0-1-gene-methylation-pca-report.md`
- `docs/2026-06-05-zeamap-v0-1-sparse-methylation-selection-report.md`
- `docs/2026-06-05-zeamap-v0-1-epigenome-decision.md`

## 阶段 4.5：final benchmark

状态：已完成。

最终主模型：

```text
genotype_population_ridge
```

最终主评估集合：

```text
66 个 robust traits
```

结果：

```text
overall median Pearson/R2 = 0.498 / 0.204
positive R2 fraction = 0.979
oil median Pearson/R2 = 0.596 / 0.321
```

结论：

- v0.1 已经足够支撑 accession-level prediction benchmark。
- 当前不进入大规模多模态预训练。
- 下一步重点转向 oil traits 的 GWAS 和候选基因解释。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-final-benchmark.md`

## 阶段 5.1：genotype attribution screen

状态：已完成。

做了什么：

- 选 final benchmark 中表现最好的 15 个 traits。
- 只在 train split 中计算 SNP-trait correlation。
- 每个 trait 输出稳定 top SNP。
- 把 SNP 映射到 B73 RefGen_v4 gene/promoter/cis-window。

结果：

- SNP-trait candidates：750 行。
- 674 个 SNP 在 5 个 seeds 都入选。
- gene-level candidates：587 行。

结论：

- 这是候选解释性 screen。
- 它不是正式 GWAS，不能用来声称 causal variant。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-genotype-attribution-report.md`

## 阶段 5.2：covariate-only GWAS

状态：已完成，但只作为诊断 baseline。

做了什么：

- 对 10 个 high-priority oil traits 做逐 SNP association。
- 每个 trait 有 440 个非缺失 accession。
- SNP 数为 199,856。
- 用 PC1-PC3 和 K1-K3 做 covariate residualization。
- 输出 Bonferroni/FDR、LD clumping、gene mapping、Manhattan/QQ 图。

结果：

```text
lambda GC = 2.41-3.97
```

解释：

- lambda GC 明显偏高，说明统计膨胀严重。
- 这一步不能作为论文主 GWAS。
- 它的作用是证明必须用 mixed linear model 处理 kinship。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-gwas-baseline-report.md`

## 阶段 5.3：GEMMA LMM GWAS

状态：已完成，是当前论文主 GWAS baseline。

做了什么：

- 对同样 10 个 high-priority oil traits 做 GEMMA LMM。
- 每个 trait 有 440 个非缺失 accession。
- SNP 数为 199,856。
- 使用 genotype-derived kinship matrix。
- 加入 PC1-PC3、K1-K3 covariates。
- 使用 GEMMA `p_lrt`。
- 输出 Bonferroni/FDR、LD clumped lead SNP、gene mapping、Manhattan/QQ 图。

结果：

```text
lambda GC range = 0.984-1.018
median lambda GC = 0.998
Bonferroni hits per trait = 1-21
```

和 covariate-only GWAS 对比：

```text
covariate-only lambda GC = 2.41-3.97
GEMMA LMM lambda GC       = 0.984-1.018
```

结论：

- GEMMA LMM 有效消除了统计膨胀。
- GEMMA LMM 是当前能面向论文的 GWAS 主结果。
- lead SNP/gene 表可以进入 candidate loci 初稿。
- 还不能直接写 causal claim，下一步必须做功能注释、文献核查和 locus 图。

主要报告：

- `docs/2026-06-05-zeamap-v0-1-gemma-lmm-report.md`

## 阶段 5.4：GEMMA lead loci 注释

状态：已完成初版。

目标：

把 GEMMA lead SNP 变成论文能用的 candidate locus/candidate gene 结果。

已完成：

1. 整理每个 oil trait 的 GEMMA lead SNP。
2. 按同一 trait、同一染色体、相邻 lead SNP 距离 1 Mb 合并为 locus。
3. 给 locus 匹配 candidate gene。
4. 从 B73 RefGen_v4 Ensembl/Gramene GFF3 提取 gene description 和 biotype。
5. 标注 Bonferroni、FDR、suggestive、nominal 等显著等级。
6. 输出 manuscript-facing 表，排除 nominal-only loci。
7. 标注和 ridge attribution screen 的 gene/SNP overlap。
8. 自动标注 lipid/fatty-acid、seed、transport/membrane、hormone/regulatory 等功能关键词。
9. 生成 Nature 风格 summary figure，输出 PDF/SVG/PNG。

结果：

- 完整 candidate loci：795 个。
- manuscript candidate loci：184 个。
- manuscript candidate genes：147 个。
- Bonferroni loci：38 个。
- FDR loci：131 个。
- suggestive loci：15 个。
- 有 ridge attribution 支持的 manuscript loci：63 个。
- 有 lipid/fatty-acid keyword 的 manuscript loci：11 个。
- manuscript candidate gene rows 缺少 GFF description：22 行。

产出：

- `scripts/build_zeamap_v0_1_gemma_candidate_loci.py`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_candidate_loci.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_candidate_genes.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_genes.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_candidate_lead_snps_annotated.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.svg`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.png`
- `docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md`

成功标准：

- 每个 high-priority oil trait 有清楚的 top locus/candidate gene 表。
- 表中区分 genome-wide significant、FDR significant 和 suggestive loci。
- 图表可以进入论文结果草稿。
- 所有结论都保持 candidate locus 口径，不写成 causal variant。

## 阶段 5.5：top locus 优先级和局部图

状态：已完成初版。

目标：

从 184 个 manuscript candidate loci 中优先挑出最适合写论文主结果的 top loci，并先生成可审稿级打磨的 regional association/locus/LD/gene-track 图。

已完成：

1. 建立 top locus priority score。
2. 把 GEMMA 显著等级、`-log10(P)`、ridge attribution overlap、lipid/fatty-acid keyword、多 oil traits 复现、candidate gene 数量合并成排序依据。
3. 输出 184 个 manuscript loci 的优先级表。
4. 标出 18 个 tier1 main-text loci 和 22 个 tier2 strong loci。
5. 选择 8 个 top regional targets。
6. 为 8 个 top regions 生成 Nature 风格 PDF/SVG/PNG 区域图。
7. 建立 seed literature evidence 表，用于指导文献核查。

最重要结果：

- chr6 `Zm00001d036982` / linoleic acid1 是当前最强主结果候选，跨 7 个 oil traits 复现，最佳 `P = 2.35e-25`。
- chr4 `Zm00001d049511`、chr1 `Zm00001d031002`、chr8 `Zm00001d009150` 是多 trait 复现的 tier1 regions。
- chr9 `Zm00001d045383` 区域虽然是 tier2，但局部包含 `Zm00001d045387` fatty acyl-ACP thioesterase2，应优先做功能注释补强。

产出：

- `scripts/build_zeamap_v0_1_top_locus_priority.py`
- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_locus_priority.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_region_targets.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_literature_evidence_seed.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.pdf`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.svg`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.png`
- `docs/2026-06-05-zeamap-v0-1-top-locus-priority-report.md`

限制：

- priority score 是排序工具，不是新的统计检验。
- regional figure 是 association + LD context + gene model，不是 fine-mapping。
- seed literature evidence 不是完整系统综述，下一阶段还要逐个 top region 补 MaizeGDB/UniProt/Gramene/论文证据。

## 阶段 5.6：论文主表和 Results 初稿

状态：已完成初版。

目标：

把 8 个 top regional loci 从“统计候选”推进到“论文写作材料”。

已完成：

1. 建立 8 个 top regional loci 的 evidence table。
2. 给每个 top region 标注 evidence level、推荐 manuscript claim 和 claim boundary。
3. 输出 18 行 tier1 main-text locus table。
4. 输出 184 行 supplementary manuscript candidate loci table。
5. 输出 6 条 literature/source records。
6. 写出 Results draft，覆盖 prediction benchmark、GEMMA LMM inflation control、prioritized oil-trait loci 和 claim boundary。

最重要判断：

- chr6 `Zm00001d036982` 是 A 级 direct prior lipid locus，适合作为第一个 Results 重点区域。
- chr9 `Zm00001d045383`/附近 `Zm00001d045387` fatty acyl-ACP thioesterase2 是 A 级 C16:0 fatty-acid candidate interval，适合和 chr6 一起作为重点图。
- chr4、chr1、chr8 等多 trait 复现区域要保持 indirect/recurrent candidate 口径。

产出：

- `scripts/build_zeamap_v0_1_stage5_6_manuscript_tables.py`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/top_regional_loci_evidence.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/main_tier1_locus_table.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/supplementary_manuscript_candidate_loci.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_tables/literature_sources.tsv`
- `docs/2026-06-05-zeamap-v0-1-results-draft.md`
- `docs/2026-06-05-zeamap-v0-1-stage5-6-manuscript-tables-report.md`

限制：

- 当前 evidence table 是 curated first pass，不是系统综述。
- A 级证据表示有较强先验/通路/区域支持，不等于本研究证明 causal gene。
- 后续还要继续补 MaizeGDB/UniProt/Gramene 的逐基因外部注释。

## 阶段 5.7：Methods 草稿和主图整合

状态：已完成初版。

目标：

把当前结果组织成正式论文骨架。

已完成：

- 整合 Figure 1：v0.1 dataset construction + prediction benchmark。
- 整合 Figure 2：沿用 GEMMA LMM calibration + candidate-locus summary。
- 整合 Figure 3：chr6 和 chr9 regional candidate intervals。
- 写 Methods 草稿：dataset construction、prediction benchmark、methylation ablation、GEMMA LMM、candidate-locus annotation、regional figure generation。
- 写 Figure 1-3 captions draft。
- 输出 main figure plan。

产出：

- `scripts/build_zeamap_v0_1_stage5_7_methods_and_figures.py`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.pdf`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.svg`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure1_dataset_prediction_nature.png`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.pdf`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.svg`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_7/figure3_chr6_chr9_regional_loci_nature.png`
- `docs/2026-06-05-zeamap-v0-1-methods-draft.md`
- `docs/2026-06-05-zeamap-v0-1-main-figure-plan.md`
- `docs/2026-06-05-zeamap-v0-1-figure-captions-draft.md`
- `docs/2026-06-05-zeamap-v0-1-stage5-7-methods-figures-report.md`

限制：

- Figure 1/3 是论文主图初版，投稿前还要做最后视觉微调。
- Figure 2 暂用 Stage 5.4 的 GEMMA summary figure。
- Methods draft 还不是完整投稿格式，需要和 Results/Introduction 合并后再统一润色。

## 阶段 5.8：manuscript skeleton

状态：已完成初版。

目标：

把已有 Results、Methods、Figures、Tables 合并成完整论文骨架。

已完成：

- 写 working title。
- 写 Abstract draft。
- 写 Keywords。
- 写 Introduction draft。
- 合并 Results draft。
- 合并 Methods draft。
- 添加 Figure 1-3 captions。
- 添加 Table 1 和 Supplementary Table captions。
- 写 Discussion outline。
- 添加 Data Availability、Code Availability、Acknowledgements、Author Contributions、Competing Interests 和 References placeholders。
- 输出 manuscript readiness checklist。

产出：

- `scripts/build_zeamap_v0_1_stage5_8_manuscript_skeleton.py`
- `docs/2026-06-05-zeamap-v0-1-manuscript-skeleton.md`
- `docs/2026-06-05-zeamap-v0-1-table-captions-draft.md`
- `docs/2026-06-05-zeamap-v0-1-manuscript-readiness-checklist.md`
- `docs/2026-06-05-zeamap-v0-1-stage5-8-manuscript-skeleton-report.md`

限制：

- manuscript skeleton 不是投稿稿。
- Introduction 和 Discussion 还需要扩展文献和更完整论证。
- Methods 还需要补 exact software versions、参数和命令细节。
- 引用还没有转换成正式 reference list。

## 阶段 5.9：manuscript polish and citation audit

状态：已完成初版。

目标：

开始把 skeleton 打磨成更接近投稿前草稿，并给出投稿路线和中稿率判断。

已完成：

- 输出投稿策略和中稿率估计。
- 输出 citation audit 初版。
- 输出 Methods software versions 初版。
- 明确推荐投稿路线。
- 明确仍需补 ZEAMAP/GEMMA/B73 annotation/reference list。

推荐投稿路线：

```text
平衡路线：The Plant Genome -> G3 -> BMC Plant Biology
保守路线：G3 or BMC Plant Biology
冲刺路线：Journal of Experimental Botany presubmission enquiry
暂不首投：Nature Plants / Plant Physiology
```

中稿率估计：

```text
当前 skeleton：合理期刊 eventual acceptance 35-55%
Stage 5.9-5.10 打磨后：55-75%
有独立验证/更强多组学支持后：70-85%
```

产出：

- `docs/2026-06-05-zeamap-v0-1-journal-strategy-and-acceptance-estimate.md`
- `docs/2026-06-05-zeamap-v0-1-citation-audit.md`
- `docs/2026-06-05-zeamap-v0-1-methods-software-versions.md`
- `docs/2026-06-05-zeamap-v0-1-stage5-9-polish-citation-report.md`

## 阶段 5.10：manuscript polish round 2

状态：已完成初版。

做了什么：

- 把 manuscript skeleton 扩展成 polished manuscript draft。
- 把 Introduction、Results、Discussion 和 Methods 串成一条完整论文逻辑。
- 添加 ZEAMAP、GEMMA、B73 RefGen_v4、maize oil GWAS 和软件 reference list draft。
- 输出 Methods parameter supplement，记录 dataset、prediction、methylation、GEMMA 和 candidate-locus 关键参数。
- 按 academic-research-suite 思路输出自评，明确审稿风险、claim boundary 和投稿定位。

产出：

- `docs/2026-06-06-zeamap-v0-1-polished-manuscript-draft.md`
- `docs/2026-06-06-zeamap-v0-1-reference-list-draft.md`
- `docs/2026-06-06-zeamap-v0-1-methods-parameter-supplement.md`
- `docs/2026-06-06-zeamap-v0-1-ars-self-review.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-10-report.md`

## 阶段 5.11：external annotation hardening

状态：下一步。

目标：

把 top regional loci 的生物学解释从 local GFF description 提升到投稿级外部数据库注释。

需要做：

- 补 MaizeGDB/Gramene/UniProt/GO 等外部注释。
- 核查 chr6 `Zm00001d036982` 和 chr9 `Zm00001d045387` 的 gene symbol、description 和文献支持。
- 给 8 个 regional loci 增加可放入 Supplementary Table 的注释字段。
- 做 reference DOI/author audit。
- 检查 Figure 1-3 字体、尺寸和 caption 一致性。

## GitHub 更新规则

每完成一个小阶段都更新并提交：

- `README.md`
- `docs/progress-plan.md`
- `docs/model-architecture.md`
- 阶段报告：`docs/YYYY-MM-DD-*.md`

本地大矩阵和 raw result 不提交到 GitHub，只提交脚本、summary table、报告和小图表。


## 阶段 5.12：final manuscript assembly

状态：下一步。

目标：

把当前预投稿稿件包转成某个目标期刊可直接检查的投稿文件。

需要做：

- 选择目标期刊格式。
- 把 polished manuscript draft 转成 journal-style manuscript。
- 给 supplementary tables 写 column dictionary。
- 最终检查 Figure 1-3 的字体、线宽、panel 标签和 caption。
- 完成 Data availability、Code availability、Author contributions、Competing interests。


## 阶段 5.13：final submission gate

状态：下一步。

目标：

把 Stage 5.12 的 near-submission package 过一遍最终投稿闸门。

需要做：

- 确认首投期刊：The Plant Genome 或 G3。
- 完成 reference DOI/author-list audit。
- 生成人工最终检查版 cover letter。
- 完成 reviewer suggestion / opposed reviewer 草稿。
- 检查 Figure 1-3 最终版视觉质量。
- 明确 GitHub release、Zenodo/Figshare DOI 或 data availability 方案。


## 阶段 5.14：human metadata and release finalization

状态：下一步。

目标：

把已经完成的 near-submission package 转成可由作者确认并实际上传的最终投稿文件。

需要人工信息：

- 作者名单、单位和通讯作者。
- 基金、致谢和利益冲突。
- 命名审稿人和回避审稿人。
- GitHub release/Zenodo DOI 是否执行。
- Figure 1-3 最终人工视觉确认。


## 阶段 5.15：author-confirmed release execution

状态：下一步，需要作者信息。

目标：

把 Stage 5.14 的模板填成真实投稿元数据，并执行最终 release/DOI。

需要人工输入：

- 作者姓名、排序、单位、邮箱、ORCID。
- 通讯作者和共同一作信息。
- CRediT contribution。
- funding、acknowledgements、competing interests。
- 命名推荐审稿人和回避审稿人。
- Figure 1-3 人工视觉确认。
- 是否创建 GitHub release 和 Zenodo/Figshare DOI。


## 阶段 5.16：author-confirmed release execution

状态：下一步，需要真实作者元数据。

目标：

在 Stage 5.15 preflight 通过后，执行真正的 release/tag/DOI，并把 release DOI 写回最终稿件。

执行条件：

- author metadata template 无 `TO_COMPLETE`。
- 所有 yes/no 字段已确认。
- final figure manual checklist 全部 pass。
- reviewer worksheet 有命名审稿人并完成 conflict check。
- repository visibility 已确认。


## 阶段 5.17：final metadata insertion and release

状态：下一步，需要真实作者元数据。

目标：

在 author/reviewer/figure 模板全部填完后，将真实元数据写回目标期刊稿件，并执行 release/tag/DOI。

执行条件：

- Stage 5.15 preflight 为 `READY_FOR_RELEASE_EXECUTION`。
- Stage 5.16 metadata ingestion dry-run 为 `READY_TO_INSERT_METADATA`。
- 通讯作者确认 final upload package。


## 阶段 5.17：single human-input package

状态：已完成初版，但真实作者信息仍未填。

为什么做这一步：

投稿前必须有人确认作者、单位、基金、利益冲突、审稿人和图件人工检查。之前这些内容散在多个模板中，容易漏填。Stage 5.17 把它们收敛成一个总表，填完后可自动同步回 Stage 5.14 模板。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-single-human-input-form.tsv`
- `docs/2026-06-06-zeamap-v0-1-single-human-input-form-guide.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-single-form-sync-audit.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-sync-report.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-17-ars-self-review.md`

下一步：

真实信息填完后执行 Stage 5.17 `--apply`，再重跑 Stage 5.15 和 Stage 5.16。只有两个门槛都通过后，才进入真实 release/tag/DOI。


## 阶段 5.18：reviewer-risk register

状态：已完成初版。

为什么做这一步：

论文投稿前最容易被审稿人攻击的点已经不是“有没有结果”，而是：稿件是否足够完整、方法能否复现、GWAS 诊断是否透明、chr6/chr9 文献支撑是否足够、prediction-guided 这个说法有没有过度、以及作者/图件/release 信息是否齐全。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-18-reviewer-risk-register.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-revision-roadmap.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-submission-gate-matrix.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-ars-reviewer-synthesis.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-18-report.md`

当前判断：

核心分析主线可以继续向论文推进，但还不是最终投稿包。机器侧下一步应优先做 result-to-script reproducibility crosswalk 和 GWAS diagnostic appendix；人工侧仍需填写 Stage 5.17 单表并完成图件人工检查。


## 阶段 5.19：result-to-script reproducibility crosswalk

状态：已完成初版。

为什么做这一步：

审稿人经常会问每个主结果、主表和主图到底由哪个脚本生成，输入是什么，输出在哪里，关键参数是什么。Stage 5.19 把这些信息整理成 crosswalk，让论文从“有结果”进一步变成“结果能追踪、能复核”。

主要产出：

- `docs/2026-06-06-zeamap-v0-1-stage5-19-result-script-crosswalk.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-reproducibility-file-inventory.tsv`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-methods-reproducibility-insert.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-ars-reproducibility-review.md`
- `docs/2026-06-06-zeamap-v0-1-stage5-19-report.md`

当前判断：

可复现性风险从“缺少映射表”降为“最终 release 包装还要说明哪些大文件不进 GitHub”。下一步机器侧应做 GWAS diagnostic appendix，把每个 oil trait 的统计诊断整理成投稿附录表。
