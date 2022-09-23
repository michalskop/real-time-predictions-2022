"""Prepare lists for polling stations."""

from select import poll
import pandas as pd

localpath = "2022/preparation/"
localpath2 = "previous/2018/"

assemblies = pd.read_csv(localpath + "assemblies_rt.csv")
polling_stations = pd.read_csv(localpath + "polling_stations.csv")

# save min 80 okrseks
assemblies[assemblies["N_OKRSEK"] >= 80].to_csv(localpath + "polling_stations/assemblies_80.csv", index=False)



# praha - 554782
groups2018 = pd.read_csv(localpath2 + "tests/reality_554782_mds_groups.csv")
groups = polling_stations.loc[polling_stations["KODZASTUP"] == 554782].merge(groups2018.loc[:, ["OKRSEK", "group"]], on="OKRSEK")
results = pd.read_csv(localpath2 + "results/554782/results.csv")
pt = results.pivot_table(values="HLASY", index=["OKRSEK"], aggfunc=sum).reset_index()
groups = groups.merge(pt, on="OKRSEK", how="left")
groups.fillna(0, inplace=True)
groups["group"] = groups["group"].astype(int)
groups.to_csv(localpath + "polling_stations/554782.csv", index=False)





polling_stations_2018 = pd.read_csv(localpath2 + "polling_stations.csv")

# check if all polling stations from 2022 are in 2018
# t = polling_stations.merge(polling_stations_2018, on="id", how="left")
# t.loc[t["OKRSEK_y"].isna()]


