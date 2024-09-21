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
path = "/home/michal/dev/real-time-predictions-2022/2024/kraje/estimate/" # ** for testing only **
if exists(path + "../settings.json"):
  with open(path + '../settings.json') as f:
    settings = json.load(f)
else:
  # stop with an error
  raise FileNotFoundError("Settings file not found.")

# test or not
if settings['test']:
  teststr = '-test'
else:
  teststr = ''

# for each region
for i in range(1, 14):
  # load results and polling stations
  results = pd.read_csv(path + '../extract/results' + teststr + '/results_' + str(i) + '.csv')
  polling_stations = pd.read_csv(path + '../extract/polling_stations/polling_stations_' + str(i) + '.csv')
  polling_stations.rename(columns={'votes': 'votes_model'}, inplace=True)

  # stop by 0 results
  if len(results) == 0:
    print('no results yet')
    continue

  # NAIVE
  # naive estimates
  ptn = results.pivot_table(values='HLASY', index=['STRANA'], aggfunc=np.sum)
  gtn = ptn.T / ptn.T.sum().sum() * 100

  # CLOSEST
  # load ordered matrix
  ordered_matrix = pd.read_pickle(path + 'matrix/reality_ordered_matrix_1_' + str(i) + '.pkl')
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
  counted_perc = np.floor(polling_stations[polling_stations['id'].isin(resultse['id'].unique())]['votes_model'].sum() / totalsum * 100)

  # last time
  batchesdone = pd.read_csv(path + '../extract/batches' + teststr + '.csv')
  lasttime = batchesdone['time'].max()

  # candidates
  candidates = pd.read_csv(path + 'candidates/candidates_' + str(i) + '.csv')



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
  confi['value'] = confi['value'] * 1 # estimate for 90% confidence interval

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
  gaint = round(gain.T, 3).merge(candidates, left_index=True, right_on='id', how='left').sort_values(by='mean', ascending=False)

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

  # output file
  output = {
    'note': note,
    'data-exist': True,
    'datetime': datetime.datetime.now().isoformat()[0:19],
    'datatime-data': lasttime,
    'counted': counted,
    'confidence': confidence,
    'candidates': []
  }
  for j, r in gaint.iterrows():
    output['candidates'].append({
      'number': r['id'],
      'id': r['id'],
      'full_name': r['full_name'],
      'name': r['ZKRATKAK8'],
      'shorter_name': r['ZKRATKAK30'],
      'values': {
        'mean': r['mean'],
        'hi': r['hi'],
        'lo': r['lo']
      }
    })

  output_table = gaint.loc[:, ['ZKRATKAK8', 'mean', 'hi', 'lo', 'id', 'ZKRATKAK30', 'full_name']].rename(columns={'ZKRATKAK8': 'strana', 'mean': 'sečteno ' + str(int(counted_perc)) + ' %'})
  output_table['counted'] = counted
  output_table['datetime'] = output['datetime']
  output_table['value'] = output_table['sečteno ' + str(int(counted_perc)) + ' %']
  output_table['datatime-data'] = output['datatime-data']


  # with open(path + '../../../docs/president-2023/round-1/result-v1' + teststr + '.json', 'w') as outfile:
  with open(path + 'estimates/result-v1' + teststr + '_' + '.json', 'w') as outfile:
    json.dump(output, outfile, ensure_ascii=False)

  with open(path + 'estimates/result-v1' + teststr + '_' + str(i) + '.csv', 'w') as outfile:
    output_table.to_csv(outfile, index=False)


# # output to GSheet
# sheetkey = "1-rJaM99i28h_ilmKQKRe2rCargTZ0r6A3Jfrd3n4NDI"

# # connect to GSheet
# gc = gspread.service_account()
# sh = gc.open_by_key(sheetkey)

# # write closest prediction
# ws = sh.worksheet('closest-current-prediction')
# gaintn = gaint.merge(gtn.T, left_on='number', right_index=True , how='left').rename(columns={'HLASY': 'really-counted'})
# ws.update('A1', [gaintn.reset_index().columns.values.tolist()] + gaintn.reset_index().values.tolist())

# # write histories
# # mean, hi, lo
# updates = ['mean', 'hi', 'lo']
# for update in updates:
#   ws = sh.worksheet('closest-history-' + update)
#   history = pd.DataFrame(ws.get_all_records())
#   item = gaint.sort_values(by='number').loc[:, update]
#   item.index = gaint.sort_values(by='number')['id']
#   item['datetime'] = gaint.iloc[0]['datetime']
#   item['datatime-data'] = gaint.iloc[0]['datatime-data']
#   item['counted'] = gaint.iloc[0]['counted']
#   itemT = pd.DataFrame(item).T.reset_index(drop=True)
#   history = pd.concat([history, itemT], axis=0, ignore_index=True).drop_duplicates()
#   history = history.fillna(0)
#   ws.update('A1', [history.columns.values.tolist()] + history.values.tolist())
