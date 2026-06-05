# ZEAMAP 当前进展评估

日期：2026-06-05

## 评估结论

当前项目已经完成从数据下载、ID 对齐、`v0.1` processed dataset、baseline benchmark、trait 筛选、methylation 消融到 genotype 候选解释性 screen 的闭环。

整体评估：

```text
进展状态：良好
当前结论可靠性：中高
是否适合继续：适合
下一步方向：genotype 侧严格解释性分析，而不是扩大模型复杂度
```

## 已完成度评估

### 数据层

完成度：高。

已完成：

- ZEAMAP 第一批和第二批数据检查。
- accession ID 统一索引。
- genotype、population、phenotype/metabolome 强配对集合。
- 461 个 accession 的 `v0.1` processed dataset。
- 236 个 methylation-covered accession 的 coverage/missing-modality 标记。

主要风险：

- expression 当前不是 AMP accession-level paired expression，因此不能用于 accession-level 输入。
- chromatin accessibility 和 interaction 不是当前主模型可直接使用的 accession-level matrix。

评估：

数据层已经足够支撑当前小模型 benchmark。暂时不需要下载原始 FASTQ 或全量 assembly。

### 模型层

完成度：中高。

已完成：

- population-only baseline。
- genotype PCA + ridge baseline。
- genotype + population ridge/ElasticNet。
- small MLP 对照。
- 5-seed robustness。
- final benchmark 汇总。

关键结果：

- `genotype_population_ridge` 在 66 个 robust traits 上 median Pearson/R2 为 0.498/0.204。
- positive R2 fraction 为 0.979。
- small MLP 不稳定，R2 为负。

评估：

当前主模型选择合理。样本量只有 461，正则线性模型优于小神经网络是符合预期的。继续堆复杂模型的收益低，过拟合风险高。

### trait 筛选层

完成度：高。

已完成：

- 317 个可评估 traits 的初始 benchmark。
- 130 个 selected traits。
- 66 个 robust selected traits。
- family-level performance summary。

关键结论：

- oil traits 最强。
- agronomic traits 次之。
- metabolite 和 amino acid 有信号，但稳定性较弱。

评估：

66 个 robust traits 可以作为后续主评估集合。oil traits 应作为第一优先目标。

### methylation 层

完成度：中高。

已完成：

- global methylation summary。
- gene/promoter/cis-window methylation PCA。
- sparse gene-window methylation feature selection。
- epigenome decision。

关键结果：

- global summary 几乎没有增益。
- gene methylation PCA 有小幅 R2 增益。
- sparse raw gene-window methylation 低于 genotype+population baseline。

评估：

methylation 的当前定位清楚：辅助消融和候选解释，不作为主输入。这个决策降低了过拟合和模型复杂度风险。

### genotype attribution 层

完成度：初步完成。

已完成：

- top 15 traits 的 train-split SNP correlation screen。
- SNP 到 B73 RefGen_v4 gene/promoter/cis-window 的映射。
- SNP summary 和 gene summary。

关键结果：

- 750 个 SNP-trait candidates。
- 674 个 SNP 在 5 个 seeds 都入选。
- 488 个候选落在 gene body。

评估：

这是有价值的候选发现步骤，但不是正式 association analysis。下一步必须加入 population covariates、LD clumping 和多重检验控制。

## 当前最大风险

### 风险 1：样本量限制

461 个 accession 对复杂模型偏少，236 个 methylation-covered accession 更少。

影响：

- 深度模型容易过拟合。
- 高维 methylation sparse selection 不稳定。
- 单个 trait 的 test set 可能只有几十个有效样本。

应对：

- 使用 ridge/ElasticNet。
- 多 seed robustness。
- trait family-level 总结。
- 不扩大模型复杂度。

### 风险 2：群体结构混杂

玉米群体结构强，population covariates 可能解释很多 phenotype variation。

影响：

- 如果不控制 population，genotype association 可能虚高。
- attribution candidates 可能反映 population difference，而非 causal variant。

应对：

