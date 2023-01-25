# 2018

1. data from https://www.volby.cz/opendata/prez2018/prez2018_opendata.htm: `pecoco.csv` and `pet1.csv` to `preparation/sources`.
2. batches from https://www.volby.cz/opendata/prez2018/prez2018_opendata.htm - `download_batches.py`

## list of batches
`create_batches_list.py` creates list of batches

## list of polling stations
`create_list.py` creates list of polling stations

## model from 2013
a) join data from 2013 and 2018 to create model for 2018
`join_lists.py`
note: only for first round, second round is estimated from the first round

b) `add_voters.py` adds voters 
note: for second round only

## extractor
extract data from batches to `results.csv` and `results_XXX.csv` files
`extractor.py`

## estimate results
`estimate_results.py` estimates results

## prepare groups
`prepare_groups.py` prepares groups for other elections