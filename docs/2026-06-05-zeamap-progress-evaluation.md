# ZEAMAP 当前进展评估

日期：2026-06-05

## 总评

当前项目进展是好的，而且方向应该继续冲论文。

现在已经不是“刚把数据跑通”的阶段，而是已经有了一个可以写成论文结果雏形的 v0.1：

```text
v0.1 processed dataset
+ prediction benchmark
+ robust trait selection
+ methylation ablation
+ GEMMA LMM oil-trait GWAS
```

当前最适合的论文定位是：

```text
ZEAMAP maize accession-level genotype-to-phenotype benchmark
and mixed-linear-model GWAS for oil-related traits
```

不是：

```text
large-scale plant multi-omics foundation model
```

后者现在样本量和模态配对都不够。

## 当前能写进论文的内容

### 可以写

1. 数据集构建

我们可以写 ZEAMAP processed data 被整理成 accession-level v0.1 数据集，包含 461 个强配对 accession、199,856 个 SNP、318 个数值 traits 和 population covariates。

2. 预测 benchmark

我们可以写 ridge/ElasticNet 在 66 个 robust traits 上建立了稳定预测基准，其中 oil traits 表现最好。

3. 模型选择

我们可以写在当前样本量下，正则线性模型优于 small MLP，说明复杂模型会有过拟合风险。

4. methylation 消融

我们可以写 methylation PCA 有小幅增益，但 raw gene-window methylation features 在 236 个 accession 上不稳定，所以 methylation 不作为 v0.1 主输入。

5. GWAS 方法升级

我们可以写 covariate-only GWAS 出现明显 inflation，而 GEMMA LMM 通过 kinship correction 把 lambda GC 控制到接近 1。

6. oil-trait candidate loci

我们可以写 GEMMA LMM 为 10 个 high-priority oil traits 产生了 candidate loci，并已进一步整理出 top priority loci 和 regional locus figures 初稿。

### 不能写

1. 不能说当前模型是大规模预训练模型。
2. 不能说 small MLP 或 transformer 优于线性模型。
3. 不能把 B73/SK/HZS/Mo17 expression 当成 AMP accession expression。
4. 不能把 attribution screen 的 SNP 当成 GWAS lead SNP。
5. 不能把 covariate-only GWAS 的 hits 当成最终论文 loci。
6. 不能把 GEMMA lead SNP 直接写成 causal variant。

## 各部分完成度

| 模块 | 完成度 | 评价 |
|---|---|---|
| 数据下载检查 | 高 | 文件完整，可读性检查完成 |
| accession ID 对齐 | 高 | phenotype、population、VCF 已对齐 |
| v0.1 processed dataset | 高 | 461 个强配对 accession 已构建 |
| prediction benchmark | 高 | ridge/ElasticNet baseline 完成 |
| robust trait selection | 高 | 66 个 robust traits 已确定 |
| methylation ablation | 中高 | 已证明不适合作为主输入 |
| genotype attribution screen | 中 | 可作为候选解释，不能作为正式 GWAS |
| covariate-only GWAS | 中 | 工具链完成，但 inflation 高 |
| GEMMA LMM GWAS | 中高 | 当前论文主 GWAS baseline 已完成 |
| candidate gene annotation | 中高 | 已完成 GFF description、top loci priority 和 Stage 5.6 evidence table；逐基因外部数据库注释还需补强 |
| manuscript figures | 中高 | Nature 风格 GWAS summary figure 和 8 个 regional locus/LD 图已有初版 |
| manuscript tables/results | 中高 | 已输出 top regional evidence table、tier1 主表、184 loci 补充表和 Results draft |
| manuscript methods/figures | 中高 | 已输出 Methods draft、Figure 1、Figure 3、figure plan 和 captions draft |
| manuscript skeleton | 中 | 已输出完整骨架，但还需要文献扩展、citation audit 和正式润色 |
| submission strategy | 中 | 已输出投稿策略和中稿率估计，但需按最终稿质量更新 |

## 当前最大优势

### 1. oil traits 信号强

oil family 的 benchmark 表现最好：

```text
oil median Pearson/R2 = 0.596 / 0.321
```

这说明 oil traits 是最适合继续深入的论文主线。

### 2. GWAS inflation 已经被处理

covariate-only GWAS：

```text
lambda GC = 2.41-3.97
```

GEMMA LMM：

```text
lambda GC = 0.984-1.018
median = 0.998
```

这是一条很清楚的方法学故事：

```text
简单协变量校正不够 -> mixed linear model 必要 -> GEMMA 后 inflation 得到控制
```

### 3. 当前模型选择稳健

ridge/ElasticNet 优于 small MLP，这和样本量、特征维度关系一致。这个结果虽然不花哨，但可信。

## 当前最大风险

