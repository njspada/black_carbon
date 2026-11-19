# BC and I-80 traffic: progress and next steps

Update meeting: November 19, 2026

## Progress so far

- Prepared September BC using California dates while preserving UTC timestamps, original columns, negative values, and duplicates. September has no recorded coordinates, and local coverage ends September 20.
- Selected May for its stronger coordinate coverage. Prepared 932,491 BC readings across 22 sensors, preserving 392,161 negative readings, and 15,624 hourly traffic records across 21 I-80 mainline stations.
- Completed an initial hourly comparison using the nearest station in each direction. Mean BC showed no consistent positive relationship with traffic flow; some P95 associations weakened after accounting for daily patterns.
- Created an [interactive comparison](may26/comparison/comparison.html) and [study-area map](may26/comparison/sensor_station_map.html). Download the HTML files and open them in a browser; GitHub displays their source rather than the interactive view.

## Main question for the next phase

Does the weak BC–traffic relationship persist when we select geographically convincing pairs and examine traffic conditions alongside flow?

The current comparison has 44 directional sensor–station pairs with no maximum-distance cutoff. Only 11 pairs have at least 100 matched hours meeting the exploratory ≥80% traffic-observation threshold; 26 have none. Geographic suitability and coverage therefore come first. This threshold is a sensitivity filter, not a verified instrument-validity rule.

## Planned next steps

| Priority | Work | Purpose |
| --- | --- | --- |
| 1 | Review the map and select 3–5 pairs based on road alignment, ramps, distance, and overlapping coverage. Record the selection rationale. | Identify stations that plausibly represent traffic near each BC sensor. |
| 2 | Confirm BC and traffic units; summarize negative BC readings by sensor/day and inspect reading counts and unique measurement minutes. | Assess whether measurement quality or sparse sampling affects the comparison. |
| 3 | Verify speed availability and quality, then plot BC, flow, speed, and observation coverage on aligned timelines. Compare similar-flow hours at different speeds. | Investigate whether traffic conditions add information beyond vehicle counts. |
| 4 | Define a consistent high-BC event rule and examine selected events alongside ordinary comparison periods and neighboring sensors. | Explore whether elevated BC is localized, shared across sensors, or accompanied by traffic changes. |
| 5 | Investigate weather coverage, particularly wind direction and speed, for the selected pairs. | Compare periods when wind travels from the highway toward a sensor with other wind conditions. |
| 6 | Investigate suitable truck or vehicle-class data for the selected locations and dates. | Assess whether traffic composition adds information beyond total flow. |

## Immediate deliverable

Create a selected-pair case study for 3–5 geographically convincing pairs, with:

- A map inset and written reason for selecting each pair.
- A summary of BC and traffic coverage and usable overlapping hours.
- Aligned BC mean/P95, traffic flow, speed where available, and observation-coverage plots for May and selected days.
- A short interpretation of what is supported, what remains uncertain, and which additional data would be most useful.

This case study will guide whether the next investment should be weather, truck data, or further measurement-quality work. A broader statistical comparison across sensors can follow once the pair selection and data-quality questions are clearer.

## Analysis principles

- Select pairs using geography and coverage before inspecting correlations.
- Distinguish sensor-to-station distance from sensor-to-highway distance.
- Preserve all source readings. Document any quality-filtered analysis as a separate sensitivity comparison; do not remove negative BC values by default.
- Treat hourly P95 as a summary statistic. Define pollution episodes separately before selecting events.
- Keep missing hours as gaps, and retain weak or negative results in the interpretation.
- Treat these findings as exploratory associations. Temporal dependence, shared stations, weather, and other sources limit causal interpretation.

See the [comparison methods and findings](may26/comparison/README.md) and [May preparation report](reports/MAY_PREPARATION.md) for details.
