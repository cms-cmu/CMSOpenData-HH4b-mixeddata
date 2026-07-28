from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT))

import awkward as ak
import numpy as np
import uproot

from scripts.extract_jets import ROOT_FILES, TREE_NAME


BRANCHES_TO_COMPARE = ["run", "event", "luminosityBlock"]


def validate_event_ids_for_year(year):
    """
    Compare event-identification branches between the original ROOT file
    and the extracted Parquet files for one year.
    """
    print(f"\nChecking ROOT vs Parquet event IDs for {year}...")

    with uproot.open(ROOT_FILES[year]) as f:
        tree = f[TREE_NAME]
        root_arrays = tree.arrays(BRANCHES_TO_COMPARE, library="ak")

    parquet_files = sorted(Path(f"outputs/jets/{year}").glob("*.parquet"))

    if not parquet_files:
        print(f"FAIL: No Parquet files found for {year}")
        return False

    parquet_arrays = ak.concatenate(
        [ak.from_parquet(parquet_file) for parquet_file in parquet_files],
        axis=0,
    )

    print(f"ROOT events: {len(root_arrays)}")
    print(f"Parquet events: {len(parquet_arrays)}")

    passed = True

    for branch in BRANCHES_TO_COMPARE:
        root_values = ak.to_numpy(root_arrays[branch])
        parquet_values = ak.to_numpy(parquet_arrays[branch])

        same_length = len(root_values) == len(parquet_values)
        same_values = np.array_equal(root_values, parquet_values)

        print(f"{branch}:")
        print(f"  Same length: {same_length}")
        print(f"  Same values: {same_values}")

        if not same_length or not same_values:
            passed = False

    if passed:
        print(f"PASS: {year} event ID branches match ROOT.")
    else:
        print(f"FAIL: {year} event ID branches do not match ROOT.")

    return passed


def main():
    all_passed = True

    for year in ["2016", "2017", "2018"]:
        year_passed = validate_event_ids_for_year(year)
        all_passed = all_passed and year_passed

    print("\nEvent ID validation summary:")

    if all_passed:
        print("All event ID branches match ROOT.")
    else:
        print("One or more event ID checks failed.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
