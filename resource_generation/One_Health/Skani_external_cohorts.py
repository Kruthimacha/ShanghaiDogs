import pandas as pd
import glob
import os

# Create output directory
output_dir = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs'
os.makedirs(output_dir, exist_ok=True)

# Load SPIRE metadata
meta = pd.read_csv('/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/spire_v1_genome_metadata.tsv',
                   sep='\t', low_memory=False)
print(f"Total SPIRE genomes: {len(meta)}")

# Quality filters
hq = meta[(meta['completeness'] > 90) & (meta['contamination'] < 5)]
mq = meta[(meta['completeness'] >= 50) & (meta['completeness'] <= 90) & (meta['contamination'] < 10)]
print(f"HQ MAGs in SPIRE: {len(hq)}")
print(f"MQ MAGs in SPIRE: {len(mq)}")

# Cohort directories
cohort_dirs = {
    'Coelho_2018_dog':            '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Coelho_2018_dog/Coelho_2018_dog',
    'Wang_2019_dogs':             '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Wang_2019_dogs',
    'Yarlagadda_2022_global_dog': '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Yarlagadda_2022_global_dog',
    'Allaway_2020_dogs':          '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Allaway_2020_dogs',
    'Liu_2021_Canidae':           '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Liu_2021_Canidae',
    'Xu_2019_dogs':               '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Xu_2019_dogs',
    'Worsley-Tonks_2020_dog':     '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Worsley-Tonks_2020_dog',
}

print(f"\n{'Cohort':<30} {'Total':>8} {'HQ':>8} {'MQ':>8}")
print("-" * 60)

for name, mag_dir in cohort_dirs.items():
    # Get all MAG IDs for this cohort
    files   = glob.glob(f'{mag_dir}/*.fa.gz')
    mag_ids = [os.path.basename(f).replace('.fa.gz', '') for f in files]

    # Filter HQ and MQ for this cohort
    cohort_hq = hq[hq['genome_id'].isin(mag_ids)]
    cohort_mq = mq[mq['genome_id'].isin(mag_ids)]

    # Save HQ list
    hq_paths = [f'{mag_dir}/{gid}.fa.gz' for gid in cohort_hq['genome_id']]
    hq_out   = f'{output_dir}/{name}_HQ_list.txt'
    with open(hq_out, 'w') as f:
        f.write('\n'.join(hq_paths) + '\n')

    # Save MQ list
    mq_paths = [f'{mag_dir}/{gid}.fa.gz' for gid in cohort_mq['genome_id']]
    mq_out   = f'{output_dir}/{name}_MQ_list.txt'
    with open(mq_out, 'w') as f:
        f.write('\n'.join(mq_paths) + '\n')

    print(f"{name:<30} {len(mag_ids):>8} {len(hq_paths):>8} {len(mq_paths):>8}")

print(f"\nAll list files saved to: {output_dir}")

#####

import pandas as pd
import os

SKANI_DIR = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs/Skani'
QUAL_DIR  = '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Quality_MAGs'

cohorts = [
    'Coelho_2018_dog',
    'Wang_2019_dogs',
    'Yarlagadda_2022_global_dog',
    'Allaway_2020_dogs',
    'Liu_2021_Canidae',
    'Xu_2019_dogs',
    'Worsley-Tonks_2020_dog',
]

print("Quality thresholds:")
print("  HQ = High Quality  (completeness >90%, contamination <5%)")
print("  MQ = Medium Quality (completeness ≥50%–<90%, contamination <10%)")
print()

header = f"{'Cohort':<30} {'Quality':<25} {'Ref MAGs (total)':>18} {'Ref MAGs matched':>18} {'% Ref covered':>15} {'Mean ANI (%)':>13}"
print(header)
print("-" * len(header))

for cohort in cohorts:
    for quality, label in [('HQ', 'High Quality (HQ)'), ('MQ', 'Medium Quality (MQ)')]:

        list_file = f'{QUAL_DIR}/{cohort}_{quality}_list.txt'
        ref_mags  = sum(1 for _ in open(list_file))

        df     = pd.read_csv(f'{SKANI_DIR}/{cohort}_{quality}_ani.tsv', sep='\t')
        shared = df[df['ANI'] >= 95].copy()
        shared['genome_id'] = shared['Ref_file'].apply(lambda x: os.path.basename(x).replace('.fa.gz', ''))

        ref_matched = shared['genome_id'].nunique()
        mean_ani    = shared['ANI'].mean()

        print(f"{cohort:<30} {label:<25} {ref_mags:>18} {ref_matched:>18} {ref_matched/ref_mags*100:>14.1f}% {mean_ani:>13.2f}")

print("-" * len(header))
