import pandas as pd
import glob

mimag = pd.read_csv('/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv')
reps = mimag[mimag['Representative'] == 'Yes'].copy()
reps['path'] = '/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/' + reps['Bin ID']
reps['path'].to_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_MAGs_list.txt',
                    index=False, header=False)

total_species_reps = sum(1 for _ in open('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_MAGs_list.txt'))
total_human = len(glob.glob('/work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta'))

#run skani

df = pd.read_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_vs_Human_ani.tsv', sep='\t')
shared = df[df['ANI'] >= 95].copy()
unique_shanghai = shared['Query_file'].nunique()
unique_human = shared['Ref_file'].nunique()

print(f"Total SHD species representatives: {total_species_reps}")
print(f"Total human MAGs in catalog: {total_human}")
print(f"\nSHD species WITH human counterpart: {unique_shanghai} ({unique_shanghai/total_species_reps*100:.1f}%)")
print(f"SHD species WITHOUT human counterpart: {total_species_reps - unique_shanghai} ({(total_species_reps-unique_shanghai)/total_species_reps*100:.1f}%)")
print(f"\nHuman MAGs matched by SHD: {unique_human} ({unique_human/total_human*100:.1f}%)")
print(f"\nANI distribution:")
print(shared['ANI'].describe())

# Find dog-specific species
matched_files = shared['Query_file'].unique()
reps['full_path'] = '/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/' + reps['Bin ID']
dog_specific = reps[~reps['full_path'].isin(matched_files)].copy()
dog_specific['species'] = dog_specific['Classification'].str.extract(r's__(.+)$')

print(f"\n DOG-SPECIFIC SPECIES (no human counterpart) ")
print(f"Total: {len(dog_specific)}")
print(f"\nNamed species:")
named = dog_specific[dog_specific['species'].notna()]
print(named[['Bin ID', 'species', 'Quality']].to_string(index=False))
print(f"\nNovel unnamed species: {dog_specific['species'].isna().sum()}")
