"""Polling stations for map."""

import pandas as pd

path = "/home/michal/dev/real-time-predictions-2022/previous/2023/"
path0 = "/home/michal/dev/real-time-predictions-2022/president-2023/round-2/extract/results/"

polling_stations = pd.read_csv(path + "polling_stations.csv")

results = pd.read_csv(path0 + "results.csv")

pt = pd.pivot_table(results, values='HLASY', index=['OKRSEK'], columns=['STRANA'], aggfunc=sum, fill_value=0)

pt['Babiš'] = 