# 基于预测筛选和混合模型 GWAS 的 ZEAMAP 玉米油脂性状候选区间解析

## 题名页

题名：基于预测筛选和混合模型 GWAS 的 ZEAMAP 玉米油脂性状候选区间解析

短题名：ZEAMAP 玉米油脂性状预测与 GWAS

作者：×××

单位：×××

通讯作者：×××

ORCID/email：×××

作者确认：×××

## 核心观点

- 将 ZEAMAP 公共 processed 数据整理为严格按 accession 对齐的分析数据集。
- 在正则化基因型预测模型中，油脂和脂肪酸性状比其他性状家族更稳定、可预测性更强。
- 混合模型 GWAS 是必要步骤：仅使用协变量的 GWAS 存在膨胀，而 GEMMA 能有效控制 lambda GC。
- chr6 和 chr9 区间提供了当前最清晰的脂肪酸相关候选信号。
- 本研究定位为候选区间优先级排序，不声称已经证明因果变异或完成基因功能验证。

## 摘要

玉米籽粒油分含量和脂肪酸组成是重要的籽粒品质性状，但在玉米多样性群体中进行关联分析时，必须区分真实局部信号与群体结构、亲缘关系带来的混杂。我们将 ZEAMAP 公共 processed 数据整理为一个保守的 accession 水平分析集，包含 461 个 accession、199,856 个过滤后的 SNP 以及 318 个数值型表型或代谢性状。重复的基因型到表型预测筛选出 66 个稳健可预测性状；其中油脂性状是表现最强的性状家族，genotype plus population ridge 模型在稳健油脂性状上的 median Pearson/R2 为 0.597/0.338。基于这一结果，我们对 10 个高优先级油脂性状开展 GWAS。仅使用协变量的扫描存在明显膨胀，而加入基因型亲缘矩阵的 GEMMA 混合线性模型将 lambda GC 控制在 0.984-1.018，中位数为 0.998。在排除 nominal-only 信号后，我们注释并排序了 184 个候选 locus 和 147 个候选基因。证据最强的是一个反复出现的 chr6 linoleic acid1 区间，以及一个与 C16:0 相关、附近含 acyl-ACP thioesterase 注释的 chr9 区间。本研究提供了从公共玉米 processed 数据走向校准后油脂性状候选区间的可复现流程，并明确限制因果性表述。

## 关键词

玉米；ZEAMAP；籽粒油分；脂肪酸组成；基因组预测；混合模型 GWAS；GEMMA；候选区间

## 引言

籽粒油分含量和脂肪酸组成影响玉米籽粒品质、营养价值和工业利用。这类性状也具有较强的生物学解释价值，因为它们连接了脂肪酸代谢、籽粒发育和碳分配等过程。已有玉米研究报道了油分和脂肪酸相关位点，包括与 linoleic acid、DGAT 介导的油分积累以及籽粒组成相关的遗传信号（Alrefai et al., 1995; Zheng et al., 2008; Li et al., 2013; Zhang et al., 2023）。不过，公共多样性群体数据不能直接当作一个已经整理好的分析矩阵使用。

ZEAMAP 为玉米多组学和性状研究提供了重要公共资源（Gui et al., 2020）。实际分析中的难点在于，不同 processed 表格的 accession、模态和生物学单位并不天然一致。参考基因型或组织水平表达数据不能直接当作 AMP accession 水平表达；只有部分 accession 覆盖的 methylation 数据也不能强行作为全样本主输入。因此，我们先构建一个严格对齐的 accession 水平分析集，只在 genotype、population 和 phenotype/metabolite 能够对应的范围内进行主要建模。

第二个难点是统计尺度。461 个 accession 和近 20 万个 SNP 足以支持正则化预测和 GWAS，但不足以支撑不受约束的复杂深度模型。复杂模型可能看起来先进，却更容易学习群体结构或噪声。因此，本研究采用正则化模型和重复评估来筛选稳定的性状家族，再将筛选结果用于聚焦油脂性状 GWAS。

第三个难点是 GWAS 校准。玉米多样性群体中的关联分析很容易受到残余群体结构影响。如果候选基因故事建立在膨胀的检验结果上，即使注释看起来合理也不稳固。因此，本研究将 covariate-only GWAS 作为诊断层，而将 GEMMA 混合线性模型作为正式关联分析层（Zhou & Stephens, 2012; Zhou & Stephens, 2014）。随后通过统计显著性、跨油脂性状复现、预测证据重叠和 B73 参考基因组注释来解释候选区间（Jiao et al., 2017; Yates et al., 2022）。

