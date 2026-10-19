"""Compare the primary RDS with the backup CSV without modifying either source.

Run: python3 review_timestamps.py
Requires Rscript and the R data.table package. Python uses only its standard library.
Exit codes: 0 = match after midnight text normalization, 2 = differences,
1 = comparison could not finish. See comparison/latest_run.json for current status.
"""

from pathlib import Path
import argparse
from datetime import datetime, timezone
import hashlib
import json
import shutil
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent


def checksum(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--rds", type=Path, default=ROOT / "data/Black Carbon Concentrations.RDS")
    parser.add_argument("--csv", type=Path, default=ROOT / "data/Black Carbon Concentrations.csv")
    parser.add_argument("--output", type=Path, default=ROOT / "comparison")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    status = {"started_utc": datetime.now(timezone.utc).isoformat(),
              "status": "running", "rds": args.rds.name, "csv": args.csv.name,
              "method": "Compare original row order; normalize date-only CSV text to midnight for comparison only.",
              "sources_modified": False}
    status_path = args.output / "latest_run.json"
    status_path.write_text(json.dumps(status, indent=2) + "\n")
    try:
        rscript = shutil.which("Rscript")
        if not rscript:
            raise RuntimeError("Rscript is required. Install R and its data.table package.")
        status["sha256"] = {"rds": checksum(args.rds), "csv": checksum(args.csv)}
        with tempfile.TemporaryDirectory(prefix="ucdavis_compare_") as temp:
            result = subprocess.run(
                [rscript, str(ROOT / "scripts/compare_sources.R"),
                 str(args.rds.resolve()), str(args.csv.resolve()), temp],
                capture_output=True, text=True)
            if result.returncode not in (0, 2):
                raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "R comparison failed.")
            for report in Path(temp).iterdir():
                shutil.copy2(report, args.output / report.name)
            status["status"] = "match" if result.returncode == 0 else "differences_found"
            (args.output / "source_sha256.txt").write_text(
                f'{status["sha256"]["rds"]}  {args.rds.name}\n'
                f'{status["sha256"]["csv"]}  {args.csv.name}\n')
            print(result.stdout)
            if result.stderr:
                print(result.stderr)
        code = result.returncode
    except Exception as error:
        status.update(status="failed", error=str(error),
                      note="Previous comparison tables, if present, were not refreshed. Do not treat them as results for this run.")
        print(f"Comparison could not finish: {error}")
        code = 1
    status["finished_utc"] = datetime.now(timezone.utc).isoformat()
    status_path.write_text(json.dumps(status, indent=2) + "\n")
    print(f'Status: {status["status"]}. Reports: {args.output}')
    return code


if __name__ == "__main__":
    raise SystemExit(main())
