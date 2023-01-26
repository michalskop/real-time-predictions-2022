"""Estimate final results from known results."""

import datetime
import gspread
from inspect import getsourcefile
import json
import numpy as np
from os.path import abspath, exists
import pandas as pd

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
path = "/home/michal/dev/real-time-predictions-2022/president-2023/round-2/estimate/" # ** for testing only **
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
polling_stations = pd.read_csv(path + 'polling_stations_2018.csv')
polling_stations.rename(columns={'votes': 'votes_model'}, inplace=True)
last_batch = results['batch'].max()

## ** QUICK HACK FOR TESTING **
results['STRANA'].replace(9, 4, inplace=True)

# stop by 0 results
if len(results) == 0:
  print('no results yet')
  exit()

# NAIVE
# naive estimates
ptn = results.pivot_table(values='HLASY', index=['STRANA'], aggfunc=np.sum)
gtn = ptn.T / ptn.T.sum().sum() * 100

# CLOSEST
# load ordered matrix
ordered_matrix = pd.read_pickle(path + '/reality_ordered_matrix_1.pkl')
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
resultse = results.merge(polling_stations.loc[:, ['id']], left_on='OKRSEK', right_on="id", how='left')
counted = polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 100
counted_perc = np.floor(polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 1000) / 10
counted_ps = len(resultse['id'].unique())
counted_ps_perc = int(np.floor(len(resultse['id'].unique()) / len(polling_stations) * 1000)) / 10

# last time
batchesdone = pd.read_csv(path + '../extract/batches' + teststr + '.csv')
lasttime = batchesdone['time'].max()

# candidates
candidates = pd.read_csv(path + 'candidates.csv')

# confidence itervals
# confidence intervals parameters
confi = pd.DataFrame([
  [0, 1],
  [0.002, 0.65],
  [0.1, 0.25],
  [0.7, 0.012],
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
  [100, 0.000001]
], columns=['counted', 'value'])
confi['value'] = confi['value'] * 1.33 # estimate for 90% confidence interval

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
if counted < 2:
  precision = 0
elif counted < 99.5:
  precision = 1
else:
  precision = 2
gaint = gain.T.merge(candidates, left_index=True, right_on='number', how='left').sort_values(by='mean', ascending=False)
gaint.loc[:, 'mean'] = np.round(gaint.loc[:, 'mean'] * 10 ** precision) / 10 ** precision
gaint.loc[:, 'hi'] = np.ceil(gaint.loc[:, 'hi'] * 10 ** precision) / 10 ** precision
gaint.loc[:, 'lo'] = np.floor(gaint.loc[:, 'lo'] * 10 ** precision) / 10 ** precision

# output
# note
if settings['test']:
  note = 'These are test data. The results are not real.'
else:
  note = 'Estimates are based on partial results. The results are not final.'
# confidence
if counted < 90:
  confidence = 90
elif counted < 99:
  confidence = 95
elif counted < 99.9:
  confidence = 99
else:
  confidence = 100

# ended
if counted == 100:
  ended = True
else:
  ended = False

