"""Calculates seats."""

from inspect import getsourcefile
from os.path import abspath, exists
import pandas as pd
import numpy as np

test = False
if test:
  teststr = '-test'
else:
  teststr = ''

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
print(path)

# load basic data
errors = pd.read_csv(path + "errors.csv")
assemblies = pd.read_csv(path + "../extractor/assemblies_80.csv")

def perc2seats(perct2, maxerror, nseats):
  out = pd.DataFrame()
  for i in perct2.index:
    partyn = perct2.loc[i, "STRANA"]
    perct2['nvalue'] = perct2.loc[:, 'gain']
    perct2['mvalue'] = perct2.loc[:, 'gain']
    # add error to smallest party over 5 %
    partym = perct2[(perct2['nvalue'] > 5) & (perct2["STRANA"] != partyn)].sort_values(by='nvalue').iloc[0]['STRANA']
    partymi = perct2[perct2['STRANA'] == partym].index[0]
    perct2.loc[partymi, 'mvalue'] = perct2.loc[partymi, 'nvalue'] + maxerror
    # add error to parties just below 5%
    perct2['mvalue'] = perct2['mvalue'].apply(lambda x: x + maxerror if ((x < 5) & (x + maxerror > 5)) else x)
    # move to nvalue
    perct2['nvalue'] = perct2['mvalue']

    perct2.loc[i, 'nvalue'] = max(perct2.loc[i, 'nvalue'] - maxerror, 0)
    # select > 5 %
    if perct2.loc[i, 'nvalue'] >= 5: 
      perct2sel = perct2[perct2['nvalue'] > 5]
      order = pd.DataFrame()
      for j in range(1, nseats + 1):
        order = pd.concat([order, pd.DataFrame([perct2sel.loc[:, 'STRANA'], perct2sel.loc[:, 'nvalue'] / j]).T])
      order = order.sort_values(by='nvalue', ascending=False)
      ordersum = order[0: nseats].groupby('STRANA').count()
      out = pd.concat([out, pd.DataFrame([{'STRANA': partyn, 'seats': ordersum.loc[partyn, 'nvalue'], 'possible5': 1}])])
    else:
      if (perct2.loc[i, 'gain'] + maxerror) > 5:
        out = pd.concat([out, pd.DataFrame([{'STRANA': partyn, 'seats': 0, 'possible5': 1}])])
      else:
        out = pd.concat([out, pd.DataFrame([{'STRANA': partyn, 'seats': 0, 'possible5': 0}])])
  return out

# estimate seats
# code = 554782
for code in assemblies['KODZASTUP'].values:
  print(code)
  estimate_path = path + '../estimate/results' + teststr + '/' + str(code) + '.csv'
  if exists(estimate_path): # already data exist
    # load data
    results = pd.read_csv(estimate_path)
    counted = results['counted'].values[0]
    if counted >= 10: # counted more than 10 % of votes
      # max error
      maxerror = errors[errors['counted'] == counted]['error'].values[0]

    # calculate seats
      seats = perc2seats(results, maxerror, assemblies[assemblies['KODZASTUP'] == code]['MANDATY'].values[0])
      seats['counted'] = counted
    # save
      seats.to_csv(path + 'seats' + teststr + '/' + str(code) + '.csv', index=False)

