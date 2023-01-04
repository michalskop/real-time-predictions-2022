"""Create list of assemblies and polling stations."""

# Note: There is only 1 assembly with obvody (Lišov, 544779) and its polling stations have different numbers.

import pandas as pd

localpath = "previous/2018-municipalities/"

coco = pd.read_csv(localpath + "sources/kvrzcoco.csv", encoding="cp1250", sep=";")
parties = pd.read_csv(localpath + "sources/kvros.csv", encoding="cp1250", sep=";")
candidates = pd.read_csv(localpath + "sources/kvrk.csv", encoding="cp1250", sep=";")

# Create list of polling stations
ps_arr = []
for i in coco.index:
  for j in range(coco.loc[i, "MINOKRSEK1"], coco.loc[i, "MAXOKRSEK1"] + 1):
    if coco.loc[i, "OBVODY"] < 2: # filtering out Lišov duplicity
      item = {
        "id": str(coco.loc[i, "KODZASTUP"]) + '-' + str(j),
        "OKRSEK": j,
        "KODZASTUP": coco.loc[i, "KODZASTUP"],
        "NAZEVZAST": coco.loc[i, "NAZEVZAST"],
        "OBEC": coco.loc[i, "OBEC"],
        "NAZEVOBCE": coco.loc[i, "NAZEVOBCE"],
        "KRAJ": coco.loc[i, "KRAJ"],
        "OKRES": coco.loc[i, "OKRES"],
        "MANDATY": coco.loc[i, "MANDATY"],
        "POCOBYV": coco.loc[i, "POCOBYV"],
      }
      ps_arr.append(item)
  if coco.loc[i, "MINOKRSEK2"] > 0:
    for j in range(coco.loc[i, "MINOKRSEK2"], coco.loc[i, "MAXOKRSEK2"] + 1):
      if coco.loc[i, "OBVODY"] < 2: # filtering out Lišov duplicity
        item = {
          "id": str(coco.loc[i, "KODZASTUP"]) + '-' + str(j),
          "OKRSEK": j,
          "KODZASTUP": coco.loc[i, "KODZASTUP"],
          "NAZEVZAST": coco.loc[i, "NAZEVZAST"],
          "OBEC": coco.loc[i, "OBEC"],
          "NAZEVOBCE": coco.loc[i, "NAZEVOBCE"],
          "KRAJ": coco.loc[i, "KRAJ"],
          "OKRES": coco.loc[i, "OKRES"],
          "MANDATY": coco.loc[i, "MANDATY"],
          "POCOBYV": coco.loc[i, "POCOBYV"],
        }
        ps_arr.append(item)
  if (i % 200 == 0):
    print(i)

pss = pd.DataFrame(ps_arr)

# create list of assemblies
assemblies = pd.pivot_table(pss, index=["KODZASTUP"], values=["OKRSEK"], aggfunc="count").reset_index()
assemblies.rename(columns={"OKRSEK": "N_OKRSEK"}, inplace=True)

assemblies = assemblies.merge(pd.pivot_table(pss, index=["KODZASTUP"], values=["NAZEVZAST", "KRAJ", "OKRES", "MANDATY", "POCOBYV"], aggfunc="first").reset_index(), on="KODZASTUP")

pt = pd.pivot_table(parties, index=["KODZASTUP"], values=["POR_STR_HL"], aggfunc="count").reset_index()

assemblies = assemblies.merge(pt, on="KODZASTUP", how="left").fillna(0)
assemblies.rename(columns={"POR_STR_HL": "N_STRANA"}, inplace=True)

assemblies["N_STRANA"] = assemblies["N_STRANA"].astype(int)

assemblies["type"] = "rt"
assemblies.loc[(assemblies["N_STRANA"] <= 1), "type"] = "1party"
assemblies.loc[(assemblies["N_OKRSEK"] == 1) & (assemblies["N_STRANA"] > 1), "type"] = "1okrsek_moreparties"

assemblies.to_csv(localpath + "assemblies_all.csv", index=False)
for t in assemblies["type"].unique():
  assemblies.loc[assemblies["type"] == t].to_csv(localpath + "assemblies_" + t + ".csv", index=False)
  
# create list of polling stations
pss.loc[:, ["id", "OKRSEK", "KODZASTUP", "NAZEVZAST"]].to_csv(localpath + "polling_stations.csv", index=False)

# create list of parties
pt = pd.pivot_table(candidates, index=["KODZASTUP", "OSTRANA"], values="PORCISLO", aggfunc="count").reset_index().rename(columns={"PORCISLO": "N_CANDIDATE"})
parties.merge(pt, on=["KODZASTUP", "OSTRANA"]).to_csv(localpath + "parties.csv", index=False)