- 保留 population-only baseline。
- 主模型使用 genotype+population。
- 下一步解释性分析必须加入 residualization 或 covariate-adjusted association。

### 风险 3：特征维度远大于样本数

199,856 SNP 对 461 accession，methylation gene-window 也远多于样本。

影响：

- 容易选到偶然相关特征。
- 稀疏模型不稳定。

应对：

- PCA/降维。
- 正则化。
- train-only feature selection。
- 跨 seed 稳定性筛选。

### 风险 4：模态不是完全配对

methylation 只有 236 个 accession，expression 不是 AMP accession-level。

影响：

- 多模态模型会损失大量样本。
- 错误使用 expression 会造成错误结论。

应对：

- v0.1 主模型不使用 expression。
- methylation 只做辅助消融。
- modality mask 保留，等待后续更完整数据。

## 当前结论可信度

高可信：

- 数据配对数量和 modality coverage。
- 66 个 robust traits 的存在。
- ridge/ElasticNet 强于 small MLP。
- oil traits 是最稳定 family。
- methylation raw features 不适合作为 v0.1 主输入。

中等可信：

- methylation PCA 有小幅增益。
- genotype attribution candidates 的稳定性。
- metabolite/amino acid family 的可预测性排序。

低可信或不能声称：

- 某个 SNP/gene 是 causal。
- methylation sparse selected gene 是真实调控因子。
- 当前数据足以训练大规模多模态预训练模型。
- reference/tissue expression 可代表 AMP accession expression。

## 是否达到阶段目标

阶段目标 1：验证 ZEAMAP processed data 能否构建统一 accession-level 数据集。

结果：达到。

阶段目标 2：判断当前样本量能否做 baseline benchmark。

结果：达到。

阶段目标 3：找出稳定可预测 trait。

结果：达到，66 个 robust traits。

阶段目标 4：判断 methylation 是否进入主模型。

结果：达到，结论是不进入主模型。

阶段目标 5：开始 genotype 解释性方向。

结果：初步达到，已完成候选 screen。

## 下一步建议

### 首选任务：严格 genotype association/attribution

目标：

- 从候选 screen 走向更可信的候选基因列表。

建议做法：

- 对 oil high-priority traits 优先。
- 对 phenotype 做 population covariate residualization。
- 对 SNP 做 single-marker association 或 regularized feature attribution。
- 加 LD clumping。
- 做 permutation/FDR。
- 输出 trait-SNP-gene annotated table。

成功标准：

- 每个 high-priority oil trait 得到稳定候选 locus/gene。
- 候选 locus 不只是 population structure artifact。

### 第二任务：gene-window genotype representation

目标：

- 把 SNP-level 高维输入变成 gene-level 可解释输入。

建议做法：

- 根据 B73 RefGen_v4 gene body/promoter/cis-window 聚合 SNP dosage。
- 构建 gene-window burden 或 variant count features。
- 比较 gene-window ridge/ElasticNet 与 genotype PCA ridge。

成功标准：

- 性能接近 PCA baseline。
- 可解释性更强。

### 第三任务：结果汇报材料

目标：

- 把当前进展整理成图表和报告。

建议图表：

- final benchmark model comparison barplot。
- trait family performance boxplot。
- top 15 traits performance table。
- methylation ablation comparison。
- genotype attribution candidate locus/gene table。

## 暂不建议做的事

- 训练 transformer 或复杂多模态模型。
- 下载并处理 raw SRA/FASTQ。
- 把 methylation raw gene-window features 直接并入主训练。
- 把 expression 文件当作 accession-level paired expression。
- 对 attribution candidates 做强生物学结论。

## 项目当前定位

当前项目最适合定位为：

```text
ZEAMAP 玉米 accession-level genotype-to-phenotype benchmark
+ robust trait selection
+ epigenome ablation
+ genotype candidate attribution
```

不是：

```text
大规模泛植物多模态预训练模型
```

后者需要更多 accession-level paired omics、更大样本量和更严格的跨数据源 harmonization。
