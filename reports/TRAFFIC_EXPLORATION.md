# Hourly traffic exploration

Open [the interactive page](../traffic_data/i80_bc_area_ml/plots/hourly_traffic_exploration.html) in a browser. It works offline. Select a station for all graphs and a date for the daily curve. Hover for values and drag to zoom.

Three views:

1. Mean hourly flow on weekdays versus weekends.
2. Day-by-hour flow heatmap for September 2026.
3. Hourly flow on the selected date.

Use [the notebook](../notebooks/hourly_traffic_exploration.ipynb) to edit or rerun the analysis. Dependencies: `pandas`, `plotly`, and a Python notebook environment. Run `python3 explore_hourly.py` from this folder to rebuild the HTML and summary CSVs.

`station_summary.csv` lists coverage and mean percent observed. `peak_hours_by_station.csv` lists each station's highest mean-flow hour separately for weekdays and weekends, retaining ties. The starting station, 400128 westbound, peaks at 05:00 on weekdays and 10:00 on weekends in this month's data.

All supplied flow values are included. Several stations report zero percent observed throughout the month, so review that quality field before treating patterns as directly measured. Stations are not summed together. Weekdays include holidays. A high-flow hour is not necessarily the most congested hour.

BC has not been compared yet. For that next step, choose an overlapping date and suitable sensor, confirm the source timezones, and average valid BC minutes into hours. The current graphs preserve the traffic source timestamps.
