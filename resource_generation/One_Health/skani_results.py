import pandas as pd
import os

# Base 
BASE_DIR = "/work/microbiome/shanghai_dogs"

# Define paths
mimag_path = os.path.join(BASE_DIR, "data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv")
skani_path   = os.path.join(BASE_DIR, "resource_generation/MAGs_Onehealth/SHD_Species_Rep_vs_Human_ani.tsv")
mag_dir    = os.path.join(BASE_DIR, "data/ShanghaiDogsMAGs")

# Load data
mimag = pd.read_csv(mimag_path)

# Get species representatives
reps = mimag[mimag['Representative'] == 'Yes'].copy()
reps['full_path'] = reps['Bin ID'].apply(lambda x: os.path.join(mag_dir, x))

# Load SKANI results
df = pd.read_csv(skani_path, sep='\t')
shared = df[df['ANI'] >= 95]

# Identify dog-specific MAGs
matched_files = shared['Query_file'].unique()
dog_specific = reps[~reps['full_path'].isin(matched_files)].copy()

# Extract taxonomy
dog_specific['species'] = dog_specific['Classification'].str.extract(r's__(.+)$')
dog_specific['genus']   = dog_specific['Classification'].str.extract(r'g__([^;]+)')

#missing species
dog_specific['species'] = dog_specific['species'].fillna('Novel unnamed species')

# Final table
final = dog_specific[['Bin ID', 'species', 'genus', 'Quality']].copy()
final = final.reset_index(drop=True)
final.index = final.index + 1

# Display 
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Print summary
print("\nSummary")
print(f"Total dog-specific MAGs: {len(final)}")
print(f"Named species: {(final['species'] != 'Novel unnamed species').sum()}")
print(f"Novel unnamed species: {(final['species'] == 'Novel unnamed species').sum()}")

# Print table
print("\nDog-specific species table:\n")
print(final)

print(f"Saved: {out}")
