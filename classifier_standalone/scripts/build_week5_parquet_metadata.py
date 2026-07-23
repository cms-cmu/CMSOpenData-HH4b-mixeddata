from pathlib import Path
import shutil
import yaml

repo = Path.cwd()

src = (
    repo
    / "classifier_standalone/configs/metadata/"
    "datasets_HH4b_Run2/2024_v2_cmu"
)

dst = (
    repo
    / "classifier_standalone/configs/metadata/"
    "datasets_HH4b_Run2/2024_v2_week5_parquet"
)

production = repo / "outputs/consolidated_production"

dst.mkdir(parents=True, exist_ok=True)

metadata_files = [
    "data.yml",
    "TT.yml",
    "GluGluToHHTo4B.yml",
    "ZH4b.yml",
    "ZZ4b.yml",
]

for name in metadata_files:
    shutil.copy2(src / name, dst / name)


def parquet_path(dataset: str) -> str:
    return str(
        production
        / f"{dataset}_consolidated.parquet"
    )


def set_if_available(pico: dict, dataset: str) -> bool:
    path = production / f"{dataset}_consolidated.parquet"

    if path.exists():
        pico["files"] = [str(path)]
        return True

    pico["files"] = []
    return False


# ------------------------------------------------------------
# DATA
# ------------------------------------------------------------
path = dst / "data.yml"

with path.open() as handle:
    data = yaml.safe_load(handle)

data_ready = []
data_missing = []

for year, year_info in data["data"].items():
    pico = year_info.get("picoAOD", {})

    for era, info in pico.items():
        if not isinstance(info, dict):
            continue

        if year.startswith("UL16"):
            dataset = f"data2016{era}_{year}"
        elif year == "UL17":
            dataset = f"data2017{era}_UL17"
        elif year == "UL18":
            dataset = f"data2018{era}_UL18"
        else:
            continue

        if set_if_available(info, dataset):
            data_ready.append(dataset)
        else:
            data_missing.append(dataset)

with path.open("w") as handle:
    yaml.safe_dump(
        data,
        handle,
        sort_keys=False,
    )


# ------------------------------------------------------------
# TTBAR
# ------------------------------------------------------------
path = dst / "TT.yml"

with path.open() as handle:
    tt = yaml.safe_load(handle)

tt_processes = [
    "TTTo2L2Nu",
    "TTToHadronic",
    "TTToSemiLeptonic",
]

tt_ready = []
tt_expected = []

for process in tt_processes:
    for year, info in tt[process].items():
        if year in {"xs", "nSamples"}:
            continue

        if not isinstance(info, dict):
            continue

        pico = info.get("picoAOD")

        if not isinstance(pico, dict):
            continue

        dataset = f"{process}_{year}"
        expected = parquet_path(dataset)

        pico["files"] = [expected]
        tt_expected.append(dataset)

        if Path(expected).exists():
            tt_ready.append(dataset)

with path.open("w") as handle:
    yaml.safe_dump(
        tt,
        handle,
        sort_keys=False,
    )


# ------------------------------------------------------------
# HH
# Keep only cHHH1.
# ------------------------------------------------------------
path = dst / "GluGluToHHTo4B.yml"

with path.open() as handle:
    hh = yaml.safe_load(handle)

for process, years in hh.items():
    if not isinstance(years, dict):
        continue

    for year, info in years.items():
        if not isinstance(info, dict):
            continue

        pico = info.get("picoAOD")

        if not isinstance(pico, dict):
            continue

        dataset = f"{process}_{year}"

        if process == "GluGluToHHTo4B_cHHH1":
            set_if_available(pico, dataset)
        else:
            pico["files"] = []

with path.open("w") as handle:
    yaml.safe_dump(
        hh,
        handle,
        sort_keys=False,
    )


# ------------------------------------------------------------
# ZH
# Keep only ZH4b.
# ------------------------------------------------------------
path = dst / "ZH4b.yml"

with path.open() as handle:
    zh = yaml.safe_load(handle)

for process, years in zh.items():
    if not isinstance(years, dict):
        continue

    for year, info in years.items():
        if not isinstance(info, dict):
            continue

        pico = info.get("picoAOD")

        if not isinstance(pico, dict):
            continue

        dataset = f"{process}_{year}"

        if process == "ZH4b":
            set_if_available(pico, dataset)
        else:
            pico["files"] = []

with path.open("w") as handle:
    yaml.safe_dump(
        zh,
        handle,
        sort_keys=False,
    )


# ------------------------------------------------------------
# ZZ
# ------------------------------------------------------------
path = dst / "ZZ4b.yml"

with path.open() as handle:
    zz = yaml.safe_load(handle)

for process, years in zz.items():
    if not isinstance(years, dict):
        continue

    for year, info in years.items():
        if not isinstance(info, dict):
            continue

        pico = info.get("picoAOD")

        if not isinstance(pico, dict):
            continue

        dataset = f"{process}_{year}"

        set_if_available(
            pico,
            dataset,
        )

with path.open("w") as handle:
    yaml.safe_dump(
        zz,
        handle,
        sort_keys=False,
    )


print("=" * 72)
print("WEEK 5 PARQUET METADATA CREATED")
print("=" * 72)
print("Directory:", dst)
print()
print("Data ready:", len(data_ready))
print("Data unavailable:", data_missing)
print(
    "ttbar currently ready:",
    f"{len(tt_ready)}/{len(tt_expected)}",
)
print()
print("Created:")

for name in metadata_files:
    print(" ", dst / name)
