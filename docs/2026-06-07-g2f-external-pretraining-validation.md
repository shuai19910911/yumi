# 2026-06-07 G2F 外部预训练阶段审查

## Material Passport

```text
Project: yumi / maize genotype-to-trait model paper
Mode: academic-research-suite experiment-agent validate
Status: ANALYZED
Stage: G2F native genotype pretraining preparation
Primary data:
  ZEAMAP v0.1 deep learning package
  G2F 2014-2023 genotypic VCF
Primary scripts:
  scripts/analyze_g2f_zeamap_variant_overlap.py
  scripts/prepare_g2f_native_pretrain_inputs.py
  scripts/train_snp_window_transformer_multitask.py
```

## 通俗结论

当前方向已经从“整理 GWAS 投稿包”拉回到“训练一个模型”。

但要注意：

```text
现在还不能说模型已经成功。
现在完成的是：找到了更合理的外部预训练路线，并开始构建训练数据。
```

## 为什么这一步是必要的

之前 ZEAMAP-only Transformer 没有超过 ridge：

```text
ridge:                         Pearson 0.498 / R2 0.204
supervised SNPWindowFormer:     Pearson 0.351 / R2 0.076
ZEAMAP pretrain + fine-tune:    Pearson 0.251 / R2 0.021
small regularized WindowFormer: Pearson 0.325 / R2 0.040
```

原因不是脚本没跑通，而是样本量太小：

```text
ZEAMAP 只有 461 个 accession。
SNP 有 199,856 个。
这是典型的小样本、高维特征问题。
```

所以如果文章要主打深度模型，就必须用更多 genotype-only 数据做预训练。

## G2F 和 ZEAMAP 不能直接合并

已经检查：

```text
ZEAMAP: AGPv4 / B73 RefGen_v4, 199,856 SNP
G2F: B73 v5 / G2F PHG marker space, 437,214 SNP
```

直接重叠结果：

```text
可直接共用 SNP: 9
ZEAMAP 覆盖比例: 0.0045%
```

判断：

```text
不能做共同 SNP 交集矩阵。
不能把 G2F 当成 ZEAMAP 的扩展样本直接拼接。
```

正确做法：

```text
G2F 在自己的 SNP 空间做 masked-genotype pretraining；
ZEAMAP 在自己的 SNP 空间做 trait fine-tuning；
只迁移 shape-compatible encoder weights。
```

## 当前实验状态

已完成：

```text
G2F 下载完整性检查
G2F-ZEAMAP SNP 重叠检查
G2F native pretraining tensor parser 编写
训练脚本 partial checkpoint loading 编写
小型 20-SNP dry run 验证
```

dry run 结果：

```text
genotype matrix: 2,193 x 20
dummy phenotype target: 2,193 x 1
dummy population covariate: 2,193 x 1
split: train 1,754 / val 219 / test 220
```

正在排队：

```text
job 8460577: g2f_native_pretrain
partition: q08
target output: data/deep_model/external_pretrain_v0/g2f_native_b73v5/
```

## 下一阶段成败标准

G2F 预训练后，必须和这些模型公平比较：

```text
ridge
ElasticNet
small MLP
ZEAMAP-only supervised SNPWindowFormer
ZEAMAP-only pretrain + fine-tune
G2F-pretrain + ZEAMAP fine-tune
```

最低可接受目标：

```text
G2F-pretrain + ZEAMAP fine-tune 的 test median Pearson 接近或超过 0.50。
G2F-pretrain + ZEAMAP fine-tune 的 test median R2 接近或超过 0.20。
```

较理想投稿目标：

```text
test median Pearson >= 0.55
test median R2 >= 0.25
oil traits 和部分 agronomic traits 有稳定提升
多 seed 后仍然成立
```

如果仍然低于 ridge，不能硬写成“深度模型更好”。那时论文应转成：

```text
公共玉米多组学数据上的模型基准和小样本深度学习边界分析。
```

## 统计和实验风险检查

| 风险 | 当前判断 | 处理方式 |
|---|---|---|
| 数据泄漏 | 中等风险 | G2F 只用于 genotype-only pretraining，不使用 ZEAMAP test trait |
| 坐标混用 | 高风险 | 不直接合并 SNP，只迁移模型权重 |
| 过拟合 | 高风险 | 多 seed、early stopping、ridge/ElasticNet 强基线 |
| 只看单次结果 | 高风险 | 后续必须重复 seed |
| 结果低于基线还强行包装 | 高风险 | 明确设置成败标准 |
| 外部数据 accession 重复 | 中等风险 | G2F tensor 完成后检查与 ZEAMAP accession 名称重叠 |
| 预训练任务和 trait prediction 不一致 | 中等风险 | 用 fine-tuning test metrics 判断是否真正转化 |
| 位置嵌入误迁移 | 已控制 | partial checkpoint loading 会跳过 shape mismatch |
| q08 资源排队 | 工程风险 | 已提交任务，等待调度 |
| GPU 显存占用别人任务 | 工程风险 | 后续按空闲显存选卡 |
| 结论外推过度 | 高风险 | 论文只声称 ZEAMAP/G2F 公共数据范围内的结果 |

## 当前审查结论

```text
实验设计合理，可以继续。
当前还没有最终模型结果，不能写最终论文结论。
最关键的下一步是完成 G2F native tensor，然后跑 G2F pretrain + ZEAMAP fine-tune。
```

## 2026-06-07 完成更新

q08 长时间没有资源后，G2F native tensor 构建任务已切换到 q07 并完成：

```text
old job: 8460577 on q08, cancelled
new job: 8460638 on q07, completed
elapsed: 00:09:39
max memory: about 1.25 GB
output: data/deep_model/external_pretrain_v0/g2f_native_b73v5/
```

完整性检查结果：

```text
genotype matrix: (2193, 437214) int8
target matrix: (2193, 1) float32
target mask: (2193, 1) bool, observed count 0
population covariate: (2193, 1) float32
accessions: 2193
variants: 437214
split counts: train 1754 / val 219 / test 220
manifest samples/variants matched matrix shape
```

登录节点 CPU smoke test 也完成：

```text
test package: 2,193 x 20
mode: pretrain
epochs: 1
test reconstruction loss: 0.354
```

这说明训练脚本可以读取 G2F 风格数据包。正式训练应在 GPU 节点运行。

新增 GPU 脚本：

```text
jobs/gpu_run_windowformer_g2f_native_pretrain.sh
jobs/gpu_run_windowformer_g2f_native_finetune.sh
```

更新后的审查结论：

```text
G2F native tensor 已完成。
下一步进入 G2F masked-genotype pretraining。
预训练完成后再做 ZEAMAP fine-tuning 和基线比较。
```

## 2026-06-07 GPU Pretraining Launch

G2F masked-genotype pretraining has been launched on the GPU node:

```text
node: gpu10
launcher PID: 60098
launcher log: logs/windowformer_g2f_native_pretrain_launcher_20260607_122354.log
training log: logs/windowformer_g2f_native_pretrain_20260607_122357.log
output directory: results/deep_model/windowformer_g2f_native_pretrain_v0/
```

Initial GPU selection:

```text
CUDA_VISIBLE_DEVICES=2,5
selection rule: free memory only, >=30 GB free
```

Observed early training:

```text
epoch 1: train_loss 0.7243 / val_loss 0.6068
epoch 7: train_loss 0.5658 / val_loss 0.5597
```

Interpretation:

```text
The external genotype pretraining job is running and the reconstruction loss is decreasing.
Final assessment should wait for completion, test loss, and subsequent ZEAMAP fine-tuning.
```