## 结果

### accession 对齐得到保守但可解释的 ZEAMAP 分析集

在整理 ZEAMAP processed genotype、population 和 phenotype/metabolome 表格后，最终分析集保留了 461 个具备必要配对信息的 accession、199,856 个过滤后的双等位 SNP 和 318 个数值型性状。236 个 accession 具有 methylation 覆盖，因此 methylation 被记录为部分配对的辅助模态，而不是并入主模型。当前工作数据中的 expression 资源不能与多样性群体 accession 一一匹配，因此没有用于 genotype-to-phenotype 预测。

这种筛选降低了表面数据规模，但提高了结果解释性。所有主要预测和 GWAS 结果都基于同一个 accession 水平分析单位。对于结构复杂的玉米群体，这一点尤其重要，因为样本身份或模态配对松散会放大混杂风险。

### 油脂性状具有最强、最稳定的预测信号

重复预测 benchmark 表明，油脂性状是最清晰的目标性状家族。在已筛选性状家族中，油脂性状的 median Pearson 为 0.597，median R2 为 0.338，最佳油脂性状达到 Pearson/R2 = 0.924/0.827。在最终稳健性状中，29 个为油脂相关性状。表现最好的性状包括总油分和主要脂肪酸组分，说明 genotype 和 population 特征捕捉到了有生物学意义的油脂性状差异。

模型比较也支持保守建模策略。在当前样本量下，ridge 和 ElasticNet 比小型多层感知机更稳定。这并不是否定神经网络在玉米遗传研究中的价值，而是说明在当前数据规模和配对结构下，正则化模型更适合用于性状筛选和生物学解释。

### methylation 只适合作为辅助层

我们以 global methylation summary、gene/promoter/cis-window 主成分和 sparse gene-window 特征三种方式评估 methylation。Global 特征整体增益有限，gene-level component 提供少量辅助信号，而 sparse 特征在 236 个 accession 子集中不稳定。因此，methylation 没有进入主预测模型。这一处理避免了过强的多组学机制性声称，使主分析集中在完整配对的 genotype 和 trait 数据上。

### GEMMA 控制了 covariate-only GWAS 中仍然存在的膨胀

预测结果将关联分析聚焦到 10 个高优先级油脂性状。covariate-only 扫描显示，即使加入 population covariates，基因组膨胀仍然明显。相比之下，使用 genotype-derived kinship 的 GEMMA 混合线性模型将 lambda GC 控制在 0.984-1.018，中位数为 0.998。这一校准结果是本文的关键，因为它支持将局部峰解释为候选区间，而不是残余亲缘关系的产物。

在 10 个油脂性状中，每个性状使用 440 个非缺失 accession 和 199,856 个 SNP 进行检验。每个性状的 Bonferroni 显著 hit 数为 1 到 21，总计 126 个 Bonferroni 水平 hit 和 338 个 FDR 水平 hit。最强信号集中在 very-long-chain fatty-acid composition、C18 脂肪酸性状和 C16:0。Manhattan 和 QQ 图作为诊断图保留，正文重点呈现校准后的统计结果和优先候选区间。

### 候选 locus 排序区分了直接脂质候选和更宽泛的调控区间

GEMMA lead signals 被合并为物理候选区间，并用 B73 RefGen_v4 基因模型进行注释。去除 nominal-only 信号后，候选集合包含 184 个 locus 和 147 个候选基因。其中 63 个 locus 与 ridge attribution 证据重叠，11 个 locus 带有 fatty-acid 或 lipid 相关注释。分层排序将直接脂质代谢候选区间与更宽泛的调控或运输相关区间区分开来。

证据最强的是 chr6 上的 R01_Zm00001d036982。该区间在 7 个油脂性状中反复出现，最佳 P = 2.35e-25，并包含 B73 RefGen_v4 基因 Zm00001d036982，该基因对应当前 B73 v5 基因 Zm00001eb277490。局部注释和外部 xref 支持其与 lipid acyltransferase/DGAT-like 或 linoleic-acid 生物学相关。因此，该区间同时具备跨性状复现、强统计显著性、预测证据重叠和先验脂肪酸证据，是当前最强候选区间。

