#! /bin/env python

'''
Main training script for tree-related classifiers (non NN)
'''

import rootpy.io as io
import rootpy
from ROOT import TH1D, TObjString
import numpy as np
np.set_printoptions(precision=5)
import root_numpy as rootnp
from sklearn.externals import joblib
log = rootpy.log["/sklearn_training_RFC"]
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
import localsettings as site
import pickle
import features
import sklearn_to_tmva as convert

parser = ArgumentParser()
parser.add_argument('trainingTag', help='Tag to be used')
parser.add_argument('--pickEvery', type=int, default=10, help='pick one training event every')
parser.add_argument('--testEvery', type=int, default=1,  help='pick one testing event every')
parser.add_argument('-o', dest='out', default='', help='pickle the training in one file')
parser.add_argument('--ntrees', type=int, default=500, help='number of trees')
parser.add_argument('--absoluteSplit', type=int, default=100, help='RFC min_samples_split')
parser.add_argument('--relativeSplit', type=float, default=-1, help='RFC min_samples_split')
parser.add_argument('--learningRate', type=float, default=0.2, help='GBC only')
parser.add_argument('--maxDepth', type=int, default=-1, help='max tree depth')
parser.add_argument('--njobs', type=int, default=8, help='number of cores to be used (RFC only)')
parser.add_argument('--notest', action='store_true')
parser.add_argument('--signal', default='C', help='signal for training')
parser.add_argument('--bkg', default='DUSG', help='background for training')
parser.add_argument('--algo', default='RFC', help='options RFC (Random Forest) or GBC (Gradient boost)')
parser.add_argument('--batch', action='store_true', help='batch mode')
parser.add_argument('--category', default='*', help='category to be used for training/testing (POSIX regex)')
parser.add_argument('--TMVAOut', action='store_true', help='return output in TMVA Style (BDT output in [-1,1] range')
parser.add_argument('--inputs', default='data/flat_trees/qcd_flat.list', help='training file list')
parser.add_argument('--testInputs', default='data/flat_trees/ttjets_flat.list', help='category to be used for training/testing (POSIX regex)')

#parser.add_argument('--apply-pteta-weight',  dest='kin_weight', action='store_true', help='applies pt-eta weight')
args = parser.parse_args()

args_dict = deepcopy(args.__dict__)
current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))

watermark = TObjString(prettyjson.dumps(args_dict))
codeset = open(current_file).read() #zlib.compress(open(current_file).read()) compressing does not work well with root...
codemark = TObjString(
   codeset
)

#
#   TRAINING
#

