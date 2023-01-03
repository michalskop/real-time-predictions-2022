# Year 2018

1. From https://volby.cz/opendata/kv2018/kv2018_opendata.htm we download the following files: https://www.volby.cz/opendata/kv2018/KV2022reg20221018_csv.zip and extract `csv_od/kvros.csv` and `csv_od/kvrzcoco.csv` to `preparation/sources`. It has cp1250 encoding, so we convert it to utf-8.

2. create lists of assemblies `create_list.py`

3. batches: `create_baches.py`

4. create results: `create_results.py`

x. test results: `trial_results.py`

X. `polling_stations_list.py` - create list of polling stations

5. prepare groups for selected assemblies: `prepare_groups.py`

Y. `polling_stations_list.py` - create list of polling stations