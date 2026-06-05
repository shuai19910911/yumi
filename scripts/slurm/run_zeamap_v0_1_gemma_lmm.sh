#!/usr/bin/env bash
#SBATCH -J yumi_gemma
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -o logs/gemma_lmm_%j.out
#SBATCH -e logs/gemma_lmm_%j.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

mamba run -n yumi python scripts/prepare_zeamap_v0_1_gemma_inputs.py

GEMMA_IN="data/processed/v0_1/gemma_gwas_v0_1"
GEMMA_OUT="results/v0_1_baseline/gemma_v0_1"
mkdir -p "${GEMMA_OUT}"

mamba run -n yumi gemma \
  -g "${GEMMA_IN}/zeamap_v0_1_filtered_snps.bimbam.txt" \
  -p "${GEMMA_IN}/$(awk -F '\t' 'NR==2 {print $2}' "${GEMMA_IN}/phenotype_manifest.tsv")" \
  -a "${GEMMA_IN}/zeamap_v0_1_filtered_snps.annotation.txt" \
  -gk 1 \
  -outdir "${GEMMA_OUT}" \
  -o zeamap_v0_1_kinship

while IFS=$'\t' read -r trait phenotype_file non_missing; do
  if [[ "${trait}" == "trait" ]]; then
    continue
  fi
  safe_trait="${trait//\//_}"
  safe_trait="${safe_trait//:/_}"
  mamba run -n yumi gemma \
    -g "${GEMMA_IN}/zeamap_v0_1_filtered_snps.bimbam.txt" \
    -p "${GEMMA_IN}/${phenotype_file}" \
    -a "${GEMMA_IN}/zeamap_v0_1_filtered_snps.annotation.txt" \
    -c "${GEMMA_IN}/covariates.txt" \
    -k "${GEMMA_OUT}/zeamap_v0_1_kinship.cXX.txt" \
    -lmm 4 \
    -outdir "${GEMMA_OUT}" \
    -o "${safe_trait}.gemma_lmm"
done < "${GEMMA_IN}/phenotype_manifest.tsv"