scripts_dir = os.path.join(os.environ['CTRAIN'], 'scripts')
fname_regex = re.compile('[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
qcd_txt_path= os.path.join(scripts_dir, args.inputs)
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
if args.batch:
   #use xrootd to fetch file in batch mode
   input_files = [ site.local_2_xrd(i) for i in input_files]
pool_files = []

log.info('Merging and converting the samples')
X = np.ndarray((0,len(variables)),float) # container to hold the combined trees in numpy array structure
y = np.ones(0) # container to hold the truth signal(1) or background(0) information
weights = np.ones(0) # container holding the weights for each of the jets
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
   
   extfile = fileserver.serve(fname)
   pool_files.append(extfile)
   nfiles_per_sample = None
   tree = rootnp.root2array(extfile.path,'tree',variables,None,0,nfiles_per_sample,args.pickEvery,False,'weight')
   tree = rootnp.rec2array(tree)
   X = np.concatenate((X, tree),0)
   if flavor == args.signal:
   	y = np.concatenate((y,np.ones(tree.shape[0])))
   else:
   	y = np.concatenate((y,np.zeros(tree.shape[0])))
   
   # Getting the weights out
   weights_tree = rootnp.root2array(extfile.path,'tree','total_weight',None,0,nfiles_per_sample,args.pickEvery,False,'total_weight')
   weights = np.concatenate((weights,weights_tree),0)


log.info('Starting training')
import time	
from sklearn.ensemble import RandomForestClassifier 
from sklearn.ensemble import GradientBoostingClassifier
splitting = int(args.relativeSplit*len(X)) if args.relativeSplit > 0 else args.absoluteSplit
max_depth = args.maxDepth if args.maxDepth > 0 else None

clf = None
if args.algo == 'RFC':
   clf = RandomForestClassifier(
      n_estimators=args.ntrees, n_jobs =args.njobs, verbose = 1,
      min_samples_split=splitting, max_depth=max_depth)
elif args.algo == 'GBC':
   clf = GradientBoostingClassifier(
      n_estimators=args.ntrees, verbose = 1, max_depth=max_depth,
      min_samples_split=splitting, learning_rate=args.learningRate)      
else:
   raise RuntimeError('algo option can olny be RFC or GBC')

start = time.time()
clf.fit(X, y,weights)
end = time.time()
log.info('training completed --> Elapsed time: %.1f minutes' % ((end-start)/60))

## num_nodes = [nnodes(i.tree_) for i in clf.estimators_]
## 
## tot_nodes = sum(num_nodes)
## mean = float(tot_nodes)/len(num_nodes)
## print tot_nodes, mean

if args.out:
   log.info('Dumping training file in: ' + args.out)
   out_ext = (args.out).split('.')[-1]
   if (out_ext == 'xml'):
   	convert.gbr_to_tmva(clf,X,args.out,mva_name = "BDTG",coef = 10, var_names = variables)
   else:
   	joblib.dump(clf, args.out, compress=True)

#################################
#				#
# 	Validation		#
#				#
#################################

# you can reload the training if needed (or if you only want to do a validation on an existing training)
# but it is much faster to use the still existing classifier from the training
'''
print 'Loading training file from: ' + training_file
clf_val = joblib.load(training_file)
'''
clf_val = clf
#fname_regex = re.compile('[a-zA-Z_0-9\/]*\/(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
ttj_txt_path= os.path.join(scripts_dir, args.testInputs)
input_files = [i.strip() for i in open(ttj_txt_path)]
if args.category != '*':
   input_files = [i for i in input_files if fnmatch(os.path.basename(i), args.category)]
if args.batch:
   #use xrootd to fetch file in batch mode
   input_files = [ site.local_2_xrd(i) for i in input_files]

dirpath = 'tested_files/%s' % args.trainingTag if not args.batch else ''
if not os.path.isdir(dirpath) and not args.batch:
   os.makedirs(dirpath)

var_ranking = zip(variables,clf.feature_importances_)
var_ranking.sort(key=lambda x: x[1], reverse=True)
picklename = '%sranking.p' % (args.trainingTag if args.batch else '')
picklename = os.path.join(dirpath, picklename)
pickle.dump( var_ranking, open( picklename, "wb" ) )

pool_files = []
for fname in input_files:
   log.info('processing file %s' % fname)
   ## with io.root_open(fname) as tfile:
   base = os.path.basename(fname)
   match = fname_regex.match(base)
   if not match:
      raise ValueError("Could not match the regex to the file %s" % fname)
   flavor = match.group('flavor')
   full_category = match.group('category')
   category = [i for i in sv_categories if i in full_category][0]
   
   extfile = fileserver.serve(fname)
   pool_files.append(extfile)
   nfiles_per_sample = None
   X_val = rootnp.root2array(extfile.path,'tree',variables,None,0,nfiles_per_sample,args.testEvery,False,'weight')
   X_val = rootnp.rec2array(X_val)
   BDTG =  clf_val.predict_proba(X_val)[:,1]
   if (args.TMVAOut):
   	BDTG = [i*2-1 for i in BDTG]
   	
   Output_variables = ['flavour','vertexCategory','jetPt','jetEta']
   Output_tree = rootnp.root2array(extfile.path,'tree',Output_variables,None,0,nfiles_per_sample,args.testEvery,False,'weight')
   Output_tree = rootnp.rec2array(Output_tree)

   Output_tree_final = np.ndarray((Output_tree.shape[0],),dtype=[('flavour', float), ('vertexCategory', float), ('jetPt', float), ('jetEta', float), ('BDTG', float)])#, buffer = np.array([1,2,3,4,5]))
   for idx,val in enumerate(BDTG):
    Output_tree_final[idx][0] = Output_tree[idx][0]
    Output_tree_final[idx][1] = Output_tree[idx][1]
    Output_tree_final[idx][2] = Output_tree[idx][2]
    Output_tree_final[idx][3] = Output_tree[idx][3]
    Output_tree_final[idx][4] = BDTG[idx]
    
   Output_tree_final = Output_tree_final.view(np.recarray)
   outname = 'trainPlusBDTG_CombinedSV%s_%s.root' % (category, flavor) if not args.batch else \
      '%strainPlusBDTG_CombinedSV%s_%s.root' % (args.trainingTag, category, flavor)
   outfile = os.path.join(dirpath, outname)
   tree = rootnp.array2root(Output_tree_final, outfile, 'tree')
   with io.root_open(outfile, 'update') as tout:
      tout.WriteTObject(watermark, 'watermark')
      tout.WriteTObject(codemark, 'codemark')
   log.info('Output file dumped in %s' % outfile)
log.info('done')