### 风险 1：样本量仍然偏小

461 个 accession 对 199,856 SNP 是小样本高维问题。236 个 methylation accession 更小。

应对：

- 继续使用 ridge/ElasticNet。
- 保持 multi-seed robustness。
- 不上复杂深度模型。

### 风险 2：群体结构很强

玉米 accession 存在明显 population structure。如果控制不够，GWAS 和 prediction 都可能虚高。

应对：

- prediction 里保留 population-only baseline。
- GWAS 主结果使用 GEMMA LMM。
- covariate-only GWAS 只作为 diagnostic baseline。

### 风险 3：candidate locus 还没有生物学解释

GEMMA 已经给出 lead SNP，Stage 5.4 也已整理出 manuscript candidate loci 和 GFF description。但还缺更强的生物学解释：

- oil/fatty-acid pathway support
- 已知 maize QTL/GWAS 文献对照
- locus/LD 图

应对：

- 下一阶段优先做 GEMMA lead loci 注释。

### 风险 4：模态配对不完整

expression 不是 AMP accession-level，methylation 只有 236 个 accession。

应对：

- v0.1 主模型只用 genotype + population。
- methylation 只做辅助消融。
- expression 暂不进入主数据集。

## 对当前结果的可信度分级

高可信：

- 461 个强配对 accession。
- 66 个 robust traits。
- oil traits 是最强 trait family。
- ridge/ElasticNet 是当前最稳模型。
- methylation raw features 不适合作为 v0.1 主输入。
- GEMMA LMM 后 lambda GC 接近 1。

中等可信：

- methylation PCA 的小幅增益。
- genotype attribution screen 的候选 SNP/gene。
- metabolite 和 amino acid traits 的可预测性。

低可信或不能声称：

- causal SNP。
- causal gene。
- methylation sparse selected genes 是真实调控因子。
- 当前数据足够做大规模多模态预训练。

## 是否适合继续

适合继续，但方向要明确。

适合继续做：

- 8 个 top regional loci 的逐个文献注释。
- 缺失/泛化 gene description 的外部注释补充。
- oil/fatty-acid pathway 文献核查。
- Nature 风格 regional locus/LD 图继续打磨。
- final benchmark 图表整理。
- ridge attribution 和 GEMMA lead loci overlap。

不适合继续做：

- 直接上 transformer。
- 扩大 neural network。
- 处理 raw FASTQ。
- 把 methylation raw features 强行加进主模型。
- 把 expression 文件强行配到 AMP accession。

## 已完成的新阶段：Stage 5.4

Stage 5.4 已完成第一版 GEMMA lead loci annotation。

结果：

```text
manuscript candidate loci = 184
manuscript candidate genes = 147
Bonferroni loci = 38
FDR loci = 131
suggestive loci = 15
ridge-supported manuscript loci = 63
lipid/fatty-acid keyword loci = 11
```

产出：

- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_loci.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/candidate_loci/gemma_manuscript_candidate_genes.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/manuscript_figures/figure_gemma_lmm_summary_nature.pdf`
- `docs/2026-06-05-zeamap-v0-1-gemma-candidate-loci-report.md`

评估：

这一步把 GEMMA 统计结果推进到了论文候选表初稿。功能注释现在来自 B73 RefGen_v4 GFF3，已经足够做第一轮筛选，但还需要对重点 locus 做 MaizeGDB/UniProt/Gramene/文献层面的增强注释。

## 已完成的新阶段：Stage 5.5

Stage 5.5 已完成 top locus priority 和 regional figure 初版。

结果：

```text
prioritized loci = 184
tier1 main-text loci = 18
tier2 strong loci = 22
top regional figures = 8
```

最强候选：

```text
chr6 Zm00001d036982 / linoleic acid1
best P = 2.35e-25
recurrent oil traits = 7
significance = Bonferroni
support = lipid/fatty-acid annotation + ridge attribution overlap
```

需要特别保留的 tier2 候选：

```text
chr9 Zm00001d045383 region
trait = Oil_C16_0
best P = 7.76e-17
nearby lipid gene = Zm00001d045387 fatty acyl-ACP thioesterase2
```

产出：

- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_locus_priority.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_top_region_targets.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/top_loci/gemma_literature_evidence_seed.tsv`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.pdf`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.svg`
- `results/v0_1_baseline/gemma_lmm_v0_1/regional_figures/*regional_locus_nature.png`
- `docs/2026-06-05-zeamap-v0-1-top-locus-priority-report.md`

评估：

这一步已经把“候选表初稿”推进到“论文主结果候选池”。现在可以开始写 Results 的 GWAS 候选位点段落，但还必须把 seed literature evidence 扩展成逐 locus 的外部数据库和论文核查。

## 已完成的新阶段：Stage 5.6

