#!/usr/bin/env bash
#SBATCH -J yumi_panzea_fetch
#SBATCH -p q08
#SBATCH -c 2
#SBATCH --mem=16G
#SBATCH -o logs/yumi_panzea_fetch_%j.out
#SBATCH -e logs/yumi_panzea_fetch_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

mkdir -p logs data/external/panzea/hapmap3/hmp321_agpv4

mamba run -n yumi python scripts/fetch_panzea_hapmap321_agpv4.py --download
mamba run -n yumi python scripts/inspect_external_genotype_downloads.py --root data/external
mamba run -n yumi python scripts/prepare_external_genotype_pretrain_inputs.py
