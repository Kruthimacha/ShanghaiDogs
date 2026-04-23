import pandas as pd
from pathlib import Path
import re

BASE = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts")
QUALITY_DIR = BASE / "Skani_lists" / "Quality_MAGs"
SKANI_DIR = QUALITY_DIR / "Skani_Quality_Results"

def clean_id(p):
    return re.sub(r"\.(fa|fna|fasta)(\.gz)?$", "", Path(p).name)

def read_skani(path):
    df = pd.read_csv(path, sep="\t", header=None, low_memory=False)
    df = df.iloc[:, :7]
    df.columns = ["Ref_file", "Query_file", "ANI", "AF_ref", "AF_query", "Ref_name", "Query_name"]
    df["ANI"] = pd.to_numeric(df["ANI"], errors="coerce")
    df["Ref_id"] = df["Ref_file"].apply(clean_id)
    return df

cohorts = [
    "Coelho_2018_dog",
    "Wang_2019_dogs",
    "Yarlagadda_2022_global_dog",
    "Allaway_2020_dogs",
    "Liu_2021_Canidae",
    "Xu_2019_dogs",
    "Worsley-Tonks_2020_dog",
]

rows_filtered = []
rows_unfiltered = []

for cohort in cohorts:
    for quality in ["HQ", "MQ", "ALL"]:
        list_file = QUALITY_DIR / f"{cohort}_{quality}_list.txt"
        ani_file = SKANI_DIR / f"{cohort}_{quality}_ani.tsv"

        if not list_file.exists() or not ani_file.exists():
            print(f"Skipping {cohort} {quality} (missing file)")
            continue

        total = sum(1 for _ in open(list_file) if _.strip())
        df = read_skani(ani_file)

        # ANI >= 95
        df95 = df[df["ANI"] >= 95]
        matched95 = df95["Ref_id"].nunique()

        rows_filtered.append({
            "Cohort": cohort,
            "Quality": quality,
            "Ext MAGs (total)": total,
            "Ext MAGs matched": matched95,
            "% Ext covered": round(matched95 / total * 100, 1) if total else 0,
            "Mean ANI (%)": round(df95["ANI"].mean(), 2) if not df95.empty else None,
        })

        # All ANI hits
        matched_all = df["Ref_id"].nunique()
        rows_unfiltered.append({
            "Cohort": cohort,
            "Quality": quality,
            "Ext MAGs (total)": total,
            "Ext MAGs matched": matched_all,
            "% Ext covered": round(matched_all / total * 100, 1) if total else 0,
            "Mean ANI (%)": round(df["ANI"].mean(), 2) if not df.empty else None,
        })

print("\n=TABLE A: ANI ≥ 95 =\n")
print(pd.DataFrame(rows_filtered).to_string(index=False))

print("\n=TABLE B: NO FILTER (ALL ANI) =\n")
print(pd.DataFrame(rows_unfiltered).to_string(index=False))
