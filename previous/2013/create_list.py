"""Create list of polling stations."""

# Note: There is no municipalitity with obvody.

import pandas as pd

localpath = "previous/2013/"

coco = pd.read_csv(localpath + "sources/pecoco.csv", encoding="cp1250", sep=";")

# Create list of polling stations
ps_arr = []
for i in coco.index:
  for j in range(coco.loc[i, "MINOKRSEK1"], coco.loc[i, "MAXOKRSEK1"] + 1):
    item = {
      "id": str(coco.loc[i, "OBEC"]) + '-' + str(j),
      "OKRSEK": j,
      "OBEC": coco.loc[i, "OBEC"],
      "NAZEVOBCE": coco.loc[i, "NAZEVOBCE"],
      "KRAJ": coco.loc[i, "KRAJ"],
      "OKRES": coco.loc[i, "OKRES"],
    }
    ps_arr.append(item)
  # if coco.loc[i, "MINOKRSEK2"] > 0:
  #   for j in range(coco.loc[i, "MINOKRSEK2"], coco.loc[i, "MAXOKRSEK2"] + 1):
  #     if coco.loc[i, "OBVODY"] < 2: # filtering out Lišov duplicity
  #       item = {
  #         "id": str(coco.loc[i, "KODZASTUP"]) + '-' + str(j),
  #         "OKRSEK": j,
  #         "KODZASTUP": coco.loc[i, "KODZASTUP"],
  #         "NAZEVZAST": coco.loc[i, "NAZEVZAST"],
  #         "OBEC": coco.loc[i, "OBEC"],
  #         "NAZEVOBCE": coco.loc[i, "NAZEVOBCE"],
  #         "KRAJ": coco.loc[i, "KRAJ"],
  #         "OKRES": coco.loc[i, "OKRES"],
  #         "MANDATY": coco.loc[i, "MANDATY"],
  #         "POCOBYV": coco.loc[i, "POCOBYV"],
  #       }
  #       ps_arr.append(item)
  if (i % 200 == 0):
    print(i)

pss = pd.DataFrame(ps_arr)

# create list of polling stations
pss.loc[:, ["id", "OKRSEK", "OBEC", "NAZEVOBCE"]].to_csv(localpath + "polling_stations.csv", index=False)