chr9 的 C16:0 区间提供了另一类重要信号。围绕 Zm00001d045383 的 lead interval 在 C16:0 中达到最佳 P = 7.76e-17。Lead gene 本身不是 FatB 注释，而是 DXS/isoprenoid-related 注释；更强的脂肪酸解释来自附近 Zm00001d045387/Zm00001eb377350 的 acyl-ACP hydrolase、palmitoyl-ACP thioesterase 和 fatty-acid biosynthesis 注释。因此，该区域是高优先级饱和脂肪酸候选区间，但还不能写成已经 fine-mapped 的 FatB 因果基因。

chr1、chr4 和 chr8 上的其他 tier-1 区间也具有跨性状复现和 ridge 支持，但注释更宽泛，包括 MYB-domain、protein-transport 和 tetratricopeptide-repeat 等类型。这些区域值得保留，因为跨油脂性状复现提示其关联结构较稳定；但目前更适合写成 hypothesis-generating intervals，而不是直接油脂合成基因。

### 扩展后的图表体系更清楚地表达证据层级

修订后的主图包含 4 张。Figure 1 展示数据整理和预测 benchmark；Figure 2 展示混合模型 GWAS 校准和候选 locus 总结；Figure 3 展示 chr6 和 chr9 区域证据；Figure 4 进一步整合 trait-family predictability、GEMMA calibration、top region association strength 和 prioritized loci evidence class。表格体系包含 1 个主表和 4 个补充表：主表展示 8 个 top regional loci，补充表覆盖完整 candidate-locus set、tier-1 loci、external annotation hardening 和 column definitions。这样的结构既保持正文可读性，也给审稿人足够材料检查候选区间排序逻辑。

## 讨论

本研究提供了从 ZEAMAP 公共 processed 数据到玉米油脂性状候选区间的一条校准分析路线。最重要的结果并不只是发现了若干油脂性状关联峰，而是说明这些关联峰为什么可以被解释：输入 accession 经过统一整理，油脂性状由重复预测结果支持，covariate-only GWAS 被证明存在膨胀，而 GEMMA 混合模型将 lambda GC 控制在接近 1 的范围。

预测结果解释了为什么本文聚焦油脂性状。油脂和脂肪酸性状并不是因为生物学上有吸引力才被选择，而是在当前分析集中表现为最稳定、最可预测的性状家族。总油分和主要脂肪酸组分的强预测性能说明，现有 SNP 特征捕捉到了这些性状的一部分遗传结构。从育种应用角度看，这支持将油脂性状作为 ZEAMAP-derived panel 中正则化基因组预测的近期目标；而可预测性较弱的代谢物或氨基酸性状可能需要更大样本、更好的环境元数据或不同特征表示。

covariate-only 与 mixed-model GWAS 的差异同样关键。在玉米结构化群体中，仅有 population covariates 不足以控制混杂。如果没有 kinship 项，关联扫描的膨胀程度足以削弱候选解释。GEMMA 不只是改善了一个技术诊断指标，而是提高了生物学结论的可信度。10 个油脂性状中 lambda GC 均接近 1，说明最终候选区间较少受到残余亲缘关系主导。

chr6 区间是本文最重要的生物学锚点。它的强度来自多层证据收敛：多个油脂性状指向同一区间，统计显著性很强，ridge-derived evidence 支持该区域，局部注释连接到 linoleic-acid 或 lipid-acyltransferase 生物学，已有玉米油脂和脂肪酸研究也提供了合理背景（Alrefai et al., 1995; Zheng et al., 2008; Li et al., 2013; Zhang et al., 2023）。因此，合适的表述是强但有边界的：这是当前分析中的 leading recurrent fatty-acid candidate interval，而不是已经验证的因果基因。

chr9 C16:0 区间则更具性状特异性，也说明了基因水平解释必须谨慎。Lead gene 本身不是 FatB 注释，更强的脂肪酸解释来自附近的 acyl-ACP thioesterase candidate，这一通路类别与饱和脂肪酸组成直接相关。因此，该区间值得作为 C16:0 follow-up 重点，但不能过度表述为已确认的 FatB 因果等位基因。

