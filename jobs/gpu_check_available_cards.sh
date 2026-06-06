#!/usr/bin/env bash
# Check GPU status on the GPU node without launching training.

set -euo pipefail

MIN_FREE_MB="${MIN_FREE_MB:-30000}"
MAX_UTIL="${MAX_UTIL:-20}"

if ! command -v nvidia-smi >/dev/null 2>&1; then
  echo "nvidia-smi not found. Run this on the GPU node." >&2
  exit 1
fi

echo "Full GPU status:"
nvidia-smi
echo

echo "Card-level summary:"
nvidia-smi --query-gpu=index,name,memory.total,memory.used,memory.free,utilization.gpu --format=csv,noheader,nounits \
  | awk -F, -v min_free="${MIN_FREE_MB}" -v max_util="${MAX_UTIL}" '
    BEGIN {
      printf "%-6s %-24s %-10s %-10s %-10s %-8s %-12s\n", "GPU", "Name", "TotalMB", "UsedMB", "FreeMB", "Util%", "Status"
    }
    {
      for (i=1; i<=NF; i++) gsub(/^ +| +$/, "", $i)
      status = ($5 >= min_free && $6 <= max_util) ? "AVAILABLE" : "BUSY/SKIP"
      printf "%-6s %-24s %-10s %-10s %-10s %-8s %-12s\n", $1, $2, $3, $4, $5, $6, status
    }
  '
echo

echo "Compute processes:"
nvidia-smi --query-compute-apps=gpu_uuid,pid,process_name,used_memory --format=csv,noheader,nounits || true

