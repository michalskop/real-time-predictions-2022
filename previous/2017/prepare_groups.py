"""Prepare groups of polling stations."""

# import os
import pandas as pd
import numpy as np
# Distance matrix / MDS
import dcor
# from sklearn.manifold import MDS

localpath = "previous/2017/"

results = pd.read_csv(localpath + 'sources/pst4p.csv', sep=';')

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

results.loc[:, 'id'] = results['OBEC'].astype(str) + '-' + results['OKRSEK'].astype(str)

pt = pd.pivot_table(results, values='POC_HLASU', index=['id'], columns=['KSTRANA'], aggfunc=sum).fillna(0).T

exclude = pt.columns[pt.sum() == 0]

ptp = pt / pt.sum(axis=0)

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

from scipy.stats import rankdata
ordered_arrs = dist.apply(lambda x: rankdata(x, method='ordinal'), axis=1)
ordered_matrix = pd.DataFrame(list(ordered_arrs), index=dist.index, columns=dist.columns)

ordered_matrix.iloc[0:10, 0:10]



import random
test = [(random.random() > 0.66) for i in range(0, len(ordered_matrix))]
ordered_matrix_sel = ordered_matrix.mul(test, axis=1).replace(0, len(ordered_matrix))

ordered_matrix2 = pd.DataFrame(list(ordered_matrix_sel.apply(lambda x: rankdata(x, method='ordinal'), axis=1)))
ordered_matrix2.apply(lambda x: np.argsort(x), axis=1)

ordered_matrix2.apply(lambda x: np.argsort(x), axis=0).apply(lambda x: x[0])