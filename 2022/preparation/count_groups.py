"""Test counting by groups."""

import os
import pandas as pd

localpath = "2022/preparation/"
localpath2 = "previous/2018/"

# praha - 554782
code = 554782

file_path = localpath2 + 'results/' + str(code) + "/" # + 'results.csv'

batches = pd.read_csv(localpath2 + 'batches.csv')

totals = pd.read_csv(file_path + 'results.csv')
ptt = pd.pivot_table(totals, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
ptt['percent'] = ptt['HLASY'] / ptt['HLASY'].sum() * 100
test = ptt.copy()

polling_stations = pd.read_csv(localpath + 'polling_stations/' + str(code) + '.csv')
totalsum = polling_stations["HLASY"].sum()
groupsums = polling_stations.groupby("group")["HLASY"].sum()
group_weights = polling_stations.groupby("group")["HLASY"].sum() / totalsum

for f in sorted(os.listdir(file_path))[1:]:
  results = pd.read_csv(file_path + f)
  results = results.merge(polling_stations.loc[:, ['OKRSEK', 'group']], on='OKRSEK', how='left')
  pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
  if len(pt.columns) == (len(groupsums) + 1):
    perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
    perct2 = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
    t = batches[batches['n'] == int(f.split('_')[1].split('.')[0])]['time'].values[0]
    perct2.columns = [t]
    perct2['STRANA'] = pt['STRANA']
    # pt.rename(columns={'HLASY': t}, inplace=True)
    test = test.merge(perct2.loc[:, ['STRANA', t]], on='STRANA')
  else:
    print("Missing groups in file", len(pt.columns), f)

test.to_csv(localpath2 + 'tests/model1_' + str(code) + '.csv', index=False)