from pathlib import Path
import awkward as ak

base = Path("inputs/parquet_friends/week3_eval2")

for p in sorted(base.rglob("*.parquet")):
    print("\nFILE:", p)
    arr = ak.from_parquet(p)
    print("fields:", arr.fields)
    print("events:", len(arr))
    for field in arr.fields[:5]:
        print(f"  {field}:", arr[field][:3])
