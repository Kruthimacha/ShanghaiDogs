from pathlib import Path
import re
import pandas as pd

fastani_dir = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/FastANI/FastANI_results")
meta_file = Path("/work/microbiome/shanghai_dogs/resource_generation/MAGs_Onehealth/External_cohorts/Skani_lists/spire_v1_genome_metadata.tsv")
out_xlsx = fastani_dir / "FastANI_by_cohort_taxonomy.xlsx"

# Load taxonomy metadata
meta = pd.read_csv(
    meta_file,
    sep="\t",
    low_memory=False,
    usecols=["genome_id", "family", "genus", "species"]
)

def clean_id(path_str):
    name = Path(str(path_str)).name
    return re.sub(r"\.(fa|fna|fasta)(\.gz)?$", "", name)

def sheet_name_from_file(path):
    name = path.stem.replace("_vs_shanghai_fastani", "")
    return name[:31]  # Excel sheet name limit

def read_fastani_tsv(path):
    df = pd.read_csv(path, sep="\t", header=None)
    df = df.iloc[:, :5]
    df.columns = ["spire_file", "shd_file", "ANI", "fragments", "total_fragments"]
    return df

summary_rows = []

with pd.ExcelWriter(out_xlsx, engine="openpyxl") as writer:
    for tsv in sorted(fastani_dir.glob("*_vs_shanghai_fastani.tsv")):
        df = read_fastani_tsv(tsv)

        df["spire_id"] = df["spire_file"].apply(clean_id)
        df["shd_id"] = df["shd_file"].apply(clean_id)

        # Merge taxonomy for the SPIRE MAG
        df = df.merge(
            meta,
            left_on="spire_id",
            right_on="genome_id",
            how="left"
        ).drop(columns=["genome_id"])

        # Put taxonomy columns near the end
        cols = [
            "spire_id", "spire_file",
            "shd_id", "shd_file",
            "ANI", "fragments", "total_fragments",
            "family", "genus", "species"
        ]
        df = df[cols]

        sheet = sheet_name_from_file(tsv)
        df.to_excel(writer, sheet_name=sheet, index=False)

        summary_rows.append({
            "sheet": sheet,
            "rows": len(df),
            "unique_spire_ids": df["spire_id"].nunique(),
            "unique_shd_ids": df["shd_id"].nunique()
        })

    # Add a summary sheet
    summary = pd.DataFrame(summary_rows)
    summary.to_excel(writer, sheet_name="Summary", index=False)

print(f"Saved workbook to: {out_xlsx}")
