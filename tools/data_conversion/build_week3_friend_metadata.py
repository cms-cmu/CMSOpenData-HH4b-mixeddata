#!/usr/bin/env python3

import argparse
import json
from pathlib import Path

import uproot
import yaml

TREE = "Events"

MAP_PATH = Path("docs/dataset_files_map.yml")
OUT_DIR = Path("configs/metadata/datasets_HH4b_Run2/2024_v2")

HCR_OUT = OUT_DIR / "classifier_inputs_week3_cmu.json"
FVT_OUT = OUT_DIR / "fvt_inputs_week3_cmu.json"


def fetch_root_chunk(path):
    with uproot.open(path) as f:
        tree = f[TREE]
        return {
            "path": path,
            "name": TREE,
            "uuid": str(f.file.uuid),
            "branches": list(tree.keys()),
            "num_entries": tree.num_entries,
            "entry_start": None,
            "entry_stop": None,
        }


def target_json(chunk):
    return {
        "path": chunk["path"],
        "name": chunk["name"],
        "uuid": chunk["uuid"],
    }


def friend_item_json(friend_chunk):
    return {
        "start": 0,
        "stop": friend_chunk["num_entries"],
        "chunk": {
            "path": friend_chunk["path"],
            "name": friend_chunk["name"],
            "uuid": friend_chunk["uuid"],
            "num_entries": friend_chunk["num_entries"],
            "entry_start": None,
            "entry_stop": None,
        },
    }


def build_friend_metadata(dataset_map, friend_key, friend_name, max_files_per_dataset):
    data = []
    branches = None
    used = 0
    skipped = []

    for dataset, files in dataset_map.items():
        pico_files = files.get("picoAOD", [])
        friend_files = files.get(friend_key, [])

        if not pico_files or not friend_files:
            skipped.append((dataset, "missing picoAOD or friend files"))
            continue

        if len(pico_files) != len(friend_files):
            skipped.append(
                (
                    dataset,
                    f"file count mismatch: picoAOD={len(pico_files)}, {friend_key}={len(friend_files)}",
                )
            )
            continue

        pairs = list(zip(pico_files, friend_files))
        if max_files_per_dataset is not None:
            pairs = pairs[:max_files_per_dataset]

        for pico_path, friend_path in pairs:
            print(f"[{friend_name}] {dataset}")
            print(f"  target: {pico_path}")
            print(f"  friend: {friend_path}")

            pico_chunk = fetch_root_chunk(pico_path)
            friend_chunk = fetch_root_chunk(friend_path)

            if pico_chunk["num_entries"] != friend_chunk["num_entries"]:
                print(
                    f"  NOTE: picoAOD has {pico_chunk['num_entries']} entries, "
                    f"{friend_key} has {friend_chunk['num_entries']} entries. "
                    "Keeping the friend-tree entry range."
                )

            if branches is None:
                branches = friend_chunk["branches"]
            elif set(branches) != set(friend_chunk["branches"]):
                print(f"  WARNING: branch set differs for {friend_path}")

            data.append([
                target_json(pico_chunk),
                [friend_item_json(friend_chunk)],
            ])
            used += 1

    if branches is None:
        raise RuntimeError(f"No usable files found for {friend_key}")

    print(f"\nBuilt {friend_name}: {used} matched picoAOD ↔ {friend_key} pairs")

    if skipped:
        print(f"Skipped {len(skipped)} datasets:")
        for dataset, reason in skipped:
            print(f"  - {dataset}: {reason}")

    return {
        friend_name: {
            "name": friend_name,
            "branches": branches,
            "data": data,
        }
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--max-files-per-dataset",
        type=int,
        default=2,
        help="Limit files per dataset for the Week 4 tiny test metadata.",
    )
    args = parser.parse_args()

    with MAP_PATH.open() as f:
        dataset_map = yaml.safe_load(f)

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    hcr = build_friend_metadata(
        dataset_map,
        friend_key="HCR_input",
        friend_name="HCR_input",
        max_files_per_dataset=args.max_files_per_dataset,
    )

    fvt = build_friend_metadata(
        dataset_map,
        friend_key="FvT_weight",
        friend_name="FvT_weight",
        max_files_per_dataset=args.max_files_per_dataset,
    )

    HCR_OUT.write_text(json.dumps(hcr, indent=2))
    FVT_OUT.write_text(json.dumps(fvt, indent=2))

    print(f"\nWrote {HCR_OUT}")
    print(f"Wrote {FVT_OUT}")


if __name__ == "__main__":
    main()
