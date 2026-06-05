#!/usr/bin/env bash
#SBATCH -J yumi_pop_assoc
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -o logs/population_corrected_association_%j.out
#SBATCH -e logs/population_corrected_association_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mamba run -n yumi python scripts/run_zeamap_v0_1_population_corrected_association.py
