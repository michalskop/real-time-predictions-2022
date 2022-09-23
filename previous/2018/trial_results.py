"""Test - trials with results."""

import os
import pandas as pd

localpath = "previous/2018/"

batches = pd.read_csv(localpath + 'batches.csv')

code = 554782 # Praha

assemblies = pd.read_csv(localpath + 'assemblies_all.csv')

assemblies[assemblies['KODZASTUP'] == code]

file_path = localpath + 'results/' + str(code) + "/" # + 'results.csv'

totals = pd.read_csv(file_path + 'results.csv')
ptt = pd.pivot_table(totals, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
ptt['percent'] = ptt['HLASY'] / ptt['HLASY'].sum() * 100

test = ptt.copy()

for f in sorted(os.listdir(file_path))[1:]:
  results = pd.read_csv(file_path + f)
  pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], aggfunc=sum).reset_index()
  pt['percent'] = pt['HLASY'] / pt['HLASY'].sum() * 100
  t = batches[batches['n'] == int(f.split('_')[1].split('.')[0])]['time'].values[0]
  pt.rename(columns={'HLASY': t}, inplace=True)
  test = test.merge(pt.loc[:, ['STRANA', t]], on='STRANA')
    
test.to_csv(localpath + 'realityv_' + str(code) + '.csv', index=False)

# FROM SMALLEST TO LARGEST
results = pd.read_csv(localpath + 'results/' + str(code) + '/results.csv')

pt = pd.pivot_table(results, values='HLASY', index=['STRANA'], columns=['OKRSEK'], aggfunc=sum).reset_index()

size = pt.iloc[:, 1:].sum(axis=0).sort_values(ascending=False)
size.index

provisonal = pt.loc[:, ['STRANA']]
provisonal[0] = 0
for i in size.index:
  provisonal[i] = provisonal.iloc[:, -1] + pt[i]
provisonal.T.to_csv(localpath + 'realityv_' + str(code) + '_b2s.csv', index=False)

# Distance matrix / MDS
import dcor
from scipy.spatial import distance_matrix
from sklearn.manifold import  MDS

pt
ptp = pt.iloc[:, 1:] / pt.iloc[:, 1:].sum(axis=0)
ptp.index = pt['STRANA']

dist_arr = dcor.distances.pairwise_distances(ptp.T)
dist = pd.DataFrame(dist_arr, index=ptp.columns, columns=ptp.columns)

mds = MDS()
X_transform = mds.fit_transform(ptp.T)

import numpy as np
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


dims = pd.DataFrame(cmdscale(dist_arr)[0])
dims.loc[:, 0:3].to_csv(localpath + 'reality_' + str(code) + '_mds.csv', index=False)

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
