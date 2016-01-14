#! /bin/env python

'''
Plotting Correlation matrix for variables of specified input samples
'''

import rootpy.io as io
import rootpy
from ROOT import TH1D, TObjString
import numpy as np
np.set_printoptions(precision=5)
import root_numpy as rootnp
from sklearn.externals import joblib
log = rootpy.log["/Correlation_Matrix"]
log.setLevel(rootpy.log.INFO)
from argparse import ArgumentParser
from binning import pt_bins, eta_bins, flavors, sv_categories
import pandas as pd
import matplotlib.pyplot as plt
import os
import re
import inspect
import zlib
from copy import deepcopy
import prettyjson
import fileserver
from fnmatch import fnmatch
import localsettings as site
import features


parser = ArgumentParser()
parser.add_argument('--flavour', default='C', help='the flavour fto be used for drawing the correlation matrix')
parser.add_argument('--category', default='*', help='category to be used for drawing correlation matrix (POSIX regex)')
parser.add_argument('--pickEvery', type=int, default=10, help='pick one event every to draw the correlation matrix')
parser.add_argument('--batch', action='store_true', help='batch mode')

args = parser.parse_args()

args_dict = deepcopy(args.__dict__)
current_file = os.path.abspath(inspect.getfile(inspect.currentframe()))

watermark = TObjString(prettyjson.dumps(args_dict))
codeset = open(current_file).read() #zlib.compress(open(current_file).read()) compressing does not work well with root...
codemark = TObjString(
   codeset
)


#
# 	CORRELATION MATRIX
#



scripts_dir = os.path.join(os.environ['CTRAIN'], 'scripts')
fname_regex = re.compile('[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
qcd_txt_path= os.path.join(scripts_dir, 'data/flat_trees/qcd_flat.list')
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
for fname in input_files:
   ## with io.root_open(fname) as tfile:
   base = os.path.basename(fname)
   match = fname_regex.match(base)
   if not match:
      raise ValueError("Could not match the regex to the file %s" % fname)
   flavor = match.group('flavor')
   full_category = match.group('category')
   category = [i for i in sv_categories if i in full_category][0]
   if flavor != args.flavour: 
      continue
   
   log.info('processing file %s' % fname)
   extfile = fileserver.serve(fname)
   pool_files.append(extfile)
   nfiles_per_sample = None
   tree = rootnp.root2array(extfile.path,'tree',variables,None,0,nfiles_per_sample,args.pickEvery,False,'weight')
   tree = rootnp.rec2array(tree)
   X = np.concatenate((X, tree),0)
   y = np.concatenate((y,np.ones(tree.shape[0]))) # This is needed for pandas DataFrame Structure

log.info('Converting data to pandas DataFrame structure')
# Create a pandas DataFrame for our data
# this provides many convenience functions
# for exploring your dataset
# see http://betatim.github.io/posts/sklearn-for-TMVA-users/ for more info
# need to reshape y so it is a 2D array with one column
df = pd.DataFrame(np.hstack((X, y.reshape(y.shape[0], -1))),columns=variables+['y'])

corrmat = df.drop('y', 1).corr(method='pearson', min_periods=1)

fig, ax1 = plt.subplots(ncols=1, figsize=(12,10))
    
opts = {'cmap': plt.get_cmap("RdBu"),'vmin': -1, 'vmax': +1}
heatmap1 = ax1.pcolor(corrmat, **opts)
plt.colorbar(heatmap1, ax=ax1)

cat_ext = ''
if args.category != '*':
	cat_ext = ' (' + args.category.split('*')[1] + ')'
ax1.set_title("Correlation Matrix: " + args.flavour + cat_ext)

labels = corrmat.columns.values
for ax in (ax1,):
	# shift location of ticks to center of the bins
	ax.set_xticks(np.arange(len(labels))+0.5, minor=False)
	ax.set_yticks(np.arange(len(labels))+0.5, minor=False)
	ax.set_xticklabels(labels, minor=False, ha='right', rotation=70)
	ax.set_yticklabels(labels, minor=False)
        
plt.tight_layout()


if args.category != '*':
	log.info("Dumping output in ./Correlation_Matrix_" + args.flavour + "_" + args.category.split('*')[1] + ".png" )
	plt.savefig("Correlation_Matrix_" + args.flavour + "_" + args.category.split('*')[1] + ".png")
else:
	log.info("Dumping output in ./Correlation_Matrix_" + args.flavour + "_Inclusive.png" )
	plt.savefig("Correlation_Matrix_" + args.flavour + "_Inclusive.png")
   	
log.info('done')
