#Step 1 Download the data

spire --study download mags Coelho_2018_dog -o Coelho_2018_dog/
spire --study download mags Wang_2019_dogs -o Wang_2019_dogs/
spire --study download mags Yarlagadda_2022_global_dog -o Yarlagadda_2022_global_dog/
spire --study download mags Allaway_2020_dogs -o Allaway_2020_dogs/
spire --study download mags Liu_2021_Canidae -o Liu_2021_Canidae/
spire --study download mags Xu_2019_dogs -o Xu_2019_dogs/
spire --study download mags Worsley-Tonks_2020_dog -o Worsley-Tonks_2020_dog/

#STEP 2 gunzip and create the lists for SkaANI input
#!/bin/bash
set -euo pipefail

BASE="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts"
LIST_DIR="$BASE/Skani_lists"
MIMAG="/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv"
MAG_DIR="/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs"

mkdir -p "$LIST_DIR"

echo "Unzipping external cohort genomes..."
find "$BASE" -name "*.fa.gz" -exec gunzip {} \;

create_list () {
    local input_dir="$1"
    local output_file="$2"
    find "$input_dir" -type f -name "*.fa" > "$output_file"
    echo "$(basename "$output_file"): $(wc -l < "$output_file") files"
}

echo "Creating Skani lists for external cohorts..."
for cohort in Allaway_2020_dogs Coelho_2018_dog Liu_2021_Canidae Wang_2019_dogs Worsley-Tonks_2020_dog Xu_2019_dogs Yarlagadda_2022_global_dog; do
    create_list "$BASE/$cohort" "$LIST_DIR/${cohort}_MAGs_list.txt"
done

echo "Creating Skani list for SHD MAGs..."
awk -F',' -v dir="$MAG_DIR" 'NR>1 {print dir "/" $1}' "$MIMAG" > "$LIST_DIR/SHD_All_MAGs_list.txt"

echo "SHD_All_MAGs_list.txt: $(wc -l < "$LIST_DIR/SHD_All_MAGs_list.txt") files"
head "$LIST_DIR/SHD_All_MAGs_list.txt"


#step 3
#download spire genome metadata file
cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists
wget -O spire_v1_genome_metadata.tsv.gz \
https://swifter.embl.de/~fullam/spire/metadata/spire_v1_genome_metadata.tsv.gz

# Unzip
gunzip -f spire_v1_genome_metadata.tsv.gz

#  Verify
ls -lh spire_v1_genome_metadata.tsv
head spire_v1_genome_metadata.tsv


#STEP 4
#run skani
#!/usr/bin/env bash
set -euo pipefail

BASE="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists"
QUERY="$BASE/SHD_All_MAGs_list.txt"

QUAL="$BASE/Quality_MAGs"

RESULTS="$BASE/Skani_results"
LOGS="$RESULTS/Logs"

THREADS=40

mkdir -p "$RESULTS" "$LOGS" "$QUAL/Skani_Quality_Results"

COHORTS=(
  Coelho_2018_dog
  Wang_2019_dogs
  Yarlagadda_2022_global_dog
  Allaway_2020_dogs
  Liu_2021_Canidae
  Xu_2019_dogs
  Worsley-Tonks_2020_dog
)

echo "===== STEP 3: ALL MAGs vs SHD ====="
for cohort in "${COHORTS[@]}"; do

    REF="$BASE/${cohort}_MAGs_list.txt"
    OUT="$RESULTS/${cohort}_vs_SHD_ani.tsv"
    LOG="$LOGS/${cohort}.log"

    if [ ! -s "$REF" ]; then
        echo "Skipping $REF"
        continue
    fi

    echo "Running skani: $cohort (ALL MAGs)"

    skani dist \
        --ql "$QUERY" \
        --rl "$REF" \
        -t "$THREADS" \
        -o "$OUT" \
        > "$LOG" 2>&1

done


echo "===== STEP 5: HQ & MQ ====="
for cohort in "${COHORTS[@]}"; do
  for quality in HQ MQ; do

    REF="$QUAL/${cohort}_${quality}_list.txt"
    OUT="$QUAL/Skani_Quality_Results/${cohort}_${quality}_ani.tsv"

    if [ ! -s "$REF" ]; then
      echo "Skipping $REF"
      continue
    fi

    echo "Running skani: $cohort $quality"

    skani dist \
      --ql "$QUERY" \
      --rl "$REF" \
      -t "$THREADS" \
      -o "$OUT"

  done
done


echo "===== STEP 6: ALL (quality-filtered lists) ====="
for cohort in "${COHORTS[@]}"; do

    REF="$QUAL/${cohort}_ALL_list.txt"
    OUT="$QUAL/Skani_Quality_Results/${cohort}_ALL_ani.tsv"

    if [ ! -s "$REF" ]; then
        echo "Skipping $REF"
        continue
    fi

    echo "Running skani: $cohort ALL"

    skani dist \
        --ql "$QUERY" \
        --rl "$REF" \
        -t "$THREADS" \
        -o "$OUT"

done

echo "===== ALL SKANI RUNS COMPLETED ====="
