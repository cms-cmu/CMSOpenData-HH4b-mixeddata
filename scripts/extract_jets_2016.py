import uproot
import awkward as ak
from pathlib import Path


# Remote ROOT file for the 2016 mixeddata sample
ROOT_FILE = (
    "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/"
    "mixed2016_3bDvTMix4bDvT_v0/"
    "picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root"
)

# Text file containing only the Jet branch names
BRANCH_LIST_FILE = Path("metadata/jet_branches_mixed2016.txt")

# Output Parquet file we will create
OUTPUT_FILE = Path("outputs/jets_2016_test_from_script.parquet")


def load_branch_list(branch_list_file):
    """
    Read branch names from a text file.

    Each line in metadata/jet_branches_mixed2016.txt contains one branch name,
    for example:
        nJet
        Jet_pt
        Jet_eta
    """
    with branch_list_file.open("r") as f:
        branches = [line.strip() for line in f if line.strip()]

    return branches


def main():
    """
    Main workflow:
    1. Load Jet branch names.
    2. Open the ROOT file.
    3. Read only the first 5 events.
    4. Save those events to a Jet-only Parquet file.
    5. Read the Parquet file back to verify it worked.
    """
    print("Loading Jet branch list...")
    jet_branches = load_branch_list(BRANCH_LIST_FILE)

    print(f"Number of Jet branches: {len(jet_branches)}")
    print("First 5 Jet branches:", jet_branches[:5])

    print("\nOpening ROOT file...")
    root_file = uproot.open(ROOT_FILE)
    tree = root_file["Events"]

    print("ROOT file opened successfully.")
    print(f"Total events in ROOT file: {tree.num_entries}")

    print("\nReading first 5 events with only Jet branches...")
    arrays = tree.arrays(
        jet_branches,
        entry_start=0,
        entry_stop=5,
        library="ak",
    )

    print(f"Events loaded: {len(arrays)}")
    print(f"Branches loaded: {len(ak.fields(arrays))}")

    print("\nSaving Jet-only Parquet file...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ak.to_parquet(arrays, OUTPUT_FILE)

    print(f"Saved file: {OUTPUT_FILE}")

    print("\nReading Parquet file back for verification...")
    check_arrays = ak.from_parquet(OUTPUT_FILE)

    print(f"Verified events: {len(check_arrays)}")
    print(f"Verified branches: {len(ak.fields(check_arrays))}")
    print("First event nJet:", check_arrays["nJet"][0])
    print("First event Jet_pt:", check_arrays["Jet_pt"][0])

    print("\nJet extraction test completed successfully.")


if __name__ == "__main__":
    main()
