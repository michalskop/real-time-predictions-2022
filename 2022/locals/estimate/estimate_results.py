"""Estimate final results from knows results."""

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

assemblies = pd.read_csv(path + '../extractor/assemblies_80.csv')

# estimate results
# code = 554782
for code in assemblies['KODZASTUP'].values:
  print(code)
  
  extractor_path = path + '../extractor/results' + teststr + '/' + str(code) + "/" # + 'results.csv'
  
  if exists(extractor_path): # already data exist
    # read known results and polling stations, calc their weights
    results = pd.read_csv(extractor_path + 'results.csv')
    polling_stations = pd.read_csv(path + 'polling_stations/' + str(code) + '.csv')
    results = results.merge(polling_stations.loc[:, ['OKRSEK', 'group']], on='OKRSEK', how='left')
    totalsum = polling_stations["HLASY"].sum()
    groupsums = polling_stations.groupby("group")["HLASY"].sum()
    group_weights = polling_stations.groupby("group")["HLASY"].sum() / totalsum

    # estimate percentage counted
    counted_perc = np.floor(polling_stations[polling_stations['OKRSEK'].isin(results['OKRSEK'].unique())]['HLASY'].sum() / totalsum * 100)

    # sums by 5 groups
    pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
    # if there are data from all groups:
    if len(pt.columns) == (len(groupsums) + 1):
      # gain in each group
      perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
      # weighted gain
      gainw = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
      gainw.columns = ['gain']
      gainw['STRANA'] = pt['STRANA']
      gainw['counted'] = counted_perc

      # save
      gainw.to_csv(path + 'results' + teststr + '/' + str(code) + '.csv', index=False)