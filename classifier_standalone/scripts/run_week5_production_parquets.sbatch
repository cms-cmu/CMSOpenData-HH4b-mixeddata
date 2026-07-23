#!/bin/bash

#SBATCH --job-name=week5_parquets
#SBATCH --partition=work
#SBATCH --qos=cpu_medium
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=16G
#SBATCH --time=1-00:00:00
#SBATCH --output=logs/slurm/week5_parquets_%j.out
#SBATCH --error=logs/slurm/week5_parquets_%j.err

set -euo pipefail

cd ~/pursue2026/CMSOpenData-HH4b-mixeddata

echo "============================================================"
echo "Week 5 production Parquet build"
echo "============================================================"
echo "Hostname: $(hostname)"
echo "Start:    $(date)"
echo "Job ID:   ${SLURM_JOB_ID}"
echo "PWD:      $(pwd)"
echo

mkdir -p \
    outputs/consolidated_production \
    logs/production_parquets

/usr/bin/time -v \
    classifier_standalone/.pixi/envs/default/bin/python \
    classifier_standalone/scripts/build_production_parquets.py \
    --step-size 25000

echo
echo "============================================================"
echo "Production build complete"
echo "End: $(date)"
echo "============================================================"
