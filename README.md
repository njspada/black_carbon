# Black carbon data validation

Volunteer work to explore, validate, and clean sensor measurements for future analysis. The current focus is data quality; no specific research question has been defined yet.

## Findings so far

The dataset contains **6,059,765 records from 27 sensors**, with parsed dates spanning December 2025–September 2026.

| Finding | Status |
| --- | --- |
| 63 timestamps contain a date but no time of day | Extracted for review; no corrections applied. |
| Latitude and longitude are each missing in 55.9% of rows | Investigate against sensor deployment records. |
| `Smoothed` is missing in 9.7% of rows | Confirm how this field is generated. |
| 39.5% of BC readings are negative | Review instrument guidance before deciding how to handle them. |
| Sensor coverage is uneven | Check deployment periods, sampling intervals, and gaps. |

Counts and missingness checks cover the full file. Distribution plots and correlations use a reproducible 50,000-row sample.

## Files

- [exploratory.ipynb](exploratory.ipynb): initial exploration, summaries, and plots.
- [review_timestamps.py](review_timestamps.py): copies the source, verifies its checksum, and extracts timestamp issues in batches.
- [timestamp_review/](timestamp_review/): affected records, source record numbers, and extraction metadata.
- [Timestamp review](timestamp_review/TIMESTAMP_REVIEW.md): readable table of all 63 affected timestamps.

## Run locally

Keep `Black Carbon Concentrations.csv` in the repository folder alongside the notebook and script. The source CSV and its large working copy are excluded from Git.

```bash
python3 -m pip install pandas numpy matplotlib jupyter
python3 review_timestamps.py
jupyter notebook exploratory.ipynb
```

Run the notebook from top to bottom. The timestamp script creates its working copy and review outputs in `timestamp_review/`.

## Next steps

1. Inspect neighboring readings for the 63 date-only timestamps. Confirm whether the export omitted midnight times before assigning a time.
2. Check full-file duplicates, conflicting sensor/timestamp pairs, and sampling gaps.
3. Investigate missing coordinates, missing smoothed values, and unusual measurements by sensor and date.
4. Confirm units, timezone, sampling frequency, deployment history, and instrument quality-control rules with the project coordinator.
5. Apply agreed cleaning rules and document each change, with before/after checks.

Preserve the raw data. Flag uncertain records rather than silently deleting or filling them. Keep source record identifiers and reasons for all corrections or exclusions.
