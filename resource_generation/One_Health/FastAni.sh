#!/usr/bin/env bash
set -euo pipefail

REF="/work/microbiome/users/kruthi/MAGs_Onehealth/dog_mags_list.txt"
QUERY_DIR="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/FastANI/Unmatched_MAGs"
OUTDIR="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/FastANI/FastANI_results"
LOGDIR="$OUTDIR/logs"

mkdir -p "$OUTDIR" "$LOGDIR"

# Use fewer threads per FastANI job to avoid memory kills.
THREADS=8

for QUERY in "$QUERY_DIR"/*_unmatched_paths.txt; do
    [ -e "$QUERY" ] || continue

    base="$(basename "$QUERY" _unmatched_paths.txt)"
    OUT="$OUTDIR/${base}_vs_shanghai_fastani.tsv"
    LOG="$LOGDIR/${base}.log"

    echo "Running FastANI for $base with $THREADS threads"

    fastANI \
        --ql "$QUERY" \
        --rl "$REF" \
        -t "$THREADS" \
        -o "$OUT" \
        > "$LOG" 2>&1

    echo "Done: $base"
done

echo "FastANI runs completed."
