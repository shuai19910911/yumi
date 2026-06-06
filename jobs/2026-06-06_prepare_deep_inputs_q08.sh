#!/usr/bin/env bash
#SBATCH -p q08
#SBATCH -c 8
#SBATCH --mem=40G
#SBATCH -J yumi_prep_deep_inputs
#SBATCH -o logs/prepare_deep_inputs_%j.out
#SBATCH -e logs/prepare_deep_inputs_%j.err

set -euo pipefail
cd /home/user/zhangzhishuai/myhermes/yumi
mkdir -p logs data/deep_model/v0_1
mamba run -n yumi python scripts/prepare_zeamap_deep_learning_inputs.py \
  --processed-dir data/processed/v0_1 \
  --results-dir results/v0_1_baseline \
  --out-dir data/deep_model/v0_1