更广泛的 recurrent loci 对育种和功能优先级排序也有价值。一些区间含有调控或运输相关候选，而不是典型油脂通路基因。这些基因仍可能通过籽粒发育、物质运输、细胞器功能或资源分配影响籽粒组成。不过，这类假设需要表达证据、fine mapping 或功能实验进一步支持。修订稿明确区分了证据层级：脂质注释区间作为较强候选，其他 recurrent regions 作为假设生成型区间保留。

本研究仍有明确局限。第一，分析集对于高维预测而言仍然偏小，复杂模型应等待更大的配对数据集。第二，methylation 只覆盖部分 accession，不能支撑强多组学机制结论。第三，GWAS 分辨率受 LD、标记密度和样本量限制。第四，候选基因尚未进行功能验证。后续更强的研究应包括独立群体验证、籽粒特异表达证据、chr6 和 chr9 周围 haplotype 分析，以及领先脂质相关基因的功能实验。

总体而言，本文最适合定位为植物基因组学资源和候选区间优先级排序研究。它贡献了可复现的 accession 水平分析、经过统计校准的油脂性状 GWAS 层，以及一套玉米油脂和脂肪酸组成候选区间排序结果。结论刻意保守，这会提高稿件在审稿中的可辩护性。

## 材料与方法

### ZEAMAP 数据和 accession 匹配

ZEAMAP processed public data 来自 CNGBdb project CNP0001565（Gui et al., 2020）。我们在 accession 水平匹配 genotype、population、phenotype 和 metabolome 表格。当 accession 具备 genotype、population 信息以及至少一个 phenotype 或 metabolome 测量值时，将其纳入分析集。SNP 过滤为具有足够样本覆盖的常见双等位标记，最终得到 199,856 个用于建模和关联分析的 variants。

### 预测分析

基因型到表型预测采用重复 train/validation/test split 进行评估。候选模型包括 genotype plus population ridge regression、genotype plus population ElasticNet、population-only ridge regression 和 small multilayer perceptron。只有在不同随机种子下性能为正且稳定的性状才进入最终结果。Held-out Pearson correlation 和 R2 是主要评价指标。

### methylation 评估

在具有 methylation 覆盖的 accession 子集中，我们将 methylation 作为辅助模态评估。测试形式包括 global methylation summaries、gene/promoter/cis-window components 和 sparse gene-window features。由于 methylation 子集明显小于完整分析集，且 sparse features 不稳定，methylation 没有进入主预测模型。

### mixed-model GWAS

从稳健预测结果中选择 10 个高优先级油脂性状进行 GWAS。Covariate-only GWAS 作为诊断对照。正式关联分析使用 GEMMA mixed linear models，并加入 genotype-derived kinship 和 population covariates（Zhou & Stephens, 2012; Zhou & Stephens, 2014）。Likelihood-ratio p-values 用于 locus ranking。Bonferroni 阈值为 0.05/199,856；FDR 结果用于候选排序而不是因果声称（Benjamini & Hochberg, 1995）。

### 候选 locus 注释和排序

Lead SNPs 被合并为物理区间，并用 B73 RefGen_v4 gene models 注释（Jiao et al., 2017）。候选区间依据 association strength、跨油脂性状复现、与 prediction-derived evidence 重叠、局部基因注释以及植物基因组资源中的外部支持进行排序（Yates et al., 2022）。区间被分为 direct lipid candidates、indirect regulatory/transport candidates 或 unresolved recurrent candidates。除非有独立功能证据，否则候选基因仅作为假设提出。

### 软件和可复现性

分析使用 Python 科学计算库和 GEMMA 进行 mixed-model association（Pedregosa et al., 2011; Harris et al., 2020; Virtanen et al., 2020; McKinney, 2010; Hunter, 2007; Zhou & Stephens, 2012）。项目仓库包含复现 accession harmonization、prediction benchmark、GWAS summaries、candidate-locus ranking 和 manuscript figures 所需的脚本和 summary tables。

## 数据可用性声明

本研究重新分析了 CNGBdb project CNP0001565 中公开的 ZEAMAP processed 数据。项目仓库包含分析脚本、summary tables、candidate-locus annotations 和 generated figures。大型公共原始输入和大型中间矩阵未纳入仓库；其来源和再生成路径已随分析文件记录。

## 代码可用性声明

