"""Download and transform batches."""

# from lxml import objectify
import requests
import xmltodict
from os.path import exists

# path = "/home/michal/dev/real-time-predictions-2022/"

# url = "https://volby.cz/pls/ps2021/vysledky_okrsky?davka="
# url = "https://www.volby.cz/pls/kv2018/vysledky_okrsky?datumvoleb=20181005&davka="
url = "https://www.volby.cz/pls/ps2017nss/vysledky_okrsky?davka="

# get current batch
r = requests.get(url, verify=False)
obj = xmltodict.parse(r.content)

# get batch number
# last_batch_n = obj['VYSLEDKY_OKRSKY']['DAVKA']['@PORADI_DAVKY']
last_batch_n = obj['VYSLEDKY_OKRSKY']['DAVKA']['@OKRSKY_DAVKA']

# download batches
for n in range(1, int(last_batch_n) + 1):
  print(n)
  # fpath = 'previous/2021/batches/' + str(n) + '.xml'
  # fpath = 'previous/2018/batches/' + str(n) + '.xml'
  fpath = 'previous/2017/batches/' + str(n) + '.xml'
  if not exists(fpath):
    r = requests.get(url + str(n), verify=False)
    with open(fpath, 'wb') as f:
      f.write(r.content)
  # time.sleep(1)
