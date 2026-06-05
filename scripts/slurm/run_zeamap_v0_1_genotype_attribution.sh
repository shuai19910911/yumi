#!/usr/bin/env bash
#SBATCH -J yumi_geno_attr
#SBATCH -c 8
#SBATCH --mem=48G
#SBATCH -o logs/genotype_attribution_%j.out
#SBATCH -e logs/genotype_attribution_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mamba run -n yumi python scripts/run_zeamap_v0_1_genotype_attribution.py
