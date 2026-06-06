#!/usr/bin/env bash
set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

source /home/user/zhangzhishuai/.bashrc
mamba run -n yumi python scripts/inspect_external_genotype_downloads.py \
  --root data/external \
  --out-tsv data/external/external_genotype_inventory.tsv \
  --out-json data/external/external_genotype_inventory.json
