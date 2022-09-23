"""Test counting by groups."""

import os
import pandas as pd

localpath = "2022/preparation/"
localpath2 = "previous/2018/"

assemblies = pd.read_csv(localpath + "/polling_stations/assemblies_80.csv")

# praha - 554782
# ostrava - 554821
code = 554821

errors = pd.DataFrame()
errors2 = pd.DataFrame()

for code in assemblies["KODZASTUP"]:
  print(code)
    
  file_path = localpath2 + 'results/' + str(code) + "/" # + 'results.csv'

  batches = pd.read_csv(localpath2 + 'batches.csv')

  totals = pd.read_csv(file_path + 'results.csv')
  ptt = pd.pivot_table(totals, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
  ptt['percent'] = ptt['HLASY'] / ptt['HLASY'].sum() * 100
  test = ptt.copy()

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
    # read known results
    results = pd.read_csv(file_path + f)
    results = results.merge(polling_stations.loc[:, ['OKRSEK', 'group']], on='OKRSEK', how='left')
    # sums by 5 groups
    pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['group'], aggfunc=sum).reset_index()
    # if there are data from all groups:
    if len(pt.columns) == (len(groupsums) + 1):
      # record batch number
      batches_in.append(int(f.split('_')[1].split('.')[0]))
      # gain in each group
      perct = pt.iloc[:, 1:].div(pt.iloc[:, 1:].sum(axis=0), axis=1)
      # weighted gain
      perct2 = pd.DataFrame((perct * group_weights.T).sum(axis=1) * 100)
      # rename to time of the batch
      t = batches[batches['n'] == int(f.split('_')[1].split('.')[0])]['time'].values[0]
      perct2.columns = [t]
      perct2['STRANA'] = pt['STRANA']
      # append current results to the test
      test = test.merge(perct2.loc[:, ['STRANA', t]], on='STRANA')
    else:
      print("Missing groups in file", len(pt.columns), f)

  # errors
  errors_time = pd.DataFrame(test.iloc[:, 3:].subtract(test.loc[:, 'percent'], axis=0).abs().max())
  errors_time.columns = [code]

  errors_perc = errors_time.copy()
  errors_perc.index = ptf[ptf['batch'].isin(batches_in)]['percent']

  errors = errors.merge(errors_time, left_index=True, right_index=True, how='outer')
  errors2 = errors2.merge(errors_perc, left_index=True, right_index=True, how='outer')

errors.to_csv(localpath2 + 'tests/model1_errors.csv')
errors2.to_csv(localpath2 + 'tests/model1_errors2.csv')

test.to_csv(localpath2 + 'tests/model1_' + str(code) + '.csv', index=False)
test.to_csv(localpath2 + 'tests/model1_' + str(code) + '.csv', index=False)