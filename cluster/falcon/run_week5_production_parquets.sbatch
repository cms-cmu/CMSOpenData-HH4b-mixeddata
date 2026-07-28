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

SCRIPT_DIR="$(
    cd -- "$(dirname -- "${BASH_SOURCE[0]}")"
    pwd
)"

REPO_ROOT="$(
    cd -- "${SCRIPT_DIR}/../.."
    pwd
)"

cd "${REPO_ROOT}"

PIXI_BIN="${PIXI_BIN:-pixi}"

if ! command -v "${PIXI_BIN}" >/dev/null 2>&1; then
    echo "ERROR: Pixi was not found in PATH."
    echo "Install Pixi or set PIXI_BIN to its executable path."
    exit 1
fi

echo "============================================================"
echo "Production Parquet build"
echo "============================================================"
echo "Hostname:   $(hostname)"
echo "Start:      $(date)"
echo "Job ID:     ${SLURM_JOB_ID:-not-set}"
echo "Repository: ${REPO_ROOT}"
echo

mkdir -p \
    outputs/consolidated_production \
    logs/production_parquets \
    logs/slurm

/usr/bin/time -v \
    "${PIXI_BIN}" run python \
    tools/data_conversion/build_production_parquets.py \
    --step-size 25000

echo
echo "============================================================"
echo "Production build complete"
echo "End: $(date)"
echo "============================================================"
