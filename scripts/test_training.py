#! /bin/env python

'''
Tests MVA performance on multiple cores to speed it up
'''

import rootpy.io as io
import rootpy
from rootpy.tree import Tree
import ROOT
import array
from sklearn.externals import joblib
log = rootpy.log["/test_training"]
log.setLevel(rootpy.log.INFO)
from argparse import ArgumentParser
from pdb import set_trace
import os
import re
import fileserver
from fnmatch import fnmatch
import localsettings as site
import pickle
import features
import multiprocessing

parser = ArgumentParser()
parser.add_argument('training', help='training to be used')
parser.add_argument('inputs', help='input root files to test on')
parser.add_argument('output', help='output directory')
parser.add_argument('--testEvery', type=int, default=1,  help='pick one testing event every')
parser.add_argument('--category', default='*', help='category to be used for training/testing (POSIX regex)')
parser.add_argument('--debug', action='store_true')
args = parser.parse_args()

class TMVAEvaluator(object):
   def __init__(self, infile, variables):
      nvars = len(variables)
      TMVA_tools = ROOT.TMVA.Tools.Instance()
      self.reader = ROOT.TMVA.Reader('TMVAClassification_BDTG')
      self.vars = [array.array('f',[0]) for _ in range(nvars)]
      self.nvars = nvars
      for idx, name in enumerate(variables):
         self.reader.AddVariable(name, self.vars[idx])
      self.reader.BookMVA(
         "BDTG",
         infile,
         )
      
   def predict_proba(vals2d):
      vals = vals2d[0]
      if len(vals) != len(self.vars):
         raise RuntimeError("Values provided are not matching the input variables (too few/many)")
      for val, var in zip(vals, self.vars):
         var[0] = val
      return [[None, self.reader.EvaluateMVA("BDTG")]] 
      

def get_training(input_file, variables):
   if input_file.endswith('.xml'):      
      return TMVAEvaluator(input_file, variables)
   else:
      return joblib.load(input_file)

def test_file(inname, outname, train_file, variables, testEvery):
   log.info('START processing: %s', os.path.basename(inname))
   bdt = get_training(train_file, variables)
   with io.root_open(outname, 'w') as tout:
      out_tree = Tree('tree')
      out_tree.create_branches({
            'flavour' : 'F',
            'vertexCategory' : 'I', 
            'jetPt' : 'F',
            'jetEta' : 'F',
            'BDTG' : 'F',
            })
      with io.root_open(inname) as tin:
         in_tree = tin.tree
         in_tree.SetBranchStatus('*', 0)
         in_tree.SetBranchStatus('flavour', 1)
         in_tree.SetBranchStatus('vertexCategory', 1)
         in_tree.SetBranchStatus('jetPt', 1)
         in_tree.SetBranchStatus('jetEta', 1)
         for var in variables:
            in_tree.SetBranchStatus(var, 1)
         for idx, entry in enumerate(in_tree):
            if (idx % testEvery) == 0: continue
            var_vals = [getattr(entry, i) for i in variables]
            btd_out = bdt.predict_proba([var_vals])[0][1]
            out_tree.flavour = entry.flavour
            out_tree.vertexCategory = entry.vertexCategory
            out_tree.jetPt = entry.jetPt
            out_tree.jetEta = entry.jetEta
            out_tree.BDTG = btd_out
            out_tree.fill()
      out_tree.write()
   log.info('DONE processing: %s', os.path.basename(inname))

input_files = [i.strip() for i in open(args.inputs)]
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


if not os.path.isdir(args.output):
   os.makedirs(args.output)

output_files=[]
for infile in input_files:
   split = os.path.basename(infile).replace('.root','').split('_')
   category = split[-2]
   flavour = split[-1]
   output_files.append( 
      os.path.join(
         args.output,
         '_'.join(['tested', category, flavour])+'.root'
         )
      )

if not args.debug:
   ncpus = multiprocessing.cpu_count()
   pool = multiprocessing.Pool(ncpus)
   for i, o in zip(input_files, output_files):
      pool.apply_async(test_file, args=(i,o, args.training, variables, args.testEvery))
      
   pool.close()
   pool.join()
else:
   for i, o in zip(input_files, output_files):
      test_file(i,o, args.training, variables, args.testEvery)
