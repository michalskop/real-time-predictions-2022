"""Joins results and points tables."""

import pandas as pd
import numpy as np

path = "/home/michal/dev/real-time-predictions-2022/previous/2023/"
teststr = "-test"

results = pd.read_csv(path + '../../president-2023/round-1/extract/results' + teststr + '/results.csv')
candidates = pd.read_csv(path + '../../president-2023/round-1/estimate/candidates.csv')
mapp = pd.read_csv(path + 'map_polling_stations_points1.csv')

# naive estimates
ptn = results.pivot_table(values='HLASY', index=['OKRSEK'], columns=['STRANA'], aggfunc=np.sum)
gtn = (ptn.T / ptn.T.sum() * 100).T

ptn.columns = [x + '_HLASY' for x in candidates['family_name']]
gtn.columns = [x for x in candidates['family_name']]

# gtn = round(gtn, 2)

# join points and results
mapp.merge(ptn, left_on="id", right_index=True, how="left").merge(gtn, left_on="id", right_index=True, how="left").to_csv(path + 'map_polling_stations_points1_results.csv', index=False)