用于 dataset construction、prediction benchmarking、methylation assessment、GWAS summarization、candidate-locus annotation 和 figure preparation 的代码位于项目仓库 `scripts/` 目录。

## 作者贡献

×××

## 基金

×××

## 致谢

×××

## 利益冲突

×××

## 伦理声明

本研究不涉及人类参与者或动物实验，仅重新分析公开植物基因组数据。

## 图例

Figure 1. ZEAMAP accession harmonization and prediction benchmark。该图总结 accession 匹配、保留数据规模、模型比较和 trait-family prediction performance。

Figure 2. GEMMA mixed-model GWAS calibration and candidate-locus summary。该图显示 GEMMA 控制了基因组膨胀，并总结过滤后的候选 locus 集合。

Figure 3. chr6 和 chr9 油脂性状候选区间的区域证据。图中突出显示反复出现的 chr6 linoleic acid1-region interval 和 chr9 C16:0-associated acyl-ACP thioesterase candidate interval。

Figure 4. Prediction 和 GWAS 综合证据。各 panel 总结 trait-family predictability、油脂性状 GEMMA calibration、top regional loci 的 association strength 以及 prioritized regions 的 evidence classes。

## 表格说明

Table 1. 玉米油脂性状优先候选区域。8 个 top loci 按 recurrence、association strength、prediction overlap、functional annotation 和 claim boundary 汇总。

Supplementary Table 1. 油脂性状 GEMMA mixed-model GWAS 的 manuscript candidate loci。

Supplementary Table 2. 用于正文解释的 tier-1 candidate loci。

Supplementary Table 3. Top regional loci 的 external annotation review。

Supplementary Table 4. 补充表 column dictionary。

## 参考文献

Alrefai, R., Berke, T. G., & Rocheford, T. R. (1995). Quantitative trait locus analysis of fatty acid concentrations in maize. *Genome*, *38*, 894-901. https://doi.org/10.1139/g95-118

Benjamini, Y., & Hochberg, Y. (1995). Controlling the false discovery rate: A practical and powerful approach to multiple testing. *Journal of the Royal Statistical Society: Series B*, *57*, 289-300. https://doi.org/10.1111/j.2517-6161.1995.tb02031.x

Bonaventure, G., Salas, J. J., Pollard, M. R., & Ohlrogge, J. B. (2003). Disruption of the FATB gene in Arabidopsis demonstrates an essential role of saturated fatty acids in plant growth. *The Plant Cell*, *15*, 1020-1033. https://doi.org/10.1105/tpc.008946

Cook, J. P., McMullen, M. D., Holland, J. B., Tian, F., Bradbury, P., Ross-Ibarra, J., Buckler, E. S., & Flint-Garcia, S. A. (2012). Genetic architecture of maize kernel composition in the nested association mapping and inbred association panels. *Plant Physiology*, *158*, 824-834. https://doi.org/10.1104/pp.111.185033

Gui, S., Yang, L., Li, J., Luo, J., Xu, X., Yuan, J., Chen, L., Li, W., Yang, X., & Wang, J. (2020). ZEAMAP, a comprehensive database adapted to the maize multi-omics era. *iScience*, *23*, 101241. https://doi.org/10.1016/j.isci.2020.101241

Harris, C. R., Millman, K. J., van der Walt, S. J., Gommers, R., Virtanen, P., Cournapeau, D., Wieser, E., Taylor, J., Berg, S., Smith, N. J., Kern, R., Picus, M., Hoyer, S., van Kerkwijk, M. H., Brett, M., Haldane, A., Del Rio, J. F., Wiebe, M., Peterson, P., ... Oliphant, T. E. (2020). Array programming with NumPy. *Nature*, *585*, 357-362. https://doi.org/10.1038/s41586-020-2649-2

Hunter, J. D. (2007). Matplotlib: A 2D graphics environment. *Computing in Science & Engineering*, *9*, 90-95. https://doi.org/10.1109/MCSE.2007.55

Jiao, Y., Peluso, P., Shi, J., Liang, T., Stitzer, M. C., Wang, B., Campbell, M. S., Stein, J. C., Wei, X., Chin, C. S., Guill, K., Regulski, M., Kumari, S., Olson, A., Gent, J., Schneider, K. L., Wolfgruber, T. K., May, M. R., Springer, N. M., ... Ware, D. (2017). Improved maize reference genome with single-molecule technologies. *Nature*, *546*, 524-527. https://doi.org/10.1038/nature22971

