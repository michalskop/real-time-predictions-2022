"""Estimate final results from known results."""

# from inspect import getsourcefile
# from os.path import abspath, exists
import pandas as pd
import numpy as np

localpath = "president-2023/round-2/"
# localpath0 = "previous/2017/"
localpath0 = "previous/2023/second/"

# batches
batches = pd.read_csv(localpath + 'extract/batches.csv')

# naive estimates
pssum = 0
out = pd.DataFrame(columns = ['time', 'n', 'size', 'counted'])
for batch in batches.iterrows():
  n = batch[1]['n']
  pssum = pssum + batch[1]['size']
  results = pd.read_csv(localpath + 'results/results_' + str(n).zfill(3) + '.csv')
  pt = results.pivot_table(values='HLASY', index=['STRANA'], aggfunc=np.sum)
  item = pd.DataFrame({
    'time': batch[1]['time'],
    'n': n,
    'size': pssum,
    'counted': pt.sum().sum()
  }, index=[n])
  gt = pt.T / pt.T.sum().sum() * 100
  gt.index = [n]
  item = pd.concat([item, gt], axis=1)

  out = pd.concat([out, item], axis=0)

out.to_csv(localpath0 + "test_naive-2.csv", index=False)

# estimate results
# read known results and polling stations, calc their weights

# out = pd.DataFrame(columns = ['time', 'n', 'counted'])
# pssum = 0

# for batch in batches.iterrows():
#   n = batch[1]['n']
#   pssum = pssum + batch[1]['size']
#   results = pd.read_csv(localpath + 'results-2/results_' + str(n).zfill(3) + '.csv')
#   polling_stations = pd.read_csv(localpath + 'polling_stations_2021_2018_groups9.csv')
#   results = results.merge(polling_stations.loc[:, ['id', 'group']], left_on='OKRSEK', right_on="id", how='left')
#   totalsum = polling_stations["votes"].sum()
#   groupsums = polling_stations.groupby("group")["votes"].sum()
#   group_weights = polling_stations.groupby("group")["votes"].sum() / totalsum

#   # estimate percentage counted
#   counted = polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100
#   counted_perc = np.floor(polling_stations[polling_stations['id'].isin(results['id'].unique())]['votes'].sum() / totalsum * 100)

#   # sums by 5 or 9 groups
#   pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
#   # if there are data from all groups:
#   if len(pt.columns) == (len(groupsums) + 1):
#     # gain in each group
#     perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
#     # weighted gain
#     gainw = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
#     gainw.columns = ['gain']
#     gainw['STRANA'] = pt['STRANA']
#     gainw['counted'] = counted_perc

#     item = pd.DataFrame({
#       'time': batch[1]['time'],
#       'n': n,
#       'counted': counted,
#       'counted_ps': pssum,
#     }, index=[n])
#     gt = gainw.loc[:, ['gain', 'STRANA']].T
#     gt.columns = gt.iloc[1]
#     gt = gt.drop('STRANA')
#     gt.index = [n]
#     item = pd.concat([item, gt], axis=1)

#     out = pd.concat([out, item], axis=0)

# # save
# out.to_csv(localpath + "test_5.csv", index=False)

