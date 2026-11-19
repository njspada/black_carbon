# May 2026 comparison inputs

BC outputs are in `may26/` at the repository root:

- `bc_may2026_california.csv`: all original fields plus `date_california`.
- `bc_may2026_hourly.csv`: the same individual readings, in the same order, plus `hour_california`, `mean_bc`, `p95_bc`, and `reading_count`.

Both preserve all 932,491 readings from 22 sensors, including all 392,161 negative BC readings and any duplicates. Coordinates are present on 891,170 rows; missing values are preserved without imputation. No geographic filter has been applied to BC.

Selection uses California May 1 inclusive through June 1 exclusive, equivalent to May 1 07:00 UTC through June 1 07:00 UTC. The original UTC `date` is retained. Hourly means and type-7 95th percentiles include negative readings and are computed separately per sensor and local hour. There are 14,954 observed sensor-hours. Statistics repeat on every original reading in the corresponding group; absent hours are not filled with zeros.

The [first hourly comparison](../may26/comparison/README.md) selects one row of hourly statistics per sensor/hour before joining to traffic, so repeated statistics do not weight hours by their reading counts. It matches the nearest station in each direction and reports all-hour and traffic-observation sensitivity results. The prepared source files remain unchanged.

Rebuild BC with `Rscript scripts/prepare_may_bc.R`. The script verifies source values and row order after CSV export, negative-value inclusion through aggregate reconciliation, and hourly counts and percentile spot checks. Original sources and the September BC files remain unchanged.

Traffic preparation and folder details: [traffic README](../traffic_data/README.md). The original September traffic outputs have moved under `traffic_data/sep26/`; the existing September notebook follows that location.
