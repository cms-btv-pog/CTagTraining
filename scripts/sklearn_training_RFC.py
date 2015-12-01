import re
import rootpy.io as io
import rootpy
from ROOT import TH1D
import numpy as np
np.set_printoptions(precision=5)
import root_numpy as rootnp
from sklearn.externals import joblib
log = rootpy.log["/toy_diagnostics"]
log.setLevel(rootpy.log.INFO)



#################################
#				#
# 	Training		#
#				#
#################################

variables = [
	'trackSip2dSig_0',
	'trackSip2dSig_1',
	'trackSip3dSig_0',
	'trackSip3dSig_1',
	'trackPtRel_0',
	'trackPtRel_1',
	'trackPPar_0',
	'trackPPar_1',
	'trackPtRatio_0',
	'trackJetDist_0',
	'trackDecayLenVal_0',
	'vertexEnergyRatio_0',
	'trackSip2dSigAboveCharm_0',
	'trackSip3dSigAboveCharm_0',
	'flightDistance2dSig_0',
	'flightDistance3dSig_0',
	'trackSumJetEtRatio',
	'trackSumJetDeltaR',
	'massVertexEnergyFraction_0',
	'leptonRatioRel_0',
]


input_files = [i.strip() for i in open('data/flat_trees/qcd_flat.list')]
flavors = ['C', 'B', 'DUSG']
sv_categories = ["NoVertex", "PseudoVertex", "RecoVertex"]
fname_regex = re.compile('[a-zA-Z_0-9\/]*\/?[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')

print 'Merging and converting the samples'
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
      skip_n_events = 10 # put this to 1 to include all the events
      tree = rootnp.root2array(fname,'tree',variables,None,0,nfiles_per_sample,skip_n_events,False,'weight')
      tree = rootnp.rec2array(tree)
      X = np.concatenate((X, tree),0)
      if flavor == "C":
      	y = np.concatenate((y,np.ones(tree.shape[0])))
      else:
      	y = np.concatenate((y,np.zeros(tree.shape[0])))
   
      # Getting the weights out
      weights_tree = rootnp.root2array(fname,'tree','weight',None,0,nfiles_per_sample,skip_n_events,False,'weight')
      weights = np.concatenate((weights,weights_tree),0)

print 'Starting training'
import time	
from sklearn.ensemble import RandomForestClassifier 
clf = RandomForestClassifier(n_estimators=500,n_jobs = 5, verbose = 3)
start = time.time()
clf.fit(X, y,weights)
end = time.time()
print 'training completed --> Elapsed time: ' , (end-start)/60 ,  'minutes'

training_file = './training_file/MVATraining.pkl'
print 'Dumping training file in: ' + training_file
joblib.dump(clf, training_file) 

	
      

#################################
#				#
# 	Validation		#
#				#
#################################

input_files = [i.strip() for i in open('data/flat_trees/ttjets_flat.list')]
pt_bins = [15, 40, 60, 90, 150, 400, 600]
eta_bins = [1.2, 2.1]
#flavors = ['C', 'B', 'DUSG']
#sv_categories = ["NoVertex", "PseudoVertex", "RecoVertex"]
fname_regex = re.compile('[a-zA-Z_0-9\/]*\/(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')

# you can reload the training if needed (or if you only want to do a validation on an existing training)
# but it is much faster to use the still existing classifier from the training
'''
print 'Loading training file from: ' + training_file
clf_val = joblib.load(training_file)
'''
clf_val = clf

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
      skip_n_events = 1 # put this to 1 to include all the events
      X_val = rootnp.root2array(fname,'tree',variables,None,0,nfiles_per_sample,skip_n_events,False,'weight')
      X_val = rootnp.rec2array(X_val)
      BDTG =  clf_val.predict_proba(X_val)[:,1]
      
      Output_variables = ['flavour','vertexCategory','jetPt','jetEta']
      Output_tree = rootnp.root2array(fname,'tree',Output_variables,None,0,nfiles_per_sample,skip_n_events,False,'weight')
      Output_tree = rootnp.rec2array(Output_tree)

      Output_tree_final = np.ndarray((Output_tree.shape[0],),dtype=[('flavour', float), ('vertexCategory', float), ('jetPt', float), ('jetEta', float), ('BDTG', float)])#, buffer = np.array([1,2,3,4,5]))
      for idx,val in enumerate(BDTG):
       Output_tree_final[idx][0] = Output_tree[idx][0]
       Output_tree_final[idx][1] = Output_tree[idx][1]
       Output_tree_final[idx][2] = Output_tree[idx][2]
       Output_tree_final[idx][3] = Output_tree[idx][3]
       Output_tree_final[idx][4] = BDTG[idx]
       
      Output_tree_final = Output_tree_final.view(np.recarray)
      tree = rootnp.array2root(Output_tree_final, 'trainPlusBDTG_CombinedSV'+category+'_'+flavor+'.root', 'tree') 
      log.info('Output file dumped in trainPlusBDTG_CombinedSV'+category+'_'+flavor+'.root')   
      
log.info('done')
