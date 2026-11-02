# Full-file duplicate review

The scan used all 6,059,765 rows in the primary RDS. Nothing was removed or edited.

## What I found

I checked for rows that match across all original columns and for records that share a sensor and timestamp. There are 1,129,237 extra copies of exact rows, mostly from sensor AL80-0035. I also found repeated sensor/timestamp records where the measurements match but coordinates are missing in some copies and present in others. I’ve kept everything for now so we can agree on how to handle those records before changing the analysis.

| Check | Result |
| --- | ---: |
| Source rows | 6,059,765 |
| Sets of exact duplicate rows | 50,461 |
| Rows belonging to an exact duplicate set, including the first copy | 1,179,698 |
| Extra exact copies beyond the first copy of each distinct row | 1,129,237 (18.63% of source rows) |
| Distinct full rows, if exact duplicates were collapsed | 4,930,528 |
| Repeated sensor/timestamp groups | 238,696 |
| Rows in those repeated-key groups | 1,556,288 |
| Repeated-key groups containing only identical rows | 50,341 |
| Repeated-key groups containing different field values | 188,355 |
| Rows in groups with different field values | 376,830 |
| Extra exact copies within groups with different field values | 120 |
| Rows with a missing sensor ID or timestamp | 0 |

Exact-row duplicates and repeated-key conflicts overlap. A sensor/timestamp group can contain two identical copies and another row with different coordinates. Do not add the two categories together.

## Where the repeats occur

Sensor **AL80-0035 accounts for 1,129,171 extra exact copies**. AL80-0031 accounts for 60; the remaining six copies are spread across five sensors. The largest repeated sensor/timestamp group contains 109 rows. See [by_sensor.csv](by_sensor.csv) for all sensors.

All 188,355 groups with differing values differ only in **Latitude and Longitude**. The seven measurement fields (Temperature, RH, Sense, Reference, Attenuation, BC, and Smoothed) match within each group. Every group has exactly one distinct nonmissing latitude and one distinct nonmissing longitude, plus missing entries. No group has competing nonmissing values for either coordinate. See [coordinate_conflict_patterns.csv](coordinate_conflict_patterns.csv).

This pattern could arise from duplicated or overlapping data processing, but the scan does not establish how it happened. Check the source export and deployment history before deciding which records to retain or whether to populate missing coordinates.

## Method and verification

- Exact duplicates compare all 11 original columns. Added source record numbers are excluded from equality checks.
- Numeric comparisons use exact stored values, with data.table numeric rounding disabled. Timestamps are compared as stored; no minute-level rounding is applied.
- Matching missing values count as equal. A missing value and a populated value differ.
- Repeated keys are the exact SensorID and timestamp pair. Different sensors at the same time are not treated as duplicates.
- Source record numbers are one-based RDS row positions. They preserve the order already checked against the CSV.
- Counts were checked with synthetic identical, conflicting, missing-key, and unique-row examples. An independent full-file distinct-row count confirmed 1,129,237 extra exact copies.
- The source SHA-256 matches the earlier RDS inspection: `302a4bb30f6b082b96d2ccc1f981ef8ac5b65c877a2dc5bdf4555a6bf177b97d`.

Run `Rscript scripts/scan_duplicates.R` from the repository to reproduce the scan. Check [status.txt](status.txt) before using outputs. The README and this report describe the inspected dataset; review them if future source data changes.

## Outputs and next step

[summary.csv](summary.csv) contains the headline counts. [example_groups.csv](example_groups.csv) shows up to ten groups per classification; [example_rows.csv](example_rows.csv) shows up to five rows from each example group. These are examples, not complete extracts.

Complete group tables, repeated-key rows, exact duplicate rows (including the first occurrence), and missing-key rows are in ignored `data/duplicate_review/`. They are reproducible local outputs and are not intended for Git.

Discuss a cleaning rule with the project coordinator before deleting any records or filling coordinates. The notebook still uses all raw rows, so its means, distributions, missingness percentages, and sensor coverage counts may be affected by repeated records. Rerun those summaries after any agreed cleaning, keeping a record of what changed.
