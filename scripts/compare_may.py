"""Exploratory May comparison; original BC/traffic inputs are read-only.

Run: python3 scripts/compare_may.py
Requires pandas, numpy, scipy, plotly. No external data or network access.
"""
from pathlib import Path
import hashlib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'may26' / 'comparison'
BC = ROOT / 'may26/bc_may2026_hourly.csv'
TRAFFIC = ROOT / 'traffic_data/may26/i80_bc_area_ml/i80_bc_area_ml_hourly.csv'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def correlation(df, bc='mean_bc', method='pearson', flow='total_flow'):
    values = df[[bc, flow]].replace([np.inf, -np.inf], np.nan).dropna()
    if len(values) < 3 or (values.nunique() < 2).any():
        return np.nan
    return values[bc].corr(values[flow], method=method)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    hashes = {p.name: digest(p) for p in (BC, TRAFFIC)}
    b = pd.read_csv(BC)
    t = pd.read_csv(TRAFFIC, dtype={'station_id': str})
    key = ['SensorID', 'hour_california']
    g = b.groupby(key, sort=True)
    # Hourly values repeat on original readings: take one, never sum them.
    assert g[['mean_bc', 'p95_bc', 'reading_count']].nunique().eq(1).all().all()
    assert g.size().eq(g.reading_count.first()).all()
    b['minute'] = b.date_california.str.slice(0, 16)
    g = b.groupby(key, sort=True)
    h = g.agg(mean_bc=('mean_bc', 'first'), p95_bc=('p95_bc', 'first'),
              reading_count=('reading_count', 'first'), unique_minutes=('minute', 'nunique'),
              latitude=('Latitude', 'first'), longitude=('Longitude', 'first'),
              coordinate_readings=('Latitude', 'count')).reset_index()
    assert g[['Latitude', 'Longitude']].nunique().le(1).all().all()
    assert not h.duplicated(key).any() and h.reading_count.sum() == len(b)
    assert np.isclose((h.mean_bc * h.reading_count).sum(), b.BC.sum())
    missing_locations = int(h[['latitude', 'longitude']].isna().any(axis=1).sum())
    h = h.dropna(subset=['latitude', 'longitude'])
    locations = h[['SensorID', 'latitude', 'longitude']].drop_duplicates()
    assert locations.SensorID.is_unique  # Current May file: one location per sensor.
    stations = t[['station_id', 'direction', 'latitude', 'longitude', 'station_name']].drop_duplicates()
    assert stations.station_id.is_unique
    assert not t.duplicated(['station_id', 'hour_california']).any()
    mappings = []
    for loc in locations.itertuples(index=False):
        for direction, candidates in stations.groupby('direction'):
            s = candidates.copy()
            lat1, lat2 = np.radians(loc.latitude), np.radians(s.latitude.to_numpy())
            dlat = lat2 - lat1
            dlon = np.radians(s.longitude.to_numpy() - loc.longitude)
            a = np.sin(dlat / 2)**2 + np.cos(lat1)*np.cos(lat2)*np.sin(dlon/2)**2
            s['distance_km'] = 6371.0088*2*np.arcsin(np.sqrt(np.clip(a, 0, 1)))
            closest = s.sort_values(['distance_km', 'station_id']).iloc[0]
            mappings.append({'SensorID': loc.SensorID, 'station_id': closest.station_id,
                             'direction': direction, 'distance_km': closest.distance_km})
    mapping = pd.DataFrame(mappings)
    assert len(mapping) == 2 * len(locations)
    pairs = h.merge(mapping, on='SensorID', validate='many_to_many')
    fields = ['station_id', 'hour_california', 'station_name', 'total_flow',
              'percent_observed', 'avg_speed', 'latitude', 'longitude']
    pairs = pairs.merge(t[fields].rename(columns={'latitude': 'station_latitude', 'longitude': 'station_longitude'}),
                        on=['station_id', 'hour_california'], how='left', validate='many_to_one', indicator=True)
    assert pairs._merge.eq('both').all() and len(pairs) == 2 * len(h)
    pairs = pairs.drop(columns='_merge')
    pairs['traffic_observed_ge80'] = pairs.percent_observed.ge(80)
    pairs['time'] = pd.to_datetime(pairs.hour_california, utc=True).dt.tz_convert('America/Los_Angeles')
    pairs = pairs.sort_values(['SensorID', 'direction', 'time'])
    records = []
    for (sensor, station), p in pairs.groupby(['SensorID', 'station_id']):
        q = p[p.traffic_observed_ge80]
        record = dict(SensorID=sensor, station_id=station, direction=p.direction.iloc[0],
                      distance_km=p.distance_km.iloc[0], matched_hours=len(p),
                      hours_observed_ge80=len(q), zero_observed_hours=int(p.percent_observed.eq(0).sum()),
                      mean_pearson_all=correlation(p), p95_pearson_all=correlation(p, 'p95_bc'),
                      mean_pearson_ge80=correlation(q), p95_pearson_ge80=correlation(q, 'p95_bc'),
                      mean_spearman_ge80=correlation(q, method='spearman'),
                      p95_spearman_ge80=correlation(q, 'p95_bc', method='spearman'))
        # Sensitivity: remove typical local hour-of-day / weekday-weekend patterns.
        residuals = q.copy()
        residuals['local_hour'] = residuals.time.dt.hour
        residuals['weekend'] = residuals.time.dt.dayofweek.ge(5)
        if len(residuals):
            group = residuals.groupby(['local_hour', 'weekend'])
            for col in ['mean_bc', 'p95_bc', 'total_flow']:
                residuals[col] -= group[col].transform('mean')
        record['mean_pearson_demeaned_ge80'] = correlation(residuals)
        record['p95_pearson_demeaned_ge80'] = correlation(residuals, 'p95_bc')
        # Exact clock shifts, not adjacent-row shifts across missing hours.
        for lag in [1, 2]:
            previous = t[t.station_id.eq(station)][['hour_california', 'total_flow', 'percent_observed']].copy()
            previous['time'] = pd.to_datetime(previous.hour_california, utc=True).dt.tz_convert('America/Los_Angeles') + pd.Timedelta(hours=lag)
            previous = previous.rename(columns={'total_flow': 'prior_flow', 'percent_observed': 'prior_observed'})
            lagged = p.merge(previous[['time', 'prior_flow', 'prior_observed']], on='time', validate='one_to_one')
            lagged = lagged[lagged.prior_observed.ge(80)]
            record[f'lag{lag}_hours_ge80'] = len(lagged)
            record[f'mean_pearson_traffic_{lag}h_earlier_ge80'] = correlation(lagged, flow='prior_flow')
        records.append(record)
    summary = pd.DataFrame(records)
    summary.to_csv(OUT / 'pair_summary.csv', index=False)
    pairs.drop(columns='time').to_csv(OUT / 'paired_hourly.csv', index=False)
    # Default pair uses coverage and proximity, never largest correlation.
    ordered = summary.assign(enough=summary.hours_observed_ge80.ge(100)).sort_values(
        ['enough', 'distance_km', 'SensorID', 'station_id'], ascending=[False, True, True, True])
    fig = make_subplots(rows=3, cols=1, vertical_spacing=0.10,
                        subplot_titles=['Hourly BC: mean and upper percentile',
                                        'Hourly traffic: all values and observation coverage',
                                        'Same-hour association: traffic observation ≥80%'])
    buttons = []
    titles = []
    for i, row in enumerate(ordered.itertuples(index=False)):
        p = pairs[pairs.SensorID.eq(row.SensorID) & pairs.station_id.eq(row.station_id)]
        # Naive local display strings avoid browser-timezone shifts in Plotly.
        calendar = pd.date_range('2026-05-01', '2026-06-01', freq='h', inclusive='left', tz='America/Los_Angeles')
        series = p.set_index('time').reindex(calendar)
        display_time = calendar.strftime('%Y-%m-%d %H:%M')
        q = p[p.traffic_observed_ge80]
        visible = i == 0
        for metric, name, color in [('mean_bc','Mean BC','#1565c0'),('p95_bc','P95 BC','#8e44ad')]:
            fig.add_trace(go.Scatter(x=display_time, y=series[metric], name=name, mode='lines',
                                    line=dict(color=color), connectgaps=False, visible=visible), row=1, col=1)
        fig.add_trace(go.Scatter(x=display_time, y=series.total_flow, name='Traffic: all hours', mode='lines',
                                line=dict(color='#9aa0a6'), connectgaps=False, visible=visible), row=2, col=1)
        fig.add_trace(go.Scatter(x=q.time.dt.strftime('%Y-%m-%d %H:%M'), y=q.total_flow,
                                name='Traffic: ≥80% observed', mode='markers', marker=dict(color='#d97706',size=4), visible=visible), row=2, col=1)
        for metric, name, color in [('mean_bc','Mean BC vs flow','#1565c0'),('p95_bc','P95 BC vs flow','#8e44ad')]:
            fig.add_trace(go.Scatter(x=q.total_flow, y=q[metric], name=name, mode='markers',
                                    marker=dict(color=color,size=5,opacity=0.5),
                                    text=q.time.dt.strftime('%Y-%m-%d %H:%M'),
                                    hovertemplate='%{text}<br>Flow: %{x}<br>BC: %{y}<extra></extra>',visible=visible),row=3,col=1)
        r = 'unavailable' if pd.isna(row.mean_pearson_ge80) else f'{row.mean_pearson_ge80:.3f}'
        title = (f'{row.SensorID} ↔ {row.station_id} {row.direction} · {row.distance_km:.2f} km'
                 f'<br><sup>≥80% observed: {row.hours_observed_ge80} hours · mean BC Pearson r: {r} · California time</sup>')
        titles.append(title)
        buttons.append(dict(label=f'{row.SensorID} / {row.station_id} {row.direction} ({row.distance_km:.2f} km)',
                            method='update', args=[{'visible': [j//6 == i for j in range(6*len(ordered))]}, {'title.text':title}]))
    fig.update_layout(title=titles[0], template='plotly_white', height=1100,
                      margin=dict(t=170,l=90,r=40,b=60), legend=dict(orientation='h',y=-0.07),
                      updatemenus=[dict(buttons=buttons,x=0,y=1.09,xanchor='left',yanchor='top')])
    fig.update_yaxes(title_text='BC (source units)',row=1,col=1)
    fig.update_yaxes(title_text='Total flow',row=2,col=1)
    fig.update_yaxes(title_text='BC (source units)',row=3,col=1)
    fig.update_xaxes(matches='x2',row=1,col=1)
    fig.update_xaxes(title_text='California date / hour',row=2,col=1)
    fig.update_xaxes(title_text='Hourly traffic total flow',row=3,col=1)
    assert len(fig.data)==6*len(summary) and sum(trace.visible for trace in fig.data)==6
    fig.write_html(OUT / 'comparison.html', include_plotlyjs=True, full_html=True)
    usable = summary[summary.hours_observed_ge80.ge(100)]
    report = [
        '# May BC–traffic comparison', '',
        f'{len(locations)} sensors, {len(summary)} nearest-station directional pairs, {len(pairs)} matched sensor-hour/station rows.',
        f'{missing_locations} sensor-hours excluded because they had no usable same-hour coordinates.',
        f'{len(usable)} pairs have at least 100 hours with traffic observation ≥80%; {int(summary.hours_observed_ge80.eq(0).sum())} have none.',
        '', '## Method', '',
        '- Great-circle distance to the nearest station in each direction within the existing 21-station I-80 mainline subset. No maximum-distance cutoff and no quality-based replacement of the nearest station.',
        '- BC location uses available coordinates within the same sensor-hour; missing source readings are not filled. Every sensor has one distinct recorded May location.',
        '- Existing hourly statistics are selected once per sensor-hour, not averaged or summed across repeated rows. All source BC negatives and duplicates remain in those statistics.',
        '- California hour labels identify interval starts. P95 is the within-hour upper percentile, not an independently defined spike event.',
        '- All matched hours remain in paired_hourly.csv. The ≥80% percent_observed threshold is an exploratory sensitivity filter, not an established instrument-validity rule. All-hour and filtered coefficients appear separately.',
        '- Pearson measures linear association; Spearman checks rank association. Demeaned Pearson subtracts the typical local hour-of-day mean separately for weekdays/weekends from each variable within eligible hours. This is descriptive, not a full causal model.',
        '- Lag columns compare BC now against traffic exactly 1 or 2 hours earlier, requiring ≥80% observation at the earlier traffic hour. Missing time intervals are not bridged.',
        '- No significance tests or causal conclusions: repeated hours are temporally dependent, pairs can share stations, and weather and other emission sources are unaccounted for.',
        '- April metadata supplies station locations. BC units and traffic export units have not been independently checked; labels retain source units.',
        '', '## Outputs', '',
        '- comparison.html: offline interactive plots with a sensor/station selector. Blank scatter panels mean no eligible hours, not zero BC or zero traffic. Missing BC hours remain gaps.',
        '- sensor_station_map.html: geographic review of sensors, stations, route geometry and selected matches. Built separately with python3 scripts/map_may.py; optional street tiles require internet. Caltrans route geometry is described as an October 2022 extraction, not a verified May road snapshot.',
        '- paired_hourly.csv: one row per sensor-hour and matched direction, including coordinates, distance, reading count, unique measurement minutes, BC metrics, traffic flow and percent observed.',
        '- pair_summary.csv: pair distances, coverage, same-hour and lagged associations. Blank coefficients indicate insufficient or constant data.',
        '', '## Findings', '',
        f'Among pairs with ≥100 eligible hours, mean-BC Pearson r ranges from {usable.mean_pearson_ge80.min():.3f} to {usable.mean_pearson_ge80.max():.3f}; P95 Pearson r ranges from {usable.p95_pearson_ge80.min():.3f} to {usable.p95_pearson_ge80.max():.3f}.',
        f'The default chart pair is {ordered.iloc[0].SensorID} / {ordered.iloc[0].station_id} {ordered.iloc[0].direction}, selected by coverage then distance, not by correlation.',
        '', '## Reproduce', '', '`python3 scripts/compare_may.py`', '',
        'Input SHA-256:', *[f'- {name}: `{value}`' for name,value in hashes.items()],
    ]
    (OUT/'README.md').write_text('\n'.join(report)+'\n')
    assert hashes == {p.name: digest(p) for p in (BC, TRAFFIC)}
    print('\n'.join(report[:6]))
    print(usable[['SensorID','station_id','direction','distance_km','hours_observed_ge80','mean_pearson_ge80','p95_pearson_ge80','mean_pearson_demeaned_ge80']].to_string(index=False))


if __name__ == '__main__':
    main()
