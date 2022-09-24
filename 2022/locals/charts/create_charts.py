"""Create charts."""

import datetime
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

# load general data
assemblies = pd.read_csv(path + '../extractor/assemblies_80.csv')
with open(path + '../extractor/time' + teststr + '.txt') as f:
  last_udpate = f.read()
last_update_formatted = datetime.datetime.fromisoformat(last_udpate).strftime("%-d. %-m. %H:%m")

# create charts
# code = 554782
for code in assemblies['KODZASTUP'].values:
  print(code)
  # load parties
  parties = pd.read_csv(path + 'parties' + teststr + '/' + str(code) + '.csv')
  # load seats
  seats_path = path + '../seats/seats' + teststr + '/' + str(code) + '.csv'
  if exists(seats_path):
    seats = pd.read_csv(seats_path)
    seats.sort_values(by=['seats', 'possible5'], ascending=False, inplace=True)
    seats = seats.merge(parties.loc[:, ['POR_STR_HL', 'ZKRATKAO30', 'name', 'color', 'inverse']], left_on='STRANA', right_on='POR_STR_HL', how='left')

  # create chart
  # wrapper
  with open(path + "templates/chart.html") as f:
    html = f.read()
  html = html.replace("__MUNI__", assemblies[assemblies['KODZASTUP'] == code]['NAZEVZAST'].values[0])
  # chart
  if exists(seats_path): # already data exist
    counted = int(seats['counted'].values[0])
    html = html.replace("__COUNTED__", str(counted) + " %")
    # html = html.replace("__TIME__", last_update_formatted)
    with open(path + "templates/csschart.html") as f:
      csschart = f.read()
    with open(path + "templates/row.html") as f:
      rowhtml = f.read()
    rows = ""
    # not divided seats
    seatstotal = assemblies[assemblies['KODZASTUP'] == code]['MANDATY'].values[0]
    seatnot = seatstotal - seats['seats'].sum()
    seatmax = np.max([seats['seats'].max(), seatnot])
    # first row
    if seatnot > 0:
      thisrow = rowhtml
      thisrow = thisrow.replace('__PARTY__', 'Zbývá').replace('__SEATS__', str(seatnot)).replace('__COLOR__', '--color: #888888').replace('__INVERSE__', 'inverse').replace('__SIZE__', str(seatnot / seatmax))
      rows += thisrow + "\n"
    # other rows
    for seatx in seats[seats['possible5'] > 0].iterrows():
      seat = seatx[1]
      # seat = seats.loc[5]
      thisrow = rowhtml
      if seat['name'] is np.nan:
        name = seat['ZKRATKAO30'][0:10]
      else:
        name = seat['name'][0:10]
      if seat['color'] is np.nan:
        color = ''
      else:
        color = '--color: ' + seat['color'] + ';'
      if seat['inverse'] == 1:
        inverse = 'inverse'
      else:
        inverse = ''
      
      thisrow = thisrow.replace('__PARTY__', name).replace('__SEATS__', str(seat['seats'])).replace('__COLOR__', color).replace('__INVERSE__', inverse).replace('__SIZE__', str(seat['seats'] / seatmax))
      rows += thisrow + "\n"
    csschart = csschart.replace('__ROWS__', rows)
  else:
    with open(path + "templates/noresults.html") as f:
      csschart = f.read()
    html = html.replace("__COUNTED__", "? %")
    # html = html.replace("__TIME__", last_update_formatted)
  
  html = html.replace("__CHART__", csschart)

  # save
  with open(path + 'charts' + teststr + '/' + str(code) + '.html', 'w') as f:
    f.write(html)
  

  

