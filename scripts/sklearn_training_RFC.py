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

parser = ArgumentParser()
parser.add_argument('trainingTag', help='Tag to be used')
parser.add_argument('--pickEvery', type=int, default=10, help='pick one training event every')
parser.add_argument('--testEvery', type=int, default=1,  help='pick one testing event every')
parser.add_argument('-o', dest='out', default='', help='pickle the training in one file')
parser.add_argument('--ntrees', type=int, default=500, help='number of trees')
parser.add_argument('--absoluteSplit', type=int, default=100, help='RFC min_samples_split')
parser.add_argument('--relativeSplit', type=float, default=-1, help='RFC min_samples_split')
parser.add_argument('--notest', action='store_true')

#parser.add_argument('--apply-pteta-weight',  dest='kin_weight', action='store_true', help='applies pt-eta weight')
args = parser.parse_args()

args_dict = deepcopy(args.__dict__)
current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))

watermark = TObjString(prettyjson.dumps(args_dict))
codeset = open(current_file).read() #zlib.compress(open(current_file).read()) compressing does not work well with root...
codemark = TObjString(
   codeset
)

#################################
#				#
# 	Training		#
#				#
#################################

variables = [
  #"flavour",
  #"vertexCategory",
  #"vertexLeptonCategory",
  #"jetPt",
  #"trackJetPt",
  #"jetEta",
  "trackSip2dSig_0", "trackSip2dSig_1",#"trackSip2dSig_2",
  "trackSip3dSig_0", "trackSip3dSig_1",#"trackSip3dSig_2",
  #"trackSip2dVal_0", "trackSip2dVal_1", "trackSip2dVal_2",
  #"trackSip3dVal_0", "trackSip3dVal_1", "trackSip3dVal_2",
  "trackPtRel_0", "trackPtRel_1",# "trackPtRel_2",
  "trackPPar_0", "trackPPar_1",# "trackPPar_2",
  "trackEtaRel_0","trackEtaRel_1",# "trackEtaRel_2",
  "trackDeltaR_0", "trackDeltaR_1",# "trackDeltaR_2",
  "trackPtRatio_0", "trackPtRatio_1",# "trackPtRatio_2",
  "trackPParRatio_0", "trackPParRatio_1",# "trackPParRatio_2",
  "trackJetDist_0","trackJetDist_1",# "trackJetDist_2",
  "trackDecayLenVal_0", "trackDecayLenVal_1",# "trackDecayLenVal_2",
  "vertexMass_0",
  "vertexEnergyRatio_0",
  "trackSip2dSigAboveCharm_0",
  "trackSip3dSigAboveCharm_0",
  "flightDistance2dSig_0",
  "flightDistance3dSig_0",
  #"flightDistance2dVal_0",
  #"flightDistance3dVal_0",
  "trackSumJetEtRatio",
  "vertexJetDeltaR_0",
  "trackSumJetDeltaR",
  #"trackSip2dValAboveCharm_0",
  #"trackSip3dValAboveCharm_0",
  #"vertexFitProb_0",
  #"chargedHadronEnergyFraction",
  #"neutralHadronEnergyFraction",
  #"photonEnergyFraction",
  #"electronEnergyFraction",
  #"muonEnergyFraction",
  "massVertexEnergyFraction_0",
  "vertexBoostOverSqrtJetPt_0",
  "leptonPtRel_0","leptonPtRel_1",#"leptonPtRel_2",
  "leptonSip3d_0","leptonSip3d_1",#"leptonSip3d_2",
  "leptonDeltaR_0","leptonDeltaR_1",#"leptonDeltaR_2",
  "leptonRatioRel_0","leptonRatioRel_1",#"leptonRatioRel_2",
  "leptonEtaRel_0","leptonEtaRel_1",#"leptonEtaRel_2",
  "leptonRatio_0","leptonRatio_1",#"leptonRatio_2",
  "vertexNTracks_0",
  "jetNSecondaryVertices",
  "jetNTracks",
  ]
###   variables = [
###   	'trackSip2dSig_0',
###   	'trackSip2dSig_1',
###   	'trackSip3dSig_0',
###   	'trackSip3dSig_1',
###   	'trackPtRel_0',
###   	'trackPtRel_1',
###   	'trackPPar_0',
###   	'trackPPar_1',
###   	'trackPtRatio_0',
###   	'trackJetDist_0',
###   	'trackDecayLenVal_0',
###   	'vertexEnergyRatio_0',
###   	'trackSip2dSigAboveCharm_0',
###   	'trackSip3dSigAboveCharm_0',
###   	'flightDistance2dSig_0',
###   	'flightDistance3dSig_0',
###   	'trackSumJetEtRatio',
###   	'trackSumJetDeltaR',
###   	'massVertexEnergyFraction_0',
###   	'leptonRatioRel_0',
###   ]

