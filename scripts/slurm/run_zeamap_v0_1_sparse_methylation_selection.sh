#!/usr/bin/env bash
#SBATCH -J yumi_sparse_meth
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -o logs/sparse_methylation_selection_%j.out
#SBATCH -e logs/sparse_methylation_selection_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mamba run -n yumi python scripts/run_zeamap_v0_1_sparse_methylation_selection.py
