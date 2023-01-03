"""Prepare groups of polling stations."""

# import os
import pandas as pd
import numpy as np
# Distance matrix / MDS
import dcor
from sklearn.manifold import MDS

localpath = "previous/2013/"

results = pd.read_csv(localpath + 'sources/pet1.csv', sep=';')

round = 1

candidates = [1, 2, 3, 4, 5, 6, 7, 8, 9]
candidates_votes = [('HLASY_' + str(c).zfill(2)) for c in candidates]

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


resround = results[results['KOLO'] == round]

pt = resround.loc[:, candidates_votes].T

exclude = pt.columns[pt.sum() == 0]

pt = pt.drop(exclude, axis=1)
# pt.loc[:, ~pt.columns.isin(list(exclude))]

ptp = pt / pt.sum(axis=0)

dist_arr = dcor.distances.pairwise_distances(ptp.T)
dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)

# dims = pd.DataFrame(cmdscale(dist.iloc[0:14000, 0:14000])[0])
# dims = pd.DataFrame(cmdscale(dist)[0])
dims = pd.DataFrame(cmdscale(dist)[0])

# dims.apply(lambda x: abs(x)).sum()

d2 = pd.DataFrame((dims.iloc[:, 0] * dims.iloc[:, 0] + dims.iloc[:, 1] * dims.iloc[:, 1]).apply(np.sqrt))
d2.columns = ['dist']
q = d2.quantile(0.33)
d2.loc[:, [0, 1]] = dims.loc[:, [0, 1]]
d2['group'] = 0
d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] >= 0), 'group'] = 1
d2.loc[(d2['dist'] > q['dist']) & (d2[0] >= 0) & (d2[1] < 0), 'group'] = 2
d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] < 0), 'group'] = 3
d2.loc[(d2['dist'] > q['dist']) & (d2[0] < 0) & (d2[1] >= 0), 'group'] = 4

d2.loc[:, ['OBEC', 'OKRSEK']] = resround[~resround.index.isin(list(exclude))].loc[:, ['OBEC', 'OKRSEK']]

d2.to_csv(localpath + 'reality_mds_5_groups.csv')
