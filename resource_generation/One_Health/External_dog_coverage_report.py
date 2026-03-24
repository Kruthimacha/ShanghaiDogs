import pandas as pd
import os

#paths
SKANI_DIR = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs/Skani'
QUAL_DIR  = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs'
META_FILE = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/spire_v1_genome_metadata.tsv'

OUTPUT_DIR = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs/Skani'
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("COVERAGE OF EXTERNAL DOG MAGs BY SHD CATALOG\n")

print("Quality thresholds:")
print(" HQ = High Quality (completeness > 90%, contamination < 5%)")
print(" MQ = Medium Quality (completeness >= 50% and < 90%, contamination < 10%)")
print()

header = f"{'Cohort':<30} {'Quality':<25} {'Ext MAGs (total)':>18} {'Ext MAGs matched':>18} {'% Ext covered':>15} {'Mean ANI (%)':>13}"
print(header)
print("-" * 98)

cohorts = [
    'Coelho_2018_dog', 'Wang_2019_dogs', 'Yarlagadda_2022_global_dog',
    'Allaway_2020_dogs', 'Liu_2021_Canidae', 'Xu_2019_dogs', 'Worsley-Tonks_2020_dog'
]

for cohort in cohorts:
    for quality, label in [('HQ', 'High Quality (HQ)'), ('MQ', 'Medium Quality (MQ)')]:
        list_file = f'{QUAL_DIR}/{cohort}_{quality}_list.txt'
        
        with open(list_file) as f:
            ext_mags = sum(1 for line in f if line.strip())

        tsv_file = f'{SKANI_DIR}/{cohort}_{quality}_ani_flipped.tsv'
        df = pd.read_csv(tsv_file, sep='\t')
        
        shared = df[df['ANI'] >= 95].copy()
        shared['ext_genome_id'] = shared['Query_file'].apply(
            lambda x: os.path.basename(x).replace('.fa.gz', '').replace('.fna.gz', '').replace('.fa', '')
        )
        
        ext_matched = shared['ext_genome_id'].nunique()
        mean_ani = shared['ANI'].mean() if len(shared) > 0 else float('nan')
        perc_covered = (ext_matched / ext_mags * 100) if ext_mags > 0 else 0.0
        
        print(f"{cohort:<30} {label:<25} {ext_mags:>18} {ext_matched:>18} {perc_covered:>14.1f}% {mean_ani:>13.2f}")

print("-" * 98)
print("\n")

# DETAILED MATCH TABLE 
meta = pd.read_csv(META_FILE, sep='\t', low_memory=False)
meta = meta[['genome_id', 'completeness', 'contamination']].copy()
meta = meta.rename(columns={'genome_id': 'ext_genome_id'})

all_matches = []

for cohort in cohorts:
    for quality in ['HQ', 'MQ']:
        tsv_file = f'{SKANI_DIR}/{cohort}_{quality}_ani_flipped.tsv'
        if not os.path.exists(tsv_file):
            continue
            
        df = pd.read_csv(tsv_file, sep='\t')
        df = df[df['ANI'] >= 95].copy()
        
        if len(df) == 0:
            continue
            
        df['ext_genome_id'] = df['Query_file'].apply(
            lambda x: os.path.basename(str(x)).replace('.fa.gz', '').replace('.fna.gz', '').replace('.fa', '')
        )
        
        df['cohort'] = cohort
        df['quality'] = quality
        
        df = df.merge(meta, on='ext_genome_id', how='left')
        
        df = df[['cohort', 'quality', 'ext_genome_id', 'completeness', 'contamination', 'Ref_file', 'ANI']]
        
        df['SHD_bin'] = df['Ref_file'].apply(
            lambda x: os.path.basename(str(x)).replace('.fna.gz', '').replace('.fa.gz', '').replace('.fa', '')
        )
        
        all_matches.append(df)

if all_matches:
    final_table = pd.concat(all_matches, ignore_index=True)
    final_table = final_table.sort_values(by=['cohort', 'quality', 'ext_genome_id', 'ANI'], 
                                          ascending=[True, True, True, False])
    
    output_file = f'{OUTPUT_DIR}/Detailed_Match_Table_All_Hits.tsv'
    final_table.to_csv(output_file, sep='\t', index=False)
    
    print(f"\nDetailed match table saved to:")
    print(output_file)
    print(f"Total rows (all hits >=95% ANI): {len(final_table)}")
    print(f"Unique external MAGs with matches: {final_table['ext_genome_id'].nunique()}")
else:
    print("No matches found.")

print("Detailed table saved as: Detailed_Match_Table_All_Hits.tsv")