Stage 5.6 已完成论文主表和 Results 初稿。

结果：

```text
top regional evidence table = 8 rows
main tier1 locus table = 18 rows
supplementary manuscript candidate loci = 184 rows
literature/source records = 6
Results draft = 1 file
```

当前证据分级：

```text
A direct-prior/direct fatty-acid intervals = 2 regions
B lipid-related indirect interval = 1 region
C indirect/recurrent/regulatory/transport candidates = 4 regions
D statistical candidate = 1 region
```

评估：

这一步很关键，因为它把“候选位点很多”变成了“哪些可以写主文、哪些只能写补充、哪些 claim 不能越界”。现在最强的两个主文候选是：

- chr6 `Zm00001d036982` / linoleic acid1。
- chr9 C16:0 区域，附近 `Zm00001d045387` fatty acyl-ACP thioesterase2。

风险：

- 当前 evidence table 是 curated first pass，不是系统综述。
- A 级表示强候选证据，不代表 causal gene 已被本研究证明。
- 仍需补 MaizeGDB/UniProt/Gramene 的逐基因注释。

## 已完成的新阶段：Stage 5.7

Stage 5.7 已完成 Methods 草稿和主图整合初版。

结果：

```text
Methods draft = 1 file
Figure 1 = PDF/SVG/PNG
Figure 3 = PDF/SVG/PNG
Figure plan = 1 file
Figure captions draft = 1 file
```

评估：

这一步把项目从“有结果和表格”推进到“能组装论文骨架”。Figure 1 负责讲数据和预测 benchmark，Figure 2 负责讲 GEMMA GWAS calibration 和 candidate loci，Figure 3 负责讲 chr6/chr9 两个重点区域。

风险：

- Figure 1/3 是主图初版，投稿前还要继续视觉微调。
- Figure 2 暂时沿用 Stage 5.4 summary figure，后续可能需要按最终叙事重新排版。
- Methods draft 还需要和最终 manuscript skeleton 统一格式和术语。

## 已完成的新阶段：Stage 5.8

Stage 5.8 已完成 manuscript skeleton 初版。

结果：

```text
manuscript skeleton = 1 file
table captions draft = 1 file
readiness checklist = 1 file
stage report = 1 file
```

评估：

这是论文推进上的重要节点。现在项目不再只是分散的 Results、Methods、figures 和 tables，而是已经有一个完整 paper-facing skeleton，包含 title、abstract、introduction、results、discussion outline、methods、figure/table captions 和 availability placeholders。

风险：

- skeleton 还不是投稿稿。
- Introduction 和 Discussion 仍偏短。
- Methods 缺 exact software versions 和详细参数。
- 引用还只是 source list，没有做正式 citation audit。
- top loci 外部数据库注释仍需补强。

## 已完成的新阶段：Stage 5.9

Stage 5.9 已完成投稿策略、citation audit 和软件版本补充初版。

结果：

```text
journal strategy = 1 file
citation audit = 1 file
methods software versions = 1 file
stage report = 1 file
```

投稿路线建议：

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

评估：

当前文章最适合定位为 crop genomics / GWAS / reproducible benchmark manuscript。它有清楚数据整理、预测 benchmark、GEMMA LMM 和 candidate loci 主线，但缺独立验证、fine-mapping 和实验功能证据。因此 The Plant Genome、G3、BMC Plant Biology 是现实路线；Nature Plants 和 Plant Physiology 暂不适合首投。

风险：

- 中稿率是基于当前稿件成熟度的主观估计，不是期刊官方概率。
- 投稿策略要在 final manuscript 完成后重新评估。
- Citation audit 仍是 first pass，还没有形成正式 reference list。

## 下一阶段目标

下一阶段建议命名为：

```text
Stage 5.10: manuscript polish round 2
```

目标：

把 skeleton 进一步改成接近投稿前草稿，并补齐正式引用和外部注释。

具体任务：

1. 扩展 Introduction 文献定位。
2. 把 Discussion outline 写成完整 Discussion。
3. 把软件版本和关键参数并入 Methods。
4. 添加 ZEAMAP、GEMMA、B73 RefGen_v4/Gramene/Ensembl 等正式引用。
5. 继续补 top loci 外部注释。
6. 检查 Figure 1-3 字体、尺寸和 caption 一致性。

成功标准：

- 每个 oil trait 有清楚的 candidate locus 表。
- 每个重点 locus 有 candidate gene 和功能解释。
- 图表能进入论文结果草稿。
- 所有表述保持 candidate 口径，不夸大成 causal。

## 当前一句话判断

项目已经有论文级雏形，并且 GWAS 主结果已经进入候选位点写作前夜。下一步不是再堆模型，而是把 8 个 top regional loci 的外部注释、文献证据、论文主表和 Results 段落补齐。
