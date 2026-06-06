#!/usr/bin/env bash
# Wait for suitable GPU cards, then launch supervised SNPWindowFormer.
# Intended to be started on the GPU node with nohup/tmux.

set -euo pipefail

cd /home/user/zhangzhishuai/myhermes/yumi
mkdir -p logs

CHECK_INTERVAL_SEC="${CHECK_INTERVAL_SEC:-300}"
MAX_WAIT_HOURS="${MAX_WAIT_HOURS:-24}"

START_TS="$(date +%s)"
MAX_WAIT_SEC="$((MAX_WAIT_HOURS * 3600))"

echo "[$(date)] Waiting for available GPU(s)."
echo "Policy: N_GPUS=${N_GPUS:-2}, MIN_FREE_MB=${MIN_FREE_MB:-30000}, MAX_UTIL=${MAX_UTIL:-20}, BATCH_SIZE=${BATCH_SIZE:-32}"

while true; do
  set +e
  bash jobs/gpu_run_windowformer_supervised.sh
  status=$?
  set -e
  if [[ "${status}" == "0" ]]; then
    echo "[$(date)] Training finished successfully."
    exit 0
  fi

  now="$(date +%s)"
  elapsed="$((now - START_TS))"
  if [[ "${status}" != "2" ]]; then
    echo "[$(date)] Launcher failed with non-availability exit code ${status}; stop waiting." >&2
    exit "${status}"
  fi
  if (( elapsed >= MAX_WAIT_SEC )); then
    echo "[$(date)] Reached MAX_WAIT_HOURS=${MAX_WAIT_HOURS}; stop waiting." >&2
    exit 2
  fi
  echo "[$(date)] No suitable GPU yet. Sleep ${CHECK_INTERVAL_SEC}s."
  sleep "${CHECK_INTERVAL_SEC}"
done
