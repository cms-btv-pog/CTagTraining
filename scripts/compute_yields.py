#! /bin/env python

from argparse import ArgumentParser
import rootpy.io as io
from rootpy.plotting import Hist2D
import prettyjson
from itertools import product 
import glob
import re
import rootpy
from pdb import set_trace
from binning import itercuts, flavors, sv_categories
log = rootpy.log["/toy_diagnostics"]
log.setLevel(rootpy.log.INFO)

parser = ArgumentParser()
parser.add_argument('sample', help='sample to run on qcd or ttjets')
parser.add_argument('--debug',  action='store_true', help='debug mode')
args = parser.parse_args()
if args.debug:
   log.setLevel(rootpy.log.DEBUG)

input_files = [i.strip() for i in open('data/inputs/%s.list' % args.sample)]

fname_regex = re.compile('[a-zA-Z_0-9\/]*\/?[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')
yields = {}

for flavor in flavors:
   yields[flavor] = {}
   for category in sv_categories:
      yields[flavor][category] = {}

for fname in input_files:
   log.info('processing file %s' % fname)
   with io.root_open(fname) as tfile:
      match = fname_regex.match(fname)
      if not match:
         raise ValueError("Could not match the regex to the file %s" % fname)
      flavor = match.group('flavor')
      full_category = match.group('category')
      category = [i for i in sv_categories if i in full_category][0]
      tree = tfile.Get(full_category)
      for cut in itercuts():
         nentries = float(tree.GetEntries(cut))
         if cut not in yields[flavor][category]:
            yields[flavor][category][cut] = 0
         yields[flavor][category][cut] += nentries

with open('data/%s_yields.json'  % args.sample, 'w') as out:
   out.write(prettyjson.dumps(yields))
