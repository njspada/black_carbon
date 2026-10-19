> Historical CSV-only review. All 63 records were later confirmed as midnight in the RDS. See ../../README.md for current findings and ../../comparison/ for the comparison outputs.

# Timestamp review

The full-file scan found 63 timestamp parsing failures. Of these, 63 contain a valid calendar date but no time of day.

These are format mismatches with the expected `YYYY-MM-DD HH:MM:SS` format, not blank timestamps. No corrections have been applied.

The original source and working copy were verified byte-identical using SHA-256. See `extraction_manifest.json` for the checksum and scan counts.

## What to inspect next

Compare surrounding observations from the same sensor and consult the export logic. A date-only value might represent midnight with its time omitted, but the current evidence does not establish that. Do not silently append `00:00:00`. If the time cannot be recovered, retain the calendar date and flag the time as unknown.

## All affected records

Record numbers are one-based CSV data-record positions, excluding the header. The companion `timestamp_parse_failures.csv` includes all original columns for these records.

| Source record | Sensor ID | Original date value |
| ------- | --------- | -----------|
| 84995   | AL80-0004 | 2026-04-13 |
| 182949  | AL80-0004 | 2026-06-20 |
| 211594  | AL80-0004 | 2026-07-18 |
| 230190  | AL80-0004 | 2026-07-31 |
| 305761  | AL80-0008 | 2025-12-25 |
| 378970  | AL80-0008 | 2026-02-14 |
| 584946  | AL80-0009 | 2026-07-04 |
| 667031  | AL80-0009 | 2026-08-30 |
| 690069  | AL80-0009 | 2026-09-15 |
| 733675  | AL80-0010 | 2026-04-01 |
| 853169  | AL80-0010 | 2026-06-23 |
| 1129602 | AL80-0012 | 2026-03-26 |
| 1174150 | AL80-0012 | 2026-04-26 |
| 1311286 | AL80-0013 | 2026-02-03 |
| 1372253 | AL80-0014 | 2025-12-14 |
| 1372254 | AL80-0014 | 2025-12-14 |
| 1469871 | AL80-0021 | 2026-04-27 |
| 1482645 | AL80-0021 | 2026-05-06 |
| 1595722 | AL80-0021 | 2026-08-19 |
| 1640610 | AL80-0022 | 2026-03-26 |
| 1792313 | AL80-0022 | 2026-07-10 |
| 1826125 | AL80-0022 | 2026-08-11 |
| 1865125 | AL80-0024 | 2025-12-12 |
| 1927390 | AL80-0024 | 2026-01-26 |
| 1960507 | AL80-0024 | 2026-02-18 |
| 2086792 | AL80-0024 | 2026-05-25 |
| 2119942 | AL80-0024 | 2026-06-17 |
| 2140105 | AL80-0024 | 2026-07-01 |
| 2183308 | AL80-0024 | 2026-07-31 |
| 2280267 | AL80-0025 | 2026-04-08 |
| 2368125 | AL80-0025 | 2026-06-08 |
| 2401246 | AL80-0025 | 2026-07-01 |
| 2459918 | AL80-0027 | 2026-04-24 |
| 2495911 | AL80-0027 | 2026-05-19 |
| 2570814 | AL80-0027 | 2026-07-10 |
| 2703775 | AL80-0028 | 2026-05-23 |
| 2723908 | AL80-0028 | 2026-06-06 |
| 2846323 | AL80-0030 | 2026-05-01 |
| 2860717 | AL80-0030 | 2026-05-11 |
| 3277796 | AL80-0031 | 2026-04-26 |
| 3277797 | AL80-0031 | 2026-04-26 |
| 3326342 | AL80-0031 | 2026-05-18 |
| 3326343 | AL80-0031 | 2026-05-18 |
| 3377244 | AL80-0031 | 2026-06-11 |
| 3725574 | AL80-0034 | 2026-04-14 |
| 3985477 | AL80-0035 | 2026-05-15 |
| 4318933 | AL80-0051 | 2026-05-18 |
| 4525284 | AL80-0051 | 2026-06-19 |
| 4572046 | AL80-0078 | 2026-02-05 |
| 4866569 | AL80-0078 | 2026-06-23 |
| 4888041 | AL80-0078 | 2026-07-08 |
| 4912165 | AL80-0078 | 2026-07-25 |
| 4928823 | AL80-0083 | 2026-04-02 |
| 5484172 | AL80-0088 | 2026-03-31 |
| 5753049 | AL80-0088 | 2026-06-14 |
| 5761688 | AL80-0088 | 2026-06-20 |
| 5770323 | AL80-0088 | 2026-06-26 |
| 5778961 | AL80-0088 | 2026-07-02 |
| 5787602 | AL80-0088 | 2026-07-08 |
| 5796243 | AL80-0088 | 2026-07-14 |
| 5806316 | AL80-0088 | 2026-07-21 |
| 5837633 | AL80-0088 | 2026-09-15 |
| 5846274 | AL80-0088 | 2026-09-21 |
