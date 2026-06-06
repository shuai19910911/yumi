#!/usr/bin/env bash
#SBATCH -J yumi_g2f_fetch
#SBATCH -p q08
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -o logs/yumi_g2f_fetch_%j.out
#SBATCH -e logs/yumi_g2f_fetch_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

mkdir -p logs data/external/g2f/genotypic_2014_2023

mamba run -n yumi python scripts/fetch_g2f_genotype_resources.py --download
mamba run -n yumi python scripts/inspect_external_genotype_downloads.py --root data/external
mamba run -n yumi python scripts/prepare_external_genotype_pretrain_inputs.py
