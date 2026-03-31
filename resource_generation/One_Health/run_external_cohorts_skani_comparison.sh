#Step 1 Download the data

spire --study download mags Coelho_2018_dog -o Coelho_2018_dog/
spire --study download mags Wang_2019_dogs -o Wang_2019_dogs/
spire --study download mags Yarlagadda_2022_global_dog -o Yarlagadda_2022_global_dog/
spire --study download mags Allaway_2020_dogs -o Allaway_2020_dogs/
spire --study download mags Liu_2021_Canidae -o Liu_2021_Canidae/
spire --study download mags Xu_2019_dogs -o Xu_2019_dogs/
spire --study download mags Worsley-Tonks_2020_dog -o Worsley-Tonks_2020_dog/

#Step 2 Create Skani Lists for external cohorts
BASE="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts"
cd "$BASE/Skani_lists"

for cohort in Allaway_2020_dogs Coelho_2018_dog Liu_2021_Canidae Wang_2019_dogs Worsley-Tonks_2020_dog Xu_2019_dogs Yarlagadda_2022_global_dog; do
    find "$BASE/$cohort" -type f -name "*.fa" > "${cohort}_MAGs_list.txt"
done

#STEP 3
#LIST FOR THE SHD DATA
#!/bin/bash

MIMAG="/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv"
MAG_DIR="/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs"
OUT="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists/SHD_All_MAGs_list.txt"

mkdir -p "$(dirname "$OUT")"

awk -F',' 'NR>1 {print "'$MAG_DIR'/" $1}' "$MIMAG" > "$OUT"

echo "Total MAGs:"
wc -l "$OUT"

echo "Preview:"
head "$OUT"

#step 4
#gunzip the external cohorts data

cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts
find . -name "*.fa.gz" -exec gunzip {} \;

find "$SHD_DIR" -name "*.fna*" > "$OUT"

wc -l "$OUT"
head "$OUT"

#step 5
#run skani

#!/usr/bin/env bash

BASE="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists"
QUERY="$BASE/SHD_All_MAGs_list.txt"

RESULTS="$BASE/Skani_results"
LOGS="$RESULTS/Logs"
THREADS=40

mkdir -p "$RESULTS" "$LOGS"

for REF in "$LISTS"/*_MAGs_list.txt; do
    REF_NAME=$(basename "$REF")
    [ "$REF_NAME" = "SHD_All_MAGs_list.txt" ] && continue

    COHORT="${REF_NAME%_MAGs_list.txt}"
    OUT="$RESULTS/${COHORT}_vs_SHD_ani.tsv"
    LOG="$LOGS/${COHORT}.log"

    echo "Running skani for: $COHORT"

    skani dist \
        --ql "$QUERY" \
        --rl "$REF" \
        -t "$THREADS" \
        -o "$OUT" \
        > "$LOG" 2>&1

    if [ $? -eq 0 ]; then
        echo "Finished: $COHORT"
    else
        echo "Failed: $COHORT (see $LOG)"
    fi
done

echo "All skani jobs completed."

#step 6
#download spire genome metadata file
cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists
wget -O spire_v1_genome_metadata.tsv.gz \
https://swifter.embl.de/~fullam/spire/metadata/spire_v1_genome_metadata.tsv.gz

# Step 3: Unzip
gunzip -f spire_v1_genome_metadata.tsv.gz

# Step 4: Verify
ls -lh spire_v1_genome_metadata.tsv
head spire_v1_genome_metadata.tsv
