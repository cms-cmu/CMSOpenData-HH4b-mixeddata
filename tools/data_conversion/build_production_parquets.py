#!/usr/bin/env python3

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import yaml


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]

MAP = SCRIPT_DIR / "dataset_files_map.yml"
MERGER = SCRIPT_DIR / "consolidate_dataset.py"
CONVERTER = SCRIPT_DIR / "convert_dataset_to_parquet.py"

# Reuse the interpreter that launched this driver instead of assuming
# a repository-specific Pixi environment path.
PYTHON = Path(sys.executable)

OUTPUT_DIR = (
    REPO_ROOT
    / "outputs"
    / "consolidated_production"
)

LOG_DIR = (
    REPO_ROOT
    / "logs"
    / "production_parquets"
)

# These currently have invalid/incomplete source pairings.
BLOCKED_DATASETS = {
    "data2016G_UL16_postVFP",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Build consolidated ROOT and Parquet "
            "files for Week 5 production datasets."
        )
    )

    parser.add_argument(
        "--step-size",
        type=int,
        default=25_000,
        help="Parquet ROOT-reading batch size.",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Print the datasets that would be "
            "processed without running them."
        ),
    )

    return parser.parse_args()


def category(dataset: str) -> str | None:

    if dataset.startswith(
        "GluGluToHHTo4B"
    ):
        return "HH"

    if dataset.startswith("ZH4b"):
        return "ZH"

    if dataset.startswith("ZZ4b"):
        return "ZZ"

    if dataset.startswith("TTTo"):
        return "ttbar"

    if dataset.startswith("data"):
        return "data"

    return None


def run_command(
    command: list[str],
    log_path: Path,
) -> None:

    print("\nRunning:")
    print(" ", " ".join(command))
    print("Log:")
    print(" ", log_path)

    with log_path.open(
        "w"
    ) as log_file:

        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1,
        )

        assert process.stdout is not None

        for line in process.stdout:
            print(
                line,
                end="",
                flush=True,
            )

            log_file.write(line)
            log_file.flush()

        return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(
            "Command failed with exit code "
            f"{return_code}:\n"
            + " ".join(command)
        )


def main() -> None:
    args = parse_args()

    with MAP.open() as handle:
        dataset_map = yaml.safe_load(
            handle
        )

    datasets = [
        dataset
        for dataset in dataset_map
        if category(dataset) is not None
    ]

    datasets = sorted(
        datasets,
        key=lambda name: (
            category(name),
            name,
        ),
    )

    valid_datasets = [
        dataset
        for dataset in datasets
        if dataset not in BLOCKED_DATASETS
    ]

    print("=" * 80)
    print("WEEK 5 PRODUCTION DATASET DRIVER")
    print("=" * 80)
    print(
        "Mapped data/signal datasets:",
        len(datasets),
    )
    print(
        "Blocked datasets:",
        len(BLOCKED_DATASETS),
    )
    print(
        "Eligible datasets:",
        len(valid_datasets),
    )

    print("\nBlocked:")
    for dataset in sorted(
        BLOCKED_DATASETS
    ):
        print(
            "  ",
            dataset,
        )

    print("\nEligible production datasets:")

    for dataset in valid_datasets:

        root_output = (
            OUTPUT_DIR
            / f"{dataset}_consolidated.root"
        )

        parquet_output = (
            OUTPUT_DIR
            / f"{dataset}_consolidated.parquet"
        )

        if (
            root_output.exists()
            and parquet_output.exists()
        ):
            status = "COMPLETE"

        elif root_output.exists():
            status = "ROOT ONLY"

        else:
            status = "PENDING"

        print(
            f"  {status:10s} "
            f"{dataset}"
        )

    if args.dry_run:
        print(
            "\nDRY RUN COMPLETE"
        )
        return

    OUTPUT_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    LOG_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    for dataset in valid_datasets:

        root_output = (
            OUTPUT_DIR
            / f"{dataset}_consolidated.root"
        )

        parquet_output = (
            OUTPUT_DIR
            / f"{dataset}_consolidated.parquet"
        )

        print("\n" + "=" * 80)
        print(
            "DATASET:",
            dataset,
        )
        print("=" * 80)

        if not root_output.exists():

            merge_log = (
                LOG_DIR
                / f"{dataset}_merge.log"
            )

            merge_command = [
                str(PYTHON),
                str(MERGER),
                dataset,
                "--output",
                str(root_output),
            ]

            run_command(
                merge_command,
                merge_log,
            )

        else:

            print(
                "Consolidated ROOT already "
                "exists. Skipping merge."
            )

        if not parquet_output.exists():

            parquet_log = (
                LOG_DIR
                / f"{dataset}_parquet.log"
            )

            parquet_command = [
                str(PYTHON),
                str(CONVERTER),
                str(root_output),
                "--output",
                str(parquet_output),
                "--step-size",
                str(args.step_size),
            ]

            run_command(
                parquet_command,
                parquet_log,
            )

        else:

            print(
                "Parquet already exists. "
                "Skipping conversion."
            )

        print(
            "\nDATASET COMPLETE:",
            dataset,
        )

    print("\n" + "=" * 80)
    print(
        "ALL ELIGIBLE MAPPED DATASETS COMPLETE"
    )
    print("=" * 80)


if __name__ == "__main__":
    main()
