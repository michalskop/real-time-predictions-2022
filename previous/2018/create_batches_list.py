"""Create list of batches."""

# import glob
import pandas as pd
import xmltodict

localpath = "previous/2018/"

# list_of_files = glob.glob(localpath + 'batches/*.xml') # * means all if need specific format then *.csv
# latest_file = max(list_of_files)

last_n = 53
last_n = 38

batches = pd.DataFrame()
for n in range(1, last_n + 1):
  fpath = localpath + 'batches-2/' + str(n) + '.xml'
  with open(fpath, 'rb') as f:
    text = f.read()
    obj = xmltodict.parse(text)
    time = obj['VYSLEDKY_OKRSKY']['@DATUM_CAS_GENEROVANI']
    size = obj['VYSLEDKY_OKRSKY']['DAVKA']['@OKRSKY_DAVKA']
    batches = pd.concat([batches, pd.DataFrame([{'n': n, 'time': time, 'size': size}])])

batches.to_csv(localpath + 'batches-2.csv', index=False)
