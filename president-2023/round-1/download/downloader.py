"""Downloads files from a list of URLs."""

import datetime
from inspect import getsourcefile
from os.path import abspath, exists
import json
import requests
import pandas as pd
import xmltodict

# load settings
path = '/'.join(abspath(getsourcefile(lambda:0)).split("/")[0:-1]) + "/"
path = "/home/michal/dev/real-time-predictions-2022/president-2023/round-1/download/" # ** for testing only **
if exists(path + "../../settings.json"):
  with open(path + '../../settings.json') as f:
    settings = json.load(f)
else:
  with open(path + '../../default_settings.json') as f:
    settings = json.load(f)

# test or not
if settings['test']:
  teststr = '-test'
  url = settings['url_server'] + "pls/prez2018/vysledky_okrsky?kolo=1&davka="  # testing on 2018 data
  url = settings['url_server_test'] + "?kolo=1&davka=" # testing on fake data
else:
  teststr = ''
  url = settings['url_server'] + "pls/prez2023/vysledky_okrsky?kolo=1&davka="

# get current batch - repeat n times
ok = False
m = 0
while (not ok) or (m > 10):
  try:
    r = requests.get(url, verify=None)
    obj = xmltodict.parse(r.content)
    ok = True
  except:
    m += 1

# get batch number
try:
  last_batch_n = int(obj['VYSLEDKY_OKRSKY']['DAVKA']['@PORADI_DAVKY'])
except:
  print(obj)
  last_batch_n = 0

# open list of batches
try:
  batches = pd.read_csv(path + 'batches' + teststr + '.csv')
except:
  batches = pd.DataFrame(columns=['n', 'time', 'size', 'downloaded'])

# get list of batches to download
if len(batches) == 0:
  batches_to_download = [x for x in range(1, last_batch_n + 1)]
else:
  batches_to_download = [x for x in range(round(batches['n'].min()), last_batch_n + 1) if (x not in list(batches['n']))]
  batches_to_download = batches_to_download + batches[batches['size'] == 0]['n'].tolist()

# download batches
news = 0
for n in batches_to_download:
  # get the batch - repeat n times
  ok = False
  m = 0
  while (not ok) or (m > 10):
    try:
      r = requests.get(url + str(n), verify=None)
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
      batches = pd.concat([batches, pd.DataFrame([{'n': n, 'time': time, 'size': size, 'downloaded': datetime.datetime.now().isoformat()}])])
    else:
      batches.loc[batches['n'] == n, 'time'] = time
      batches.loc[batches['n'] == n, 'size'] = size
      batches.loc[batches['n'] == n, 'downloaded'] = datetime.datetime.now().isoformat()
    # save the batch
    fpath = path + 'batches' + teststr + '/' + str(n) + '.xml'
    with open(fpath, 'wb') as f:
      f.write(r.content)
    news += 1


# save list of batches
batches.sort_values(by='n').to_csv(path + 'batches' + teststr + '.csv', index=False)

# success run
runs = pd.read_csv(path + 'runs.csv')
item = pd.DataFrame([{'time': datetime.datetime.now().isoformat(), 'n': news, 'test': settings['test']}])
runs = pd.concat([runs, item]).to_csv(path + 'runs.csv', index=False)