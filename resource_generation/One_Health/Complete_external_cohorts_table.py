import pandas as pd
from pathlib import Path
import re

BASE = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts")
METADATA = BASE / "Skani_lists" / "spire_v1_genome_metadata.tsv"
QUALITY_DIR = BASE / "Skani_lists" / "Quality_MAGs"
SKANI_DIR = QUALITY_DIR / "Skani_Quality_Results"

print("\nQuality filtering criteria:")
print("HQ: completeness ≥ 90 AND contamination < 5")
print("MQ: completeness ≥ 50 AND contamination < 10\n")

# Load metadata
meta = pd.read_csv(METADATA, sep="\t", low_memory=False)

# Assign quality
def assign_quality(row):
    comp = float(row["completeness"])
    cont = float(row["contamination"])

    if comp >= 90 and cont < 5:
        return "HQ"
    elif comp >= 50 and cont < 10:
        return "MQ"
    else:
        return "LQ"

meta["quality"] = meta.apply(assign_quality, axis=1)

hq = meta[meta["quality"] == "HQ"]
mq = meta[meta["quality"] == "MQ"]

# Cohorts
cohort_dirs = {
    "Coelho_2018_dog": BASE / "Coelho_2018_dog",
    "Wang_2019_dogs": BASE / "Wang_2019_dogs",
    "Yarlagadda_2022_global_dog": BASE / "Yarlagadda_2022_global_dog",
    "Allaway_2020_dogs": BASE / "Allaway_2020_dogs",
    "Liu_2021_Canidae": BASE / "Liu_2021_Canidae",
    "Xu_2019_dogs": BASE / "Xu_2019_dogs",
    "Worsley-Tonks_2020_dog": BASE / "Worsley-Tonks_2020_dog",
}

valid_suffixes = [".fa", ".fna", ".fasta", ".fa.gz", ".fna.gz", ".fasta.gz"]

created_files = []

# Create HQ/MQ lists
for cohort_name, cohort_root in cohort_dirs.items():
    mags_dir = cohort_root / "mags"

    files = []
    for pattern in ["*.fa", "*.fna", "*.fasta", "*.fa.gz", "*.fna.gz", "*.fasta.gz"]:
        files.extend(mags_dir.rglob(pattern))

    genome_to_path = {}
    for f in files:
        stem = f.name
        for suf in valid_suffixes:
            if stem.endswith(suf):
                stem = stem[: -len(suf)]
                break
        genome_to_path[stem] = str(f.resolve())

    mag_ids = list(genome_to_path.keys())

    cohort_hq = hq[hq["genome_id"].isin(mag_ids)]
    cohort_mq = mq[mq["genome_id"].isin(mag_ids)]

    hq_file = QUALITY_DIR / f"{cohort_name}_HQ_list.txt"
    mq_file = QUALITY_DIR / f"{cohort_name}_MQ_list.txt"

    with open(hq_file, "w") as f:
        for gid in cohort_hq["genome_id"]:
            f.write(genome_to_path[gid] + "\n")

    with open(mq_file, "w") as f:
        for gid in cohort_mq["genome_id"]:
            f.write(genome_to_path[gid] + "\n")

    created_files.extend([hq_file, mq_file])

print("Generated HQ/MQ list files:")
for f in created_files:
    print(f" - {f}")

# Read skani output
def clean_id(p):
    return re.sub(r"\.(fa|fna|fasta)(\.gz)?$", "", Path(p).name)

def read_skani(path):
    df = pd.read_csv(path, sep="\t", header=None)
    df = df.iloc[:, :7]
    df.columns = ["Ref_file", "Query_file", "ANI", "AF_ref", "AF_query", "Ref_name", "Query_name"]
    df["ANI"] = pd.to_numeric(df["ANI"], errors="coerce")
    df["Ref_id"] = df["Ref_file"].apply(clean_id)
    return df

rows_filtered = []
rows_unfiltered = []

for cohort in cohort_dirs.keys():
    for quality in ["HQ", "MQ"]:
        list_file = QUALITY_DIR / f"{cohort}_{quality}_list.txt"
        ani_file = SKANI_DIR / f"{cohort}_{quality}_ani.tsv"

        if not ani_file.exists():
            continue

        total = sum(1 for _ in open(list_file) if _.strip())
        df = read_skani(ani_file)

        # FILTERED (ANI ≥ 95)
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

        # UNFILTERED (ALL ANI)
        matched_all = df["Ref_id"].nunique()

        rows_unfiltered.append({
            "Cohort": cohort,
            "Quality": quality,
            "Ext MAGs (total)": total,
            "Ext MAGs matched": matched_all,
            "% Ext covered": round(matched_all / total * 100, 1) if total else 0,
            "Mean ANI (%)": round(df["ANI"].mean(), 2),
        })

# Print tables
print("\n===== TABLE A: ANI ≥ 95 =====\n")
print(pd.DataFrame(rows_filtered).to_string(index=False))

print("\n===== TABLE B: NO FILTER (ALL ANI) =====\n")
print(pd.DataFrame(rows_unfiltered).to_string(index=False))
