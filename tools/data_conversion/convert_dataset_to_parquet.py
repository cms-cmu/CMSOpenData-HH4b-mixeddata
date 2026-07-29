#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterator

import awkward as ak
import pyarrow.parquet as pq
import uproot


REQUIRED_CLASSIFIER_BRANCHES = {
    "event",
    "weight",
    "threeTag",
    "fourTag",
    "passHLT",
    "SB",
    "SR",
    "ZHSR",
    "ZZSR",
    "HHSR",
    "nSelJets",
    "xW",
    "xbW",
    "CanJet_pt",
    "CanJet_eta",
    "CanJet_phi",
    "CanJet_mass",
    "NotCanJet_pt",
    "NotCanJet_eta",
    "NotCanJet_phi",
    "NotCanJet_mass",
    "NotCanJet_isSelJet",
    "pseudoTagWeight",
    "FvT",
}

REQUIRED_REFERENCE_BRANCHES = {
    "ref_SvB_MA_phh",
    "ref_SvB_MA_pzz",
    "ref_SvB_MA_pzh",
    "ref_SvB_MA_ptt",
    "ref_SvB_MA_pmj",
    "ref_SvB_MA_q_1234",
    "ref_SvB_MA_q_1324",
    "ref_SvB_MA_q_1423",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Convert a consolidated ROOT Events tree "
            "into a validated Parquet file using "
            "streaming row groups."
        )
    )

    parser.add_argument(
        "input",
        type=Path,
        help="Input consolidated ROOT file.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output Parquet file. By default the "
            "input .root suffix is replaced by .parquet."
        ),
    )

    parser.add_argument(
        "--step-size",
        type=int,
        default=25_000,
        help=(
            "Number of ROOT events to read per batch. "
            "Default: 25000."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing Parquet output.",
    )

    return parser.parse_args()


def validate_required_branches(
    fields: set[str],
) -> None:

    missing_classifier = sorted(
        REQUIRED_CLASSIFIER_BRANCHES - fields
    )

    missing_reference = sorted(
        REQUIRED_REFERENCE_BRANCHES - fields
    )

    if missing_classifier:
        raise RuntimeError(
            "Missing required classifier branches: "
            + ", ".join(missing_classifier)
        )

    if missing_reference:
        raise RuntimeError(
            "Missing required SvB reference branches: "
            + ", ".join(missing_reference)
        )


def iterate_batches(
    tree: uproot.behaviors.TTree.TTree,
    step_size: int,
    expected_fields: set[str],
) -> Iterator[ak.Array]:

    processed = 0
    batch_number = 0

    for events in tree.iterate(
        step_size=step_size,
        library="ak",
    ):
        batch_number += 1

        current_fields = set(
            ak.fields(events)
        )

        if current_fields != expected_fields:
            missing = sorted(
                expected_fields - current_fields
            )

            extra = sorted(
                current_fields - expected_fields
            )

            raise RuntimeError(
                "ROOT batch schema mismatch.\n"
                f"Batch: {batch_number}\n"
                f"Missing: {missing}\n"
                f"Extra: {extra}"
            )

        batch_entries = len(events)
        processed += batch_entries

        print(
            f"  Batch {batch_number:4d}: "
            f"{batch_entries:8d} events "
            f"| processed={processed}"
        )

        yield events


def main() -> None:
    args = parse_args()

    input_path = args.input

    if not input_path.exists():
        raise FileNotFoundError(
            f"Input ROOT file does not exist: "
            f"{input_path}"
        )

    if args.step_size <= 0:
        raise ValueError(
            "--step-size must be greater than zero."
        )

    output_path = args.output

    if output_path is None:
        output_path = input_path.with_suffix(
            ".parquet"
        )

    if output_path.exists():

        if not args.overwrite:
            raise FileExistsError(
                f"Output already exists: "
                f"{output_path}\n"
                "Use --overwrite to replace it."
            )

        output_path.unlink()

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print("INPUT:    ", input_path)
    print("OUTPUT:   ", output_path)
    print("STEP SIZE:", args.step_size)
    print("=" * 80)

    try:
        with uproot.open(input_path) as root_file:

            if "Events" not in root_file:
                raise KeyError(
                    "Input ROOT file does not contain "
                    "an Events tree."
                )

            tree = root_file["Events"]

            root_entries = tree.num_entries
            root_fields = set(
                tree.keys()
            )

            print("\nROOT INPUT SUMMARY")
            print(
                "  entries:",
                root_entries,
            )

            print(
                "  branches:",
                len(root_fields),
            )

            validate_required_branches(
                root_fields
            )

            print(
                "\nStreaming ROOT batches "
                "into Parquet row groups..."
            )

            batches = iterate_batches(
                tree=tree,
                step_size=args.step_size,
                expected_fields=root_fields,
            )

            ak.to_parquet_row_groups(
                batches,
                output_path,
                compression="zstd",
            )

        print(
            "\nValidating Parquet metadata..."
        )

        parquet_file = pq.ParquetFile(
            output_path
        )

        parquet_entries = (
            parquet_file.metadata.num_rows
        )

        parquet_fields = set(
            parquet_file.schema_arrow.names
        )

        parquet_row_groups = (
            parquet_file.metadata.num_row_groups
        )

        print("\nPARQUET SUMMARY")
        print(
            "  entries:",
            parquet_entries,
        )

        print(
            "  branches:",
            len(parquet_fields),
        )

        print(
            "  row groups:",
            parquet_row_groups,
        )

        if parquet_entries != root_entries:
            raise RuntimeError(
                "Parquet entry count does not "
                "match ROOT input.\n"
                f"ROOT: {root_entries}\n"
                f"Parquet: {parquet_entries}"
            )

        if parquet_fields != root_fields:

            missing = sorted(
                root_fields - parquet_fields
            )

            extra = sorted(
                parquet_fields - root_fields
            )

            raise RuntimeError(
                "Parquet schema does not match "
                "ROOT input.\n"
                f"Missing: {missing}\n"
                f"Extra: {extra}"
            )

        validate_required_branches(
            parquet_fields
        )

    except Exception:

        if output_path.exists():
            output_path.unlink()

        raise

    print("\nFINAL SUMMARY")

    print(
        "  Entries:",
        parquet_entries,
    )

    print(
        "  Branches:",
        len(parquet_fields),
    )

    print(
        "  Row groups:",
        parquet_row_groups,
    )

    print(
        "  Output:",
        output_path,
    )

    print(
        "\nSTREAMING CONSOLIDATED PARQUET: PASS"
    )


if __name__ == "__main__":
    main()
