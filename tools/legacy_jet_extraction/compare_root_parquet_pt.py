from pathlib import Path
import argparse
import sys

import awkward as ak
import numpy as np
import uproot
import matplotlib.pyplot as plt


ROOT_FILES = {
    "2016": "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2016_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root",
    "2017": "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2017_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root",
    "2018": "root://cmsdata.phys.cmu.edu//store/group/HH4b/Run2/mixed2018_3bDvTMix4bDvT_v0/picoAOD_3bDvTMix4bDvT_4b_wJCM_v0_newSBDef.root",
}

TREE_NAME = "Events"
VARIABLE = "Jet_pt"

PARQUET_BASE_DIR = Path("outputs") / "jets"
PLOT_DIR = Path("plots") / "validation"


def load_root_jet_pt(year):
    """Load Jet_pt directly from the original ROOT file."""
    root_file = ROOT_FILES[year]

    print(f"Loading {VARIABLE} directly from ROOT for {year}...")
    print(f"ROOT file: {root_file}")

    with uproot.open(root_file) as f:
        tree = f[TREE_NAME]
        jet_pt = tree[VARIABLE].array(library="ak")

    print(f"ROOT events loaded: {len(jet_pt)}")
    print(f"ROOT jets loaded: {len(ak.flatten(jet_pt, axis=None))}")

    return jet_pt


