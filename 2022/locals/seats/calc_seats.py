"""Calculates seats."""

import os
import pandas as pd
import numpy as np

localpath = "2022/preparation/"
localpath2 = "previous/2018/"

errors = pd.read_csv(localpath + "errors.csv")

assemblies = pd.read_csv(localpath + "polling_stations/assemblies_80.csv")

def perc2seats(perct2, maxerror, nseats):
  out = pd.DataFrame()
  for i in perct2.index:
    partyn = perct2.loc[i, "STRANA"]
    perct2['nvalue'] = perct2.iloc[:, 0]
    # add error to parties just  below 5%
    partym = perct2[(perct2['nvalue'] > 5) & (perct2.index != partyn)].sort_values(by='nvalue').iloc[0]['STRANA']
    partymi = perct2[perct2['STRANA'] == partym].index[0]
    perct2.loc[partymi, 'mvalue'] = perct2.loc[partymi, 'nvalue'] + maxerror
    # add error to parties just  below 5%
    perct2['mvalue'] = perct2['nvalue'].apply(lambda x: x + maxerror if (x < 5) & (x + maxerror > 5) else x)
    # move to nvalue
    perct2['nvalue'] = perct2['mvalue']

    perct2.iloc[i, 2] = max(perct2.iloc[i, 2] - maxerror, 0)
    # select > 5 %
    if perct2.iloc[i]['nvalue'] >= 5: 
      perct2sel = perct2[perct2['nvalue'] > 5]
      order = pd.DataFrame()
      for j in range(1, nseats + 1):
        order = pd.concat([order, pd.DataFrame([perct2sel.loc[:, 'STRANA'], perct2sel.loc[:, 'nvalue'] / j]).T])
      order = order.sort_values(by='nvalue', ascending=False)
      ordersum = order[0: nseats].groupby('STRANA').count()
      out = pd.concat([out, pd.DataFrame([{'STRANA': partyn, 'seats': ordersum.loc[partyn, 'nvalue']}])])
    else:
      out = pd.concat([out, pd.DataFrame([{'STRANA': partyn, 'seats': 0}])])
  return out



# praha - 554782
# brno - 582786
code = 582786
nseats = assemblies[assemblies["KODZASTUP"] == code]["MANDATY"].values[0]

batches = pd.read_csv(localpath2 + 'batches.csv')

file_path = localpath2 + 'results/' + str(code) + "/" # + 'results.csv'
totals = pd.read_csv(file_path + 'results.csv')
ptt = pd.pivot_table(totals, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
ptt['percent'] = ptt['HLASY'] / ptt['HLASY'].sum() * 100
test = ptt.copy()
testseats = ptt.copy()

polling_stations = pd.read_csv(localpath + 'polling_stations/' + str(code) + '.csv')
totalsum = polling_stations["HLASY"].sum()
groupsums = polling_stations.groupby("group")["HLASY"].sum()
group_weights = polling_stations.groupby("group")["HLASY"].sum() / totalsum

final_results = pd.read_csv(file_path + 'results.csv')
ptf = pd.pivot_table(final_results, values='HLASY', index=['batch'], aggfunc=sum).reset_index()
ptf['sum'] = ptf.apply(lambda row: ptf[ptf['batch'] <= row['batch']]['HLASY'].sum(), axis=1)
ptf['percent'] = round(ptf['sum'] / ptf['sum'].max() * 100, 2)

batches_in = []
for f in sorted(os.listdir(file_path))[1:]: # for all batches
  print(f)
  # read known results
  results = pd.read_csv(file_path + f)
  results = results.merge(polling_stations.loc[:, ['OKRSEK', 'group']], on='OKRSEK', how='left')
  # sums by 5 groups
  pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
  # if there are data from all groups:
  if len(pt.columns) == (len(groupsums) + 1):
    # record batch number
    batchn = int(f.split('_')[1].split('.')[0])
    batches_in.append(batchn)
    # gain in each group
    perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
    # weighted gain
    perct2 = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
    # rename to time of the batch
    t = batches[batches['n'] == batchn]['time'].values[0]
    perct2.columns = [t]
    perct2['STRANA'] = pt['STRANA']
    # append current results to the test
    test = test.merge(perct2.loc[:, ['STRANA', t]], on='STRANA')
    # calculate max error
    counted = np.floor(ptf[ptf['batch'] == batchn]['percent'].values[0])
    if counted >= 10:
      maxerror = errors[errors['counted'] == counted]['error'].values[0]
      # calculate min gain for each party
      mingain = perc2seats(perct2, maxerror, nseats)
      mingain.columns = ['STRANA', t]
      # append current results to the testseats
      testseats = testseats.merge(mingain, on='STRANA')
    else:
      print("Not enough counted votes in batch " + str(batchn) + " (" + str(counted) + "%).")
  else:
    print("Missing groups in file", len(pt.columns), f)

testseats.to_csv(localpath2 + 'tests/model_' + str(code) + '_seats.csv', index=False)