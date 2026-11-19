# May BC–traffic comparison

22 sensors, 44 nearest-station directional pairs, 29908 matched sensor-hour/station rows.
0 sensor-hours excluded because they had no usable same-hour coordinates.
11 pairs have at least 100 hours with traffic observation ≥80%; 26 have none.

## Method

- Great-circle distance to the nearest station in each direction within the existing 21-station I-80 mainline subset. No maximum-distance cutoff and no quality-based replacement of the nearest station.
- BC location uses available coordinates within the same sensor-hour; missing source readings are not filled. Every sensor has one distinct recorded May location.
- Existing hourly statistics are selected once per sensor-hour, not averaged or summed across repeated rows. All source BC negatives and duplicates remain in those statistics.
- California hour labels identify interval starts. P95 is the within-hour upper percentile, not an independently defined spike event.
- All matched hours remain in paired_hourly.csv. The ≥80% percent_observed threshold is an exploratory sensitivity filter, not an established instrument-validity rule. All-hour and filtered coefficients appear separately.
- Pearson measures linear association; Spearman checks rank association. Demeaned Pearson subtracts the typical local hour-of-day mean separately for weekdays/weekends from each variable within eligible hours. This is descriptive, not a full causal model.
- Lag columns compare BC now against traffic exactly 1 or 2 hours earlier, requiring ≥80% observation at the earlier traffic hour. Missing time intervals are not bridged.
- No significance tests or causal conclusions: repeated hours are temporally dependent, pairs can share stations, and weather and other emission sources are unaccounted for.
- April metadata supplies station locations. BC units and traffic export units have not been independently checked; labels retain source units.

## Outputs

- sensor_station_map.html: geographic review of sensors, stations, route geometry and selected matches. Built separately with python3 scripts/map_may.py; optional street tiles require internet. Caltrans route geometry is described as an October 2022 extraction, not a verified May road snapshot.
- comparison.html: offline interactive plots with a sensor/station selector. Blank scatter panels mean no eligible hours, not zero BC or zero traffic. Missing BC hours remain gaps.
- paired_hourly.csv: one row per sensor-hour and matched direction, including coordinates, distance, reading count, unique measurement minutes, BC metrics, traffic flow and percent observed.
- pair_summary.csv: pair distances, coverage, same-hour and lagged associations. Blank coefficients indicate insufficient or constant data.

## Findings

Among pairs with ≥100 eligible hours, mean-BC Pearson r ranges from -0.327 to 0.083; P95 Pearson r ranges from 0.013 to 0.375.
The default chart pair is AL80-0088 / 408178 E, selected by coverage then distance, not by correlation.

## Reproduce

`python3 scripts/compare_may.py`

Input SHA-256:
- bc_may2026_hourly.csv: `fe4bff5e07bfe12af18b2cff2504e83aa14945aa933c9fc54fac31e73195eb11`
- i80_bc_area_ml_hourly.csv: `2b9041611ee48c81cba8851cf5b93610e94d566deb1bc257c252f1e466234c70`
