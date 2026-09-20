#!/usr/bin/env bash
# Run every "core" baseline the reviewer asked for, unattended, resumable.
#   cd binary-classifier && nohup bash baselines/run_all.sh > baselines_run_all.log 2>&1 &
# Env overrides: DEVICE=cuda:1  OUT=/path  CACHE=/path  EXTRA_ARGS="--epochs 2"  PY=python
set -uo pipefail
cd "$(dirname "$0")/.."
PY="${PY:-python}"
OUT="${OUT:-$(git rev-parse --show-toplevel 2>/dev/null || echo ..)/results/classifier-results-baselines/evaluation_results}"
CACHE="${CACHE:-$HOME/.cache/cbrs-baselines}"
DEVICE="${DEVICE:-auto}"
EXTRA_ARGS="${EXTRA_ARGS:-}"
COMMON=(--out "$OUT" --cache-dir "$CACHE" --device "$DEVICE")

echo "[run_all] $(date)  out=$OUT cache=$CACHE device=$DEVICE extra='$EXTRA_ARGS'"
$PY -m baselines.run --tags core --prefetch                          || echo "[run_all] prefetch had errors (continuing)"
$PY -m baselines.run --tags lex fasttext "${COMMON[@]}"              || true   # CPU, minutes
$PY -m baselines.run --tags emb "${COMMON[@]}" $EXTRA_ARGS           || true   # GPU, ~minutes per model
$PY -m baselines.run --tags ft --baseline distilbert_multilingual_ft "${COMMON[@]}" $EXTRA_ARGS || true  # GPU, core + sanity
$PY -m baselines.aggregate --include-paper
echo "[run_all] finished $(date)"
