# External genotype pretraining route: ARS-style review

更新日期：2026-06-06

## Material Passport

- Project: Yumi maize genotype-to-trait prediction model
- Mode: experiment-agent validate/plan
- Scope: current decision to add G2F/Panzea external genotype data for self-supervised pretraining
- Verification status: ANALYZED
- Data sensitivity: public genotype resources only

## 通俗结论

当前路线是正确的：

```text
不要继续只在 461 个 ZEAMAP accession 上硬训 Transformer。
应该先用 G2F/Panzea 大规模 maize genotype 做自监督预训练，
再回到 ZEAMAP 做 trait prediction fine-tuning/evaluation。
```

原因很简单：

```text
461 个样本太少；
199,856 个 SNP 太多；
Transformer 参数量比 ridge 大；
没有外部预训练时，深度模型很容易过拟合。
```

目前已有实验已经证明了这一点：

```text
ridge baseline:                 Pearson 0.498 / R2 0.204
supervised SNPWindowFormer:      Pearson 0.351 / R2 0.076
pretrain + fine-tune, ZEAMAP only: Pearson 0.251 / R2 0.021
small regularized WindowFormer:  Pearson 0.325 / R2 0.040
```

所以论文主线应当改成：

```text
外部 genotype 自监督预训练是否能提升玉米多性状预测？
```

而不是：

```text
我们又调了一个 Transformer 参数。
```

## 当前新增外部数据是否必要

必要。

G2F 2014-2023：

```text
inbreds_G2F_2014-2023_437k.vcf
key_inbreds_G2F_2014-2023.txt
readme.txt
```

Panzea HapMap3.2.1 AGPv4：

```text
hmp321_agpv4_chr1.vcf.gz
...
hmp321_agpv4_chr10.vcf.gz
```

这两类数据都只有 genotype，不需要 trait 标签，正适合做 masked-genotype self-supervised pretraining。

## 当前最大风险

### 1. 下载风险

当前已经确认：

```text
计算节点没有网络；
登录节点访问 CyVerse data.cyverse.org 时返回 IP verification 页面。
```

这不是代码 bug，而是 CyVerse 对当前网络出口的匿名下载拦截。后来使用用户提供的代理订阅，在登录节点临时启动 sing-box 后，G2F VCF/key/readme 已经下载成功。

已经处理：

```text
scripts/fetch_g2f_genotype_resources.py
scripts/fetch_panzea_hapmap321_agpv4.py
```

脚本会识别这种错误，不会把验证页误当作 VCF。现在脚本已经改为：如果下载到的是验证页，则自动改名为 `*.blocked.html`。

### 2. 坐标版本风险

ZEAMAP SNP 和外部 VCF 可能不是完全相同 genome build。

处理原则：

```text
先确认 chrom/pos/ref/alt；
能直接交集就直接交集；
不能直接交集再考虑 liftover；
不要把坐标不一致的数据硬拼。
```

### 3. 样本重叠风险

外部预训练数据可能包含 ZEAMAP accession 或近似同名材料。

处理原则：

```text
预训练可以使用无标签 genotype；
但 final test accession 不能通过 trait 标签泄漏；
需要单独记录 overlap accession。
```

### 4. 模型结果风险

即使加入外部预训练，深度模型也不一定超过 ridge。

论文必须保留 ridge/ElasticNet 强基线。如果深度模型只在部分 trait family 提升，也可以写成：

```text
self-supervised genotype pretraining improves prediction for genetically stable trait families,
but regularized linear models remain strong in small accession-level maize datasets.
```

这比硬说“Transformer 全面最好”更可信。

## 下一步实验门槛

外部数据下载成功后，才进入下一阶段。

最低可继续条件：

```text
至少 1 个外部 VCF 可读；
能解析样本数；
能解析 SNP 数；
能确认 chromosome/position/ref/alt；
能与 ZEAMAP SNP 做交集或可解释的坐标转换。
```

G2F 已下载成功，因此现在可以继续进入 parser/tensor 构建。Panzea 仍可作为后续补充，但不再阻塞下一步。

## 投稿故事建议

最稳的模型文章故事：

```text
1. 构建 ZEAMAP accession-level 多性状预测基准。
2. 证明 ridge/ElasticNet 在小样本高维 SNP 场景下很强。
3. 提出 SNPWindowFormer，把连续 SNP 压成窗口 token。
4. 证明 ZEAMAP-only Transformer 不足。
5. 引入 G2F/Panzea genotype-only self-supervised pretraining。
6. 比较 no-pretrain vs external-pretrain vs ridge/ElasticNet。
7. 分 trait family 分析哪些性状真正受益。
```

这个故事有失败结果、有强基线、有外部数据、有模型方法，审稿人更容易接受。

## 当前判定

```text
GO. G2F external genotype is available; proceed to parser implementation.
```

现在不应该继续消耗 GPU 训练 ZEAMAP-only Transformer。应该先把 G2F VCF 转成外部预训练 tensor，再做 masked-genotype pretraining。
