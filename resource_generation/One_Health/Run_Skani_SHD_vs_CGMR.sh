#!/bin/bash
set -e

# Download GMR dataset (Dong et al. 2025)
# wget -O GMR_REP_6664MAGs.zip https://download.cncb.ac.cn/OMIX/OMIX006649/OMIX006649-01.zip
# unzip GMR_REP_6664MAGs.zip -d GMR_REP_6664MAGs

echo "Step 1: Generate species representative MAG list"

MIMAG="/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv"
MAG_DIR="/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs"
OUT="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/SHD_Species_Rep_MAGs_list.txt"

mkdir -p "$(dirname "$OUT")"

awk -F',' 'NR>1 && $2=="Yes" {print "'$MAG_DIR'/" $1}' "$MIMAG" > "$OUT"

echo "Total species representatives:"
wc -l "$OUT"
echo "Preview:"
head "$OUT"

echo "Step 2: Run skani (SHD vs GMR)"

CGMR="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/GMR_REP_6664MAGs/*.fasta"
ANI_OUT="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/SHD_Species_Rep_vs_Human_ani.tsv"

skani dist --ql "$OUT" -r $CGMR --min-af 15 -t 40 -o "$ANI_OUT"

echo "Done"
echo "Output: $ANI_OUT"
