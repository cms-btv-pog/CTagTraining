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
log = rootpy.log["/toy_diagnostics"]
log.setLevel(rootpy.log.INFO)

parser = ArgumentParser()
parser.add_argument('sample', help='sample to run on qcd or ttjets')
parser.add_argument('--compute-flavor', dest='flav_w', action='store_true', help='compute flavor weight')
parser.add_argument('--debug',  action='store_true', help='debug mode')
args = parser.parse_args()
if args.debug:
   log.setLevel(rootpy.log.DEBUG)

input_files = [i.strip() for i in open('data/inputs/%s.list' % args.sample)]

pt_bins = [15, 40, 60, 90, 150, 400, 600]
eta_bins = [1.2, 2.1]
flavors = ['C', 'B', 'DUSG']
sv_categories = ["NoVertex", "PseudoVertex", "RecoVertex"]
weights = {}
fname_regex = re.compile('[a-zA-Z_0-9\/]*\/?[a-zA-Z_0-9]+_(?P<category>[a-zA-Z]+)_(?P<flavor>[A-Z]+)\.root')

for flavor in flavors:
   weights[flavor] = {}
   for category in sv_categories:
      weights[flavor][category] = Hist2D(pt_bins, eta_bins)

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
      for bin in weights[flavor][category]:
         pt_i, eta_i, _ = bin.xyz
         pt_cut = '%.0f <= jetPt && jetPt < %.0f' % (bin.x.low, bin.x.high)
         if pt_i == 0: #x underflow
            pt_cut = 'jetPt < %.0f' % (bin.x.high)
         elif pt_i > len(pt_bins):
            pt_cut = '%.0f <= jetPt' % (bin.x.low)

         eta_cut = '%.4f <= TMath::Abs(jetEta) && TMath::Abs(jetEta) < %.4f' % (bin.y.low, bin.y.high)
         if eta_i == 0: #y underflow
            eta_cut = 'TMath::Abs(jetEta) <= %.4f' % (bin.y.high)
         elif eta_i > len(eta_bins):
            eta_cut = '%.4f <= TMath::Abs(jetEta)' % (bin.y.low)

         nentries = float(tree.GetEntries('%s && %s' % (pt_cut, eta_cut)))
         bin.value += nentries
         weights[flavor][category].entries += nentries

#compute flavor weight 
if args.flav_w:
   flavs_entries = {}
   for flav in flavors:
      flavs_entries[flav] = sum(weights[flav].values()).GetEffectiveEntries()
   total = sum(flavs_entries.values())
   #compute weight: 1./relative population
   flav_weight = dict((i, total/j) for i, j in flavs_entries.iteritems())
   #normalize weights to max 1.
   max_w = max(*flav_weight.values())
   flav_weight = dict((i, j/max_w) for i, j in flav_weight.iteritems())
   log.info('writing flavor weight json file')
   with open('data/%s_flavor_weights.json' % args.sample, 'w') as out:
      out.write(prettyjson.dumps(flav_weight))

#compute category weight
category_weights = dict((i, {}) for i in weights)
for flav, info in weights.iteritems():
   flavs_entries = sum(info.values()).GetEffectiveEntries()
   for category, histo in info.iteritems():
      category_weights[flav][category] = flavs_entries/histo.GetEffectiveEntries()
with open('data/%s_category_weights.json' % args.sample, 'w') as out:
   out.write(prettyjson.dumps(category_weights))

#compute pt-eta weights
log.info('writing pt-eta weights root file')
with io.root_open('data/%s_pt_eta_weights.root' % args.sample, 'recreate') as outfile:
   for flav, items in weights.iteritems():
      flav_dir = outfile.mkdir(flav)
      for category, histo in items.iteritems():
         #entries = histo.GetEntries()
         for bin in histo:
            bin.value = 1./bin.value if bin.value else 0.
         flav_dir.WriteTObject(histo, category)
