#Step 1 Download the data

spire --study download mags Coelho_2018_dog -o Coelho_2018_dog/
spire --study download mags Wang_2019_dogs -o Wang_2019_dogs/
spire --study download mags Yarlagadda_2022_global_dog -o Yarlagadda_2022_global_dog/
spire --study download mags Allaway_2020_dogs -o Allaway_2020_dogs/
spire --study download mags Liu_2021_Canidae -o Liu_2021_Canidae/
spire --study download mags Xu_2019_dogs -o Xu_2019_dogs/
spire --study download mags Worsley-Tonks_2020_dog -o Worsley-Tonks_2020_dog/

#Step 2 Create Skani Lists
cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts

mkdir -p Skani_lists

for cohort in */; do
  name=$(basename "$cohort")

  # skip non-cohort folders
  if [[ "$name" == "Skani_lists" || "$name" == "logs" ]]; then
    continue
  fi

  echo "Processing $name"
  find "$cohort" -name "*.fa*" > "Skani_lists/${name}_MAGs_list.txt"
done

#STEP 3
#LIST FOR THE SHD DATA
#!/bin/bash

SHD_DIR="/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs"
OUT="/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists/SHD_ALL_MAGs_list.txt"

mkdir -p "$(dirname "$OUT")"

#step 4
#gunzip the external cohorts data

cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts
find . -name "*.fa.gz" -exec gunzip {} \;

find "$SHD_DIR" -name "*.fna*" > "$OUT"

wc -l "$OUT"
head "$OUT"

#step 5
#regenerating the lists 
cd /work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists

rm *_MAGs_list.txt

cd ..

mkdir -p Skani_lists

for cohort in */; do
  name=$(basename "$cohort")

  if [[ "$name" == "Skani_lists" ]]; then
    continue
  fi

  find "$cohort" -name "*.fa*" > "Skani_lists/${name}_MAGs_list.txt"
done
