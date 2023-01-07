# Presidential elections 2023

## Round 1

1. Downloads: downloader.py downloads data from volby.cz/dedicated server
TODO: rsync data from the other server to local backup

2. Extractor: extracts data from downloaded files to results.csv files

3. Estimate: estimate results from results.csv files, creates JSON files

4. Copy and push: copy JSON files to /docs and push to GitHub

