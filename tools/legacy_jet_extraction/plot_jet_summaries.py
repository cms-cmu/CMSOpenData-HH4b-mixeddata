from pathlib import Path

import awkward as ak
import matplotlib.pyplot as plt


YEARS = ["2016", "2017", "2018"]

INPUT_BASE_DIR = Path("outputs") / "jets"
PLOT_DIR = Path("plots") / "jets"


def load_year_arrays(year):
    """
    Load all Jet-only Parquet files for one year.

    Example input folder:
        outputs/jets/2016/

    The folder contains files such as:
        jets_2016_part0000.parquet
        jets_2016_part0001.parquet
        jets_2016_part0002.parquet
    """
    input_dir = INPUT_BASE_DIR / year
    parquet_files = sorted(input_dir.glob("*.parquet"))

    if not parquet_files:
        raise FileNotFoundError(f"No Parquet files found in {input_dir}")

    arrays = [ak.from_parquet(parquet_file) for parquet_file in parquet_files]

    return ak.concatenate(arrays)


def plot_njet(year_arrays):
    """
    Plot the nJet distribution for each year.

    nJet is event-level, so each event has one nJet value.
    """
    plt.figure()

    for year, arrays in year_arrays.items():
        njet = ak.to_numpy(arrays["nJet"])
        plt.hist(
            njet,
            bins=range(0, 16),
            histtype="step",
            density=True,
            label=year,
        )

    plt.xlabel("Number of jets per event (nJet)")
    plt.ylabel("Normalized events")
    plt.title("nJet Distribution by Year")
    plt.legend()
    plt.tight_layout()

    output_file = PLOT_DIR / "njet_by_year.png"
    plt.savefig(output_file)
    plt.close()

    print(f"Saved {output_file}")


def plot_jet_pt(year_arrays):
    """
    Plot the Jet_pt distribution for each year.

    Jet_pt is a jagged array because each event can contain multiple jets.
    We flatten the array so every jet contributes one value to the histogram.
    """
    plt.figure()

    for year, arrays in year_arrays.items():
        jet_pt = ak.to_numpy(ak.flatten(arrays["Jet_pt"]))
        plt.hist(
            jet_pt,
            bins=80,
            range=(0, 500),
            histtype="step",
            density=True,
            label=year,
        )

    plt.xlabel("Jet pT")
    plt.ylabel("Normalized jets")
    plt.title("Jet pT Distribution by Year")
    plt.legend()
    plt.tight_layout()

    output_file = PLOT_DIR / "jet_pt_by_year.png"
    plt.savefig(output_file)
    plt.close()

    print(f"Saved {output_file}")


def plot_jet_eta(year_arrays):
    """
    Plot the Jet_eta distribution for each year.

    Jet_eta is also jagged, so we flatten it before plotting.
    """
    plt.figure()

    for year, arrays in year_arrays.items():
        jet_eta = ak.to_numpy(ak.flatten(arrays["Jet_eta"]))
        plt.hist(
            jet_eta,
            bins=80,
            range=(-5, 5),
            histtype="step",
            density=True,
            label=year,
        )

    plt.xlabel("Jet eta")
    plt.ylabel("Normalized jets")
    plt.title("Jet eta Distribution by Year")
    plt.legend()
    plt.tight_layout()

    output_file = PLOT_DIR / "jet_eta_by_year.png"
    plt.savefig(output_file)
    plt.close()

    print(f"Saved {output_file}")


def main():
    PLOT_DIR.mkdir(parents=True, exist_ok=True)

    year_arrays = {}

    for year in YEARS:
        print(f"Loading {year} Parquet files...")
        arrays = load_year_arrays(year)
        year_arrays[year] = arrays

        print(f"  Events loaded: {len(arrays)}")
        print(f"  Fields loaded: {len(ak.fields(arrays))}")

    print("\nCreating plots...")
    plot_njet(year_arrays)
    plot_jet_pt(year_arrays)
    plot_jet_eta(year_arrays)

    print("\nPlotting complete.")


if __name__ == "__main__":
    main()
