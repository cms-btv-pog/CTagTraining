'''
Makes control plots to check that the input samples are properly biased with respect to the binnning
'''

from rootpy.io import root_open
import rootpy
from rootpy.plotting import Hist1D
import binning
import os
weight = 'total_weight'
intxt = [
   ('ttj', 'data/flat_trees/ttjets_flat.list'),
   ('qcd', 'data/flat_trees/qcd_flat.list'), 
   ]


plots = {}
for sample in ['qcd', 'ttj']:
   for flav in ['B','C','DUSG']:
      for i in ['unweighted', 'weighted']:
         path = '/'.join([sample, flav, i])
         plots[path] = {}   
         plots[path]['jetPt']  = Hist1D(binning.pt_bins)
         plots[path]['jetEta'] = Hist1D(binning.eta_bins)
         plots[path]['vertexCategory'] = Hist1D(4,0,4)
         plots[path]['vertexLeptonCategory'] = Hist1D(10,0,10)
variables = set(plots[path].keys())

for sample, txt in intxt:
   for infile in open(txt):
      infile = infile.strip()
      print "Processing %s..." % infile
      base = os.path.basename(infile)
      flav = base.split('_')[-1].replace('.root','')
      with root_open(infile) as tfile:
         tree = tfile.tree
         tree.SetBranchStatus('*', 0)
         if  sample == 'qcd':
            tree.SetBranchStatus(weight, 1)
         for variable in variables:
            tree.SetBranchStatus(variable, 1)
         for entry in tree:
            #weighted
            path = '/'.join([sample, flav, 'weighted'])
            w = getattr(entry, weight) if sample == 'qcd' else 1.
            for key, histo in plots[path].iteritems():
               histo.Fill(getattr(entry, key), w)

            #unweighted
            path = '/'.join([sample, flav, 'unweighted'])
            for key, histo in plots[path].iteritems():
               histo.Fill(getattr(entry, key))
      print "   ...done"

with root_open('pre_plots.root', 'w') as out:
   for path, info in plots.iteritems():
      tdir = out.mkdir(path);
      for key, histo in info.iteritems():
         tdir.WriteTObject(histo, key)

