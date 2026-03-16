#!/usr/bin/env python3
import pandas as pd
import glob

# skani results
df = pd.read_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/dog_vs_human_ani.tsv', sep='\t')
print(f"Total hits: {len(df)}")

# Count total MAGs
total_dog = len(glob.glob('/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/*.fna.gz'))
total_human = len(glob.glob('/work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta'))
print(f"\nTotal dog MAGs : {total_dog}")
print(f"Total human MAGs: {total_human}")

# Filter for 95% ANI 
shared = df[df['ANI'] >= 95].copy()
print(f"\nHits at >= 95% ANI: {len(shared)}")

# Extract human MAG names
shared['human_mag'] = shared['Ref_file'].str.extract(r'(GT_GMRSGB\d+|LT_GMRSGB\d+)')

# Unique dog MAGs with human counterpart
unique_dog = shared['Query_file'].nunique()

# Unique human MAGs matched
unique_human = shared['human_mag'].nunique()

# ANI distribution
print(f"\nANI distribution of shared hits:")
print(shared['ANI'].describe())

# Top 20 shared human MAGs
print(f"\nTop 20 most shared human MAGs:")
print(shared['human_mag'].value_counts().head(20))

# Summary
print(f"\n SUMMARY ")
print(f"Total dog MAGs in analysis: {total_dog}")
print(f"Total human MAGs in catalog: {total_human}")
print(f"Dog MAGs WITH human counterpart (>=95% ANI): {unique_dog} ({unique_dog/total_dog*100:.1f}%)")
print(f"Dog MAGs WITHOUT human counterpart: {total_dog - unique_dog} ({(total_dog-unique_dog)/total_dog*100:.1f}%)")
print(f"Human MAGs matched by dog: {unique_human} ({unique_human/total_human*100:.1f}%)")
print(f"Human MAGs NOT matched by dog: {total_human - unique_human} ({(total_human-unique_human)/total_human*100:.1f}%)")
