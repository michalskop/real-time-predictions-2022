"""Prepare groups of polling stations."""

import os
import pandas as pd
import numpy as np
# Distance matrix / MDS
import dcor
from sklearn.manifold import MDS

localpath = "previous/2018/"
localpath0 = "2022/preparation/"

batches = pd.read_csv(localpath + 'batches.csv')
selected_assemblies = pd.read_csv(localpath0 + "/polling_stations/assemblies_80.csv")
assemblies = pd.read_csv(localpath + 'assemblies_all.csv')

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

for code in selected_assemblies["KODZASTUP"]:
  print(code)
  file_path = localpath + 'results/' + str(code) + "/" # + 'results.csv'
  totals = pd.read_csv(file_path + 'results.csv')
  ptt = pd.pivot_table(totals, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
  ptt['percent'] = ptt['HLASY'] / ptt['HLASY'].sum() * 100

  results = pd.read_csv(localpath + 'results/' + str(code) + '/results.csv')

  pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['OKRSEK'], aggfunc=sum).reset_index()

  ptp = pt.iloc[:, 1:] / pt.iloc[:, 1:].sum(axis=0)

  dist_arr = dcor.distances.pairwise_distances(ptp.T)
  dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)

  mds = MDS()
  X_transform = mds.fit_transform(ptp.T)

  dims = pd.DataFrame(cmdscale(dist_arr)[0])
  # dims.loc[:, 0:3].to_csv(localpath + 'reality_' + str(code) + '_mds.csv', index=False)

  dims.index = dist.index

  # groups
  d2 = pd.DataFrame((dims.iloc[:, 0] * dims.iloc[:, 0] + dims.iloc[:, 1] * dims.iloc[:, 1]).apply(np.sqrt))
  d2.columns = ['dist']
  q = d2.quantile(0.33)
  d2['group'] = 0
  d2 = d2.merge(dims.loc[:, 0:1], left_index=True, right_index=True)
  d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] >= 0), 'group'] = 1
  d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] < 0), 'group'] = 2
  d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] < 0), 'group'] = 3
  d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] >= 0), 'group'] = 4

  d2.to_csv(localpath + 'tests/reality_' + str(code) + '_mds_groups.csv')
