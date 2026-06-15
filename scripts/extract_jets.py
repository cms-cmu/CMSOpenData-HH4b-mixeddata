import argparse
from pathlib import Path

import awkward as ak
import uproot


ROOT_FILES = {
    "2016": (
        "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/"
        "mixed2016_3bDvTMix4bDvT_v0/"
        "picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root"
    ),
    "2017": (
        "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/"
        "mixed2017_3bDvTMix4bDvT_v0/"
        "picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root"
    ),
    "2018": (
        "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/"
        "mixed2018_3bDvTMix4bDvT_v0/"
        "picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root"
    ),
}

TREE_NAME = "Events"


def parse_args():
    """
    Read command-line arguments.

    Example:
        python scripts/extract_jets.py --year 2016

    The --year argument tells the script which ROOT file to process.
    """
    parser = argparse.ArgumentParser(
        description="Extract Jet branches from CMS HH4b mixeddata ROOT files."
    )

    parser.add_argument(
        "--year",
        required=True,
        choices=["2016", "2017", "2018"],
        help="Dataset year to process.",
    )

    parser.add_argument(
        "--step-size",
        default="50 MB",
        help="Chunk size used by uproot.iterate. Default: 50 MB.",
    )

    parser.add_argument(
        "--max-parts",
        type=int,
        default=None,
        help="Optional limit on number of chunks to process for testing.",
    )

    return parser.parse_args()


def find_jet_branches(tree):
    """
    Find Jet-related branches in the Events TTree.

    We keep:
        - nJet
        - every branch that starts with Jet_

    Example:
        nJet
        Jet_pt
        Jet_eta
        Jet_phi
        Jet_mass
    """
    branches = list(tree.keys())

    jet_branches = [
        branch for branch in branches
        if branch == "nJet" or branch.startswith("Jet_")
    ]

    return jet_branches


def save_branch_metadata(year, root_file, tree, jet_branches):
    """
    Save branch metadata files for the selected year.

    This creates three files:

    1. metadata/branches_mixedYEAR.txt
       Contains all branches and their data types.

    2. metadata/jet_branches_mixedYEAR_with_types.txt
       Contains only Jet branches and their data types.

    3. metadata/jet_branches_mixedYEAR.txt
       Contains only Jet branch names.

    The third file is useful for extraction.
    The first two are useful for documentation.
    """
    metadata_dir = Path("metadata")
    metadata_dir.mkdir(parents=True, exist_ok=True)

    all_branches_file = metadata_dir / f"branches_mixed{year}.txt"
    jet_branches_with_types_file = metadata_dir / f"jet_branches_mixed{year}_with_types.txt"
    jet_branches_file = metadata_dir / f"jet_branches_mixed{year}.txt"

    all_branches = list(tree.keys())
    typenames = tree.typenames()

    with all_branches_file.open("w") as out:
        out.write(f"Input file: {root_file}\n")
        out.write(f"TTree: {TREE_NAME}\n")
        out.write(f"Number of events: {tree.num_entries}\n")
        out.write(f"Number of branches: {len(all_branches)}\n\n")
        out.write("Branches:\n")

        for branch in all_branches:
            out.write(f"{branch}: {typenames[branch]}\n")

    with jet_branches_with_types_file.open("w") as out:
        for branch in jet_branches:
            out.write(f"{branch}: {typenames[branch]}\n")

    with jet_branches_file.open("w") as out:
        for branch in jet_branches:
            out.write(f"{branch}\n")

    print(f"Saved full branch metadata: {all_branches_file}")
    print(f"Saved Jet branch metadata with types: {jet_branches_with_types_file}")
    print(f"Saved Jet branch list: {jet_branches_file}")


def extract_jets(year, root_file, jet_branches, step_size, max_parts=None):
    """
    Extract Jet branches from the ROOT file and save them as Parquet chunks.

    The output files will be saved in:

        outputs/jets/YEAR/

    Example for 2016:

        outputs/jets/2016/jets_2016_part0000.parquet
        outputs/jets/2016/jets_2016_part0001.parquet
        outputs/jets/2016/jets_2016_part0002.parquet
    """
    output_dir = Path("outputs") / "jets" / year
    output_dir.mkdir(parents=True, exist_ok=True)

    files = {root_file: TREE_NAME}

    total_saved_events = 0
    total_parts = 0

    print("\nStarting chunked Jet extraction...")
    print(f"Output directory: {output_dir}")
    print(f"Step size: {step_size}")

    for part_index, arrays in enumerate(
        uproot.iterate(
            files,
            expressions=jet_branches,
            library="ak",
            step_size=step_size,
        )
    ):
        if max_parts is not None and part_index >= max_parts:
            print(f"Stopping early because --max-parts={max_parts}")
            break

        output_file = output_dir / f"jets_{year}_part{part_index:04d}.parquet"

        ak.to_parquet(arrays, output_file)

        events_in_part = len(arrays)
        branches_in_part = len(ak.fields(arrays))

        total_saved_events += events_in_part
        total_parts += 1

        print(
            f"Saved {output_file} "
            f"with {events_in_part} events "
            f"and {branches_in_part} branches"
        )

    return total_parts, total_saved_events


def main():
    args = parse_args()

    year = args.year
    root_file = ROOT_FILES[year]

    print(f"Selected year: {year}")
    print(f"ROOT file: {root_file}")

    print("\nOpening ROOT file...")
    opened_file = uproot.open(root_file)
    tree = opened_file[TREE_NAME]

    total_events = tree.num_entries
    total_branches = len(tree.keys())

    print("ROOT file opened successfully.")
    print(f"TTree: {TREE_NAME}")
    print(f"Total events: {total_events}")
    print(f"Total branches: {total_branches}")

    print("\nFinding Jet branches...")
    jet_branches = find_jet_branches(tree)

    print(f"Number of Jet branches found: {len(jet_branches)}")
    print("First 5 Jet branches:", jet_branches[:5])

    save_branch_metadata(year, root_file, tree, jet_branches)

    total_parts, total_saved_events = extract_jets(
        year=year,
        root_file=root_file,
        jet_branches=jet_branches,
        step_size=args.step_size,
        max_parts=args.max_parts,
    )

    print("\nExtraction complete.")
    print(f"Total Parquet parts written: {total_parts}")
    print(f"Total events saved: {total_saved_events}")
    print(f"Expected events from ROOT file: {total_events}")

    if args.max_parts is None:
        if total_saved_events == total_events:
            print("Verification passed: saved event count matches ROOT file.")
        else:
            print("Warning: saved event count does not match ROOT file.")
    else:
        print("Partial test run complete. Full event-count verification skipped.")


if __name__ == "__main__":
    main()
