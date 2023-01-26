"""Create results from batches."""

import datetime
from inspect import getsourcefile
import json
from os.path import abspath, exists
import pandas as pd
import xmltodict

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
path = "/home/michal/dev/real-time-predictions-2022/president-2023/round-2/extract/" # ** for testing only **
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

# open list of batches
batches = pd.read_csv(path + '../download/batches' + teststr + '.csv')
batchesdone = pd.read_csv(path + 'batches' + teststr + '.csv')

# extract results for each batch
for n in batches['n']:
  print('batch ' + str(n))
  if n not in batchesdone['n'].tolist():
    fpath = path + '../download/batches' + teststr + '/' + str(n) + '.xml'

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
        
        # read turnout
        if exists(path + 'results' + teststr + '/turnout.csv'):
          turnout = pd.read_csv(path + 'results' + teststr + '/turnout.csv')
        else:
          turnout = pd.DataFrame(columns=['OKRSEK', 'ZAPSANI_VOLICI', 'VYDANE_OBALKY', 'ODEVZDANE_OBALKY', 'PLATNE_HLASY', 'batch'])
        
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
                  results = pd.concat([results, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK'], 'STRANA': hlasy['@PORADOVE_CISLO'], 'HLASY': hlasy['@HLASY'], 'batch': n}])])
                else:
                  results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@PORADOVE_CISLO']), 'HLASY'] = hlasy['@HLASY']
                  results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@PORADOVE_CISLO']), 'batch'] = n
          # turnout
          if 'UCAST_OKRSEK' in okrsek:
            news = True
            if okrsek['@OPAKOVANE'] == '1':
              news = False
            if news:
              turnout = pd.concat([turnout, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK'], 'ZAPSANI_VOLICI': okrsek['UCAST_OKRSEK']['@ZAPSANI_VOLICI'], 'VYDANE_OBALKY': okrsek['UCAST_OKRSEK']['@VYDANE_OBALKY'], 'ODEVZDANE_OBALKY': okrsek['UCAST_OKRSEK']['@ODEVZDANE_OBALKY'], 'PLATNE_HLASY': okrsek['UCAST_OKRSEK']['@PLATNE_HLASY'], 'batch': n}])])
            else:
              turnout.loc[(turnout['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']), 'ZAPSANI_VOLICI'] = okrsek['UCAST_OKRSEK']['@ZAPSANI_VOLICI']
              turnout.loc[(turnout['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']), 'VYDANE_OBALKY'] = okrsek['UCAST_OKRSEK']['@VYDANE_OBALKY']
              turnout.loc[(turnout['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']), 'ODEVZDANE_OBALKY'] = okrsek['UCAST_OKRSEK']['@ODEVZDANE_OBALKY']
              turnout.loc[(turnout['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']), 'PLATNE_HLASY'] = okrsek['UCAST_OKRSEK']['@PLATNE_HLASY']
              turnout.loc[(turnout['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']), 'batch'] = n

        # save results
        results.to_csv(path + 'results' + teststr + '/results.csv', index=False)
        results.to_csv(path + 'results' + teststr + '/results_' + str(n).zfill(3) + '.csv', index=False)
        # save turnout
        turnout.to_csv(path + 'results' + teststr + '/turnout.csv', index=False)
        # turnout.to_csv(path + 'results' + teststr + '/turnout_' + str(n).zfill(3) + '.csv', index=False)

        # save batches
        batchesdone = pd.concat([batchesdone, pd.DataFrame([{'n': n, 'time': time, 'size': len(obj['VYSLEDKY_OKRSKY']['OKRSEK']), 'extracted': datetime.datetime.now().isoformat()}])])

      else:
        print('no OKRSEK')
  # if n > 2:
  #   break
batchesdone.to_csv(path + 'batches' + teststr + '.csv', index=False)