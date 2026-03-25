#!/bin/bash

# Reference 
REF="/work/microbiome/users/kruthi/MAGs_Onehealth/dog_mags_list.txt"

# unmatched path files 
declare -A files
files=( ["Coelho_HQ"]="Coelho_unmatched_vs_shanghai_fastani.tsv"
        ["Coelho_MQ"]="Coelho_MQ_unmatched_vs_shanghai_fastani.tsv"
        ["Yarlagadda_HQ"]="Yarlagadda_HQ_unmatched_vs_shanghai_fastani.tsv"
        ["Yarlagadda_MQ"]="Yarlagadda_MQ_unmatched_vs_shanghai_fastani.tsv" )

# run FastANI
for cohort in "${!files[@]}"; do
    echo "Running FastANI for $cohort ..."
    fastANI \
        --ql "$cohort"_unmatched_paths.txt \
        --rl "$REF" \
        -o "${files[$cohort]}"
done

echo "FastANI runs completed!"
