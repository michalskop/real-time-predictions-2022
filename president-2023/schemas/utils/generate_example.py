"""Generates example data for a given schema."""

import json
import pandas as pd
import random

path = "president-2023/schemas/"

out = {
  "datetime": "2023-01-15T15:35:00",
  "counted": 47.59,
  "confidence": 95,
  "maps": []
}

maps = [{"level": "NUTS 3", "file": "regions.csv"}, {"level": "LAU 1", "file": "districts.csv"}]
winners = [{"id": "petr-pavel", "name": "Petr Pavel"}, {"id": "danuse-nerudova", "name": "Danuše Nerudová"}, {"id": "andrej-babis", "name": "Andrej Babiš"}, {"id": None, "name": None}]

for map in maps:
  df = pd.read_csv(path + map["file"])
  map = {"level": map["level"], "regions": []}
  for i, row in df.iterrows():
    winner = random.choice(range(0, len(winners)))
    region = {
      "id": row["id"],
      "name": row["name"],
      "counted": random.randint(0, 100),
      "winner-id": winners[winner]["id"],
      "winner-name": winners[winner]["name"],
    }
    map["regions"].append(region)
  out["maps"].append(map)

with open(path + "map-example-1.json", "w") as f:
  json.dump(out, f, indent=2, ensure_ascii=False)