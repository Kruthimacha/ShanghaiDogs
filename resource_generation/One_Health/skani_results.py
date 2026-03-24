import pandas as pd
import glob

#data

mimag = pd.read_csv('/work/microbiome/shanghai_dogs/data/ShanghaiDogsTables/SHD_bins_MIMAG_report.csv')
reps = mimag[mimag['Representative'] == 'Yes'].copy()
reps['path'] = '/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/' + reps['Bin ID']
reps['path'].to_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_MAGs_list.txt',
                    index=False, header=False)

total_species_reps = sum(1 for _ in open('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_MAGs_list.txt'))
total_human = len(glob.glob('/work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta'))

df = pd.read_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/SHD_Species_Rep_vs_Human_ani.tsv', sep='\t')
shared = df[df['ANI'] >= 95].copy()

matched_files = shared['Query_file'].unique()
reps['full_path'] = '/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/' + reps['Bin ID']
dog_specific = reps[~reps['full_path'].isin(matched_files)].copy()

dog_specific['species'] = dog_specific['Classification'].str.extract(r's__(.+)$')
dog_specific['genus']   = dog_specific['Classification'].str.extract(r'g__([^;]+)')

named   = dog_specific[dog_specific['species'].notna()][['Bin ID', 'species', 'genus', 'Quality']]
unnamed = dog_specific[dog_specific['species'].isna()][['Bin ID', 'genus', 'Quality']]
unnamed = unnamed.assign(species='Novel unnamed species')

# Save to Excel

out = '/work/microbiome/users/kruthi/MAGs_Onehealth/Dog_specific_species.xlsx'

with pd.ExcelWriter(out, engine='openpyxl') as writer:
    named.to_excel(writer, sheet_name='Dog_specific_species', index=False, startrow=1)
    unnamed.to_excel(writer, sheet_name='Dog_specific_species', index=False,
                     startrow=len(named) + 4)

print(f"Saved: {out}")
