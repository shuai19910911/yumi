# 2026-06-06 GPU run guide

## 2026-06-07 推荐主任务：G2F 外部预训练

G2F 2014-2023 genotypic data 已经下载完成。因为 G2F 是 B73 v5 坐标，ZEAMAP 是 AGPv4 坐标，二者不能直接合并 SNP 列。

现在推荐的做法是：

```text
G2F 原生 SNP 空间做 masked-genotype pretraining
ZEAMAP 原生 SNP 空间做 trait fine-tuning
只迁移形状一致的 encoder 权重
```

CPU 转换任务已经完成：

```text
job 8460638: g2f_native_pretrain
partition: q07
state: COMPLETED
输出目录：data/deep_model/external_pretrain_v0/g2f_native_b73v5/
```

在 GPU 节点推荐直接运行：

```bash
bash jobs/gpu_run_windowformer_g2f_native_pretrain.sh
```

这个脚本只按空闲显存选卡，默认要求 2 张卡各有至少 30GB 空闲显存。

G2F 预训练完成后运行 ZEAMAP 微调：

```bash
bash jobs/gpu_run_windowformer_g2f_native_finetune.sh
```

等价的手动 G2F 外部预训练命令：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/external_pretrain_v0/g2f_native_b73v5 \
  --out-dir results/deep_model/windowformer_g2f_native_pretrain_v0 \
  --mode pretrain \
  --epochs 120 \
  --batch-size 16 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6 \
  --amp
```

然后迁移到 ZEAMAP 微调：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_g2f_native_finetune_v0_1 \
  --mode finetune \
  --pretrained-checkpoint results/deep_model/windowformer_g2f_native_pretrain_v0/best.pt \
  --epochs 300 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6 \
  --amp
```

训练脚本会自动跳过形状不一致的权重，并在输出目录写：

```text
checkpoint_load_report.json
```

## 当前环境状态

`yumi` 环境已经安装 GPU 训练需要的核心包：

```text
torch 2.5.1+cu121
CUDA build 12.1
tqdm
tensorboard
einops
numpy / pandas / scipy / scikit-learn / pyarrow
matplotlib
python-docx / reportlab
```

登录节点检测结果：

```text
torch.cuda.is_available() = False
torch.cuda.device_count() = 0
```

这是正常的，因为当前是在登录节点，不是 GPU 节点。

## GPU 节点登录后先做检查

登录 GPU 节点：

```bash
ssh 12.12.12.210
```

不要把密码写入脚本。

登录后进入项目目录并检查 GPU：

```bash
cd /home/user/zhangzhishuai/myhermes/yumi
mamba run -n yumi python - <<'PY'
import torch
print("torch", torch.__version__)
print("cuda build", torch.version.cuda)
print("cuda available", torch.cuda.is_available())
print("device count", torch.cuda.device_count())
for i in range(torch.cuda.device_count()):
    print(i, torch.cuda.get_device_name(i))
PY
```

如果这里显示 2 张 A100，就可以开始训练。

## 输入数据已经准备好

CPU q08 作业已经生成：

```text
data/deep_model/v0_1/
```

核心文件：

```text
genotype_samples_by_variants.int8.npy   461 x 199,856
phenotype_targets.float32.npy           461 x 66
phenotype_observed_mask.bool.npy        461 x 66
population_covariates.float32.npy       461 x 6
splits.tsv                              5 seeds
manifest.json
```

## 自动选卡运行

登录 GPU 节点后推荐直接运行：

```bash
cd /home/user/zhangzhishuai/myhermes/yumi
bash jobs/gpu_run_windowformer_supervised.sh
```

脚本会自动选择显存空闲大于 30GB 的 GPU。
同时要求 GPU 利用率不高于 20%，避免占用别人正在跑任务的卡。

建议训练前先检查：

```bash
bash jobs/gpu_check_available_cards.sh
```

如果只想用 1 张卡：

```bash
N_GPUS=1 BATCH_SIZE=16 bash jobs/gpu_run_windowformer_supervised.sh
```

## 手动 GPU 任务：监督训练

先跑这个，确认深度模型能不能接近或超过 ridge：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_supervised_v0_1 \
  --mode supervised \
  --epochs 300 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6 \
  --amp
```

输出：

```text
results/deep_model/windowformer_supervised_v0_1/best.pt
results/deep_model/windowformer_supervised_v0_1/history.json
results/deep_model/windowformer_supervised_v0_1/test_metrics.json
```

## 第二条 GPU 任务：自监督预训练

如果监督模型不明显超过 ridge，就跑 masked-genotype pretraining：

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_pretrain_v0_1 \
  --mode pretrain \
  --epochs 500 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6 \
  --amp
```

## 第三条 GPU 任务：预训练后微调

```bash
CUDA_VISIBLE_DEVICES=1,2 mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_finetune_v0_1 \
  --mode finetune \
  --pretrained-checkpoint results/deep_model/windowformer_pretrain_v0_1/best.pt \
  --epochs 300 \
  --batch-size 32 \
  --window-size 256 \
  --d-model 192 \
  --layers 6 \
  --nhead 6 \
  --amp
```

## 训练结果怎么判断

强基线是：

```text
genotype_population_ridge
median Pearson = 0.498
median R2 = 0.204
```

深度模型最低目标：

```text
median Pearson > 0.50
median R2 > 0.20
```

比较理想的投稿目标：

```text
median Pearson >= 0.55
median R2 >= 0.25
oil traits 继续保持明显优势
```

如果深度模型低于 ridge，不要硬写成“深度模型更好”。下一步应该下载 G2F/Panzea，用更多 genotype 做预训练。
