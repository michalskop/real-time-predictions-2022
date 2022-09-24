"""Create selected parties."""

import pandas as pd

path = 'previous/2018/'
# path = '2022/preparation/'

colors =  pd.read_csv(path + 'colors.csv')

assemblies = pd.read_csv(path + 'assemblies_80.csv')

parties = pd.read_csv(path + 'parties.csv')

for code in assemblies['KODZASTUP'].values:
  print(code)
  sparties = parties[parties['KODZASTUP'] == code].reset_index()
  sparties['main_party'] = sparties['SLOZENI'].str.split(',').str[0].astype(int)
  sparties['name'] = sparties['ZKRATKAO8']
  sparties.merge(colors, left_on='main_party', right_on='VSTRANA', how='left').to_csv(path + 'parties/' + str(code) + '.csv', index=False)