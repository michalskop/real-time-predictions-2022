"""Add voters to the list of polling stations."""

import pandas as pd

localpath = "previous/2018/"

# load list of polling stations
pss = pd.read_csv(localpath + "polling_stations.csv")

# number of voters
voters = pd.read_csv(localpath + "sources/pet1.csv", encoding="cp1250", sep=";")
voters['id'] = voters['OBEC'].astype(str) + '-' + voters['OKRSEK'].astype(str)

pssgv = pss.merge(voters[voters['KOLO'] == 1].loc[:, ["id", "PL_HL_CELK"]], on="id", how="left")
pssgv.rename(columns={"PL_HL_CELK": "votes"}, inplace=True)
pssgv.fillna(0, inplace=True)

pssgv.to_csv(localpath + "polling_stations_2018.csv", index=False)
