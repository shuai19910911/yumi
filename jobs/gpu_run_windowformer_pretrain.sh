#!/usr/bin/env bash
# Run this script after logging into the GPU node.
# It selects GPUs with enough free memory and launches masked-genotype pretraining.

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mkdir -p results/deep_model/windowformer_pretrain_v0_1 logs

MIN_FREE_MB="${MIN_FREE_MB:-30000}"
N_GPUS="${N_GPUS:-2}"
BATCH_SIZE="${BATCH_SIZE:-32}"
WINDOW_SIZE="${WINDOW_SIZE:-256}"
D_MODEL="${D_MODEL:-192}"
LAYERS="${LAYERS:-6}"
NHEAD="${NHEAD:-6}"
EPOCHS="${EPOCHS:-500}"

GPU_IDS="$(
  nvidia-smi --query-gpu=index,memory.free --format=csv,noheader,nounits \
  | awk -F, -v min_free="${MIN_FREE_MB}" '{gsub(/ /,"",$1); gsub(/ /,"",$2); if ($2 >= min_free) print $1}' \
  | head -n "${N_GPUS}" \
  | paste -sd, -
)"

FOUND="$(printf '%s' "${GPU_IDS}" | awk -F, '{print NF}')"
if [[ -z "${GPU_IDS}" || "${FOUND}" -lt "${N_GPUS}" ]]; then
  echo "Need ${N_GPUS} GPU(s) with >= ${MIN_FREE_MB} MB free memory, but found: ${GPU_IDS:-none}" >&2
  nvidia-smi >&2
  exit 2
fi

echo "Using GPUs: ${GPU_IDS}"
nvidia-smi

CUDA_VISIBLE_DEVICES="${GPU_IDS}" mamba run -n yumi python scripts/train_snp_window_transformer_multitask.py \
  --data-dir data/deep_model/v0_1 \
  --out-dir results/deep_model/windowformer_pretrain_v0_1 \
  --mode pretrain \
  --epochs "${EPOCHS}" \
  --batch-size "${BATCH_SIZE}" \
  --window-size "${WINDOW_SIZE}" \
  --d-model "${D_MODEL}" \
  --layers "${LAYERS}" \
  --nhead "${NHEAD}" \
  --amp \
  2>&1 | tee logs/windowformer_pretrain_$(date +%Y%m%d_%H%M%S).log
