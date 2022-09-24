"""Downloads files from a list of URLs."""

from inspect import getsourcefile
from os.path import abspath, exists
import json
import requests
import pandas as pd
import xmltodict

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
if exists(path + "settings.json"):
  with open(path + '../settings.json') as f:
    settings = json.load(f)
else:
  with open(path + '../default_settings.json') as f:
    settings = json.load(f)

url = settings['url_server'] + "pls/kv2022/vysledky_okrsky?davka="

# get current batch - repeat n times
ok = False
m = 0
while (not ok) or (m > 10):
  try:
    r = requests.get(url, verify=False)
    obj = xmltodict.parse(r.content)
    ok = True
  except:
    m += 1

# get batch number
last_batch_n = int(obj['VYSLEDKY_OKRSKY']['DAVKA']['@PORADI_DAVKY'])

# open list of batches
try:
  batches = pd.read_csv(path + 'batches.csv')
except:
  batches = pd.DataFrame(columns=['n', 'time', 'size'])

# get list of batches to download
if len(batches) == 0:
  batches_to_download = [last_batch_n]
else:
  batches_to_download = [x for x in range(round(batches['n'].min()), last_batch_n + 1) if (x not in batches['n'])]
  batches_to_download = batches_to_download + batches[batches['size'] == 0]['n'].tolist()

# download batches
for n in batches_to_download:
  ok = False
  m = 0
  while (not ok) or (m > 10):
    try:
      r = requests.get(url + str(n), verify=False)
      obj = xmltodict.parse(r.content)
      ok = True
    except:
      m += 1
  if ok:
    time = obj['VYSLEDKY_OKRSKY']['@DATUM_CAS_GENEROVANI']
    try:
      if type(obj['VYSLEDKY_OKRSKY']['OKRSEK']) != list:
        size = 1
      else:
        size = len(obj['VYSLEDKY_OKRSKY']['OKRSEK'])
    except:
      size = 0
    if batches[batches['n'] == n].shape[0] == 0:
      batches = pd.concat([batches, pd.DataFrame([{'n': n, 'time': time, 'size': size}])])
    else:
      batches.loc[batches['n'] == n, 'time'] = time
      batches.loc[batches['n'] == n, 'size'] = size
    # save the batch
    fpath = path + 'batches/' + str(n) + '.xml'
    with open(fpath, 'wb') as f:
      f.write(r.content)


# save list of batches
batches.sort_values(by='n').to_csv(path + 'batches.csv', index=False)

