#!/usr/bin/env bash
#SBATCH -J yumi_v01_light
#SBATCH -p q07
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -o logs/v0_1_lightweight.%j.out
#SBATCH -e logs/v0_1_lightweight.%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mkdir -p logs results/v0_1_baseline

mamba run -n yumi python scripts/run_zeamap_v0_1_lightweight_models.py
