# yumi

ZEAMAP 玉米 oil-trait prediction + GWAS 项目。

当前项目只做 `/home/user/zhangzhishuai/data/plantDB/pretraining_dataset_assessment.md` 里的第一条玉米路线。现在的目标不是先做大模型，而是先把 ZEAMAP 这批数据做成能写论文的结果：

```text
数据对齐 -> v0.1 processed dataset -> trait prediction benchmark
-> oil traits GEMMA LMM GWAS -> lead loci / candidate genes / figures
```

## 先看这里：这个项目到底做了什么

这个项目可以理解成一条完整的玉米油脂性状论文路线。我们拿到的是 ZEAMAP 公共玉米数据，但这些数据一开始不是一张可以直接分析的大表，而是很多不同文件：有 genotype，有 population，有 phenotype/metabolome，有 methylation，还有一些 expression/reference 相关文件。第一件事不是建模型，而是先弄清楚哪些玉米材料能真正一一对应。

最通俗的流程是：

```text
下载 ZEAMAP 数据
-> 检查文件能不能读
-> 统一玉米材料 accession 名字
-> 构建 v0.1 分析数据集
-> 用 genotype + population 预测各种性状
-> 发现 oil / fatty-acid traits 最稳定、最有信号
-> 对 10 个高优先级 oil traits 做 GEMMA mixed-model GWAS
-> 找到候选 SNP、候选区间和候选基因
-> 做区域图、综合图、流程图、模型结构图
-> 写英文论文、中文版本和投稿材料
```

### 1. 为什么一开始不直接做大模型

一开始项目方向看起来像“多组学预训练数据集评估”，但真正检查数据后发现：

- 严格能配对的 accession 只有 461 个。
- methylation 只有 236 个 accession 覆盖。
- expression 文件不是这 461 个 accession 的表达矩阵，而更像 B73/SK/HZS/Mo17 这类 reference/tissue expression。
- SNP 很多，有 199,856 个，但样本数不大。

所以当前数据不适合直接训练复杂 transformer 或大规模多模态模型。那样很可能只是过拟合，论文也不好解释。我们选择了更稳妥的路线：先把数据整理干净，用正则化模型和 GEMMA GWAS 做出可靠、能投稿的油脂性状遗传分析。

### 2. 数据整理做了什么

ZEAMAP 里不同表的样本名字不一定完全一致。我们先做的是“对身份证”：

- phenotype 表里有哪些 accession？
- population 表里有哪些 accession？
- VCF genotype 里有哪些 accession？
- methylation 里有哪些 accession？
- 这些 accession 名字能不能对应上？

最终整理出一个统一样本索引表，并构建了 v0.1 processed dataset：

```text
461 个 accession：genotype + population + 至少一种 phenotype/metabolome
199,856 个 SNP
318 个数值 phenotype/metabolome traits
236 个 accession 有 methylation coverage
```

这里的原则是：宁可少放一些数据，也不能把不对应的样本强行拼在一起。

### 3. 预测 benchmark 在回答什么问题

整理好数据后，我们先问：

```text
只用 genotype 和 population，能不能预测玉米性状？
```

输入是：

```text
SNP + population 信息
```

输出是：

```text
phenotype/metabolome trait
```

我们比较了 ridge、ElasticNet、population-only ridge 和 small MLP。结果显示，当前样本量下最稳的是：

```text
genotype_population_ridge
```

最重要的发现是：oil traits 是所有性状里预测效果最好的家族。

```text
66 个 robust traits
oil traits median Pearson/R2 = 0.596 / 0.321
```

通俗解释：玉米油脂和脂肪酸性状里有比较强的遗传信号，值得继续做更正式的 GWAS。

### 4. methylation 为什么没有放进主模型

我们也测试了 methylation，结果是：

- global methylation summary 基本没有整体增益。
- gene-level methylation PCA 有一点辅助信号。
- sparse methylation feature 在 236 个 accession 上不稳定。

所以 methylation 目前只作为辅助分析和候选解释材料，不作为主模型输入。这样写论文更稳，不会过度声称“多组学模型已经成功”。

### 5. 为什么要做 GEMMA GWAS

预测告诉我们 oil traits 最有信号，于是我们对 10 个 high-priority oil traits 做 GWAS。

一开始做过简单版 covariate-only GWAS，但结果 lambda GC 很高：

```text
lambda GC = 2.41 - 3.97
```

这说明结果膨胀，可能有很多假阳性。原因是玉米材料有群体结构和亲缘关系，只靠 population covariates 控制不够。

所以我们改用 GEMMA mixed linear model。GEMMA 会加入 genotype-derived kinship，更好地控制亲缘关系。GEMMA 结果明显更可靠：

```text
lambda GC = 0.984 - 1.018
median lambda GC = 0.998
```

通俗解释：GEMMA 把假阳性风险压下去了，所以它是当前论文的主 GWAS 结果。

### 6. GWAS 后怎么找候选基因

GEMMA 得到显著 SNP 后，我们没有直接说“这个 SNP 就是因果变异”。我们做的是更保守的候选区间整理：

```text
lead SNP
-> 合并附近信号为 candidate locus
-> 找 locus 附近的 B73 RefGen_v4 gene
-> 加功能注释
-> 看是否有 lipid/fatty-acid keyword
-> 看是否和 prediction attribution 有交叉支持
-> 给候选区间排序
```

