"""Create results from batches."""

# from inspect import getsourcefile
from os.path import exists
# from os import mkdir
import pandas as pd
import xmltodict

localpath = "previous/2018/"

# open list of batches
batches = pd.read_csv(localpath + 'batches-2.csv')
# batchesdone = pd.read_csv(path + 'batches-2.csv')

# extract results for each batch
for n in batches['n']:
  print('batch ' + str(n))
  # if n not in batchesdone['n'].tolist():
  fpath = localpath + '/batches-2/' + str(n) + '.xml'

  with open(fpath, 'rb') as f:
    # read xml
    text = f.read()
    obj = xmltodict.parse(text)

    # save last time
    # time = obj['VYSLEDKY_OKRSKY']['@DATUM_CAS_GENEROVANI']
    # with open(path + 'time' + teststr + '.txt', 'w') as f:
    #   f.write(time)

    # if there are any results
    if 'OKRSEK' in obj['VYSLEDKY_OKRSKY']:
      if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
        obj['VYSLEDKY_OKRSKY']['OKRSEK'] = [obj['VYSLEDKY_OKRSKY']['OKRSEK']]

      # read results
      if exists(localpath + 'results-2/results.csv'):
        results = pd.read_csv(localpath + 'results-2/results.csv')
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
                results = pd.concat([results, pd.DataFrame([{'OKRSEK': okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK'], 'STRANA': hlasy['@PORADOVE_CISLO'], 'HLASY': hlasy['@HLASY'], 'batch': n}])])
              else:
                results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@PORADOVE_CISLO']), 'HLASY'] = hlasy['@HLASY']
                results.loc[(results['OKRSEK'] == okrsek['@CIS_OBEC'] + '-' + okrsek['@CIS_OKRSEK']) & (results['STRANA'] == hlasy['@PORADOVE_CISLO']), 'batch'] = n

      # save results
      results.to_csv(localpath + 'results-2/results.csv', index=False)
      results.to_csv(localpath + 'results-2/results_' + str(n).zfill(3) + '.csv', index=False)
      # save batches
      # batchesdone = pd.concat([batchesdone, pd.DataFrame([{'n': n, 'time': time, 'size': len(obj['VYSLEDKY_OKRSKY']['OKRSEK']), 'extracted': datetime.datetime.now().isoformat()}])])

    else:
      print('no OKRSEK')
  # if n > 2:
  #   break
# batchesdone.to_csv(path + 'batches' + teststr + '.csv', index=False)