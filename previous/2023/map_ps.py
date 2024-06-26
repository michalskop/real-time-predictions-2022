"""Polling stations for map."""

import gspread
import pandas as pd

path_map = "/home/michal/dev/real-time-predictions-2022/previous/2023/"
path0_map = "/home/michal/dev/real-time-predictions-2022/president-2023/round-2/extract/results/"

polling_stations_map = pd.read_csv(path_map + "polling_stations.csv")

results_map = pd.read_csv(path0_map + "results.csv")

pt_map = pd.pivot_table(results_map, values='HLASY', index=['OKRSEK'], columns=['STRANA'], aggfunc=sum, fill_value=0)

pt_map['hlasy celkem2'] = pt_map.loc[:, [4, 7]].sum(axis=1)
pt_map['Pavel % 2'] = round(pt_map[4] / pt_map['hlasy celkem2'] * 100, 2)
pt_map['Babiš % 2'] = round(pt_map[7] / pt_map['hlasy celkem2'] * 100, 2)


pt_map['jméno2'] = pt_map.loc[:, ['Pavel % 2', 'Babiš % 2']].idxmax(axis=1)
pt_map['jméno2'] = pt_map['jméno2'].str.replace(' % 2', '')
pt_map['vítěz2'] = pt_map['jméno2']

a_dict = ['Pavel', 'Babiš']
b_dict = ['Petr Pavel', 'Andrej Babiš']

pt_map['vítěz2'] = pt_map['vítěz2'].replace(a_dict, b_dict)

pt_map.rename(columns={4: 'Pavel-hlasy2', 7: 'Babiš-hlasy2'}, inplace=True)

source1 = pd.read_csv(path_map + "source_map_regions.csv")
source2 = pd.read_csv(path_map + "source_map_points.csv")

out_regions = source1.merge(pt_map, left_on='id', right_on='OKRSEK', how='left')
out_points = source2.merge(pt_map, left_on='id', right_on='OKRSEK', how='left')

out_points.loc[0, 'jméno2'] = 'vybrat:'

# output to GSheet
sheetkey = "1oBGj72hPv0F61_VyntbNbODPOEF1IUALuJqktOdNcNQ"

# connect to GSheet
gc = gspread.service_account()
sh = gc.open_by_key(sheetkey)

ws = sh.worksheet('regions')
ws.update('A1', [out_regions.reset_index().columns.values.tolist()] + out_regions.reset_index().values.tolist())

ws = sh.worksheet('points')
out_points.fillna('', inplace=True)
ws.update('A1', [out_points.reset_index().columns.values.tolist()] + out_points.reset_index().values.tolist())
