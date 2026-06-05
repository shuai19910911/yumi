#!/usr/bin/env bash
#SBATCH -J yumi_gemma_array
#SBATCH -c 8
#SBATCH --mem=80G
#SBATCH -o logs/gemma_lmm_array_%A_%a.out
#SBATCH -e logs/gemma_lmm_array_%A_%a.err

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi

GEMMA_IN="data/processed/v0_1/gemma_gwas_v0_1"
GEMMA_OUT="results/v0_1_baseline/gemma_v0_1"
PENDING="${GEMMA_IN}/phenotype_manifest.pending.tsv"
YUMI_BIN="/home/user/zhangzhishuai/.local/share/mamba/envs/yumi/bin"

"${YUMI_BIN}/python" scripts/prepare_zeamap_v0_1_gemma_inputs.py

mkdir -p "${GEMMA_OUT}"

if [[ ! -s "${GEMMA_OUT}/zeamap_v0_1_kinship.cXX.txt" ]]; then
  first_pheno="$(awk -F '\t' 'NR==2 {print $2}' "${GEMMA_IN}/phenotype_manifest.tsv")"
  "${YUMI_BIN}/gemma" \
    -g "${GEMMA_IN}/zeamap_v0_1_filtered_snps.bimbam.txt" \
    -p "${GEMMA_IN}/${first_pheno}" \
    -a "${GEMMA_IN}/zeamap_v0_1_filtered_snps.annotation.txt" \
    -gk 1 \
    -outdir "${GEMMA_OUT}" \
    -o zeamap_v0_1_kinship
fi

trait_line="$(sed -n "$((SLURM_ARRAY_TASK_ID + 1))p" "${PENDING}")"
IFS=$'\t' read -r trait phenotype_file non_missing <<< "${trait_line}"
safe_trait="${trait//\//_}"
safe_trait="${safe_trait//:/_}"

if [[ -s "${GEMMA_OUT}/${safe_trait}.gemma_lmm.assoc.txt" ]]; then
  echo "Already complete: ${safe_trait}"
  exit 0
fi

"${YUMI_BIN}/gemma" \
  -g "${GEMMA_IN}/zeamap_v0_1_filtered_snps.bimbam.txt" \
  -p "${GEMMA_IN}/${phenotype_file}" \
  -a "${GEMMA_IN}/zeamap_v0_1_filtered_snps.annotation.txt" \
  -c "${GEMMA_IN}/covariates.txt" \
  -k "${GEMMA_OUT}/zeamap_v0_1_kinship.cXX.txt" \
  -lmm 4 \
  -outdir "${GEMMA_OUT}" \
  -o "${safe_trait}.gemma_lmm"