# output file
output = {
  'note': note,
  'data-exist': True,
  'end': ended,
  'datetime': datetime.datetime.now().isoformat()[0:19],
  'datatime-data': lasttime,
  'counted': counted,
  'counted-percent': counted_perc,
  'counted-polling-stations': counted_ps,
  'counted-polling-stations-percent': counted_ps_perc,
  'last-batch': last_batch,
  'confidence': confidence,
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
with open(path + '../../../docs/president-2023/round-2/result-v1.json', 'w') as outfile:
  json.dump(output, outfile, ensure_ascii=False)

gaint['counted'] = counted
gaint['datetime'] = output['datetime']
gaint['datatime-data'] = output['datatime-data']
gaint['batch'] = last_batch
gaint.to_csv(path + 'results' + teststr + '.csv', index=False)

# # 9 GROUPS
# # group weights
# resultsg = resultse
# groupsums = polling_stations.groupby("group")["votes_model"].sum()
# group_weights = groupsums / totalsum

# ptg = pd.pivot_table(resultsg, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
# # if there are data from all groups:
# if len(ptg.columns) == (len(groupsums) + 1):
#   # gain in each group
#   perct = ptg.iloc[:, 1:].div(ptg.iloc[:, 1:].sum(axis=0), axis=1)
#   # weighted gain
#   gainw = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
#   gainw.columns = ['gain']
#   gainw['STRANA'] = ptg['STRANA']
#   gainw['counted'] = counted_perc

#   gtg = gainw.loc[:, ['gain', 'STRANA']].T
#   gtg.columns = gtg.iloc[1]
#   gtg = gtg.drop('STRANA')

# # confidence itervals
# # ** TODO **

# output to GSheet
sheetkey = "1-rJaM99i28h_ilmKQKRe2rCargTZ0r6A3Jfrd3n4NDI"

# connect to GSheet
gc = gspread.service_account()
sh = gc.open_by_key(sheetkey)

# write closest prediction
ws = sh.worksheet('closest-current-prediction')
gaintn = gaint.merge(gtn.T, left_on='number', right_index=True , how='left').rename(columns={'HLASY': 'really-counted'})
ws.update('A1', [gaintn.reset_index().columns.values.tolist()] + gaintn.reset_index().values.tolist())

# # write g9 prediction
# ws = sh.worksheet('g9-current-prediction')
# gtgi = gtg.T.merge(candidates, left_index=True, right_on='number', how='left').sort_values(by='gain', ascending=False)
# ws.update('A1', [gtgi.reset_index().columns.values.tolist()] + gtgi.reset_index().values.tolist())

# write histories
# mean, hi, lo
updates = ['mean', 'hi', 'lo']
for update in updates:
  ws = sh.worksheet('closest-history-' + update)
  history = pd.DataFrame(ws.get_all_records())
  item = gaint.sort_values(by='number').loc[:, update]
  item.index = gaint.sort_values(by='number')['id']
  item['datetime'] = gaint.iloc[0]['datetime']
  item['datatime-data'] = gaint.iloc[0]['datatime-data']
  item['counted'] = gaint.iloc[0]['counted']
  item['batch'] = last_batch
  itemT = pd.DataFrame(item).T.reset_index(drop=True)
  history = pd.concat([history, itemT], axis=0, ignore_index=True).drop_duplicates()
  history = history.fillna(0)
  ws.update('A1', [history.columns.values.tolist()] + history.values.tolist())

# # g9
# ws = sh.worksheet('g9-history')
# history = pd.DataFrame(ws.get_all_records())
# item = gtgi.sort_values(by='number').loc[:, 'gain']
# item.index = gaint.sort_values(by='number')['id']
# item['datetime'] = gaint.iloc[0]['datetime']
# item['datatime-data'] = gaint.iloc[0]['datatime-data']
# item['counted'] = gaint.iloc[0]['counted']
# itemT = pd.DataFrame(item).T.reset_index(drop=True)
# history = pd.concat([history, itemT], axis=0, ignore_index=True).drop_duplicates()
# history = history.fillna(0)
# ws.update('A1', [history.columns.values.tolist()] + history.values.tolist())


# estimate for each region
regions = pd.read_csv(path + 'regions.csv')
regional_results = pd.DataFrame()
if (counted > 2): # minimal 2% counted
  for reg in regions.iterrows():
    region = reg[1]  # ** only one!!! **
    ps2r = ps2[ps2['region_id'] == region['id']]
    resultscr = resultsc[resultsc['OKRSEK'].isin(ps2r['id'])]
    ptr = pd.pivot_table(ps2r, values='votes', index=['closest'], aggfunc=sum).sort_values(by='votes', ascending=False)
    rxr = resultscr.merge(pt, left_on='OKRSEK', right_index=True, how='left')
    rxr.loc[:, 'v'] = rxr.loc[:, 'p'] * rxr.loc[:, 'votes']
    itr = rxr.pivot_table(values='v', index=['STRANA'], aggfunc=sum) / rxr.pivot_table(values='v', index=['STRANA'], aggfunc=sum).sum() * 100
    itr.sort_values(by=['v'], ascending=False, inplace=True)
    if len(itr) >= 2:

      min_diff = 4
      if counted > 10:
        min_diff = 1.5
      if counted > 50:
        min_diff = 1
      if counted > 80:
        min_diff = 0.6
      if counted > 99:
        min_diff = 0.15
      if counted == 100:
        min_diff = 0.00001

      if (itr.iloc[0]['v'] - itr.iloc[1]['v'] > min_diff):
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
    'data-exist': True,
    'datetime': datetime.datetime.now().isoformat()[0:19],
    'datatime-data': lasttime,
    'counted': round(counted * 10) / 10,
    'counted-original': counted,
    'confidence': 90,
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
      'counted': round(r['counted'] * 10) / 10,
    })
  # with open(path + '../../../docs/president-2023/round-1/map-v1' + teststr + '.json', 'w') as outfile:
  with open(path + '../../../docs/president-2023/round-2/map-v1.json', 'w') as outfile:
    ss = json.dumps(outputr, ensure_ascii=False).replace('NaN', 'null')
    outfile.write(ss)