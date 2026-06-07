#!/usr/bin/env bash
#SBATCH -p q07
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -J g2f_native_pretrain
#SBATCH -o logs/2026-06-07_prepare_g2f_native_pretrain_q07.%j.out
#SBATCH -e logs/2026-06-07_prepare_g2f_native_pretrain_q07.%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

mamba run -n yumi python scripts/prepare_g2f_native_pretrain_inputs.py \
  --vcf data/external/g2f/genotypic_2014_2023/inbreds_G2F_2014-2023_437k.vcf \
  --out-dir data/deep_model/external_pretrain_v0/g2f_native_b73v5 \
  --split-seed 20260605 \
  --chunk-variants 512
