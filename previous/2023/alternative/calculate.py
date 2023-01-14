"""Calculate estimates based on currently known results."""

import datetime
import json
import pandas as pd

path = "/home/michal/dev/real-time-predictions-2022/previous/2023/alternative/"


# load data
values = pd.read_csv(path + 'values.csv')
candidates = pd.read_csv(path + 'candidates.csv')
coeffs = pd.read_csv(path + 'coeffs.csv')

# get coeffs based on really_counted
really_counted = values['really_counted'][0]

lo = coeffs[really_counted >= coeffs['really_counted']].iloc[-1]
hi = coeffs[really_counted <= coeffs['really_counted']].iloc[0]
# interpolate
if lo['really_counted'] != hi['really_counted']:
  val = lo + (hi - lo) * (really_counted - lo['really_counted']) / (hi['really_counted'] - lo['really_counted'])
else:
  val = lo

# calculate estimates
estimates = pd.DataFrame(values / val)
hit = estimates * (1 + val['coeff'])
lot = estimates * (1 / (1 + val['coeff']))
estimates.index = ['mean']
hit.index = ['hi']
lot.index = ['lo']


out = candidates.merge(estimates.T, left_on='id', right_index=True, how='left').merge(hit.T, left_on='id', right_index=True, how='left').merge(lot.T, left_on='id', right_index=True, how='left')

# output
# note
note = 'Estimates from the alternative model based on partial results. The results are not final.'
# confidence
if really_counted < 90:
  confidence = 90
elif really_counted < 99:
  confidence = 95
elif really_counted < 99.9:
  confidence = 99
else:
  confidence = 100

# output file
output = {
  'note': note,
  'data-exist': True,
  'datetime': datetime.datetime.now().isoformat()[0:19],
  'datatime-data': 0,
  'counted': int(really_counted),
  'confidence': confidence,
  'candidates': []
}
for i, r in out.iterrows():
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

with open(path + 'result-v1.json', 'w') as outfile:
  json.dump(output, outfile, indent=2, ensure_ascii=False)