Katral, A., Ahirwar, R. N., Gazala, P., Jaiswal, S. K., Sachan, M., Barupal, T., Hossain, F., Muthusamy, V., Saripalli, G., Mishra, S. J., Gupta, H. S., & Chhabra, R. (2022). Allelic variation in Zmfatb gene defines variability for fatty acids composition among diverse maize genotypes. *Frontiers in Nutrition*, *9*, 845255. https://doi.org/10.3389/fnut.2022.845255

Li, H., Peng, Z., Yang, X., Wang, W., Fu, J., Wang, J., Han, Y., Chai, Y., Guo, T., Yang, N., Liu, J., Warburton, M. L., Cheng, Y., Hao, X., Zhang, P., Zhao, J., Liu, Y., Wang, G., Li, J., & Yan, J. (2013). Genome-wide association study dissects the genetic architecture of oil biosynthesis in maize kernels. *Nature Genetics*, *45*, 43-50. https://doi.org/10.1038/ng.2484

McKinney, W. (2010). Data structures for statistical computing in Python. In *Proceedings of the 9th Python in Science Conference* (pp. 56-61). https://doi.org/10.25080/Majora-92bf1922-00a

Pedregosa, F., Varoquaux, G., Gramfort, A., Michel, V., Thirion, B., Grisel, O., Blondel, M., Prettenhofer, P., Weiss, R., Dubourg, V., Vanderplas, J., Passos, A., Cournapeau, D., Brucher, M., Perrot, M., & Duchesnay, E. (2011). Scikit-learn: Machine learning in Python. *Journal of Machine Learning Research*, *12*, 2825-2830. https://jmlr.org/papers/v12/pedregosa11a.html

Virtanen, P., Gommers, R., Oliphant, T. E., Haberland, M., Reddy, T., Cournapeau, D., Burovski, E., Peterson, P., Weckesser, W., Bright, J., van der Walt, S. J., Brett, M., Wilson, J., Millman, K. J., Mayorov, N., Nelson, A. R. J., Jones, E., Kern, R., Larson, E., ... van Mulbregt, P. (2020). SciPy 1.0: Fundamental algorithms for scientific computing in Python. *Nature Methods*, *17*, 261-272. https://doi.org/10.1038/s41592-019-0686-2

Yates, A. D., Allen, J., Amode, R. M., Azov, A. G., Barba, M., Becerra, A., Bhai, J., Campbell, L. I., Carbajo Martinez, M., Chakiachvili, M., Chougule, K., Christensen, M., Contreras-Moreira, B., Cuzick, A., Da Rin Fioretto, L., Davis, P., De Silva, N., Diamantakis, S., Dyer, S. C., ... Flicek, P. (2022). Ensembl Genomes 2022: An expanding genome resource for non-vertebrates. *Nucleic Acids Research*, *50*, D996-D1003. https://doi.org/10.1093/nar/gkab1007

Zhang, C., Wang, J., Wang, L., Zhang, W., Liu, J., Li, H., Zhang, Y., Zhang, J., Yang, X., & Yan, J. (2023). Genetic dissection of QTLs for oil content in four maize DH populations. *Frontiers in Plant Science*, *14*, 1174985. https://doi.org/10.3389/fpls.2023.1174985

Zheng, P., Allen, W. B., Roesler, K., Williams, M. E., Zhang, S., Li, J., Glassman, K., Ranch, J., Nubel, D., Solawetz, W., Bhattramakki, D., Llaca, V., Deschamps, S., Zhong, G. Y., Tarczynski, M. C., & Shen, B. (2008). A phenylalanine in DGAT is a key determinant of oil content and composition in maize. *Nature Genetics*, *40*, 367-372. https://doi.org/10.1038/ng.85

Zhou, X., & Stephens, M. (2012). Genome-wide efficient mixed-model analysis for association studies. *Nature Genetics*, *44*, 821-824. https://doi.org/10.1038/ng.2310

Zhou, X., & Stephens, M. (2014). Efficient multivariate linear mixed model algorithms for genome-wide association studies. *Nature Methods*, *11*, 407-409. https://doi.org/10.1038/nmeth.2848
