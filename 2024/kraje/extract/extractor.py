"""Create results from batches."""

import datetime
from inspect import getsourcefile
import json
from os.path import abspath, exists
import pandas as pd
import xmltodict

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
path = "/home/michal/dev/real-time-predictions-2022/2024/kraje/extract/" # ** for testing only **
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

# open list of batches
batches = pd.read_csv(path + '../download/batches' + teststr + '.csv')
batchesdone = pd.read_csv(path + 'batches' + teststr + '.csv')

# extract results for each batch
for n in batches['n']:
  print('batch ' + str(n))
  if n not in batchesdone['n'].tolist():
    fpath = path + '../download/batches' + teststr + '/vysledky_okrsky_' + str(n).zfill(5) + '.xml'

    with open(fpath, 'rb') as f:
      # read xml
      text = f.read()
      obj = xmltodict.parse(text)

      # save last time
      time = obj['VYSLEDKY_OKRSKY']['@DATUM_CAS_GENEROVANI']
      with open(path + 'time' + teststr + '.txt', 'w') as f:
        f.write(time)

      # if there are any results
      if 'OKRSEK' in obj['VYSLEDKY_OKRSKY']:
        if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
          obj['VYSLEDKY_OKRSKY']['OKRSEK'] = [obj['VYSLEDKY_OKRSKY']['OKRSEK']]

        # read results
        if exists(path + 'results' + teststr + '/results.csv'):
          results = pd.read_csv(path + 'results' + teststr + '/results.csv')
        else:
          results = pd.DataFrame(columns=['OKRSEK', 'STRANA', 'HLASY', 'batch'])

        # for each okrsek
        for okrsek in obj['VYSLEDKY_OKRSKY']['OKRSEK']:
          # if there are any results
          if 'HLASY_OKRSEK' in okrsek:
            # if there is only one result
            if type(okrsek['HLASY_OKRSEK']) != list:
              okrsek['HLASY_OKRSEK'] = [okrsek['HLASY_OKRSEK']]

            # if there are no results for this okrsek yet or if there are new results
            doit = False
            news = False
            if len(results[results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']]) == 0:
              doit = True
              news = True
            else:
              if okrsek['@OPAKOVANE'] == '1':
                doit = True
                news = False
            # if there are new results
            if doit:
              # process all results
              for hlasy in okrsek['HLASY_OKRSEK']:
                # if there are no results for this okrsek yet
                if news:
                  results = pd.concat([results, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK'], 'STRANA': hlasy['@KSTRANA'], 'HLASY': hlasy['@HLASY'], 'batch': n}])])
                else:
                  results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@KSTRANA']), 'HLASY'] = hlasy['@HLASY']
                  results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@KSTRANA']), 'batch'] = n

        # save results
        results.to_csv(path + 'results' + teststr + '/results.csv', index=False)
        results.to_csv(path + 'xresults' + teststr + '/results_' + str(n).zfill(3) + '.csv', index=False)
        # save batches
        batchesdone = pd.concat([batchesdone, pd.DataFrame([{'n': n, 'time': time, 'size': len(obj['VYSLEDKY_OKRSKY']['OKRSEK']), 'extracted': datetime.datetime.now().isoformat()}])])

      else:
        print('no OKRSEK')
  # if n > 2:
  #   break

# save results into different regional files
for i in range(1, 14):
  ps = pd.read_csv(path + 'polling_stations/polling_stations_' + str(i) + '.csv')
  # filter results, only polling stations from the region, id
  results_region = results[results['OKRSEK'].isin(ps['id'].tolist())]
  # save results
  results_region.to_csv(path + 'results' + teststr + '/results_' + str(i) + '.csv', index=False)

batchesdone.to_csv(path + 'batches' + teststr + '.csv', index=False)