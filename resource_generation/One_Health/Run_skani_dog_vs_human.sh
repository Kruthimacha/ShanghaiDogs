#!/bin/bash
# One Health Analysis: Compare Shanghai Dog MAGs vs Chinese Human Gut MAGs
# Reference: GMR catalog - Dong et al. 2025, Genome Medicine (OMIX006649)
# Dong, Q., Ma, B., Zhou, X. et al. Expanded gut microbial genomes from Chinese populations 
# reveal population-specific genomic features related to human physiological traits. 
# Genome Med 17, 137 (2025). https://doi.org/10.1186/s13073-025-01566-x

skani dist \
    --ql /work/microbiome/users/kruthi/MAGs_Onehealth/dog_mags_list.txt \
    -r /work/microbiome/users/kruthi/MAGs_Onehealth/GMR_REP_6664MAGs/GMR_REP/*.fasta \
    --min-af 50 \
    -t 40 \
    -o /work/microbiome/users/kruthi/MAGs_Onehealth/dog_vs_human_ani.tsv

echo "Done,results saved to dog_vs_human_ani.tsv"