fname_regex = re.compile('[a-zA-Z_0-9\/]*\/?[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
input_files = [i.strip() for i in open('data/flat_trees/qcd_flat.list')]

log.info('Merging and converting the samples')
X = np.ndarray((0,len(variables)),float) # container to hold the combined trees in numpy array structure
y = np.ones(0) # container to hold the truth signal(1) or background(0) information
weights = np.ones(0) # container holding the weights for each of the jets
for fname in input_files:
   log.info('processing file %s for training' % fname)
   with io.root_open(fname) as tfile:
      match = fname_regex.match(fname)
      if not match:
         raise ValueError("Could not match the regex to the file %s" % fname)
      flavor = match.group('flavor')
      full_category = match.group('category')
      category = [i for i in sv_categories if i in full_category][0]
      if flavor == 'B':
         log.info('flavour %s is not considered signal or background in this training and is omitted' % flavor) 
         continue
      
      nfiles_per_sample = None
      tree = rootnp.root2array(fname,'tree',variables,None,0,nfiles_per_sample,args.pickEvery,False,'weight')
      tree = rootnp.rec2array(tree)
      X = np.concatenate((X, tree),0)
      if flavor == "C":
      	y = np.concatenate((y,np.ones(tree.shape[0])))
      else:
      	y = np.concatenate((y,np.zeros(tree.shape[0])))
   
      # Getting the weights out
      weights_tree = rootnp.root2array(fname,'tree','total_weight',None,0,nfiles_per_sample,args.pickEvery,False,'total_weight')
      weights = np.concatenate((weights,weights_tree),0)


log.info('Starting training')
import time	
from sklearn.ensemble import RandomForestClassifier 
splitting = int(args.relativeSplit*len(X)) if args.relativeSplit > 0 else args.absoluteSplit

clf = RandomForestClassifier(
   n_estimators=args.ntrees, n_jobs = 5, verbose = 1,
   min_samples_split=splitting)
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
input_files = [i.strip() for i in open('data/flat_trees/ttjets_flat.list')]
dirpath = 'tested_files/%s' % args.trainingTag
if not os.path.isdir(dirpath):
   os.makedirs(dirpath)

for fname in input_files:
   log.info('processing file %s' % fname)
   with io.root_open(fname) as tfile:
      match = fname_regex.match(fname)
      if not match:
         raise ValueError("Could not match the regex to the file %s" % fname)
      flavor = match.group('flavor')
      full_category = match.group('category')
      category = [i for i in sv_categories if i in full_category][0]
      
      nfiles_per_sample = None
      X_val = rootnp.root2array(fname,'tree',variables,None,0,nfiles_per_sample,args.testEvery,False,'weight')
      X_val = rootnp.rec2array(X_val)
      BDTG =  clf_val.predict_proba(X_val)[:,1]
      
      Output_variables = ['flavour','vertexCategory','jetPt','jetEta']
      Output_tree = rootnp.root2array(fname,'tree',Output_variables,None,0,nfiles_per_sample,args.testEvery,False,'weight')
      Output_tree = rootnp.rec2array(Output_tree)

      Output_tree_final = np.ndarray((Output_tree.shape[0],),dtype=[('flavour', float), ('vertexCategory', float), ('jetPt', float), ('jetEta', float), ('BDTG', float)])#, buffer = np.array([1,2,3,4,5]))
      for idx,val in enumerate(BDTG):
       Output_tree_final[idx][0] = Output_tree[idx][0]
       Output_tree_final[idx][1] = Output_tree[idx][1]
       Output_tree_final[idx][2] = Output_tree[idx][2]
       Output_tree_final[idx][3] = Output_tree[idx][3]
       Output_tree_final[idx][4] = BDTG[idx]
       
      Output_tree_final = Output_tree_final.view(np.recarray)
      outfile = 'tested_files/%s/trainPlusBDTG_CombinedSV%s_%s.root' % (args.trainingTag, category, flavor)
      tree = rootnp.array2root(Output_tree_final, outfile, 'tree')
      with io.root_open(outfile, 'update') as tout:
         tout.WriteTObject(watermark, 'watermark')
         tout.WriteTObject(codemark, 'codemark')
      log.info('Output file dumped in %s' % outfile)
log.info('done')
