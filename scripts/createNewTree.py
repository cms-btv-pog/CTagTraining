#! /bin/env python

import sys
import os

from array import array
import time
import math
import multiprocessing
import rootpy.io as io
from rootpy.tree import Tree
import prettyjson
from RecoBTag.CTagging.trainingvars import training_vars
from argparse import ArgumentParser
import rootpy
from pdb import set_trace
import re
log = rootpy.log["/createNewTree"]
log.setLevel(rootpy.log.INFO)

def processNtuple(infile_name, outfile_name, variables, sample, 
                  flav_weight=False, pteta_weight=False, cat_weight=False,
                  tag=''):  
  log.debug("processing %s --> %s" % (infile_name, outfile_name))
  type_dict = {
    'i' : int,
    'l' : long,
    'f' : float
    }
  
  fname_regex = re.compile('[a-zA-Z_0-9\/]*\/?[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
  match = fname_regex.match(infile_name)

  if not match:
    raise ValueError("Could not match the regex to the file %s" % infile_name)
  flavor = match.group('flavor')
  full_category = match.group('category')
  if pteta_weight:    
    weight_file = io.root_open('data/%s_pt_eta_weights.root' % sample)
    flav_dir = weight_file.Get(flavor)
    categories = [i.name for i in flav_dir.keys()]
    category = [i for i in categories if i in full_category][0]
    weights = flav_dir.Get(category)

  flavor_weight = 1.
  if flav_weight:
    flavor_weight = prettyjson.loads(
      open('data/%s_flavor_weights.json' % sample).read()
      )[flavor]

  #put bias weights
  category_weight = 1.
  if cat_weight:
    categories_qcd = prettyjson.loads(
      open('data/qcd_category_weights.json').read()
      )[flavor]
    categories_ttj = prettyjson.loads(
      open('data/ttjets_category_weights.json').read()
      )[flavor]
    category = [i for i in categories_qcd.keys() if i in full_category][0]
    category_weight = categories_qcd[category] / categories_ttj[category] \
       if sample == 'qcd' else \
       categories_ttj[category] / categories_qcd[category]
  
  with io.root_open(outfile_name, 'recreate') as outfile:
    outtree = Tree('tree', title='c-tagging training tree')
    branches_def = dict((name, info['type']) for name, info in variables.iteritems())
    if pteta_weight:
      branches_def['kinematic_weight'] = 'F'
      branches_def['total_weight'] = 'F'
    if flav_weight:
      branches_def['flavour_weight'] = 'F'
      branches_def['total_weight'] = 'F'
    if cat_weight:
      branches_def['slcategory_weight'] = 'F'
      branches_def['total_weight'] = 'F'
        
    outtree.create_branches(
      branches_def
      )
    with io.root_open(infile_name) as infile:
      intree = infile.Get(full_category)
      for e_idx, entry in enumerate(intree):
        if e_idx % 1000 == 0:
          log.debug("processing entry: %i" % e_idx)
        for name, info in variables.iteritems():
          value = info['default']
          if hasattr(entry, info['var']):
            var = getattr(entry, info['var'])
            vtype = type_dict[info['type'].lower()]
            if 'idx' in info:
              if var.size() > info['idx']:
                value = vtype(var[info['idx']])
            else:
              value = vtype(var)
          #if value is nan, then set to default (maybe better if you skip the whole jet)
          value = info['default'] if math.isnan(value) else value
          setattr(outtree, name, value)
        total_weight = 1.
        if pteta_weight:
          bin_idx = weights.FindBin(entry.jetPt, abs(entry.jetEta))
          outtree.kinematic_weight = weights[bin_idx].value
          total_weight *= weights[bin_idx].value
        if flav_weight:
          outtree.flavour_weight = flavor_weight
          total_weight *= flavor_weight
        if cat_weight:
          outtree.slcategory_weight = category_weight
          total_weight *= category_weight
        if 'total_weight' in branches_def:
          outtree.total_weight = total_weight
          
        outtree.Fill()
  log.info("processing done [%s]" % tag)

def main(args):
  parallelProcesses = multiprocessing.cpu_count()
  
  outDirName = '%s/scripts/data/flat_trees/' % os.environ['CTRAIN'] if 'CTAG_FLAT_TREES_LOCATION' not in os.environ else os.environ['CTAG_FLAT_TREES_LOCATION']
  outDirName = os.path.join(outDirName, args.sample)
  if 'CTAG_FLAT_TREES_LOCATION' not in os.environ:
    log.warning("CTAG_FLAT_TREES_LOCATION was not set in the environment, therefore I will dump the trees into data/flat_trees")
  if not os.path.exists(outDirName):
    print "Creating new output directory: ", outDirName
    os.makedirs(outDirName)
  
  input_files = [i.strip() for i in open('data/inputs/%s.list' % args.sample)]
                
  variables = training_vars.keys() #just pick all for the moment
  branches = {}
  for varname in variables:
    varinfo = training_vars[varname]
    if 'max_idx' in varinfo:
      for idx in range(varinfo['max_idx']):
        branches['%s_%i' % (varname, idx)] = {
          'type' : varinfo['type'].swapcase(), 
          'default' : varinfo['default'],
          'var' : varname,
          'idx' : idx
          }
                
  # create Pool
  pool = multiprocessing.Pool(parallelProcesses)
  print "Using %i parallel processes" % parallelProcesses
  
  # run jobs
  nfiles = len(input_files)
  for idx, infile in enumerate(input_files): 
    base_input = os.path.basename(infile)
    outfile = os.path.join(outDirName, 'flat_%s' % base_input)
    proc_args = (
      infile, outfile, branches, args.sample,
      args.flav_weight, args.kin_weight, args.cat_weight
      )
    if args.debug:
      processNtuple(*proc_args)
    else:
      pool.apply_async(
        processNtuple, 
        args = (
          infile, outfile, branches, args.sample, 
          args.flav_weight, args.kin_weight, args.cat_weight,
          '%i/%i' % (idx, nfiles)
          )
        )
  pool.close()
  pool.join()
  

if __name__ == "__main__":
  parser = ArgumentParser()
  parser.add_argument('sample', help='sample to run on qcd or ttjets')
  parser.add_argument('--apply-pteta-weight',  dest='kin_weight', action='store_true', help='applies pt-eta weight')
  parser.add_argument('--apply-category-weight',  dest='cat_weight', action='store_true', help='applies category weight (from both qcd and ttjets)')
  parser.add_argument('--apply-flavor-weight', dest='flav_weight', action='store_true', help='applies flavour weight')
  parser.add_argument('--debug', action='store_true', help='does not run in parallel')
  args = parser.parse_args()
  if args.debug:
    log.setLevel(rootpy.log.DEBUG)
  import ROOT
  ROOT.gROOT.SetBatch(True)
  main(args)

#  LocalWords:  inFileList
