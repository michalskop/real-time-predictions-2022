"""Create results from batches."""

import os
import pandas as pd
import xmltodict

localpath = "previous/2018/"

batches = pd.read_csv(localpath + 'batches.csv')

assemblies = pd.read_csv(localpath + 'assemblies_all.csv')

for n in batches['n']:
  print('batch ' + str(n))
  fpath = localpath + 'batches/' + str(n) + '.xml'
  with open(fpath, 'rb') as f:
    text = f.read()
    obj = xmltodict.parse(text)
    if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
      obj['VYSLEDKY_OKRSKY']['OKRSEK'] = [obj['VYSLEDKY_OKRSKY']['OKRSEK']]
    for okrsek in obj['VYSLEDKY_OKRSKY']['OKRSEK']:
      # create directory if not exists
      file_path = localpath + 'results/' + okrsek['@KODZASTUP']
      if not os.path.exists(file_path):
        os.mkdir(file_path)
      # read results
      if os.path.exists(file_path + '/'  + 'results.csv'):
        results = pd.read_csv(file_path + '/'  + 'results.csv')
      else:
        results = pd.DataFrame()
      if type(okrsek['HLASY_OKRSEK']) != list:
        okrsek['HLASY_OKRSEK'] = [okrsek['HLASY_OKRSEK']]
      for hlasy in okrsek['HLASY_OKRSEK']:
        results = pd.concat([results, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OKRSEK'], 'STRANA': hlasy['@POR_STR_HLAS_LIST'], 'HLASY': hlasy['@HLASY'], 'batch': n}])])
      # save results
      results.to_csv(file_path + '/'  + 'results.csv', index=False)
      results.to_csv(file_path + '/'  + 'results_' + str(n).zfill(3) + '.csv', index=False)
