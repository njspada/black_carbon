# Black carbon data validation

This started as a blind exploratory review of sensor measurements, without a specific research question. The focus is understanding the data and checking its quality before making cleaning decisions.

**The RDS is the primary source for analysis.** Start with [exploratory_rds_plotly.ipynb](exploratory_rds_plotly.ipynb). The CSV is a backup for comparison, and the original CSV analysis is archived.

## Findings so far

The dataset contains **6,059,765 records from 27 sensors**, spanning December 2025–September 2026. Counts, missingness checks, sensor coverage, and daily summaries use the full file. Distributions and correlations use a reproducible 50,000-row sample.

| Finding | Status |
| --- | --- |
| 63 CSV records have a date but no time | All 63 are exact midnight (`00:00:00 UTC`) in the RDS. The main notebook includes them in daily summaries. |
| Latitude and longitude are each missing in 55.9% of rows | Missing at the same positions in both files. Check against deployment records. |
| `Smoothed` is missing in 9.7% of rows | Missing at the same positions in both files. Confirm how this field is generated. |
| 39.5% of BC readings are negative | Kept for now. Confirm instrument guidance before deciding how to handle them. |
| Sensor coverage is uneven | Review deployment periods, sampling intervals, and gaps. |
| Duplicate records and conflicting sensor/timestamp pairs | Not checked yet. This is the next validation step. |

### What the RDS comparison showed

The full-file comparison found the same 6,059,765 rows and 11 columns in both files. Sensor IDs and all nine numeric columns match exactly, including missing-value positions. These checks support comparing the records in their existing row order.

All timestamps match once the 63 date-only CSV values are expressed as midnight for comparison. The RDS contains exactly 63 midnight timestamps and no missing timestamps or fractional seconds. The main notebook reports zero invalid timestamps. For example, record 84,995 for sensor `AL80-0004` is `2026-04-13` in the CSV and `2026-04-13 00:00:00 UTC` in the RDS.

| Column | Missing in CSV | Missing in RDS | Same missing positions |
| --- | ---: | ---: | --- |
| Smoothed | 585,614 | 585,614 | Yes |
| Latitude | 3,388,529 | 3,388,529 | Yes |
| Longitude | 3,388,529 | 3,388,529 | Yes |

No other columns had missing values under the comparison's CSV `NA` interpretation. Using the RDS does not recover these missing measurements or coordinates.

The earlier 63 parsing failures came from the CSV leaving out `00:00:00`. We still cannot tell whether Excel caused this. R can also leave out midnight when converting a timestamp to text, so it could have happened during export. The RDS stores dates as `POSIXct`/`POSIXt` with a UTC timezone, but we still need to confirm how the original sensor times were recorded. Agreement between the files does not independently prove that the upstream measurements are correct.

Neither source has been edited. The main notebook reads the RDS timestamps directly and keeps source record numbers for reference. This README combines the earlier inspection findings and project notes; supporting tables are in [comparison/](comparison/).

### Why there is a new notebook

I made the RDS notebook after checking the 63 date-only records against the original timestamps. I also switched the plots to Plotly so we can hover over values, zoom into dates, and turn sensors on or off when looking at patterns. I kept the CSV notebook in the archive so we can still look back at the initial analysis.

## Project layout

```text
black_carbon/
  README.md
  exploratory_rds_plotly.ipynb       Main analysis with interactive plots
  review_timestamps.py              Optional RDS–CSV comparison entry point
  scripts/compare_sources.R        Reads the RDS and compares both files
  data/                            Local raw data; ignored by Git
    Black Carbon Concentrations.RDS
    Black Carbon Concentrations.csv
  comparison/                      Small reports suitable for version control
  archive/
    exploratory_csv.ipynb           Original CSV analysis
    extract_csv_timestamps.py       Original CSV-only extraction utility
    timestamp_review/              Historical CSV-only findings
```

The raw CSV, any `Black Carbon Concentrations` CSV working copy, and RDS files are ignored by Git, including if placed outside `data/`. Small comparison CSVs remain available for version control. Raw data must be obtained separately when cloning the repository.

