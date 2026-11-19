"""Build the May geographic review map from local data and cached Caltrans geometry.

Run: python3 scripts/map_may.py
The standalone HTML embeds Leaflet, route geometry and analysis locations.
Only the optional OpenStreetMap background needs an internet connection.
"""
from pathlib import Path
import json
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'may26/comparison'
ASSETS = OUT / 'map_assets'


def main():
    bc = pd.read_csv(ROOT / 'may26/bc_may2026_hourly.csv',
                     usecols=['SensorID','Latitude','Longitude','hour_california','BC'])
    locations = bc.dropna(subset=['Latitude','Longitude'])[['SensorID','Latitude','Longitude']].drop_duplicates()
    assert locations.SensorID.is_unique and len(locations)==22
    stats = bc.groupby('SensorID').agg(readings=('BC','size'),hours=('hour_california','nunique'),
                                     missing_coordinates=('Latitude',lambda x:int(x.isna().sum())))
    sensors = locations.merge(stats,on='SensorID',validate='one_to_one').sort_values('SensorID')
    traffic = pd.read_csv(ROOT/'traffic_data/may26/i80_bc_area_ml/i80_bc_area_ml_hourly.csv',dtype={'station_id':str})
    stations = traffic[['station_id','direction','latitude','longitude','station_name']].drop_duplicates()
    quality = traffic.groupby('station_id').agg(hours=('timestamp','size'),
                      eligible_hours=('percent_observed',lambda x:int(x.ge(80).sum())),
                      zero_observed_hours=('percent_observed',lambda x:int(x.eq(0).sum())))
    stations = stations.merge(quality,on='station_id',validate='one_to_one')
    summary = pd.read_csv(OUT/'pair_summary.csv',dtype={'station_id':str})
    matches = summary[['SensorID','station_id','direction','distance_km','matched_hours','hours_observed_ge80']]
    assert len(stations)==21 and len(matches)==44
    assert set(matches.station_id)<=set(stations.station_id)
    all_stations = pd.read_csv(ROOT/'traffic_data/may26/all_routes/traffic_station_locations.csv',dtype={'station_id':str})
    context = all_stations[all_stations.latitude.between(38.04,38.17)&all_stations.longitude.between(-122.30,-122.17)&
                           all_stations.metadata_type.eq('ML')&~all_stations.station_id.isin(stations.station_id)]
    context = context[['station_id','metadata_fwy','metadata_dir','latitude','longitude','station_name']]
    routes = json.loads((ASSETS/'routes.geojson').read_text())
    assert {f['properties']['Route'] for f in routes['features']}=={29,37,80,780}
    data = {'sensors':sensors.to_dict('records'),'stations':stations.to_dict('records'),
            'matches':matches.to_dict('records'),'context':context.to_dict('records'),'routes':routes}
    template = (ROOT/'scripts/may_map_template.html').read_text()
    result = template.replace('/*LEAFLET_CSS*/',(ASSETS/'leaflet.css').read_text())
    result = result.replace('/*LEAFLET_JS*/',(ASSETS/'leaflet.js').read_text())
    result = result.replace('/*MAP_DATA*/',json.dumps(data,allow_nan=False).replace('</','<\\/'))
    assert '/*MAP_DATA*/' not in result
    (OUT/'sensor_station_map.html').write_text(result)
    print(f'Map built: {len(sensors)} sensors, {len(stations)} comparison stations, {len(context)} optional nearby mainline stations, {len(matches)} pair links, {len(routes["features"])} route segments.')


if __name__=='__main__':
    main()
