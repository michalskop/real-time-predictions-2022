"""Estimate final results from knows results."""

# from inspect import getsourcefile
# from os.path import abspath, exists
import pandas as pd
import numpy as np

localpath = "previous/2021/"
# localpath0 = "previous/2017/"
localpath0 = "previous/2018/"

# batches
batches = pd.read_csv(localpath + 'batches.csv')

# naive estimates
out = pd.DataFrame(columns = ['time', 'n'])
for batch in batches.iterrows():
  n = batch[1]['n']
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  pt = results.pivot_table(values='HLASY', index=['STRANA'], aggfunc=np.sum)
  item = pd.DataFrame({
    'time': batch[1]['time'],
    'n': n,
  }, index=[n])
  gt = pt.T / pt.T.sum().sum() * 100
  gt.index = [n]
  item = pd.concat([item, gt], axis=1)

  out = pd.concat([out, item], axis=0)

out.to_csv(localpath + "test_naive.csv", index=False)

# estimate results
# read known results and polling stations, calc their weights

out = pd.DataFrame(columns = ['time', 'n', 'counted'])
pssum = 0

for batch in batches.iterrows():
  n = batch[1]['n']
  pssum = pssum + batch[1]['size']
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  polling_stations = pd.read_csv(localpath + 'polling_stations_2018_2021_groups9.csv')
  results = results.merge(polling_stations.loc[:, ['id', 'group']], left_on='OKRSEK', right_on="id", how='left')
  totalsum = polling_stations["votes"].sum()
  groupsums = polling_stations.groupby("group")["votes"].sum()
  group_weights = polling_stations.groupby("group")["votes"].sum() / totalsum

  # estimate percentage counted
  counted = polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100
  counted_perc = np.floor(polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100)

  # sums by 5 or 9 groups
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
out.to_csv(localpath + "test_9_2021.csv", index=False)

# closest
# load
out2 = pd.DataFrame(columns = ['time', 'n'])
ordered_matrix = pd.read_csv(localpath0 + "reality_ordered_matrix.csv", index_col=0)
for batch in batches.iterrows():
  n = batch[1]['n']
  print(n)
  # if n == 5:
  #   break
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  polling_stations = pd.read_csv(localpath + 'polling_stations_2018_2021_groups9.csv')
  polling_stations.rename(columns={'votes': 'votes_model'}, inplace=True)
  colsok = results.loc[:, 'OKRSEK'].unique()
  # find closest
  colsok = list(set(colsok).intersection(ordered_matrix.index))
  idx = ordered_matrix.loc[:, colsok].idxmin(axis=1)

  # merge closest
  ps2 = polling_stations.merge(pd.DataFrame(idx, columns=["closest"]), left_on='id', right_index=True, how='left')

  # real votes
  ptr = pd.pivot_table(results, values='HLASY', index=['OKRSEK'], aggfunc=sum).rename(columns={'HLASY': 'votes_real'})
  results = results.merge(ptr, left_on='OKRSEK', right_index=True, how='left')
  results.loc[:, 'p'] = results.loc[:, 'HLASY'] / results.loc[:, 'votes_real']

  # 
  ps2 = ps2.merge(ptr, left_on="closest", right_index=True, how="left")
  ps2['votes'] = np.where(ps2['id'].isin(results['OKRSEK'].unique()), ps2['votes_real'], ps2['votes_model'])
  pt = pd.pivot_table(ps2, values='votes', index=['closest'], aggfunc=sum).sort_values(by='votes', ascending=False)

  # 
  rx = results.merge(pt, left_on='OKRSEK', right_index=True, how='left')
  rx.loc[:, 'v'] = rx.loc[:, 'p'] * rx.loc[:, 'votes']

  # 
  it = rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum) / rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum).sum() * 100
  item = pd.DataFrame({
      'time': batch[1]['time'],
      'n': n,
    }, index=[n])
  gt = it.T
  gt.index = [n]
  item = pd.concat([item, gt], axis=1)

  out2 = pd.concat([out2, item], axis=0)

out2.to_csv(localpath + "test_closest_v1.1_2021.csv", index=False)


