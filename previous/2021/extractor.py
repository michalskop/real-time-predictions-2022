"""Create results from batches."""

from os.path import exists
import pandas as pd
import xmltodict

localpath = "previous/2021/"

batches = pd.read_csv(localpath + '/batches.csv')

for n in batches['n']:
  print('batch ' + str(n))
  fpath = localpath + '/batches/' + str(n) + '.xml'
  with open(fpath, 'rb') as f:
    text = f.read()
    obj = xmltodict.parse(text)
    # save last time
    time = obj['VYSLEDKY_OKRSKY']['@DATUM_CAS_GENEROVANI']
    # with open(path + 'time' + teststr + '.txt', 'w') as f:
    #   f.write(time)
    if 'OKRSEK' in obj['VYSLEDKY_OKRSKY']:
      if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
        obj['VYSLEDKY_OKRSKY']['OKRSEK'] = [obj['VYSLEDKY_OKRSKY']['OKRSEK']]
      for okrsek in obj['VYSLEDKY_OKRSKY']['OKRSEK']:
        # create directory if not exists

        # read results
        if exists(localpath + 'results/'  + 'results.csv'):
          results = pd.read_csv(localpath + 'results/' + 'results.csv')
        else:
          results = pd.DataFrame()
        if 'HLASY_OKRSEK' in okrsek:
          if type(okrsek['HLASY_OKRSEK']) != list:
            okrsek['HLASY_OKRSEK'] = [okrsek['HLASY_OKRSEK']]
          doit = False
          if len(results) == 0:
            doit = True
          else:
            if len(results[results['OKRSEK'] == int(okrsek['@CIS_OKRSEK'])]) == 0:
              doit = True
          if doit:
            for hlasy in okrsek['HLASY_OKRSEK']:
              results = pd.concat([results, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK'], 'STRANA': hlasy['@KSTRANA'], 'HLASY': hlasy['@HLASY'], 'batch': n}])])
            # save results
            results.to_csv(localpath + 'results/' +  'results.csv', index=False)
            results.to_csv(localpath + 'results/' +  'results_' + str(n).zfill(3) + '.csv', index=False)

    else:
      print('no OKRSEK')