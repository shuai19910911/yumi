# 2026-06-06 SNPWindowFormer compute estimate

## 当前训练数据

```text
samples: 461
train/val/test per split: 323 / 69 / 69
SNPs: 199,856
window size: 256 SNPs
window tokens: 781
traits: 66
population covariates: 6
```

## 推荐首轮配置

```text
model: SNPWindowFormer
d_model: 192
layers: 6
nhead: 6
global batch size: 32
GPUs: 2 x A100 40G
AMP: on
```

## 显存估算

粗略估算，2 卡 DataParallel 时每张卡处理 16 个样本：

```text
embedding activation per GPU: ~2.3 GB
attention matrix per layer per GPU: ~0.22 GB
rough training VRAM per GPU: ~12-17 GB
```

考虑 PyTorch 临时张量、优化器状态、DataParallel 开销，实际建议：

```text
每张 GPU 至少空闲 30 GB
```

如果只有一张 A100 40G 空闲：

```bash
N_GPUS=1 BATCH_SIZE=16 bash jobs/gpu_run_windowformer_supervised.sh
```

如果显存不足：

```bash
N_GPUS=1 BATCH_SIZE=8 D_MODEL=160 LAYERS=4 bash jobs/gpu_run_windowformer_supervised.sh
```

## 时间估算

每个 epoch 约：

```text
batch size 32: 11 train steps
batch size 16: 21 train steps
```

因为样本数很小，监督训练的主要成本不是 step 数，而是每一步的 SNP window embedding 和 Transformer attention。

经验估计：

```text
supervised 300 epochs: 0.5-2 小时
pretrain 500 epochs: 1-4 小时
finetune 300 epochs: 0.5-2 小时
```

真实时间以 GPU 节点日志为准。

## 自动选卡脚本

登录 GPU 节点后运行：

```bash
cd /home/user/zhangzhishuai/myhermes/yumi
bash jobs/gpu_run_windowformer_supervised.sh
```

脚本会自动选择显存空闲大于 30GB 的 GPU。
同时要求 GPU 利用率不高于 20%，避免选择“显存还剩很多但别人正在跑”的卡。

只检查卡状态、不启动训练：

```bash
bash jobs/gpu_check_available_cards.sh
```

如果要强制 1 张卡：

```bash
N_GPUS=1 BATCH_SIZE=16 bash jobs/gpu_run_windowformer_supervised.sh
```

如果集群上卡比较紧张，可以提高空闲显存阈值：

```bash
MIN_FREE_MB=35000 MAX_UTIL=10 bash jobs/gpu_run_windowformer_supervised.sh
```

如果监督训练结果不超过 ridge，再跑：

```bash
bash jobs/gpu_run_windowformer_pretrain.sh
bash jobs/gpu_run_windowformer_finetune.sh
```

## 当前限制

我在登录节点无法免密 SSH 到 `12.12.12.210`：

```text
Permission denied (publickey,password)
```

因此不能安全地替你自动登录 GPU 节点。不要把密码写进脚本。你登录后运行上面的脚本即可。