当前结果：

```text
184 个 manuscript candidate loci
147 个 candidate genes
63 个 loci 有 ridge attribution 支持
11 个 loci 有 lipid/fatty-acid 注释
18 个 tier-1 main-text loci
```

### 7. 目前最重要的候选区间

最强的是 chr6 区域：

```text
chr6 linoleic acid1-region
Zm00001d036982
```

它强在：

- 跨 7 个 oil traits 反复出现。
- P 值非常显著。
- 有 lipid/fatty-acid 注释。
- 有 ridge prediction evidence 支持。
- 和已有 maize oil/fatty-acid 文献方向一致。

但当前仍然只能写成：

```text
strong candidate interval
leading candidate gene
```

不能写成：

```text
已经验证的因果基因
已经证明的因果 SNP
```

第二个重点是 chr9 区域：

```text
chr9 C16:0-associated interval
Zm00001d045383 附近
nearby Zm00001d045387 / acyl-ACP thioesterase
```

这里也要谨慎。lead gene 本身不是 FatB，但附近有 acyl-ACP thioesterase / palmitoyl-ACP thioesterase 注释，和 C16:0 饱和脂肪酸组成有生物学关系。所以它是一个高优先级 C16:0 candidate interval，但还不是已经确认的因果基因。

### 8. 图表现在有哪些

目前已经做了多类图表：

```text
Figure 1：数据整理 + prediction benchmark
Figure 2：GEMMA GWAS calibration + candidate loci summary
Figure 3：chr6 / chr9 重点区域图
Figure 4：prediction + GWAS 综合证据图
Figure 5：整体工作流程图
Figure 6：模型/统计结构图
```

其中最适合快速看懂项目的是：

```text
results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure5_overall_workflow_nature.png
results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures_stage5_36/figure6_model_structure_nature.png
```

Figure 5 告诉你整个项目按什么顺序做。

Figure 6 告诉你 genotype、population、trait 怎么进入 prediction，再怎么进入 GEMMA GWAS，最后怎么排序 candidate loci。

### 9. 论文现在做到什么程度

目前已经生成：

- 英文修订稿。
- 中文对应稿。
- Word、PDF、Markdown、LaTeX 格式。
- Word 字体优化版。
- 图表审计。
- 投稿包清单。
- GitHub 同步记录。

建议优先打开这两个 Word 文件：

```text
docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-en-font-optimized.docx
docs/2026-06-06-zeamap-v0-1-stage5-36-revised-submission-manuscript-zh-font-optimized.docx
```

### 10. 这篇文章的核心故事

最简单的论文故事是：

```text
我们把 ZEAMAP 玉米公共数据重新整理成一个严格配对的数据集。
先用 genotype + population 预测所有性状，发现油脂/脂肪酸性状最有遗传信号。
然后对这些油脂性状做 GEMMA mixed-model GWAS，控制群体结构和亲缘关系导致的假阳性。
最后找到 chr6 linoleic acid1-region 和 chr9 C16:0/acyl-ACP thioesterase 相关区间等高优先级候选区域。
这些结果为玉米油脂和脂肪酸组成的后续功能验证和育种提供候选区间。
```

### 11. 这篇文章不能过度声称什么

当前不能说：

- 已经找到了确定因果基因。
- 已经证明某个 SNP 是因果变异。
- 已经完成多组学大模型。
- methylation 是主效应。

当前应该说：

- 我们优先排序了候选区间。
- GEMMA 提供了校准后的 GWAS 证据。
- chr6 和 chr9 是高优先级候选区域。
- 后续还需要 fine mapping、表达证据和功能验证。

## 当前一句话结论

我们已经把 ZEAMAP 玉米公共数据整理成一个可以写论文的油脂性状分析项目。现在已经完成了从数据清洗、样本配对、性状预测、油脂性状 GWAS、候选基因区间筛选，到论文初稿、中文稿、主图、流程图、模型结构图和 Word/PDF/LaTeX 导出的整套流程。

更白话地说，当前已经做完这些事：

- 把 ZEAMAP 里分散的 genotype、population、phenotype/metabolome 数据按 accession 对齐。
- 构建了一个可靠的 v0.1 分析数据集：461 个 accession、199,856 个 SNP、318 个数值性状。
- 先用 genotype + population 预测各种性状，发现油脂和脂肪酸性状最稳定、最有遗传信号。
- 因为 oil traits 最强，所以专门挑 10 个高优先级 oil traits 做正式 GWAS。
- 先做过简单 GWAS，发现假阳性风险高；后来改用 GEMMA mixed model，把群体结构和亲缘关系控制住。
- 从 GEMMA 结果里整理出候选 SNP、候选区间和候选基因。
- 重点发现两个最值得关注的区域：chr6 linoleic acid1 区域和 chr9 C16:0/acyl-ACP thioesterase 相关区域。
- 已经生成论文需要的主图、区域图、综合证据图、整体流程图和模型结构图。
- 已经写出英文论文稿和中文对应稿，并导出 Word、PDF、Markdown、LaTeX 格式。
- Word 版已经做过字体优化，英文/数字用 Times New Roman，中文用宋体。
- 剩下主要是人工信息：作者、单位、基金、致谢、利益冲突声明，以及最终投稿前人工确认。

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
