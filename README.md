# Black carbon and I-80 traffic exploration

Exploratory notebooks and reports for validating black carbon measurements and examining hourly I-80 traffic near the known BC sensor locations. Traffic and BC have not yet been joined for comparison.

## Start here

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
traffic_data/     Python preparation scripts; datasets and HTML remain local
archive/          Earlier CSV notebook and extraction code
data/            Local BC sources and notebook backups (ignored)
```

Full datasets, comparison tables, generated summaries, interactive HTML, and notebook outputs are excluded from the next commit. Existing data remain on disk. Some report links refer to local outputs that are not available in a fresh clone. Earlier commits may still contain previously shared comparison files.

## Run locally

Install Python dependencies:

```bash
python3 -m pip install pandas numpy plotly matplotlib nbformat jupyter
```

For the BC notebook, install R and its `data.table` package, then place `Black Carbon Concentrations.RDS` in `data/`. The CSV in that folder is optional for source comparisons.

For the traffic notebook, place the full filtered dataset at `traffic_data/i80_bc_area_ml/i80_bc_area_ml_hourly.csv`. Alternatively, restore the three PeMS source files to `traffic_data/raw/` and run, from the repository root:

```bash
python3 traffic_data/combine_hourly_metadata.py
python3 traffic_data/filter_i80.py
python3 traffic_data/filter_i80_bc_area.py
```

Open the notebooks with `jupyter notebook notebooks/`. The traffic notebook generates interactive charts locally. The shared preview alone is insufficient to reproduce the monthly analysis.

The traffic subset has 15,120 hourly records from 21 mainline stations. Check percent observed before interpreting peaks, and confirm timezone alignment before comparing traffic with BC.
