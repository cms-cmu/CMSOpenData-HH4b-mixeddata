#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

import awkward as ak
import uproot


TARGET_DATASETS = ("data2016F", "data2016G")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Convert selected ROOT friend trees to small Parquet files."
    )
    parser.add_argument(
        "--metadata-dir",
        default="configs/metadata/datasets_HH4b_Run2/2024_v2_cmu_eval2",
        help="Directory containing classifier_inputs_week3_cmu.json and fvt_inputs_week3_cmu.json",
    )
    parser.add_argument(
        "--output-dir",
        default="inputs/parquet_friends/week3_eval2",
        help="Output directory for Parquet friend files",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=5000,
        help="Maximum number of events to convert from each friend ROOT file",
    )
    return parser.parse_args()


def safe_name(path: str) -> str:
    """
    Convert a ROOT path into a stable local filename.
    Example:
      .../data_UL16_postVFPF/HCR_input.root
    becomes:
      data_UL16_postVFPF__HCR_input.parquet
    """
    parts = path.rstrip("/").split("/")
    sample = parts[-2]
    filename = parts[-1].replace(".root", ".parquet")
    return f"{sample}__{filename}"


def convert_one_friend(friend_name: str, block: dict, output_dir: Path, max_events: int):
    branches = block["branches"]
    tree_name_from_block = block.get("name")

    print(f"\n===== friend group: {friend_name} =====")
    print(f"metadata tree name: {tree_name_from_block}")
    print(f"branch count: {len(branches)}")
    print(f"branches: {branches}")

    converted = []

    for item in block["data"]:
        pico = item[0]
        friend_chunks = item[1]

        pico_path = pico["path"]
        if not any(target in pico_path for target in TARGET_DATASETS):
            continue

        for friend in friend_chunks:
            chunk = friend["chunk"]
            root_path = chunk["path"]

            entry_start = friend.get("start", 0) or 0
            entry_stop = friend.get("stop", None)

            if entry_stop is None:
                entry_stop = chunk.get("num_entries", None)

            if max_events is not None and max_events > 0:
                entry_stop = min(entry_start + max_events, entry_stop)

            out_path = output_dir / friend_name / safe_name(root_path)
            out_path.parent.mkdir(parents=True, exist_ok=True)

            print("\nPICO:", pico_path)
            print("ROOT friend:", root_path)
            print("entry range:", entry_start, entry_stop)
            print("output:", out_path)

            with uproot.open(root_path) as f:
                print("available keys:", list(f.keys()))

                # Friend ROOT files in this metadata use Events as the actual tree name.
                if "Events" in f:
                    tree_name = "Events"
                elif tree_name_from_block in f:
                    tree_name = tree_name_from_block
                else:
                    raise KeyError(
                        f"Could not find Events or {tree_name_from_block} in {root_path}"
                    )

                tree = f[tree_name]
                available = set(tree.keys())
                selected = [b for b in branches if b in available]
                missing = [b for b in branches if b not in available]

                print("using tree:", tree_name)
                print("selected branches:", selected)
                if missing:
                    print("missing branches:", missing)

                arrays = tree.arrays(
                    selected,
                    entry_start=entry_start,
                    entry_stop=entry_stop,
                    library="ak",
                )

            ak.to_parquet(arrays, out_path)
            print(f"WROTE {out_path}")

            converted.append(
                {
                    "friend_name": friend_name,
                    "pico_path": pico_path,
                    "root_friend_path": root_path,
                    "parquet_path": str(out_path),
                    "tree_name": tree_name,
                    "entry_start": entry_start,
                    "entry_stop": entry_stop,
                    "branches": selected,
                }
            )

    return converted


def main():
    args = parse_args()

    metadata_dir = Path(args.metadata_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    inputs = [
        metadata_dir / "classifier_inputs_week3_cmu.json",
        metadata_dir / "fvt_inputs_week3_cmu.json",
    ]

    all_converted = []

    for metadata_file in inputs:
        print("\n" + "=" * 100)
        print("metadata file:", metadata_file)

        if not metadata_file.exists():
            print("missing, skipping")
            continue

        data = json.loads(metadata_file.read_text())

        for friend_name, block in data.items():
            all_converted.extend(
                convert_one_friend(
                    friend_name=friend_name,
                    block=block,
                    output_dir=output_dir,
                    max_events=args.max_events,
                )
            )

    manifest = output_dir / "manifest.json"
    manifest.write_text(json.dumps(all_converted, indent=2))
    print("\n" + "=" * 100)
    print(f"converted files: {len(all_converted)}")
    print(f"manifest: {manifest}")


if __name__ == "__main__":
    main()
