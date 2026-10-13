"""Copy the raw CSV and extract timestamp problems without correcting values.

Run: python3 review_timestamps.py
Requires pandas. Outputs are in timestamp_review/ beside this script.
"""

from pathlib import Path
import hashlib
import json
import shutil
from io import StringIO

import pandas as pd


ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "Black Carbon Concentrations.csv"
OUTPUT = ROOT / "timestamp_review"
COPY = OUTPUT / "Black Carbon Concentrations_working_copy.csv"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
CHUNK_SIZE = 100_000


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def write_review(invalid):
    date_only = invalid["date"].str.fullmatch(r"\d{4}-\d{2}-\d{2}")
    valid_dates = pd.to_datetime(invalid["date"], format="%Y-%m-%d", errors="coerce").notna()
    count = int((date_only & valid_dates).sum())
    lines = [
        "# Timestamp review", "",
        f"The full-file scan found {len(invalid)} timestamp parsing failures. "
        f"Of these, {count} contain a valid calendar date but no time of day.", "",
        "These are format mismatches with the expected `YYYY-MM-DD HH:MM:SS` format, "
        "not blank timestamps. No corrections have been applied.", "",
        "The original source and working copy were verified byte-identical using SHA-256. "
        "See `extraction_manifest.json` for the checksum and scan counts.", "",
        "## What to inspect next", "",
        "Compare surrounding observations from the same sensor and consult the export logic. "
        "A date-only value might represent midnight with its time omitted, but the current "
        "evidence does not establish that. Do not silently append `00:00:00`. If the time "
        "cannot be recovered, retain the calendar date and flag the time as unknown.", "",
        "## All affected records", "",
        "Record numbers are one-based CSV data-record positions, excluding the header. "
        "The companion `timestamp_parse_failures.csv` includes all original columns for these records.", "",
        "| Source record | Sensor ID | Original date value |",
        "| --- | --- | --- |",
    ]
    for row in invalid.itertuples(index=False):
        sensor = str(row.SensorID).replace("|", "\\|")
        date = str(row.date).replace("|", "\\|")
        lines.append(f"| {row.source_record_number} | {sensor} | {date} |")
    (OUTPUT / "TIMESTAMP_REVIEW.md").write_text("\n".join(lines) + "\n")


def main():
    OUTPUT.mkdir(exist_ok=True)
    source_hash = checksum(SOURCE)
    if not COPY.exists():
        # Exclusive creation prevents accidentally overwriting a working copy.
        with SOURCE.open("rb") as source, COPY.open("xb") as target:
            shutil.copyfileobj(source, target, length=1024 * 1024)
    copy_hash = checksum(COPY)
    if copy_hash != source_hash:
        raise RuntimeError("Working copy differs from the source. No files were overwritten. "
                           "Review the existing copy before running this extraction again.")
    print("Verified byte-identical working copy.", flush=True)

    failures, missing_records = [], []
    offset = 0
    # Disable NA conversion to preserve every original field as written.
    for chunk in pd.read_csv(COPY, dtype=str, keep_default_na=False,
                             chunksize=CHUNK_SIZE):
        raw = chunk["date"]
        parsed = pd.to_datetime(raw, format=DATE_FORMAT, errors="coerce")
        # Mirror pandas' default missing-marker handling used in the EDA,
        # while keeping the raw strings in the exported review records.
        missing = pd.read_csv(StringIO(raw.to_frame().to_csv(index=False)),
                              dtype="string", skip_blank_lines=False)["date"].isna()
        missing.index = chunk.index
        for mask, reason, collection in [
            (parsed.isna() & ~missing, "timestamp_parse_failure", failures),
            (missing, "missing_timestamp", missing_records),
        ]:
            rows = chunk.loc[mask].copy()
            rows.insert(0, "source_record_number", rows.index + 1)
            rows.insert(1, "issue", reason)
            collection.append(rows)
        offset += len(chunk)
        if offset % 1_000_000 == 0:
            print(f"Scanned {offset:,} records...", flush=True)

    invalid = pd.concat(failures, ignore_index=True)
    absent = pd.concat(missing_records, ignore_index=True)
    invalid.to_csv(OUTPUT / "timestamp_parse_failures.csv", index=False)
    absent.to_csv(OUTPUT / "missing_timestamps.csv", index=False)
    counts = invalid.groupby("date", dropna=False).size().rename("records").reset_index()
    counts.to_csv(OUTPUT / "timestamp_value_counts.csv", index=False)
    write_review(invalid)
    manifest = {
        "source": SOURCE.name, "working_copy": COPY.name,
        "sha256": source_hash, "rows_scanned": offset,
        "timestamp_format": DATE_FORMAT,
        "parse_failures": len(invalid), "missing_timestamps": len(absent),
        "source_record_number": "One-based CSV data-record number, excluding the header; not a physical line number.",
        "corrections_applied": False,
    }
    (OUTPUT / "extraction_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest, indent=2))
    print("\nOriginal timestamp values that failed parsing:")
    print(counts.to_string(index=False))


if __name__ == "__main__":
    main()
