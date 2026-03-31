import pandas as pd
from pathlib import Path
import re

BASE = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts")
METADATA = BASE / "Skani_lists" / "spire_v1_genome_metadata.tsv"
QUALITY_DIR = BASE / "Skani_lists" / "Quality_MAGs"
SKANI_DIR = QUALITY_DIR / "Skani_Quality_Results"

# ---------------------------
# Print filtering criteria
# ---------------------------
print("\nQuality filtering criteria:")
print("HQ: completeness ≥ 90 AND contamination < 5")
print("MQ: completeness ≥ 50 AND contamination < 10\n")

# ---------------------------
# Load metadata
# ---------------------------
meta = pd.read_csv(METADATA, sep="\t", low_memory=False)

# ---------------------------
# Assign quality
# ---------------------------
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

# ---------------------------
# Cohorts
# ---------------------------
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

# ---------------------------
# Create HQ/MQ lists
# ---------------------------
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

# ---------------------------
# Print created files
# ---------------------------
print("Generated HQ/MQ list files:")
for f in created_files:
    print(f" - {f}")

# ---------------------------
# Summary from skani
# ---------------------------
def clean_genome_id(path_str):
    name = Path(str(path_str)).name
    return re.sub(r"\.(fa|fna|fasta)(\.gz)?$", "", name)

def read_skani_tsv(path):
    df = pd.read_csv(path, sep="\t", header=None)
    df = df.iloc[:, :7]
    df.columns = [
        "Ref_file","Query_file","ANI",
        "Align_fraction_ref","Align_fraction_query",
        "Ref_name","Query_name"
    ]
    return df

rows = []

for cohort in cohort_dirs.keys():
    for quality in ["HQ", "MQ"]:
        list_file = QUALITY_DIR / f"{cohort}_{quality}_list.txt"
        ani_file = SKANI_DIR / f"{cohort}_{quality}_ani.tsv"

        if not ani_file.exists():
            continue

        ref_mags = sum(1 for _ in open(list_file))

        df = read_skani_tsv(ani_file)
        df["ANI"] = pd.to_numeric(df["ANI"], errors="coerce")

        shared = df[df["ANI"] >= 95].copy()
        shared["Ref_genome_id"] = shared["Ref_file"].apply(clean_genome_id)

        ref_matched = shared["Ref_genome_id"].nunique()
        pct_covered = (ref_matched / ref_mags * 100) if ref_mags else 0
        mean_ani = shared["ANI"].mean() if not shared.empty else None

        rows.append({
            "Cohort": cohort,
            "Quality": quality,
            "Ext MAGs (total)": ref_mags,
            "Ext MAGs matched": ref_matched,
            "% Ext covered": round(pct_covered, 1),
            "Mean ANI (%)": round(mean_ani, 2) if mean_ani else None,
        })

summary = pd.DataFrame(rows)

print("\nFinal coverage table:\n")
print(summary.to_string(index=False))
