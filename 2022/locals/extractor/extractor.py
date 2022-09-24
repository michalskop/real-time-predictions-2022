"""Create results from batches."""

from inspect import getsourcefile
from os.path import abspath, exists
from os import mkdir
import pandas as pd
import xmltodict

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
print(path)
batches = pd.read_csv(path + '../downloads/batches.csv')

for n in batches['n']:
  print('batch ' + str(n))
  fpath = path + '../downloads/batches/' + str(n) + '.xml'
  with open(fpath, 'rb') as f:
    text = f.read()
    obj = xmltodict.parse(text)
    if 'OKRSEK' in obj['VYSLEDKY_OKRSKY']:
      if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
        obj['VYSLEDKY_OKRSKY']['OKRSEK'] = [obj['VYSLEDKY_OKRSKY']['OKRSEK']]
      for okrsek in obj['VYSLEDKY_OKRSKY']['OKRSEK']:
        # create directory if not exists
        file_path = path + 'results/' + okrsek['@KODZASTUP']
        if not path.exists(file_path):
          mkdir(file_path)
        # read results
        if exists(file_path + '/'  + 'results.csv'):
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
    else:
      print('no OKRSEK')