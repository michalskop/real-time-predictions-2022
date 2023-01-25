"""Prepare groups of polling stations."""

# import os
import pandas as pd
import numpy as np
# Distance matrix / MDS
import dcor
# from sklearn.manifold import MDS

localpath = "previous/2018/"

results = pd.read_csv(localpath + 'sources/pet1.csv', sep=';')

def cmdscale(D):
  """                                                                                       
  Classical multidimensional scaling (MDS)                                                  
                                                                                              
  Parameters                                                                                
  ----------                                                                                
  D : (n, n) array                                                                          
      Symmetric distance matrix.                                                            
                                                                                              
  Returns                                                                                   
  -------                                                                                   
  Y : (n, p) array                                                                          
      Configuration matrix. Each column represents a dimension. Only the                    
      p dimensions corresponding to positive eigenvalues of B are returned.                 
      Note that each dimension is only determined up to an overall sign,                    
      corresponding to a reflection.                                                        
                                                                                              
  e : (n,) array                                                                            
      Eigenvalues of B.                                                                     
                                                                                              
  """
  # Number of points                                                                        
  n = len(D)

  # Centering matrix                                                                        
  H = np.eye(n) - np.ones((n, n))/n

  # YY^T                                                                                    
  B = -H.dot(D**2).dot(H)/2

  # Diagonalize                                                                             
  evals, evecs = np.linalg.eigh(B)

  # Sort by eigenvalue in descending order                                                  
  idx   = np.argsort(evals)[::-1]
  evals = evals[idx]
  evecs = evecs[:,idx]

  # Compute the coordinates using positive-eigenvalued components only                      
  w, = np.where(evals > 0)
  L  = np.diag(np.sqrt(evals[w]))
  V  = evecs[:,w]
  Y  = V.dot(L)

  return Y, evals

round = 1

candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9]
candidates_votes = [('HLASY_' + str(c).zfill(2)) for c in candidates]

resround = results[results['KOLO'] == round]
resround.loc[:, 'id'] = resround['OBEC'].astype(str) + '-' + resround['OKRSEK'].astype(str)
resround.index = resround['id']

pt = resround.loc[:, candidates_votes].T

# exclude = pt.columns[pt.sum() == 0]
# pt = pt.drop(exclude, axis=1)

ptp = pt / pt.sum(axis=0)
ptp.fillna(0, inplace=True)

## groups 

dist_arr = dcor.distances.pairwise_distances(ptp.T)
dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)

dims = pd.DataFrame(cmdscale(dist)[0])

d2 = pd.DataFrame((dims.iloc[:, 0] * dims.iloc[:, 0] + dims.iloc[:, 1] * dims.iloc[:, 1]).apply(np.sqrt))
d2.columns = ['dist']
q = d2.quantile(0.33)
d2.loc[:, [0, 1]] = dims.loc[:, [0, 1]]
d2['group'] = 0
d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] >= 0), 'group'] = 1
d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] < 0), 'group'] = 2
d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] < 0), 'group'] = 3
d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] >= 0), 'group'] = 4

d2.loc[:, ['id']] = [e for e in pt.columns if e not in list(exclude)] 
d2.to_csv(localpath + 'reality_mds_5_groups.csv')

## d3
d3 = pd.DataFrame((dims.iloc[:, 0] * dims.iloc[:, 0] + dims.iloc[:, 1] * dims.iloc[:, 1]).apply(np.sqrt))
d3.columns = ['dist']
q = d3.quantile(0.2)
d3.loc[:, [0, 1, 2]] = dims.loc[:, [0, 1, 2]]
d3['group'] = 0
d3.loc[(d3['dist'] > q['dist']) & (d3[0] >= 0) & (d3[1] >= 0) & (d3[2] >= 0), 'group'] = 1
d3.loc[(d3['dist'] > q['dist']) & (d3[0] < 0) & (d3[1] >= 0) & (d3[2] >= 0), 'group'] = 2
d3.loc[(d3['dist'] > q['dist']) & (d3[0] >= 0) & (d3[1] < 0) & (d3[2] >= 0), 'group'] = 3
d3.loc[(d3['dist'] > q['dist']) & (d3[0] < 0) & (d3[1] < 0) & (d3[2] >= 0), 'group'] = 4
d3.loc[(d3['dist'] > q['dist']) & (d3[0] >= 0) & (d3[1] >= 0) & (d3[2] < 0), 'group'] = 5
d3.loc[(d3['dist'] > q['dist']) & (d3[0] < 0) & (d3[1] >= 0) & (d3[2] < 0), 'group'] = 6
d3.loc[(d3['dist'] > q['dist']) & (d3[0] >= 0) & (d3[1] < 0) & (d3[2] < 0), 'group'] = 7
d3.loc[(d3['dist'] > q['dist']) & (d3[0] < 0) & (d3[1] < 0) & (d3[2] < 0), 'group'] = 8

d3.loc[:, ['id']] = [e for e in pt.columns if e not in list(exclude)] 

d3.to_csv(localpath + 'reality_mds_9_groups.csv')

##
# Closest zones
# calculate the distance matrix with NANs
dist_arr = dcor.distances.pairwise_distances(ptp.T)
dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)
# dist.apply(lambda x: np.argsort(x), axis=1)

# penalty for small okrseks
max_penalty = 1 # * (1 + penalty)
polling_stations = pd.read_csv(localpath + 'polling_stations_2018.csv')
x = [0, polling_stations['votes'].quantile(0.5), polling_stations['votes'].quantile(1)]
y = [1 + max_penalty, 1 + 0.5 * max_penalty, 1]
a = np.polyfit(x, y, 2)
np.polyval(a, polling_stations['votes'].quantile(0))
np.polyval(a, polling_stations['votes'].quantile(0.5))
np.polyval(a, polling_stations['votes'].quantile(1))

distw0 = dist.merge(polling_stations.loc[:, ['id', 'votes']], left_index=True, right_on='id', how='right')
# distw0T = distw0.T.merge(polling_stations.loc[:, ['id', 'votes']], left_index=True, right_on='id', how='right')
distw0.index = distw0['id']
distw0.drop('id', axis=1, inplace=True)
# distw0 = distw0.apply(lambda x: x * np.polyval(a, x['votes']), axis=1)
distw = distw0.apply(lambda x: x * np.polyval(a, x['votes']), axis=1).drop('votes', axis=1).T

# clean up
del(distw0)

from scipy.stats import rankdata
ordered_arrs = distw.apply(lambda x: rankdata(x, method='ordinal'), axis=1)
ordered_matrix = pd.DataFrame(list(ordered_arrs), index=distw.index, columns=distw.columns)
# ordered_matrix.index = [e for e in pt.columns if e not in list(exclude)]
# ordered_matrix.columns = [e for e in pt.columns if e not in list(exclude)]

ordered_matrix.to_csv(localpath + 'reality_ordered_matrix_' + str(max_penalty) + '.csv')

# .pkl
ordered_matrix = pd.read_csv(localpath + 'reality_ordered_matrix_' + str(max_penalty) + '.csv', index_col=0)
ordered_matrix.to_pickle(localpath + 'reality_ordered_matrix_' + str(max_penalty) + '.pkl')

# test
test = pd.DataFrame([[1, 2, 3], [4, 5, 6], [1, 2, 3]], index=['a', 'x', 'c'], columns=['a', 'b', 'c'])
test.T.apply(lambda x: rankdata(x, method='ordinal'), axis=1)
test.sort_index(axis=0, inplace=True)