def load_parquet_jet_pt(year):
    """Load Jet_pt from the extracted Jet-only Parquet files."""
    parquet_dir = PARQUET_BASE_DIR / year
    parquet_files = sorted(parquet_dir.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files found in {parquet_dir}")

    print(f"\nLoading {VARIABLE} from Parquet for {year}...")
    print(f"Parquet directory: {parquet_dir}")
    print(f"Number of Parquet files: {len(parquet_files)}")

    arrays = []
    for parquet_file in parquet_files:
        print(f"  Reading {parquet_file}")
        arr = ak.from_parquet(parquet_file)
        arrays.append(arr[VARIABLE])

    jet_pt = ak.concatenate(arrays, axis=0)

    print(f"Parquet events loaded: {len(jet_pt)}")
    print(f"Parquet jets loaded: {len(ak.flatten(jet_pt, axis=None))}")

    return jet_pt


def flatten_to_numpy(array):
    """Flatten a jagged Awkward array into a regular NumPy array."""
    flat = ak.flatten(array, axis=None)
    return ak.to_numpy(flat)


def compare_arrays(root_jet_pt, parquet_jet_pt):
    """Compare event counts, jet counts, and values."""
    print("\nComparing ROOT and Parquet arrays...")

    root_event_count = len(root_jet_pt)
    parquet_event_count = len(parquet_jet_pt)

    root_jet_counts = ak.num(root_jet_pt, axis=1)
    parquet_jet_counts = ak.num(parquet_jet_pt, axis=1)

    same_event_count = root_event_count == parquet_event_count
    same_jets_per_event = bool(ak.all(root_jet_counts == parquet_jet_counts))

    root_flat = flatten_to_numpy(root_jet_pt)
    parquet_flat = flatten_to_numpy(parquet_jet_pt)

    same_flat_length = len(root_flat) == len(parquet_flat)

    if same_flat_length:
        same_values = np.allclose(
            root_flat,
            parquet_flat,
            rtol=0,
            atol=1e-6,
            equal_nan=True,
        )
        max_abs_diff = np.nanmax(np.abs(root_flat - parquet_flat))
    else:
        same_values = False
        max_abs_diff = None

    print(f"Same number of events: {same_event_count}")
    print(f"Same jets per event: {same_jets_per_event}")
    print(f"Same flattened jet count: {same_flat_length}")
    print(f"Same Jet_pt values in order: {same_values}")
    print(f"Maximum absolute difference: {max_abs_diff}")

    return root_flat, parquet_flat, same_event_count, same_jets_per_event, same_flat_length, same_values


def make_comparison_plot(year, root_flat, parquet_flat, bins, pt_min, pt_max):
    """Make ROOT vs Parquet Jet_pt comparison plot."""
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    # Remove non-finite values for histogramming.
    root_clean = root_flat[np.isfinite(root_flat)]
    parquet_clean = parquet_flat[np.isfinite(parquet_flat)]

    bin_edges = np.linspace(pt_min, pt_max, bins + 1)

    root_hist, _ = np.histogram(root_clean, bins=bin_edges)
    parquet_hist, _ = np.histogram(parquet_clean, bins=bin_edges)

    hist_match = np.array_equal(root_hist, parquet_hist)

    ratio = np.divide(
        parquet_hist,
        root_hist,
        out=np.full_like(parquet_hist, np.nan, dtype=float),
        where=root_hist != 0,
    )

    print("\nHistogram comparison:")
    print(f"Histogram bins: {bins}")
    print(f"Histogram range: {pt_min} to {pt_max}")
    print(f"ROOT histogram total entries in range: {root_hist.sum()}")
    print(f"Parquet histogram total entries in range: {parquet_hist.sum()}")
    print(f"Histogram bin counts match exactly: {hist_match}")

    fig, (ax_top, ax_bottom) = plt.subplots(
        2,
        1,
        figsize=(8, 7),
        sharex=True,
        gridspec_kw={"height_ratios": [3, 1]},
    )

    ax_top.hist(
        root_clean,
        bins=bin_edges,
        histtype="step",
        density=True,
        label="ROOT direct",
    )

    ax_top.hist(
        parquet_clean,
        bins=bin_edges,
        histtype="step",
        density=True,
        label="Parquet extracted",
        linestyle="--",
    )

    ax_top.set_ylabel("Normalized entries")
    ax_top.set_title(f"{year} ROOT vs Parquet comparison: Jet_pt")
    ax_top.legend()

    ax_bottom.step(
        bin_edges[:-1],
        ratio,
        where="post",
        label="Parquet / ROOT",
    )

    ax_bottom.axhline(1.0, linestyle="--")
    ax_bottom.set_xlabel("Jet_pt")
    ax_bottom.set_ylabel("Ratio")
    ax_bottom.set_ylim(0.8, 1.2)

    output_path = PLOT_DIR / f"root_vs_parquet_Jet_pt_{year}.png"
    fig.tight_layout()
    fig.savefig(output_path, dpi=150)
    plt.close(fig)

    print(f"\nSaved comparison plot: {output_path}")

    return hist_match, output_path


def main():
    parser = argparse.ArgumentParser(
        description="Compare Jet_pt directly from ROOT with Jet_pt from extracted Parquet files."
    )

    parser.add_argument(
        "--year",
        required=True,
        choices=["2016", "2017", "2018"],
        help="Run 2 year to compare.",
    )

    parser.add_argument(
        "--bins",
        type=int,
        default=80,
        help="Number of histogram bins.",
    )

    parser.add_argument(
        "--pt-min",
        type=float,
        default=0.0,
        help="Minimum Jet_pt value for histogram.",
    )

    parser.add_argument(
        "--pt-max",
        type=float,
        default=500.0,
        help="Maximum Jet_pt value for histogram.",
    )

    args = parser.parse_args()

    root_jet_pt = load_root_jet_pt(args.year)
    parquet_jet_pt = load_parquet_jet_pt(args.year)

    (
        root_flat,
        parquet_flat,
        same_event_count,
        same_jets_per_event,
        same_flat_length,
        same_values,
    ) = compare_arrays(root_jet_pt, parquet_jet_pt)

    hist_match, output_path = make_comparison_plot(
        year=args.year,
        root_flat=root_flat,
        parquet_flat=parquet_flat,
        bins=args.bins,
        pt_min=args.pt_min,
        pt_max=args.pt_max,
    )

    passed = (
        same_event_count
        and same_jets_per_event
        and same_flat_length
        and same_values
        and hist_match
    )

    print("\nFinal result:")
    if passed:
        print("PASS: ROOT and Parquet Jet_pt match.")
        print(f"Plot saved at: {output_path}")
    else:
        print("FAIL: ROOT and Parquet Jet_pt do not fully match.")
        sys.exit(1)


if __name__ == "__main__":
    main()
