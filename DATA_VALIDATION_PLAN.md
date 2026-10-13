# Black carbon data validation and cleaning plan

Prepared: October 7, 2026

## Purpose

Prepare the volunteer project's black carbon dataset for reliable future analysis. There is no specific research question yet. The immediate goal is to understand the data, identify quality issues, document validation rules, and produce a traceable cleaned dataset.

This document records initial findings and proposed work. The validation and cleaning steps below have not yet been performed unless explicitly described as completed EDA.

## Data and completed exploration

- Source: `Black Carbon Concentrations.csv` (approximately 666 MB).
- Exploration code: `exploratory.ipynb`.
- Observations: 6,059,765 rows across 27 sensor IDs.
- Columns: `SensorID`, `date`, `Temperature`, `RH`, `Sense`, `Reference`, `Attenuation`, `BC`, `Smoothed`, `Latitude`, and `Longitude`.
- Full-file checks covered missing values, numeric parsing, timestamp parsing, sensor coverage, negative BC counts, and daily BC summaries.
- Distributions, quantiles, and correlations used a reproducible random sample of 50,000 rows. They are not exact full-file statistics.
- The notebook's code cells were run successfully against the complete source file. The source CSV was not modified.

## Initial findings and what they mean

| Finding | Interpretation and validation follow-up |
| --- | --- |
| Parsed timestamps span December 1, 2025, through September 21, 2026. | Confirm the intended collection period and timestamp timezone. This range excludes timestamps that failed parsing. |
| 63 timestamps failed parsing with the format `%Y-%m-%d %H:%M:%S`. | Inspect original values for alternate formats, malformed dates, or other issues. A parsing failure does not by itself prove an invalid observation. |
| Latitude and longitude are each missing in 3,388,529 rows, approximately 55.9% of the file. | Geographic analysis has substantial gaps. Check missingness patterns and whether an authoritative location/deployment registry exists. Do not assume a sensor stayed in one place. |
| `Smoothed` is missing in 585,614 rows, approximately 9.7%. | Determine how it is generated and when it should exist. Missing values may reflect processing or deployment differences. |
| 2,395,127 BC readings are negative, approximately 39.5% of valid numeric BC readings. | Investigate patterns by sensor and time and consult instrument quality-control guidance. Do not automatically delete negatives or replace them with zero. |
| Sensor row counts range from 7 to 1,324,313. | Coverage is uneven. Deployment length, sampling frequency, interruptions, or repeated records could contribute. Counts alone do not identify the cause. |
| `BC`, `Temperature`, `RH`, `Sense`, `Reference`, and `Attenuation` have no missing values or numeric parsing failures. | These fields are structurally complete under the current missing-value and parsing rules. This does not establish measurement accuracy or exclude undocumented sentinel values. |

### Limits of the current EDA

The EDA has not established whether the data contain exact duplicate rows, conflicting measurements at the same sensor and timestamp, unexpected sampling intervals, outages, flatlined signals, or readings outside instrument limits. It has not verified units, calibration, timezone, or deployment metadata.

Sample correlations do not establish causation. Pooled statistics may reflect differences between sensors, deployment periods, or locations. Sample results can miss rare issues. Daily means retain negative readings, exclude missing or unparseable numeric values, and weight observations equally rather than weighting by elapsed time. Uneven sampling may therefore affect their interpretation.

## Principles for cleaning

1. Preserve the original CSV unchanged. Write derived data to separate files.
2. Separate detection from correction: flag an issue before deciding how to handle it.
3. Preserve original values alongside parsed or corrected values when a field changes.
4. Give each source record a stable identifier, such as its one-based CSV data-record number, and record the source file checksum. A record number is not necessarily a physical text-line number.
5. Distinguish missing values, parsing failures, instrument flags, and unusual but potentially valid measurements.
6. Do not invent units, thresholds, timezone conversions, deployment dates, or replacement values.
7. Document each cleaning rule, its rationale, supporting guidance, and the number of affected records.
8. Make the process reproducible and reconcile all retained, excluded, and quarantined records with the original row count.

## Information to request from the project coordinator

| Information | Why it matters |
| --- | --- |
| Data dictionary and units for every field | Establishes what values mean and which checks are appropriate. |
| Instrument make/model and quality-control documentation | Supports valid ranges and interpretation of negative readings, attenuation, and other instrument signals. |
| Expected sampling interval and whether it changes | Allows meaningful gap, timing, and coverage checks. |
| Timestamp timezone and daylight-saving handling | Prevents incorrect conversions, apparent duplicates, and misleading daily summaries. |
| Deployment start/end dates and sensor-location history | Separates expected inactivity from outages and supports location validation. |
| Calibration, maintenance, restart, and filter-change logs | Helps explain discontinuities and periods requiring review. |
| Definition and processing history of `Smoothed` | Establishes expected missingness, zeros, and relationships to raw BC. |
| Missing-value codes, instrument error codes, and export history | Identifies sentinel values and possible overlapping exports. |
| Existing project acceptance and exclusion rules | Keeps cleaning consistent with the project's scientific procedures. |

## Proposed procedure

### 1. Record the source and establish a baseline

- Record filename, byte size, checksum, columns, row count, software versions, and run date.
- Verify CSV structure and identify malformed records without silently skipping them.
- Retain sensor IDs as text and preserve raw timestamp strings.
- Use chunked processing for routine scans of the large file.

**Output:** source inventory and reproducible baseline summary.

