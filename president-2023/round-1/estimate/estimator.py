"""Estimate final results from known results."""

import datetime
from inspect import getsourcefile
import json
import numpy as np
from os.path import abspath, exists
import pandas as pd

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
path = "/home/michal/dev/real-time-predictions-2022/president-2023/round-1/estimate/" # ** for testing only **
if exists(path + "../../settings.json"):
  with open(path + '../../settings.json') as f:
    settings = json.load(f)
else:
  with open(path + '../../default_settings.json') as f:
    settings = json.load(f)

# test or not
if settings['test']:
  teststr = '-test'
else:
  teststr = ''

# load results and polling stations
results = pd.read_csv(path + '../extract/results' + teststr + '/results.csv')
polling_stations = pd.read_csv(path + 'polling_stations_2021_2023_groups9.csv')
polling_stations.rename(columns={'votes': 'votes_model'}, inplace=True)

# stop by 0 results
if len(results) == 0:
  print('no results yet')
  exit()

# closest
# load ordered matrix
ordered_matrix = pd.read_pickle(path + '/reality_ordered_matrix_2021.pkl')
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
ps2 = ps2.merge(ptr, left_on="closest", right_index=True, how="left")
ps2['votes'] = np.where(ps2['id'].isin(resultsc['OKRSEK'].unique()), ps2['votes_real'], ps2['votes_model'])
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
resultse = results.merge(polling_stations.loc[:, ['id', 'group']], left_on='OKRSEK', right_on="id", how='left')
counted = polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 100
counted_perc = np.floor(polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 100)

# last time
batchesdone = pd.read_csv(path + '../extract/batches' + teststr + '.csv')
lasttime = batchesdone['time'].max()

# candidates
candidates = pd.read_csv(path + 'candidates.csv')

# estimate for each region
regions = pd.read_csv(path + 'regions.csv')
regional_results = pd.DataFrame()
for reg in regions.iterrows():
  region = reg[1]
  ps2r = ps2[ps2['region_id'] == region['id']]
  resultscr = resultsc[resultsc['OKRSEK'].isin(ps2r['id'])]
  ptr = pd.pivot_table(ps2r, values='votes', index=['closest'], aggfunc=sum).sort_values(by='votes', ascending=False)
  rxr = resultscr.merge(pt, left_on='OKRSEK', right_index=True, how='left')
  rxr.loc[:, 'v'] = rxr.loc[:, 'p'] * rxr.loc[:, 'votes']
  itr = rxr.pivot_table(values='v', index=['STRANA'], aggfunc=sum) / rxr.pivot_table(values='v', index=['STRANA'], aggfunc=sum).sum() * 100
  itr.sort_values(by=['v'], ascending=False, inplace=True)
  # TODO: add better logic for confidence intervals / null vs. winner
  if len(itr) >= 2:
    if (itr.iloc[0]['v'] - itr.iloc[1]['v'] > 1.5) and (counted > 2):
      item = pd.DataFrame({
        'id': region['id'],
        'region': region['name'],
        'winner_number': itr.index[0],
        'counted': counted,
      }, index=[region['id']])
    else:
      item = pd.DataFrame({
        'id': region['id'],
        'region': region['name'],
        'winner_number': np.nan,
        'counted': counted,
      }, index=[region['id']])
  else:
    item = pd.DataFrame({
      'id': region['id'],
      'region': region['name'],
      'winner_number': np.nan,
      'counted': counted,
    }, index=[region['id']])
  
  regional_results = pd.concat([regional_results, item], axis=0)

regional_results = regional_results.merge(candidates.rename(columns={'id': 'candidate_id'}), left_on='winner_number', right_on='number', how='left')

