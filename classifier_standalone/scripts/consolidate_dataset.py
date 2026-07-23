#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path

import awkward as ak
import uproot
import yaml


DEFAULT_MAP = Path(
    "classifier_standalone/docs/dataset_files_map.yml"
)

COMPONENTS = (
    "picoAOD",
    "HCR_input",
    "JCM_weight",
    "FvT_weight",
    "SvB_MA",
)

REQUIRED_CLASSIFIER_BRANCHES = {
    "event",
    "weight",
    "threeTag",
    "fourTag",
    "passHLT",
    "SB",
    "SR",
    "ZHSR",
    "ZZSR",
    "HHSR",
    "nSelJets",
    "xW",
    "xbW",
    "CanJet_pt",
    "CanJet_eta",
    "CanJet_phi",
    "CanJet_mass",
    "NotCanJet_pt",
    "NotCanJet_eta",
    "NotCanJet_phi",
    "NotCanJet_mass",
    "NotCanJet_isSelJet",
    "pseudoTagWeight",
    "FvT",
}

REQUIRED_REFERENCE_BRANCHES = {
    "ref_SvB_MA_phh",
    "ref_SvB_MA_pzz",
    "ref_SvB_MA_pzh",
    "ref_SvB_MA_ptt",
    "ref_SvB_MA_pmj",
    "ref_SvB_MA_q_1234",
    "ref_SvB_MA_q_1324",
    "ref_SvB_MA_q_1423",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Merge picoAOD and classifier friend trees "
            "into one consolidated ROOT file."
        )
    )

    parser.add_argument(
        "dataset",
        help="Dataset key from dataset_files_map.yml.",
    )

    parser.add_argument(
        "--map",
        type=Path,
        default=DEFAULT_MAP,
        help="Dataset file map.",
    )

    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help=(
            "Output ROOT path. Default: "
            "outputs/consolidated_production/"
            "<dataset>_consolidated.root"
        ),
    )

    parser.add_argument(
        "--max-entries-per-chunk",
        type=int,
        default=None,
        help=(
            "Optional smoke-test limit applied to "
            "each synchronized chunk."
        ),
    )

    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite an existing output file.",
    )

    return parser.parse_args()


def load_dataset_map(path: Path) -> dict:
    with path.open() as handle:
        data = yaml.safe_load(handle)

    if not isinstance(data, dict):
        raise RuntimeError(
            f"Invalid dataset map: {path}"
        )

    return data


def get_entry_count(url: str) -> int:
    with uproot.open(url) as root_file:
        return root_file["Events"].num_entries


def read_tree(
    url: str,
    start: int,
    stop: int,
) -> ak.Array:
    with uproot.open(url) as root_file:
        tree = root_file["Events"]

        return tree.arrays(
            entry_start=start,
            entry_stop=stop,
            library="ak",
        )


def merge_components(
    pico: ak.Array,
    hcr: ak.Array,
    jcm: ak.Array,
    fvt: ak.Array,
    svb: ak.Array,
) -> ak.Array:

    canonical_friend_names = (
        set(ak.fields(hcr))
        | set(ak.fields(jcm))
    )

    merged: dict[str, ak.Array] = {}

    for branch in ak.fields(pico):
        if branch in canonical_friend_names:
            output_name = f"pico_{branch}"
        else:
            output_name = branch

        merged[output_name] = pico[branch]

    for branch in ak.fields(hcr):
        merged[branch] = hcr[branch]

    for branch in ak.fields(jcm):
        merged[branch] = jcm[branch]

    for branch in ak.fields(fvt):
        merged[branch] = fvt[branch]

    for branch in ak.fields(svb):
        normalized_branch = branch

        if normalized_branch.startswith("SvB_MA_"):
            normalized_branch = normalized_branch.removeprefix(
                "SvB_MA_"
            )

        merged[
            f"ref_SvB_MA_{normalized_branch}"
        ] = svb[branch]

    return ak.zip(
        merged,
        depth_limit=1,
    )


def validate_required_branches(
    fields: set[str],
) -> None:

    missing_classifier = sorted(
        REQUIRED_CLASSIFIER_BRANCHES - fields
    )

    missing_reference = sorted(
        REQUIRED_REFERENCE_BRANCHES - fields
    )

    if missing_classifier:
        raise RuntimeError(
            "Missing required classifier branches: "
            + ", ".join(missing_classifier)
        )

    if missing_reference:
        raise RuntimeError(
            "Missing required SvB reference branches: "
            + ", ".join(missing_reference)
        )


