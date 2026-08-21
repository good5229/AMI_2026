#!/usr/bin/env python3
"""Create a pre-confirmatory provenance manifest without reading MAD y_test."""
from __future__ import annotations

import argparse
from pathlib import Path
import zipfile

import numpy as np

from v13_common import (
    RAW_ROOT, ROOT, V13_DATA, V13ContractError, atomic_write_json, load_json,
    mad_paths, sha256_file,
)


def file_record(path: Path) -> dict[str, object]:
    return {"path": str(path.relative_to(ROOT)), "bytes": path.stat().st_size, "sha256": sha256_file(path)}


def label_counts(values: np.ndarray) -> dict[str, int]:
    return {str(int(label)): int(count) for label, count in zip(*np.unique(values, return_counts=True))}


def npz_headers(path: Path) -> dict[str, dict[str, object]]:
    """Read NPY headers only.  In particular this never deserializes y_test."""
    headers: dict[str, dict[str, object]] = {}
    with zipfile.ZipFile(path) as archive:
        names = {name.removesuffix(".npy") for name in archive.namelist() if name.endswith(".npy")}
        expected = {"x_train", "y_train", "x_test", "y_test"}
        if names != expected:
            raise V13ContractError(f"MAD schema mismatch: {sorted(names)}")
        for name in sorted(names):
            with archive.open(f"{name}.npy") as handle:
                version = np.lib.format.read_magic(handle)
                reader = np.lib.format.read_array_header_1_0 if version == (1, 0) else np.lib.format.read_array_header_2_0
                shape, _fortran_order, dtype = reader(handle)
                headers[name] = {"shape": list(shape), "dtype": str(dtype)}
    return headers


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--confirmatory-y-test-counts", action="store_true", help="Explicitly allow aggregate MAD y_test counts.")
    args = parser.parse_args()
    registry = load_json(V13_DATA / "v13_external_dataset_registry.json")
    records = {record["dataset_id"]: record for record in registry.get("records", [])}
    mad_npz, mad_readme = mad_paths()
    if not mad_npz.is_file():
        raise V13ContractError("MAD.npz is required for audit")
    headers = npz_headers(mad_npz)
    shapes = {key: value["shape"] for key, value in headers.items()}
    dtypes = {key: value["dtype"] for key, value in headers.items()}
    if shapes["x_train"][1:] != [14, 48] or shapes["x_test"][1:] != [14, 48]:
        raise V13ContractError("MAD tensors are not [sample,14,48]")
    if shapes["y_train"] != [shapes["x_train"][0]] or shapes["y_test"] != [shapes["x_test"][0]]:
        raise V13ContractError("MAD label/sample cardinalities mismatch")
    with np.load(mad_npz, allow_pickle=False) as archive:
        y_train_counts = label_counts(archive["y_train"])
        y_test_counts = label_counts(archive["y_test"]) if args.confirmatory_y_test_counts else "NOT_READ_PRE_CONFIRMATORY"
    mad_files = [file_record(path) for path in (mad_npz, mad_readme, RAW_ROOT / "MAD" / "LICENSE") if path.is_file()]
    ucr_dir = RAW_ROOT / "UCR_Italianpowerdemand"
    ucr_files = [file_record(path) for path in sorted(ucr_dir.glob("2*_UCR_Anomaly_Italianpowerdemand_*.txt"))]
    for record in ucr_files:
        absolute = ROOT / str(record["path"])
        record["rows"] = sum(1 for _ in absolute.open(encoding="utf-8"))
    archive_path = RAW_ROOT / "UCR_TimeSeriesAnomalyDatasets2021.zip"
    if archive_path.is_file():
        ucr_files.append(file_record(archive_path))
    manifest = {
        "schema_version": "v13-raw-external-manifest-1",
        "phase": "CONFIRMATORY_Y_TEST_COUNTS_ONLY" if args.confirmatory_y_test_counts else "PRE_CONFIRMATORY",
        "claim_boundary": "External benchmark provenance only; never streetlight field accuracy or fault probability.",
        "datasets": {
            "MAD": {
                "source_url": records["MAD_METERING_ANOMALY_DIAGNOSIS_GITHUB_2025"]["source_url"],
                "license": records["MAD_METERING_ANOMALY_DIAGNOSIS_GITHUB_2025"]["license"],
                "access_status": "LOCAL_IGNORED_SOURCE_PRESENT",
                "files": mad_files,
                "mad_npz_sha256": sha256_file(mad_npz),
                "shapes": shapes,
                "dtypes": dtypes,
                "train_label_counts": y_train_counts,
                "test_label_counts": y_test_counts,
                "meter_ids": "NOT_PRESENT",
                "timestamps": "NOT_PRESENT",
                "track_b": "NOT_ASSESSABLE",
                "lg_s3": "UNAVAILABLE_NORMALIZATION_PROVENANCE",
            },
            "REFIT_ANNOTATED_LOAD": {
                "source_url": records["REFIT_ANNOTATED_LOAD_ANOMALIES_2019"]["source_url"],
                "license": records["REFIT_ANNOTATED_LOAD_ANOMALIES_2019"]["license"],
                "access_status": "LOCAL_OFFICIAL_FILES_UNAVAILABLE" if not (RAW_ROOT / "REFIT").exists() else "LOCAL_FILES_PRESENT_UNVERIFIED",
                "files": [],
            },
            "UCR_ITALIANPOWERDEMAND": {
                "source_url": records["UCR_ANOMALY_ARCHIVE_ITALIANPOWERDEMAND_2021"]["source_url"],
                "license": records["UCR_ANOMALY_ARCHIVE_ITALIANPOWERDEMAND_2021"]["license"],
                "access_status": "LOCAL_FILES_PRESENT_LICENSE_UNKNOWN" if ucr_files else "LOCAL_FILES_UNAVAILABLE",
                "files": ucr_files,
            },
        },
    }
    # A v0.12R freeze witness is intentionally a hash pointer, not a copy.
    v12_source = ROOT / "lightguard_v0_1" / "reports" / "v12r" / "reproducibility_manifest.json"
    if not v12_source.is_file():
        raise V13ContractError("Cannot witness v0.12R freeze: reproducibility manifest is missing")
    v12_freeze = {
        "schema_version": "v12r-freeze-witness-1",
        "phase": "PRE_CONFIRMATORY",
        "v12r_reproducibility_manifest": str(v12_source.relative_to(ROOT)),
        "v12r_reproducibility_manifest_sha256": sha256_file(v12_source),
        "purpose": "v0.13 external benchmark code must not mutate v0.12R artifacts.",
    }
    atomic_write_json(V13_DATA / "v12r_freeze_manifest.json", v12_freeze, immutable=not args.confirmatory_y_test_counts)
    atomic_write_json(V13_DATA / "v13_raw_external_manifest.json", manifest)
    print(f"Wrote {V13_DATA / 'v13_raw_external_manifest.json'} ({manifest['phase']})")


if __name__ == "__main__":
    main()
