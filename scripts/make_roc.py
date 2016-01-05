#! /bin/env python

'''
makes ROC graphs from the output of the MVA testing step. It can optionally optimize the cut on the discriminator output
between different categories in case the MVA has been trained separately for them
'''

from rootpy.io import root_open
import rootpy.plotting as plt
from argparse import ArgumentParser
from glob import glob
import ROOT
import rootpy
import os
from pdb import set_trace
import sys
log = rootpy.log["/roc.py"]
log.setLevel(rootpy.log.INFO)

parser = ArgumentParser()
parser.add_argument('inputdir')
parser.add_argument('outputdir')
parser.add_argument('--optimize', action='store_true')
parser.add_argument('--quiet', action='store_true')
parser.add_argument('--filter', default='')
parser.add_argument('--tag', default='')

args = parser.parse_args()

if args.quiet:
   log.setLevel(rootpy.log.ERROR)

if not os.path.isdir(args.outputdir):
   os.makedirs(args.outputdir)

infiles = glob('%s/%s*.root' % (args.inputdir, args.filter))
if not infiles:
   log.error("empty input list! -- %s" % args.tag)
   sys.exit(0)

def get_roc(compressed):
   sig_yield, bkg_yield = 0, 0
   for vals in compressed.itervalues():
      sig, bkg = vals[-1]
      sig_yield += sig
      bkg_yield += bkg

   #set_trace()
   points = []
   keep_going = True

   current_sig_yield = sig_yield
   current_bkg_yield = bkg_yield
   iteration = 0
   while keep_going:
      log.debug("roc iteration %d, point %s" % (iteration, points[-1].__repr__() if len(points) else ''))
      iteration += 1
      #find minimal ratio among categories
      effs = []
      for category, info in compressed.iteritems():
         if len(info) > 1:
            val = info[-2]
            effs.append((category, val[0]/val[1]))
         elif len(info) == 1:
            effs.append((category, 1.)) #0, 0 equivalent
         else:
            pass #nothing left, skip

      best = min(effs, key=lambda x: x[1])[0]
      compressed[best].pop(-1)

      sval, bval = 0, 0
      for vals in compressed.itervalues():
         if len(vals):
            sval += vals[-1][0]
            bval += vals[-1][1]
      points.append((sval, bval))

      keep_going = any(len(i) for i in compressed.values())
   
   points = [(i/sig_yield, j/bkg_yield) for i, j in points]
   new_points = [None for i in range(100)]
   for point in points:
      eff, _ = point
      round_eff = round(eff, 2)
      idx = int(round_eff*100)
      if idx > 99: continue
      if new_points[idx] is not None:
         old_eff, _ = new_points[idx]
         if abs(eff - round_eff) > abs(old_eff - round_eff): continue
      new_points[idx] = point
   new_points = [i for i in new_points if i is not None]
   new_points.append((1,1))
   return new_points

def compress(hsig, hbkg, invert=True):
   sig = [i.value for i in hsig]
   bkg = [i.value for i in hbkg]
   if invert:
     sig = sig[::-1]
     bkg = bkg[::-1]
   cumulatives = []
   sum_s, sum_b = 0, 0
   par_s, par_b = 0, 0
   for sbin, bbin in zip(sig, bkg):
      sum_s += sbin
      sum_b += bbin
      par_s += sbin
      par_b += bbin
      if par_s > 0 and par_b > 0:
         cumulatives.append((sum_s, sum_b))
         par_s, par_b= 0, 0
   return cumulatives

def roc(infiles, sig, bkg, optimize):
   sigs = {}
   bkgs = {}
   ROOT.TH1.AddDirectory(False)
   for fname in infiles:
      bname = os.path.basename(fname)
      _, category, flavour = tuple(bname.strip('.root').split('_'))
      if flavour != sig and flavour != bkg: continue
      log.info('reading file %s' % fname)
      with root_open(fname) as tfile:
         tree = tfile.tree
         tree.SetBranchStatus('*', 0)
         tree.SetBranchStatus('BDTG', 1)
         histo = plt.Hist1D(1010,0,1.01)
         for entry in tree:
            histo.Fill(entry.BDTG)
         cat = 'all' if not optimize else category
         if flavour == sig:
            if cat not in sigs:
               sigs[cat] = histo.Clone()
            else:
               sigs[cat] += histo
         else:
            if cat not in bkgs:
               bkgs[cat] = histo.Clone()
            else:
               bkgs[cat] += histo
   
   new_sigs = {}
   compressed = {}
   for cat in sigs:
      compressed[cat] = compress(sigs[cat], bkgs[cat])
   return get_roc(compressed)


tag = args.tag+'_' if args.tag else ''
outfile = '%s/%sROCs.root' % (args.outputdir, tag)
with root_open(outfile, 'recreate') as out:
   c_vs_l = roc(infiles, 'C', 'DUSG', args.optimize)
   cl_roc = plt.Graph(len(c_vs_l))
   for idx, point in enumerate(c_vs_l):
      cl_roc.SetPoint(idx, *point)
   cl_roc.title = 'DUSG vs C ROC'
   cl_roc.name = 'ROC_C_light_Inclusive'
   out.WriteTObject(cl_roc, 'ROC_C_light_Inclusive')
   
   c_vs_b = roc(infiles, 'C', 'B', args.optimize)
   cb_roc = plt.Graph(len(c_vs_l))
   for idx, point in enumerate(c_vs_b):
      cb_roc.SetPoint(idx, *point)
   cb_roc.title = 'DUSG vs C ROC'
   cb_roc.name = 'ROC_C_B_Inclusive'
   out.WriteTObject(cb_roc, 'ROC_C_B_Inclusive')
