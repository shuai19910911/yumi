#!/usr/bin/env bash
#SBATCH -J yumi_v01_baseline
#SBATCH -p q07
#SBATCH -c 8
#SBATCH --mem=32G
#SBATCH -o logs/v0_1_baseline.%j.out
#SBATCH -e logs/v0_1_baseline.%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mkdir -p logs results/v0_1_baseline data/processed/v0_1/splits

mamba run -n yumi python scripts/run_zeamap_v0_1_baseline.py --n-pcs 100