# output regions
outputr = {
  'note': 'These are test data. The results are not real.',
  'datetime': datetime.datetime.now().isoformat()[0:19],
  'datatime-data': lasttime,
  'counted': counted,
  'confidence': 95,
  'maps': [{
    'level': 'NUTS 3',
    'regions': []
  }]
}
for i, r in regional_results.iterrows():
  outputr['maps'][0]['regions'].append({
    'id': r['id'],
    'name': r['region'],
    'winner': r['winner_number'],
    'winner-name': r['name'],
    'winner-id': r['candidate_id'],
    'counted': r['counted'],
  })
# with open(path + '../../../docs/president-2023/round-1/map-v1' + teststr + '.json', 'w') as outfile:
with open(path + '../../../docs/president-2023/round-1/map-v1.json', 'w') as outfile:
  ss = json.dumps(outputr, ensure_ascii=False).replace('NaN', 'null')
  outfile.write(ss)

# confidence itervals
# confidence intervals parameters
confi = pd.DataFrame([
[0, 1],
[0.02, 0.4],
[1, 0.14],
[2, 0.1],
[5, 0.08],
[10, 0.07],
[15, 0.045],
[20, 0.04],
[30, 0.028],
[50, 0.015],
[60, 0.011],
[80, 0.008],
[90, 0.005],
[99, 0.004],
[100, 0.003]
], columns=['counted', 'value'])
confi['value'] = confi['value'] * 1.4 # estimate for 95% confidence interval

lo = confi[counted >= confi['counted']].iloc[-1]
hi = confi[counted <= confi['counted']].iloc[0]
# interpolate
if lo['counted'] != hi['counted']:
  val = lo['value'] + (hi['value'] - lo['value']) * (counted - lo['counted']) / (hi['counted'] - lo['counted'])
else:
  val = lo['value']

hit = gt * (1 + val)
lot = gt * (1 / (1 + val))

# prepare output
# gains + candidates
gain = pd.concat([gt, hit, lot], axis=0)
gain.index = ['mean', 'hi', 'lo']
gaint = round(gain.T, 2).merge(candidates, left_index=True, right_on='number', how='left').sort_values(by='mean', ascending=False)

# output
output = {
  'note': 'These are test data. The results are not real.',
  'datetime': datetime.datetime.now().isoformat()[0:19],
  'datatime-data': lasttime,
  'counted': counted,
  'confidence': 95,
  'candidates': []
}
for i, r in gaint.iterrows():
  output['candidates'].append({
    'number': r['number'],
    'id': r['id'],
    'family_name': r['family_name'],
    'given_name': r['given_name'],
    'abbreviated_name': r['abbreviated_name'],
    'name': r['name'],
    'values': {
      'mean': r['mean'],
      'hi': r['hi'],
      'lo': r['lo']
    }
  })

# with open(path + '../../../docs/president-2023/round-1/result-v1' + teststr + '.json', 'w') as outfile:
with open(path + '../../../docs/president-2023/round-1/result-v1.json', 'w') as outfile:
  json.dump(output, outfile, ensure_ascii=False)

gaint['counted'] = counted
gaint['datetime'] = output['datetime']
gaint['datatime-data'] = output['datatime-data']
gaint.to_csv(path + 'results' + teststr + '.csv', index=False)

# 9 groups
# group weights
resultsg = resultse
groupsums = polling_stations.groupby("group")["votes_model"].sum()
group_weights = groupsums / totalsum

ptg = pd.pivot_table(resultsg, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
# if there are data from all groups:
if len(ptg.columns) == (len(groupsums) + 1):
  # gain in each group
  perct = ptg.iloc[:, 1:].div(ptg.iloc[:, 1:].sum(axis=0), axis=1)
  # weighted gain
  gainw = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
  gainw.columns = ['gain']
  gainw['STRANA'] = ptg['STRANA']
  gainw['counted'] = counted_perc

  gtg = gainw.loc[:, ['gain', 'STRANA']].T
  gtg.columns = gtg.iloc[1]
  gtg = gtg.drop('STRANA')

# confidence itervals
# ** TODO **