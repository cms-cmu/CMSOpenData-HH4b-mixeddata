#!/usr/bin/env python3

import copy
import json
from pathlib import Path

METADATA_DIR = Path("configs/metadata/datasets_HH4b_Run2/2024_v2_cmu_eval2")
PARQUET_DIR = Path("inputs/parquet_friends/week3_eval2")
MANIFEST = PARQUET_DIR / "manifest.json"

OUTPUTS = {
    "classifier_inputs_week3_cmu.json": "classifier_inputs_week3_cmu_parquet.json",
    "fvt_inputs_week3_cmu.json": "fvt_inputs_week3_cmu_parquet.json",
}


def main():
    manifest = json.loads(MANIFEST.read_text())

    lookup = {}
    for row in manifest:
        key = (row["friend_name"], row["pico_path"], row["root_friend_path"])
        lookup[key] = row

    for input_name, output_name in OUTPUTS.items():
        src = METADATA_DIR / input_name
        dst = METADATA_DIR / output_name

        data = json.loads(src.read_text())
        new_data = {}

        for friend_name, block in data.items():
            new_block = copy.deepcopy(block)
            new_block["data"] = []

            for item in block["data"]:
                pico = item[0]
                friends = item[1]
                new_friends = []

                for friend in friends:
                    root_friend_path = friend["chunk"]["path"]
                    key = (friend_name, pico["path"], root_friend_path)

                    if key not in lookup:
                        continue

                    row = lookup[key]
                    new_friend = copy.deepcopy(friend)

                    n_events = row["entry_stop"] - row["entry_start"]

                    new_friend["start"] = 0
                    new_friend["stop"] = n_events
                    new_friend["chunk"]["path"] = row["parquet_path"]
                    new_friend["chunk"]["uuid"] = None
                    new_friend["chunk"]["num_entries"] = n_events
                    new_friend["chunk"]["entry_start"] = None
                    new_friend["chunk"]["entry_stop"] = None
                    new_friend["chunk"]["branches"] = row["branches"]

                    new_friends.append(new_friend)

                if new_friends:
                    new_data_item = [copy.deepcopy(pico), new_friends]
                    new_block["data"].append(new_data_item)

            new_data[friend_name] = new_block

        dst.write_text(json.dumps(new_data, indent=2))
        print(f"WROTE {dst}")


if __name__ == "__main__":
    main()
