"""Estimate final results from knows results."""

# from inspect import getsourcefile
from os.path import abspath, exists
import pandas as pd
import numpy as np

localpath = "previous/2018/"
localpath0 = "previous/2017/"

# batches
batches = pd.read_csv(localpath + '/batches.csv')

# estimate results
# read known results and polling stations, calc their weights

out = pd.DataFrame(columns = ['time', 'n', 'counted'])
pssum = 0

for batch in batches.iterrows():
  n = batch[1]['n']
  pssum = pssum + batch[1]['size']
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  polling_stations = pd.read_csv(localpath + 'polling_stations_2017_2018_groups9.csv')
  results = results.merge(polling_stations.loc[:, ['id', 'group']], left_on='OKRSEK', right_on="id", how='left')
  totalsum = polling_stations["votes"].sum()
  groupsums = polling_stations.groupby("group")["votes"].sum()
  group_weights = polling_stations.groupby("group")["votes"].sum() / totalsum

  # estimate percentage counted
  counted = polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100
  counted_perc = np.floor(polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100)

  # sums by 5 groups
  pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
  # if there are data from all groups:
  if len(pt.columns) == (len(groupsums) + 1):
    # gain in each group
    perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
    # weighted gain
    gainw = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
    gainw.columns = ['gain']
    gainw['STRANA'] = pt['STRANA']
    gainw['counted'] = counted_perc

    item = pd.DataFrame({
      'time': batch[1]['time'],
      'n': n,
      'counted': counted,
      'counted_ps': pssum,
    }, index=[n])
    gt = gainw.loc[:, ['gain', 'STRANA']].T
    gt.columns = gt.iloc[1]
    gt = gt.drop('STRANA')
    gt.index = [n]
    item = pd.concat([item, gt], axis=1)

    out = pd.concat([out, item], axis=0)

# save
out.to_csv(localpath + "test_9.csv", index=False)

# load
out2 = pd.DataFrame(columns = ['time', 'n'])
ordered_matrix = pd.read_csv(localpath0 + "reality_ordered_matrix.csv", index_col=0)
for batch in batches.iterrows():
  n = batch[1]['n']
  print(n)
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  polling_stations = pd.read_csv(localpath + 'polling_stations_2017_2018_groups9.csv')
  colsok = results.loc[:, 'OKRSEK'].unique()
  # find closest
  colsok = list(set(colsok).intersection(ordered_matrix.index))
  idx = ordered_matrix.loc[:, colsok].idxmin(axis=1)

  # merge
  ps2 = polling_stations.merge(pd.DataFrame(idx, columns=["closest"]), left_on='id', right_index=True, how='left')

  # 
  pt = pd.pivot_table(ps2, values='votes', index=['closest'], aggfunc=sum).sort_values(by='votes', ascending=False)

  ptr = pd.pivot_table(results, values='HLASY', index=['OKRSEK'], aggfunc=sum).rename(columns={'HLASY': 'votes'})
  results = results.merge(ptr, left_on='OKRSEK', right_index=True, how='left')
  results.loc[:, 'p'] = results.loc[:, 'HLASY'] / results.loc[:, 'votes']

  rx = results.merge(pt, left_on='OKRSEK', right_index=True, how='left')
  rx.loc[:, 'v'] = rx.loc[:, 'p'] * rx.loc[:, 'votes_y']

  it = rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum) / rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum).sum() * 100
  item = pd.DataFrame({
      'time': batch[1]['time'],
      'n': n,
    }, index=[n])
  gt = it.T
  gt.index = [n]
  item = pd.concat([item, gt], axis=1)

  out2 = pd.concat([out2, item], axis=0)

out2.to_csv(localpath + "test_closest.csv", index=False)






cols = list(ordered_matrix.columns)
om = ordered_matrix.copy()

colsok = results.loc[:, 'OKRSEK'].unique()
colsnotok = list(set(cols) - set(colsok))


