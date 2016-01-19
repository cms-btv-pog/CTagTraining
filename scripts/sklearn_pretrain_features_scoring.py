#! /bin/env python

'''
ranks the features according different criteria and return the list (and score)
'''

import rootpy.io as io
import rootpy
from ROOT import TH1D, TObjString
import numpy as np
np.set_printoptions(precision=5)
import root_numpy as rootnp
from sklearn.externals import joblib
log = rootpy.log["/sklearn_pretrain_features_scoring"]
log.setLevel(rootpy.log.INFO)
from argparse import ArgumentParser
from pdb import set_trace
import os
from glob import glob
from binning import pt_bins, eta_bins, flavors, sv_categories
import re
import inspect
import zlib
from copy import deepcopy
import prettyjson
import fileserver
from fnmatch import fnmatch
import pickle
import features
from sklearn.feature_selection import SelectKBest, chi2, f_classif
import prettyjson

parser = ArgumentParser()
parser.add_argument('out', help='pickle/json the ranking in one file')
parser.add_argument('--pickEvery', type=int, default=10, help='pick one training event every')
parser.add_argument('--category', default='*', help='category to be used for training/testing (POSIX regex)')
parser.add_argument('--sample', default='qcd', help='which sample to use qcd/ttjets')
parser.add_argument('--bkg', default='DUSG', help='background for evaluation')
parser.add_argument('--signal', default='C', help='signal for training')

args = parser.parse_args()


scripts_dir = os.path.join(os.environ['CTRAIN'], 'scripts')
fname_regex = re.compile('[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
qcd_txt_path= os.path.join(scripts_dir, 'data/flat_trees/%s_flat.list' % args.sample.lower())
input_files = [i.strip() for i in open(qcd_txt_path)]
if args.category != '*':
   input_files = [i for i in input_files if fnmatch(os.path.basename(i), args.category)]
   variables = features.general
   #add vtx vars
   if 'RecoVertex' in args.category:
      log.info('adding SV input variables')
      variables.extend(features.vertex)
   elif 'NoVertex' in args.category or 'PseudoVertex' in args.category:
      log.info('skipping SV input variables')
   else:
      log.info('Category selection does not specify SV type, adding SV input variables for safety')
      variables.extend(features.vertex)
   #add lep vars
   if 'SoftElectron' in args.category or 'SoftMuon' in args.category:
      log.info('adding SL input variables')
      variables.extend(features.leptons)
   elif 'NoSoftLepton' in args.category:
      log.info('skipping SL input variables')
   else:
      log.info('Category selection does not specify SL type, adding SL input variables for safety')
      variables.extend(features.leptons)
else:
   log.info('No category selection, using all the input variables')
   variables=features.general+features.vertex+features.leptons

log.info('Merging and converting the samples')
X = np.ndarray((0,len(variables)),float) # container to hold the combined trees in numpy array structure
y = np.ones(0) # container to hold the truth signal(1) or background(0) information
# weights = np.ones(0) # container holding the weights for each of the jets
for fname in input_files:
   log.info('processing file %s for training' % fname)
   ## with io.root_open(fname) as tfile:
   base = os.path.basename(fname)
   match = fname_regex.match(base)
   if not match:
      raise ValueError("Could not match the regex to the file %s" % fname)
   flavor = match.group('flavor')
   full_category = match.group('category')
   category = [i for i in sv_categories if i in full_category][0]
   if flavor != args.signal and flavor != args.bkg:
      log.info('flavour %s is not considered signal or background in this training and is omitted' % flavor) 
      continue
   
   nfiles_per_sample = None
   tree = rootnp.root2array(fname,'tree',variables,None,0,nfiles_per_sample,args.pickEvery,False,'weight')
   tree = rootnp.rec2array(tree)
   X = np.concatenate((X, tree),0)
   if flavor == args.signal:
      y = np.concatenate((y,np.ones(tree.shape[0])))
   else:
      y = np.concatenate((y,np.zeros(tree.shape[0])))
   
   # Getting the weights out
   ## if args.sample.lower() == 'qcd':
   ##    weights_tree = rootnp.root2array(fname,'tree','total_weight',None,0,nfiles_per_sample,args.pickEvery,False,'total_weight')   
   ##    weights = np.concatenate((weights,weights_tree),0)
   ## else:
   ##    weights = np.concatenate((weights,np.ones(tree.shape[0])))

log.info('Starting ANOVA feature ranking...')
anova_ranking = SelectKBest(f_classif, 'all')
anova_ranking.fit(X, y)
log.info('... done')


log.info('Starting chi2 feature ranking...')
#chi2 does not allow negativa values --> transform into 0-100 range
log.info('...scaling variables...')
mins = X.min(0)
maxes = X.max(0)
scales=[]
offsets=[]
for imin, imax in zip(mins, maxes):
   offsets.append(-1*imin)
   delta = imax-imin
   scales.append(100./delta if delta else 1.)

for row in X:
   for idx in range(len(row)):
      row[idx] = scales[idx]*(row[idx]+offsets[idx])
      if row[idx] < 0: set_trace()
log.info('... ranking ...')
chi2_ranking  = SelectKBest(chi2, 'all')
chi2_ranking.fit(X, y)
log.info('... done')

anova_scores = zip(variables, anova_ranking.scores_)
anova_scores.sort(key=lambda x: x[1], reverse=True)

chi2_scores = zip(variables, chi2_ranking.scores_)
chi2_scores.sort(key=lambda x: x[1], reverse=True)

scores = [
   {'method' : 'ANOVA', 'scores' : anova_scores}, 
   {'method' : 'chi2', 'scores' : anova_scores}
   ]

if '.json' in args.out:
   with open(args.out, 'w') as out:
      out.write(prettyjson.dumps(scores))
else:
   pickle.dump(scores, open(args.out, "wb"))
