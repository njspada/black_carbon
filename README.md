# Black carbon and I-80 traffic exploration

Exploratory notebooks and reports for validating black carbon measurements and examining hourly I-80 traffic near the known BC sensor locations. The first May hourly comparison is available in [may26/comparison](may26/comparison/README.md).

## Start here

- [Next steps and meeting update](NEXT_STEPS.md): progress, priorities, and the planned selected-pair case study.

- [May sensor and station map](may26/comparison/sensor_station_map.html): road routes, BC sensor locations, directional traffic stations and selected proximity matches.
- [May interactive comparison](may26/comparison/comparison.html): select a BC sensor and nearby traffic station; [method and limitations](may26/comparison/README.md).
- [May preparation](reports/MAY_PREPARATION.md): full BC readings with California hours and hourly statistics; [monthly traffic workflow](traffic_data/README.md).
- [Black carbon notebook](notebooks/exploratory_rds_plotly.ipynb): RDS data quality, coverage, and interactive plots.
- [Hourly traffic notebook](notebooks/hourly_traffic_exploration.ipynb): weekday/weekend patterns, day-by-hour heatmap, and selected-date traffic.
- [Traffic preview](samples/preview.csv): first 100 records of the filtered I-80 mainline dataset. This is a structure preview, not a representative sample for finding peak hours.

## Reports

- [BC validation findings](reports/BC_VALIDATION.md)
- [Duplicate review](reports/DUPLICATES.md)
- [I-80 research plan](reports/I80_RESEARCH_PLAN.md)
- [Traffic preparation and filters](reports/TRAFFIC_DATA.md)
- [Traffic exploration](reports/TRAFFIC_EXPLORATION.md)

## Folder layout

```text
notebooks/        Active analysis notebooks, saved without outputs
reports/          Written findings and methodology
samples/          preview.csv — the only shared dataset
scripts/          R validation scripts
traffic_data/     Local preparation scripts, metadata, and monthly traffic (ignored)
may26/           May BC readings with California timestamps and hourly statistics
sep26/           September BC extracts
archive/          Earlier CSV notebook and extraction code
data/            Local BC sources and notebook backups (ignored)
```

The two May interactive HTML files and their methods README are included for review. The HTML embeds plotted summaries and map features. Full datasets, comparison CSV tables, map build assets, September folders, and notebook outputs remain local and ignored. Some report links refer to local files unavailable in a fresh clone; rebuilding the analysis requires those inputs. Earlier commits may still contain previously shared comparison files.

## Run locally

Install Python dependencies:

```bash
python3 -m pip install pandas numpy plotly matplotlib nbformat jupyter
```

For the BC notebook, install R and its `data.table` package, then place `Black Carbon Concentrations.RDS` in `data/`. The CSV in that folder is optional for source comparisons.

For the September traffic notebook, the filtered dataset is now at `traffic_data/sep26/i80_bc_area_ml/i80_bc_area_ml_hourly.csv`. Monthly hourly and daily downloads live in `traffic_data/sep26/raw/` or `traffic_data/may26/raw/`; shared station metadata lives in `traffic_data/raw/`. To rebuild September, run from the repository root:

```bash
python3 traffic_data/combine_hourly_metadata.py --month 2026-09
python3 traffic_data/filter_i80.py --month 2026-09
python3 traffic_data/filter_i80_bc_area.py --month 2026-09
```

Open the notebooks with `jupyter notebook notebooks/`. The traffic notebook generates interactive charts locally. The shared preview alone is insufficient to reproduce the monthly analysis.

The traffic subset has 15,120 hourly records from 21 mainline stations. Check percent observed before interpreting peaks, and confirm timezone alignment before comparing traffic with BC.
