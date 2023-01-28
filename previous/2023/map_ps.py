"""Polling stations for map."""

import pandas as pd

path_map = "/home/michal/dev/real-time-predictions-2022/previous/2023/"
path0_map = "/home/michal/dev/real-time-predictions-2022/president-2023/round-2/extract/results/"

polling_stations_map = pd.read_csv(path_map + "polling_stations.csv")

results_map = pd.read_csv(path0_map + "results.csv")

pt_map = pd.pivot_table(results_map, values='HLASY', index=['OKRSEK'], columns=['STRANA'], aggfunc=sum, fill_value=0)

pt_map['Pavel'] = pt_map[4] / pt_map.sum(axis=1)
pt_map['Pavel'] = pt_map[7] / pt_map.sum(axis=1)