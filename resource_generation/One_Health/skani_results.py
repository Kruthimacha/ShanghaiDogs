#!/usr/bin/env python3
import pandas as pd
import glob

# skani results
df = pd.read_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/dog_vs_human_ani.tsv', sep='\t')

# Count total MAGs
total_dog = len(glob.glob('/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/*.fna.gz'))
total_human = len(glob.glob('/work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta'))

# Filter for 95% ANI 
shared = df[df['ANI'] >= 95].copy()

# Extract names
shared['human_mag'] = shared['Ref_file'].str.extract(r'(GT_GMRSGB\d+|LT_GMRSGB\d+)')
matched_mags = set(shared['Query_file'].str.extract(r'(SHD1_\d+\.fna\.gz)')[0].dropna())
all_mags = set([f.split('/')[-1] for f in glob.glob('/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/*.fna.gz')])
dog_specific = all_mags - matched_mags

# Unique dog MAGs with human counterpart
unique_dog = shared['Query_file'].nunique()
unique_human = shared['human_mag'].nunique()

# Load MIMAG for taxonomy
mimag = pd.read_csv('/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv')
mimag_dog = mimag[mimag['Bin ID'].isin(dog_specific)].copy()
mimag_dog['phylum'] = mimag_dog['Classification'].str.extract(r'p__([^;]+)')
mimag_dog['species'] = mimag_dog['Classification'].str.extract(r's__(.+)$')
mimag_dog['species'] = mimag_dog['species'].fillna('Novel species (unnamed)')

# Print results
print(f"{'='*60}")
print(f"SHANGHAI DOGS vs GMR HUMAN CATALOG")
print(f"{'='*60}")
print(f"Total dog MAGs:   {total_dog}")
print(f"Total human MAGs: {total_human}")
print(f"Total hits:       {len(df)}")

print(f"\n{'='*60}")
print(f"OVERLAP SUMMARY (>=95% ANI)")
print(f"{'='*60}")
print(f"Dog MAGs WITH human counterpart:    {unique_dog} ({unique_dog/total_dog*100:.1f}%)")
print(f"Dog MAGs WITHOUT human counterpart: {total_dog - unique_dog} ({(total_dog-unique_dog)/total_dog*100:.1f}%)")
print(f"Human MAGs matched by dogs:         {unique_human} ({unique_human/total_human*100:.1f}%)")
print(f"Human MAGs NOT matched by dogs:     {total_human - unique_human} ({(total_human-unique_human)/total_human*100:.1f}%)")

print(f"\n{'='*60}")
print(f"ANI DISTRIBUTION OF MATCHED PAIRS")
print(f"{'='*60}")
print(shared['ANI'].describe())

print(f"\n{'='*60}")
print(f"DOG-SPECIFIC SPECIES (not found in human gut)")
print(f"{'='*60}")
print(f"Total dog-specific MAGs: {len(mimag_dog)}")
print(f"\nNamed species:")
print(mimag_dog[mimag_dog['species'] != 'Novel species (unnamed)']['species'].value_counts().to_string())
print(f"\nNovel unnamed species: {len(mimag_dog[mimag_dog['species'] == 'Novel species (unnamed)'])}")
print(f"\nPhylum breakdown:")
print(mimag_dog['phylum'].value_counts().to_string())
