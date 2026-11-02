# Hourly traffic with station coordinates

Data paths below are relative to `traffic_data/`. Full files are local-only; the shared sample is [`samples/preview.csv`](../samples/preview.csv).

## BC-area mainline subset

The current filtered dataset is `i80_bc_area_ml/i80_bc_area_ml_hourly.csv`. It keeps freeway 80 and station type `ML`, with latitude **38.066572–38.140259** and longitude **−122.275333–−122.200120**, inclusive. Both directions are retained. These are the known BC coordinate bounds, not a distance buffer around each sensor.

The folder also contains `station_locations.csv`, a first-100-row `preview.csv`, and `filter_report.json`. The complete I-80 dataset remains unchanged in `i80/` so the selection can be revised. Rebuild with `python3 traffic_data/filter_i80_bc_area.py` from the repository root.

## Folder layout

- `raw/`: original metadata, daily traffic, and hourly traffic files.
- `all_routes/`: full-district joined data, preview, station lookup, and join report.
- `i80/`: I-80-only data, preview, station lookup, and filter report.
- Scripts remain here in `traffic_data/`. Report file paths are relative to `traffic_data/`.

## I-80 subset

Use `i80/i80_hourly_with_coordinates.csv` for the current exploration. It keeps only rows where `freeway == 80`, retaining both directions, every station type, and all original columns. No latitude/longitude limits have been applied yet.

`i80/i80_hourly_preview.csv` contains the first 100 retained rows. `i80/i80_station_locations.csv` contains the corresponding station locations for choosing geographic bounds. Counts and checks are recorded in `i80/i80_filter_report.json`.

Rebuild after creating the full combined file with `python3 traffic_data/filter_i80.py` from the repository root.

## Full combined source

`all_routes/traffic_hourly_with_coordinates.csv` joins September 2026 hourly observations to the April 8, 2026 station metadata using station ID. Each source record remains one row. All routes, directions, and station types are retained; no Vallejo or BC-area boundary has been applied. Daily records are not included.

## Open these first

- `all_routes/traffic_hourly_preview.csv`: first 100 combined rows for a quick look; not a representative sample.
- `all_routes/traffic_station_locations.csv`: one row per observed station, with coordinates and hourly record counts. Use this smaller table to explore geographic coverage.
- `all_routes/hourly_join_report.json`: row counts, date coverage, unmatched stations, metadata conflicts, and source checksums.

## Columns

`timestamp`, `station_id`, `freeway`, `direction`, `station_type`, `latitude`, `longitude`, and `station_name` identify when and where an observation was recorded. `source_record_number` is its one-based record position in the headerless hourly source.

The 42 traffic fields follow the standard Station Hour layout: timestamp, station ID, district, freeway, direction, type, station length, samples, percent observed, total flow, average occupancy, average speed, six delay thresholds (35–60), then flow/occupancy/speed for lanes 1–8. Headers are assigned from this layout because the source has no header. Source values, including empty lane fields, are retained. Consult the matching PeMS export documentation before interpreting units or applying quality thresholds.

Metadata fields retain their source names with a `metadata_` prefix, except for `latitude`, `longitude`, and `station_name`. The metadata ID is retained for join auditing. `metadata_matched` flags whether the station was found; `metadata_consistent` compares district, freeway, direction, and type. `metadata_date` records the snapshot date.

The April metadata predates the September measurements; the join does not establish that station locations remained unchanged. Timestamps are preserved without timezone conversion. No BC observations have been joined.

## Explore in Python

```python
from pathlib import Path
import pandas as pd

# When running from the repository root:
folder = Path('traffic_data/i80')
stations = pd.read_csv(folder / 'i80_station_locations.csv')
preview = pd.read_csv(folder / 'i80_hourly_preview.csv')
display(preview[['timestamp', 'station_id', 'freeway', 'direction',
                 'total_flow', 'latitude', 'longitude', 'station_name']])

# Read the full dataset in manageable batches when ready to filter it.
for chunk in pd.read_csv(folder / 'i80_hourly_with_coordinates.csv', chunksize=100_000):
    # Apply your chosen route and coordinate bounds here.
    pass
```

To rebuild: `python3 traffic_data/combine_hourly_metadata.py` from the repository root. This rewrites the derived outputs while leaving source files unchanged.