# closest
# load
max_penalty = 1
out2 = pd.DataFrame(columns = ['time', 'n'])
ordered_matrix = pd.read_pickle(localpath + 'estimate/reality_ordered_matrix_' + str(max_penalty) + '.pkl')
for batch in batches.iterrows():
  n = batch[1]['n']
  print(n)
  # break
  # if n == 5:
  #   break
  results = pd.read_csv(localpath + 'extract/results/results_' + str(n).zfill(3) + '.csv')
  polling_stations = pd.read_csv(localpath + 'estimate/polling_stations.csv')
  polling_stations.rename(columns={'votes': 'votes_model'}, inplace=True)

  #  14000 polling stations ~ 90 % counted votes
  if len(results['OKRSEK'].unique()) >= 14000:
    ordered_matrix = pd.read_pickle(localpath + 'estimate/' + 'reality_ordered_matrix_0.pkl')
   
  colsok = results.loc[:, 'OKRSEK'].unique()
  # find closest
  colsok = list(set(colsok).intersection(ordered_matrix.index))
  idx = ordered_matrix.loc[:, colsok].idxmin(axis=1)

  # merge closest
  ps2 = polling_stations.merge(pd.DataFrame(idx, columns=["closest"]), left_on='id', right_index=True, how='left')

  # real votes
  ptr = pd.pivot_table(results, values='HLASY', index=['OKRSEK'], aggfunc=sum).rename(columns={'HLASY': 'votes_real'})
  resultsc = results.merge(ptr, left_on='OKRSEK', right_index=True, how='left')
  resultsc.loc[:, 'p'] = resultsc.loc[:, 'HLASY'] / resultsc.loc[:, 'votes_real']

  # merge real votes with, calculate votes/weight for each counted polling station
  # ps2 is the df with closest polling stations
  ps2 = ps2.merge(ptr, left_on="closest", right_index=True, how="left")
  ps2['votes'] = np.where(ps2['id'].isin(resultsc['OKRSEK'].unique()), ps2['votes_real'], ps2['votes_model'])
  # pt is the df with number of votes (weight) for already counted polling stations in the model
  pt = pd.pivot_table(ps2, values='votes', index=['closest'], aggfunc=sum).sort_values(by='votes', ascending=False)

  # votes for each candidate in okrseks
  rx = resultsc.merge(pt, left_on='OKRSEK', right_index=True, how='left')
  rx.loc[:, 'v'] = rx.loc[:, 'p'] * rx.loc[:, 'votes']

  # final estimate in %
  it = rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum) / rx.pivot_table(values='v', index=['STRANA'], aggfunc=sum).sum() * 100
  gt = it.T

  # counted percentage
  totalsum = polling_stations["votes_model"].sum()

  # estimate percentage counted
  resultse = results.merge(polling_stations.loc[:, ['id']], left_on='OKRSEK', right_on="id", how='left')
  counted = polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 100
  counted_perc = np.floor(polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 1000) / 10
  counted_ps = len(resultse['id'].unique())
  counted_ps_perc = int(np.floor(len(resultse['id'].unique()) / len(polling_stations) * 1000)) / 10

  # last time
  # batchesdone = pd.read_csv(path + '../extract/batches' + teststr + '.csv')
  # lasttime = batchesdone['time'].max()

  # candidates
  # candidates = pd.read_csv(path + 'candidates.csv')

  # confidence itervals
  # confidence intervals parameters
  confi = pd.DataFrame([
    [0, 1],
    [0.002, 0.65],
    [0.1, 0.25],
    [0.7, 0.02],
    [2.5, 0.011],
    [6, 0.01],
    [60, 0.0032],
    [75, 0.0027],
    [89, 0.0024],
    [93, 0.0021],
    [95, 0.0017],
    [97, 0.0012],
    [98, 0.0009],
    [99, 0.00063],
    [99.5, 0.0005],
    [99.9, 0.00009],
    [100, 0.0000001]
  ], columns=['counted', 'value'])
  confi['value'] = confi['value'] * 1.4 # estimate for 95% confidence interval

  lo = confi[counted >= confi['counted']].iloc[-1]
  hi = confi[counted <= confi['counted']].iloc[0]
  # interpolate
  if lo['counted'] != hi['counted']:
    val = lo['value'] + (hi['value'] - lo['value']) * (counted - lo['counted']) / (hi['counted'] - lo['counted'])
  else:
    val = lo['value']

  hit = np.clip(gt * (1 + val), a_max=100, a_min=None)
  lot = np.clip(gt * (1 / (1 + val)), a_max=None, a_min=0)

  # prepare output
  # gains + candidates
  gain = pd.concat([gt, hit, lot], axis=0)
  gain.index = ['mean', 'hi', 'lo']

  # 2 candidates: we used the lower values (2nd) to estimate the upper values (1st)
  imin = gain.loc['mean', :].idxmin() # we cannot use idxmax() because of ties
  cols = list(gain.columns)
  iother = [ele for ele in cols if ele != imin][0]
  gain.loc['mean', iother] = 100 - gain.loc['mean', imin]
  gain.loc['lo', iother] = 100 - gain.loc['hi', imin]
  gain.loc['hi', iother] = 100 - gain.loc['lo', imin]

  # output
  item = pd.DataFrame({
      'time': batch[1]['time'],
      'n': n,
    }, index=[str(n)])
  item = pd.concat([item, gain.T.loc[:, ]])
  item['time'] = item.iloc[0]['time']
  item['n'] = item.iloc[0]['n']
  item = item[1:]
  item = pd.concat([item.iloc[0].to_frame().T, item.iloc[1].to_frame().T], axis=1, ignore_index=True)
  
  out2 = pd.concat([out2, item], axis=0)

out2.to_csv(localpath0 + "test_closest-2_" + str(max_penalty) + ".csv", index=False)


