import pandas as pd
import glob

total_shanghai = len(glob.glob('/work/microbiome/shanghai_dogs/data/ShanghaiDogsMAGs/*.fna.gz'))

cohorts = {
    'GMR_Human_2025':        ('/work/microbiome/users/kruthi/MAGs_Onehealth/dog_vs_human_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta'),
    'Coelho_2018_dog':       ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Coelho_2018_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Coelho_2018_dog/Coelho_2018_dog/*.fa.gz'),
    'Wang_2019_dog':         ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Wang_2019_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Wang_2019_dogs/*.fa.gz'),
    'Yarlagadda_2022_dog':   ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Yarlagadda_2022_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Yarlagadda_2022_global_dog/*.fa.gz'),
    'Xu_2019_dog':           ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Xu_2019_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Xu_2019_dogs/*.fa.gz'),
    'Allaway_2020_dog':      ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Allaway_2020_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Allaway_2020_dogs/*.fa.gz'),
    'Liu_2021_dog':          ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_Liu_2021_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Liu_2021_Canidae/*.fa.gz'),
    'WorsleyTonks_2020_dog': ('/work/microbiome/users/kruthi/MAGs_Onehealth/shanghai_vs_WorsleyTonks_2020_ani.tsv',
                              '/work/microbiome/users/kruthi/MAGs_Onehealth/external_dog_cohorts/Worsley-Tonks_2020_dog/*.fa.gz'),
}

print(f"Total Shanghai dog MAGs: {total_shanghai}\n")
print(f"{'Cohort':<25} {'Type':<8} {'Ref MAGs':>10} {'>=95% ANI':>10} {'Unique Shanghai':>16} {'Percentage':>12} {'Mean ANI':>10}")
print("-" * 95)

for name, (path, mag_path) in cohorts.items():
    df = pd.read_csv(path, sep='\t')
    shared = df[df['ANI'] >= 95]
    unique_shanghai = shared['Query_file'].nunique()
    mean_ani = shared['ANI'].mean()
    ref_mags = len(glob.glob(mag_path))
    cohort_type = 'Human' if 'Human' in name else 'Dog'
    print(f"{name:<25} {cohort_type:<8} {ref_mags:>10} {len(shared):>10} {unique_shanghai:>16} {unique_shanghai/total_shanghai*100:>11.1f}% {mean_ani:>10.2f}%")

print("-" * 95)
print(f"\nPercentage = Shanghai MAGs with counterpart at >=95% ANI out of {total_shanghai} total")