## Run the main analysis

Place the RDS in `data/`. The backup CSV is only needed for the optional comparison cell and comparison script. Run commands below from the repository folder.

Install R with `Rscript` on your PATH. In R:

```r
install.packages("data.table")
```

Install the Python dependencies and open the notebook:

```bash
python3 -m pip install pandas numpy plotly nbformat jupyter
jupyter notebook exploratory_rds_plotly.ipynb
```

Run the cells from top to bottom. R loads the RDS into memory and transfers dates as epoch seconds through a temporary file. Python scans that file in chunks, then deletes it. Allow enough memory for the RDS and temporary disk space roughly the size of the CSV. The notebook discovers `data/` when opened from the repository, its parent, or `archive/`; update `DATA_DIR` for another location.

Use Jupyter or a Plotly-capable VS Code environment for interactive charts. Static previews may not display them. The final notebook section shows how to export a standalone interactive HTML chart.

## Compare the RDS with the backup CSV

If something looks wrong in the RDS, use the CSV as a cross-check:

```bash
python3 review_timestamps.py
```

This uses Python's standard library plus R and `data.table`. It reads both sources without changing them or creating a full CSV working copy. It compares rows in their original order, including all non-date fields, missing-value positions, and timestamps. Date-only CSV strings are expanded to midnight only for comparison. Differences may indicate changed values or changed row order; investigate before deciding which file to trust. This is not a duplicate-record check or an automatic repair tool.

For another pair of files, use `--rds PATH --csv PATH`; use `--output DIRECTORY` to keep their reports separate. A missing, unreadable, or structurally unexpected RDS is reported as a failed comparison. The script does not silently switch the analysis to CSV.

Exit codes are `0` for a match after midnight formatting normalization, `2` for differences, and `1` if the comparison could not finish. Check [comparison/latest_run.json](comparison/latest_run.json) first: after a failed run, older tables remain available but are explicitly marked as not refreshed.

Comparison outputs:

- [column_comparison.csv](comparison/column_comparison.csv): full-file value comparisons and missing counts for each non-date column.
- [date_only_comparison.csv](comparison/date_only_comparison.csv): all date-only CSV records, RDS UTC timestamps, epoch seconds, and matching checks.
- [other_timestamp_differences.csv](comparison/other_timestamp_differences.csv): remaining timestamp differences; header-only when none are found. Fractional seconds are flagged conservatively for review.
- [neighboring_timestamps.csv](comparison/neighboring_timestamps.csv): affected records and adjacent source rows with sensor IDs.
- [inspection_log.txt](comparison/inspection_log.txt): scan results and R session information.
- [source_sha256.txt](comparison/source_sha256.txt): source checksums, also recorded in `latest_run.json`. The current CSV checksum matches the archived extraction manifest.

## Archived CSV work

[archive/exploratory_csv.ipynb](archive/exploratory_csv.ipynb) preserves the initial analysis and strict date parsing. Its 63 parsing failures are explained above. It now reads the backup from `data/` and needs `matplotlib` in addition to pandas, NumPy, and Jupyter.

[archive/timestamp_review/](archive/timestamp_review/) preserves the original affected records and extraction metadata. Its unresolved-time interpretation predates the RDS comparison and is superseded by this README. To reproduce the old extraction, run `python3 archive/extract_csv_timestamps.py`; this creates an ignored working copy in `data/` and refreshes the historical extraction outputs. Use `review_timestamps.py` for current comparisons.

## Next steps

1. Check full-file duplicates and conflicting sensor/timestamp pairs. The exploratory sample is not sufficient for these checks.
2. Review sampling intervals and gaps by sensor against deployment periods.
3. Investigate missing coordinates, missing smoothed values, and unusual measurements by sensor and date.
4. Confirm units, original sensor timezone handling, sampling frequency, deployment history, and instrument quality-control rules, including negative BC readings.
5. Apply agreed cleaning rules and document each change with before/after checks.

Preserve raw data, source record identifiers, and the reasons for any corrections or exclusions. Flag uncertain records rather than silently deleting or filling them.
