from pathlib import Path

import awkward as ak


EXPECTED_EVENTS = {
    "2016": 115764,
    "2017": 111951,
    "2018": 162896,
}

EXPECTED_FIELD_COUNT = 41

REQUIRED_BRANCHES = [
    "run",
    "event",
    "luminosityBlock",
    "nJet",
    "Jet_pt",
]


def validate_year(year, expected_events):
    """
    Validate the Jet-only Parquet outputs for one year.

    This checks:
    1. Parquet files exist.
    2. Each file can be read with Awkward Array.
    3. Each file has the expected number of selected fields.
    4. Required event ID and Jet branches are present.
    5. The total event count matches the original ROOT file event count.
    """
    print(f"\nChecking year {year}...")

    output_dir = Path("outputs") / "jets" / year
    parquet_files = sorted(output_dir.glob("*.parquet"))

    if not parquet_files:
        print(f"FAIL: No Parquet files found in {output_dir}")
        return False

    print(f"Parquet files found: {len(parquet_files)}")

    total_events = 0
    field_counts = set()
    reference_fields = None
    passed = True

    for parquet_file in parquet_files:
        arrays = ak.from_parquet(parquet_file)

        events_in_file = len(arrays)
        fields = list(ak.fields(arrays))

        total_events += events_in_file
        field_counts.add(len(fields))

        if reference_fields is None:
            reference_fields = fields
        elif fields != reference_fields:
            print(f"WARNING: Field mismatch found in {parquet_file}")
            passed = False

        missing_required = [
            branch for branch in REQUIRED_BRANCHES if branch not in fields
        ]

        if missing_required:
            print(f"FAIL: Missing required branches in {parquet_file}: {missing_required}")
            passed = False

        print(
            f"  {parquet_file.name}: "
            f"{events_in_file} events, "
            f"{len(fields)} selected fields"
        )

    print(f"Total events read from Parquet: {total_events}")
    print(f"Expected events: {expected_events}")
    print(f"Field counts seen: {sorted(field_counts)}")
    print(f"Required branches checked: {REQUIRED_BRANCHES}")

    if total_events != expected_events:
        print(f"FAIL: Event count mismatch for {year}")
        passed = False

    if field_counts != {EXPECTED_FIELD_COUNT}:
        print(f"FAIL: Expected {EXPECTED_FIELD_COUNT} selected fields for {year}")
        passed = False

    if passed:
        print(f"PASS: {year} Parquet validation passed.")
    else:
        print(f"FAIL: {year} Parquet validation failed.")

    return passed


def main():
    all_passed = True

    for year, expected_events in EXPECTED_EVENTS.items():
        year_passed = validate_year(year, expected_events)
        all_passed = all_passed and year_passed

    print("\nValidation summary:")

    if all_passed:
        print("All Jet Parquet outputs passed validation.")
    else:
        print("One or more Jet Parquet outputs failed validation.")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