def main() -> None:
    args = parse_args()

    datasets = load_dataset_map(
        args.map
    )

    if args.dataset not in datasets:
        available = "\n  ".join(
            sorted(datasets)
        )

        raise KeyError(
            f"Unknown dataset: {args.dataset}\n\n"
            f"Available datasets:\n  {available}"
        )

    files = datasets[args.dataset]

    missing_components = [
        component
        for component in COMPONENTS
        if component not in files
    ]

    if missing_components:
        raise RuntimeError(
            "Dataset is missing components: "
            + ", ".join(missing_components)
        )

    chunk_counts = {
        component: len(files[component])
        for component in COMPONENTS
    }

    if len(set(chunk_counts.values())) != 1:
        raise RuntimeError(
            "Component file-list lengths do not match: "
            f"{chunk_counts}"
        )

    nchunks = chunk_counts["picoAOD"]

    if nchunks == 0:
        raise RuntimeError(
            "Dataset has no input chunks."
        )

    output = args.output

    if output is None:
        output = Path(
            "outputs/consolidated_production"
        ) / (
            f"{args.dataset}_consolidated.root"
        )

    if output.exists() and not args.overwrite:
        raise FileExistsError(
            f"Output already exists: {output}\n"
            "Use --overwrite to replace it."
        )

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    print("=" * 80)
    print("DATASET:", args.dataset)
    print("CHUNKS: ", nchunks)
    print("OUTPUT: ", output)

    if args.max_entries_per_chunk is not None:
        print(
            "SMOKE LIMIT PER CHUNK:",
            args.max_entries_per_chunk,
        )

    print("=" * 80)

    reference_fields: list[str] | None = None

    total_source_entries = 0
    total_written_entries = 0

    output_file = uproot.recreate(
        output
    )

    try:
        output_tree = None

        for index in range(nchunks):

            print(
                f"\n--- Chunk {index + 1}/{nchunks} ---"
            )

            urls = {
                component: files[component][index]
                for component in COMPONENTS
            }

            entry_counts = {
                component: get_entry_count(url)
                for component, url in urls.items()
            }

            for component in COMPONENTS:
                print(
                    f"  {component:12s}: "
                    f"{entry_counts[component]} entries"
                )

            if len(set(entry_counts.values())) != 1:
                raise RuntimeError(
                    "\nSource component entry-count "
                    f"mismatch in dataset {args.dataset}, "
                    f"chunk {index}:\n"
                    + "\n".join(
                        f"  {component}: {count}"
                        for component, count
                        in entry_counts.items()
                    )
                )

            source_entries = entry_counts[
                "picoAOD"
            ]

            total_source_entries += (
                source_entries
            )

            read_entries = source_entries

            if (
                args.max_entries_per_chunk
                is not None
            ):
                read_entries = min(
                    source_entries,
                    args.max_entries_per_chunk,
                )

            print(
                "  Reading:",
                read_entries,
                "entries",
            )

            read_step_size = 25_000

            for batch_start in range(
                0,
                read_entries,
                read_step_size,
            ):
                batch_stop = min(
                    batch_start + read_step_size,
                    read_entries,
                )

                print(
                    f"  Batch: [{batch_start}, {batch_stop})"
                )

                pico = read_tree(
                    urls["picoAOD"],
                    batch_start,
                    batch_stop,
                )

                hcr = read_tree(
                    urls["HCR_input"],
                    batch_start,
                    batch_stop,
                )

                jcm = read_tree(
                    urls["JCM_weight"],
                    batch_start,
                    batch_stop,
                )

                fvt = read_tree(
                    urls["FvT_weight"],
                    batch_start,
                    batch_stop,
                )

                svb = read_tree(
                    urls["SvB_MA"],
                    batch_start,
                    batch_stop,
                )

                merged = merge_components(
                    pico=pico,
                    hcr=hcr,
                    jcm=jcm,
                    fvt=fvt,
                    svb=svb,
                )

                current_fields = list(
                    ak.fields(merged)
                )

                validate_required_branches(
                    set(current_fields)
                )

                if reference_fields is None:
                    reference_fields = (
                        current_fields
                    )

                    print(
                        "  Merged branches:",
                        len(reference_fields),
                    )

                else:
                    reference_set = set(
                        reference_fields
                    )

                    current_set = set(
                        current_fields
                    )

                    missing = sorted(
                        reference_set
                        - current_set
                    )

                    extra = sorted(
                        current_set
                        - reference_set
                    )

                    if missing or extra:
                        raise RuntimeError(
                            "\nMerged schema mismatch in "
                            f"dataset {args.dataset}, "
                            f"chunk {index}.\n"
                            f"Missing branches: {missing}\n"
                            f"Extra branches: {extra}"
                        )

                    merged = ak.zip(
                        {
                            branch: merged[branch]
                            for branch
                            in reference_fields
                        },
                        depth_limit=1,
                    )

                payload = {
                    branch: merged[branch]
                    for branch
                    in reference_fields
                }

                if output_tree is None:
                    output_file["Events"] = payload
                    output_tree = output_file[
                        "Events"
                    ]
                else:
                    output_tree.extend(
                        payload
                    )

                total_written_entries += len(
                    merged
                )

                print(
                    "  Written so far:",
                    total_written_entries,
                )

    except Exception:
        output_file.close()

        if output.exists():
            output.unlink()

        raise

    else:
        output_file.close()

    print("\nReopening consolidated output...")

    with uproot.open(output) as root_file:
        tree = root_file["Events"]

        final_entries = tree.num_entries
        final_fields = set(
            tree.keys()
        )

    validate_required_branches(
        final_fields
    )

    if (
        final_entries
        != total_written_entries
    ):
        raise RuntimeError(
            "Final output entry-count mismatch: "
            f"expected {total_written_entries}, "
            f"found {final_entries}."
        )

    print("\nFINAL SUMMARY")
    print(
        "  Dataset:",
        args.dataset,
    )
    print(
        "  Source entries:",
        total_source_entries,
    )
    print(
        "  Written entries:",
        final_entries,
    )
    print(
        "  Branches:",
        len(final_fields),
    )
    print(
        "  Output:",
        output,
    )

    print(
        "\nCONSOLIDATED DATASET: PASS"
    )


if __name__ == "__main__":
    main()
