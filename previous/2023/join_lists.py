"""Join lists of polling stations."""

import pandas as pd

localpath = "previous/2023/"
# localpath0 = "previous/2017/"
localpath0 = "previous/2021/"

# load list of polling stations
pss = pd.read_csv(localpath + "polling_stations.csv")
pss0 = pd.read_csv(localpath0 + "polling_stations.csv")

pss.merge(pss0, on="id", how="left", suffixes=("", "_0")).to_csv(localpath + "polling_stations_2021_2023.csv", index=False)

# join groups
groups = pd.read_csv(localpath0 + "reality_mds_9_groups.csv")
pssg = pss.merge(groups.loc[: , ["group", "id"]], on="id", how="left")

# number of voters
# voters = pd.read_csv(localpath0 + "sources/pst4.csv", encoding="cp1250", sep=";")
voters = pd.read_csv(localpath0 + "sources/pst4.csv")
voters['id'] = voters['OBEC'].astype(str) + '-' + voters['OKRSEK'].astype(str)

pssgv = pssg.merge(voters.loc[:, ["id", "PL_HL_CELK"]], on="id", how="left")
pssgv.rename(columns={"PL_HL_CELK": "votes"}, inplace=True)
pssgv.fillna(0, inplace=True)

pssgv.to_csv(localpath + "polling_stations_2021_2023_groups9.csv", index=False)