### 2. Validate schema, missingness, and parsing

- Check required columns and unexpected columns against the agreed data dictionary.
- Count missing values by column, sensor, and time period.
- Inspect literal placeholders and possible sentinel values separately from standard missing markers.
- Inspect the 63 timestamp parsing failures and test only justified alternative formats.
- Report invalid numeric values and nonfinite values separately from missing values.
- Preserve raw strings for records requiring correction.

**Output:** field-quality table and a record-level issue table with original values and reasons.

### 3. Validate record identity and duplicates

- Count exact duplicate rows across the full file, including duplicates spanning chunks.
- Identify repeated `(SensorID, parsed timestamp)` pairs, keeping unparseable timestamps in a separate review group.
- Distinguish identical records from same-time records with conflicting measurements.
- Investigate whether repeated timestamps reflect expected instrument behavior or overlapping exports.
- Define a justified duplicate-handling rule before excluding records. Do not average conflicts automatically.

**Output:** duplicate summary and reviewable groups of repeated or conflicting records.

**Implementation note:** independent per-chunk duplicate checks are insufficient. Use a global grouping method, disk-backed database, or appropriately partitioned processing to compare records across the complete file.

### 4. Validate timestamps and coverage by sensor

- Check source-order timestamp reversals within each sensor before sorting.
- Sort a derived view by sensor and parsed timestamp for interval analysis.
- Calculate interval distributions and identify repeated timestamps and unusually long gaps.
- Compare gaps with expected cadence and deployment windows when available.
- Summarize daily valid measurement counts, first/last timestamps, and coverage for each sensor.
- Calculate completeness percentages only after expected measurement counts are defined.

**Output:** sensor coverage table, interval summaries, and a gap report.

### 5. Validate measurements and instrument behavior

- Summarize negative BC frequency and magnitude by sensor and time period.
- Inspect extreme values, abrupt shifts, long runs of identical readings, and suspicious repeated zeros.
- Compare candidate events with temperature, RH, attenuation, sense, reference, and available maintenance logs.
- Apply instrument range and error-code checks only after confirming definitions and units.
- Use statistical outlier rules as review flags, not automatic evidence of invalid measurements.
- Define the duration and tolerance for flatline flags using expected cadence and instrument precision.

**Output:** measurement-quality flags, diagnostic plots, and a list of events requiring project review.

### 6. Validate location and derived fields

- Check latitude and longitude against geographic coordinate bounds and identify incomplete coordinate pairs.
- Inspect coordinate changes by sensor and compare them with deployment history.
- Do not fill missing coordinates from a sensor ID alone unless location is verified for the relevant period.
- Examine missing and zero `Smoothed` values by sensor and date.
- Compare `Smoothed` with BC only after its algorithm, window, and expected behavior are known.

**Output:** location-quality report and derived-field review.

### 7. Review findings and establish cleaning rules

- Separate structural corrections from decisions that require instrument or project knowledge.
- Document each proposed action: retain, normalize formatting, correct from an authoritative source, flag, or quarantine.
- Review scientifically consequential choices with the project coordinator, particularly negative BC handling, conflicting duplicates, outlier exclusions, and imputation.
- Retain unresolved observations with explicit flags or in a separate review dataset rather than silently discarding them.

**Output:** a cleaning decision log with rule IDs, rationale, status, and affected record counts.

### 8. Produce and verify derived data

- Implement agreed rules in a rerunnable script or notebook.
- Save cleaned data separately from the raw CSV, with source identifiers and quality flags.
- Save excluded or quarantined records and their reasons.
- Reconcile input and output row counts, accounting explicitly for any duplicate consolidation.
- Compare missingness, sensor/date coverage, and BC summaries before and after cleaning.
- Verify that changed values match documented rules and that rerunning the same inputs produces the same results.

**Output:** cleaned dataset, issue records, decision log, and a before/after validation report.

## Work that can proceed now

Without a research question or additional metadata, we can run structural checks, inspect timestamp failures, identify full-file duplicates and conflicts, describe observed sampling intervals and gaps, profile missingness by sensor/time, check coordinate bounds, and flag unusual measurement patterns.

The next practical step is to create a full-file validation report and record-level issue table. These checks can proceed while project metadata are being requested. Instrument-specific validity judgments, gap acceptance thresholds, location imputation, and measurement exclusions should follow documented project guidance.

## Planned deliverables

| Deliverable | Purpose |
| --- | --- |
| Validation notebook or script | Reproduce all checks and report their parameters. |
| Validation summary | Report issue counts by field, sensor, and period, including limitations. |
| Record-level issue table | Link each flag to its source record, rule, original value, and review status. A record can have multiple flags. |
| Cleaning decision log | Explain each approved transformation or exclusion and its rationale. |
| Cleaned dataset | Supply analysis-ready records with provenance and quality flags under the agreed rules. |
| Quarantine/exclusion dataset | Preserve records set aside and the reasons for doing so. |
| Before/after report | Show how cleaning changed counts, coverage, missingness, and measurement summaries. |

## Completion criteria

- All proposed checks are completed or explicitly documented as awaiting metadata.
- All transformations and exclusions are traceable to a rule and source record.
- Raw data remain unchanged and record counts reconcile.
- Remaining uncertainty and unresolved quality issues are visible to future analysts.
- The project coordinator has reviewed the domain-dependent cleaning decisions.
- Another person can rerun the documented workflow and reproduce the outputs.
