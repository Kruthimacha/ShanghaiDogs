import re
from pathlib import Path
from collections import defaultdict

import pandas as pd

BASE = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts")
QUALITY_DIR = BASE / "Skani_lists" / "Quality_MAGs"
SKANI_DIR = QUALITY_DIR / "Skani_Quality_Results"
OUTDIR = BASE / "FastANI" / "Unmatched_MAGs"
OUTDIR.mkdir(parents=True, exist_ok=True)

cohorts = [
    "Coelho_2018_dog",
    "Wang_2019_dogs",
    "Yarlagadda_2022_global_dog",
    "Allaway_2020_dogs",
    "Liu_2021_Canidae",
    "Xu_2019_dogs",
    "Worsley-Tonks_2020_dog",
]

def clean_id(path):
    name = Path(path).name
    return re.sub(r"\.(fa|fna|fasta)(\.gz)?$", "", name)

for cohort in cohorts:
    for quality in ["HQ", "MQ"]:
        list_file = QUALITY_DIR / f"{cohort}_{quality}_list.txt"
        ani_file = SKANI_DIR / f"{cohort}_{quality}_ani.tsv"

        if not list_file.exists() or not ani_file.exists():
            print(f"Skipping {cohort} {quality}")
            continue

        with open(list_file) as f:
            all_paths = [line.strip() for line in f if line.strip()]

        # Keep all original paths for each cleaned ID
        id_to_paths = defaultdict(list)
        for p in all_paths:
            id_to_paths[clean_id(p)].append(p)

        # Read ANI table: first 7 columns are expected
        df = pd.read_csv(ani_file, sep="\t", header=None, usecols=range(7))
        df.columns = [
            "Ref_file", "Query_file", "ANI",
            "AF_ref", "AF_query", "Ref_name", "Query_name"
        ]
        df["ANI"] = pd.to_numeric(df["ANI"], errors="coerce")

        # Any genome that appears in either Ref_file or Query_file
        # in a comparison with ANI >= 95 is considered matched
        high_ani = df[df["ANI"] >= 95]

        matched_ids = set(high_ani["Ref_file"].dropna().map(clean_id)) | \
                      set(high_ani["Query_file"].dropna().map(clean_id))

        unmatched = []
        for cid, paths in id_to_paths.items():
            if cid not in matched_ids:
                unmatched.extend(paths)

        out_file = OUTDIR / f"{cohort}_{quality}_unmatched_paths.txt"
        with open(out_file, "w") as f:
            f.write("\n".join(unmatched) + ("\n" if unmatched else ""))

        print(f"{cohort} {quality}: {len(unmatched)} unmatched -> {out_file}")
