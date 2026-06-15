import uproot
import awkward as ak
from pathlib import Path


ROOT_FILE = (
    "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/"
    "mixed2016_3bDvTMix4bDvT_v0/"
    "picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root"
)

TREE_NAME = "Events"

BRANCH_LIST_FILE = Path("metadata/jet_branches_mixed2016.txt")

OUTPUT_DIR = Path("outputs/jets/2016")

STEP_SIZE = "50 MB"


def load_branch_list(branch_list_file):
    """
    Load branch names from a text file.

    The file should contain one branch name per line.
    Example:
        nJet
        Jet_pt
        Jet_eta
    """
    with branch_list_file.open("r") as f:
        branches = [line.strip() for line in f if line.strip()]

    return branches


def main():
    print("Loading Jet branch list...")
    jet_branches = load_branch_list(BRANCH_LIST_FILE)

    print(f"Number of Jet branches: {len(jet_branches)}")
    print("First 5 Jet branches:", jet_branches[:5])

    print("\nCreating output directory...")
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    print("\nOpening ROOT file to check total events...")
    root_file = uproot.open(ROOT_FILE)
    tree = root_file[TREE_NAME]
    total_events = tree.num_entries

    print(f"Tree name: {TREE_NAME}")
    print(f"Total events in ROOT file: {total_events}")

    print("\nStarting chunked extraction...")

    files = {ROOT_FILE: TREE_NAME}

    total_saved_events = 0
    total_parts = 0

    for part_index, arrays in enumerate(
        uproot.iterate(
            files,
            expressions=jet_branches,
            library="ak",
            step_size=STEP_SIZE,
        )
    ):
        output_file = OUTPUT_DIR / f"jets_2016_part{part_index:04d}.parquet"

        ak.to_parquet(arrays, output_file)

        events_in_part = len(arrays)
        total_saved_events += events_in_part
        total_parts += 1

        print(
            f"Saved {output_file} "
            f"with {events_in_part} events "
            f"and {len(ak.fields(arrays))} branches"
        )

    print("\nExtraction complete.")
    print(f"Total Parquet parts written: {total_parts}")
    print(f"Total events saved: {total_saved_events}")
    print(f"Expected events from ROOT file: {total_events}")

    if total_saved_events == total_events:
        print("Verification passed: saved event count matches ROOT file.")
    else:
        print("Warning: saved event count does not match ROOT file.")


if __name__ == "__main__":
    main()
