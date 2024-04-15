"""Prepare distance matrix."""

import pandas as pd
import numpy as np

# # calculate the distance matrix with NANs
# dist_arr = dcor.distances.pairwise_distances(ptp.T)
# dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)
# # dist.apply(lambda x: np.argsort(x), axis=1)

# # penalty for small okrseks
# max_penalty = 2 # * (1 + penalty)
# polling_stations = pd.read_csv(localpath + 'polling_stations.csv')
# x = [0, polling_stations['votes'].quantile(0.5), polling_stations['votes'].quantile(1)]
# y = [1 + max_penalty, 1 + 0.5 * max_penalty, 1]
# a = np.polyfit(x, y, 2)
# np.polyval(a, polling_stations['votes'].quantile(0))
# np.polyval(a, polling_stations['votes'].quantile(0.5))
# np.polyval(a, polling_stations['votes'].quantile(1))

# distw0 = dist.merge(polling_stations.loc[:, ['id', 'votes']], left_index=True, right_on='id', how='right')
# # distw0T = distw0.T.merge(polling_stations.loc[:, ['id', 'votes']], left_index=True, right_on='id', how='right')
# distw0.index = distw0['id']
# distw0.drop('id', axis=1, inplace=True)
# # distw0 = distw0.apply(lambda x: x * np.polyval(a, x['votes']), axis=1)
# distw = distw0.apply(lambda x: x * np.polyval(a, x['votes']), axis=1).drop('votes', axis=1).T

localpath = "pl-2023/"
res = pd.read_csv(localpath + 'gains2019.csv')
res = res.replace("-", 0)
res = res.replace("#DIV/0!", 0)

res.fillna(0, inplace=True)

res.index = res['code']
res.drop('code', axis=1, inplace=True)
res = res.apply(pd.to_numeric)

# distance matrix

import dcor

dist_arr = dcor.distances.pairwise_distances(res)
dist = pd.DataFrame(dist_arr, index=res.index, columns=res.index)

dist.to_pickle(localpath + 'dist.pkl')

# load distance matrix
dist = pd.read_pickle(localpath + 'dist.pkl')




# load current data
f = "wyniki_gl_na_listy_po_obwodach_sejm_utf8.csv"
data = pd.read_csv(localpath + f, sep=";", encoding="utf-8")
data = data.replace("-", 0)

selected_columns = ['KOMITET WYBORCZY BEZPARTYJNI SAMORZĄDOWCY', 'KOALICYJNY KOMITET WYBORCZY TRZECIA DROGA POLSKA 2050 SZYMONA HOŁOWNI - POLSKIE STRONNICTWO LUDOWE', 'KOMITET WYBORCZY NOWA LEWICA', 'KOMITET WYBORCZY PRAWO I SPRAWIEDLIWOŚĆ', 'KOMITET WYBORCZY KONFEDERACJA WOLNOŚĆ I NIEPODLEGŁOŚĆ', 'KOALICYJNY KOMITET WYBORCZY KOALICJA OBYWATELSKA PO .N IPL ZIELONI', 'KOMITET WYBORCZY POLSKA JEST JEDNA', 'KOMITET WYBORCZY WYBORCÓW RUCHU DOBROBYTU I POKOJU', 'KOMITET WYBORCZY NORMALNY KRAJ', 'KOMITET WYBORCZY ANTYPARTIA', 'KOMITET WYBORCZY RUCH NAPRAWY POLSKI', 'KOMITET WYBORCZY WYBORCÓW MNIEJSZOŚĆ NIEMIECKA']

data['TERYT Gminy'].fillna(0, inplace=True)
data['TERYT Gminy'] = data['TERYT Gminy'].astype(int)
data['code'] = data['TERYT Gminy'].astype(str) + "-" + data['Nr komisji'].astype(str)

data.index = data['code']

data['sum'] = data[selected_columns].sum(axis=1)

counted_codes = data[data['sum'] > 0].index
not_counted_codes = data[data['sum'] == 0].index

datac = data.loc[counted_codes, selected_columns].div(data.loc[counted_codes, :]['sum'], axis=0).fillna(0)

 

from scipy.stats import rankdata

# existing in 2019
counted_codes_existing = [x for x in counted_codes if x in dist.index]


dist_existing = dist.loc[:, counted_codes_existing]
idx = dist_existing.idxmin(axis=1).to_frame().rename(columns={0: 'closest'})

# merge closest
estimated = idx.merge(datac, left_on='closest', right_index=True, how='left')

# add total numbers of votes
# counted
estimated = estimated.merge(data.loc[:, ['sum']], left_index=True, right_index=True, how='left')
# previous election
sum2019 = pd.read_csv(localpath + 'sum2019.csv', index_col=0)
estimated = estimated.merge(sum2019, left_index=True, right_index=True, how='left')
estimated['sum2019'] = estimated['sum2019'].fillna(0)
# estimated sum - existing or previous
estimated['sum_estimated'] = estimated['sum']
estimated.loc[estimated['sum_estimated'] == 0, 'sum_estimated'] = estimated.loc[estimated['sum_estimated'] == 0, 'sum2019']

# estimated votes for each party from selected_columns
out = estimated.loc[:, selected_columns].mul(estimated['sum_estimated'], axis=0)
# get percents
out.sum(axis=0) / out.sum(axis=0).sum() * 100


# only counted
# counted_codes_existing
data.loc[counted_codes_existing, selected_columns].sum(axis=0) / data.loc[counted_codes_existing, selected_columns].sum(axis=0).sum() * 100
# year 2019

d2019 = pd.merge(sum2019.loc[counted_codes_existing, :], res.loc[counted_codes_existing, :], left_index=True, right_index=True, how='left')

# d2019.iloc[:, 1:] = 
d2019.iloc[:, 1:].mul(d2019['sum2019'], axis=0).sum(axis=0) 
d2019c = d2019.iloc[:, 1:].mul(d2019['sum2019'], axis=0).sum(axis=0) 
d2019c / d2019c.sum() * 100

