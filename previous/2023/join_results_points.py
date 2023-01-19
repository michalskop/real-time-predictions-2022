"""Joins results and points tables."""

import pandas as pd
import numpy as np

path = "/home/michal/dev/real-time-predictions-2022/previous/2023/"
teststr = "-test"
teststr = ""

results = pd.read_csv(path + '../../president-2023/round-1/extract/results' + teststr + '/results.csv')
candidates = pd.read_csv(path + 'alternative/candidates.csv')
mapp = pd.read_csv(path + 'map_polling_stations_points1.csv')

mapp2 = pd.read_csv(path + 'polling_stations_areas.csv')

# naive estimates
ptn = results.pivot_table(values='HLASY', index=['OKRSEK'], columns=['STRANA'], aggfunc=np.sum)
gtn = (ptn.T / ptn.T.sum() * 100).T

ptn.columns = [x for x in candidates['family_name']]
jmeno = ptn.idxmax(axis=1)

ptn.columns = [x for x in candidates['name']]
gtn.columns = [x for x in candidates['family_name']]

ptn['vítěz'] = ptn.idxmax(axis=1)

ptn.columns = [x + '_HLASY' for x in candidates['family_name']] + ['vítěz']
ptn['jméno'] = jmeno

ptn['hlasy celkem'] = ptn.loc[:, [x + '_HLASY' for x in candidates['family_name']]].sum(axis=1)


# gtn = round(gtn, 2)

# join points and results
mapp.merge(ptn, left_on="id", right_index=True, how="left").merge(round(gtn, 2), left_on="id", right_index=True, how="left").illna(0).to_csv(path + 'map_polling_stations_points1_results.csv', index=False)

mapp2.merge(ptn, left_on="id", right_index=True, how="left").merge(round(gtn, 2), left_on="id", right_index=True, how="left").fillna(0).to_csv(path + 'map_polling_stations_areas1_results.csv', index=False)

polling_stations = pd.read_csv(path + 'polling_stations.csv')
pretty = pd.read_csv(path + 'polling_stations_pretty_names.csv')
gtn.merge(ptn, left_index=True, right_index=True, how="left").merge(polling_stations, left_index=True, right_on="id", how="left").merge(pretty, on="id", how="left").fillna(0).to_csv(path + 'results_polling_stations.csv', index=False)