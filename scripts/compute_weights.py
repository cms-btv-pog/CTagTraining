#! /bin/env python

from argparse import ArgumentParser
import rootpy.io as io
from rootpy.plotting import Hist2D
import prettyjson
import glob
import re
import rootpy
from pdb import set_trace
import copy
import binning 
import ROOT
log = rootpy.log["/compute_weights"]
log.setLevel(rootpy.log.INFO)

qcd_yields = prettyjson.loads(open('data/qcd_yields.json'   ).read())
ttj_yields = prettyjson.loads(open('data/ttjets_yields.json').read())

biased_qcd = copy.deepcopy(qcd_yields)

cat_weight = copy.deepcopy(qcd_yields)
bin_weight = copy.deepcopy(qcd_yields)

flavours = qcd_yields.keys()
categories = qcd_yields[flavours[0]].keys()
bins = qcd_yields[flavours[0]][categories[0]].keys()

total_yield = sum( k for i in qcd_yields.itervalues() for j in i.itervalues() for k in j.itervalues() ) #sum( k for k in j.itervalues() for j in i.itervalues() for i in qcd_yields.itervalues() )


flav_weights = {}
for flavour in flavours:
   qcd_flav = sum( k for j in qcd_yields[flavour].itervalues() for k in j.itervalues() )
   ttj_flav = sum( k for j in ttj_yields[flavour].itervalues() for k in j.itervalues() )
   flav_weights[flavour] = ttj_flav/qcd_flav

def ratios_are_ok(one, two):
   slim1 = [i for i in one if i]
   slim2 = [i for i in two if i]
   if not slim1 and not slim2: return True
   elif len(slim1) != len(slim2): return False
   r1 = [i/slim1[0] for i in slim1]
   r2 = [i/slim2[0] for i in slim2]
   for i, j in zip(r1, r2):
      if abs(i-j)/i > 10**-6: return False
   return True

for flavour in flavours:
   log.info('inspecting flavour: %s' % flavour)
   for bin in bins:
      cat_weights = []
      qcds = []
      ttjs = []
      bin_yield  = 0
      corr_yield = 0
      for category in categories:
         qcd = qcd_yields[flavour][category][bin]
         ttj = ttj_yields[flavour][category][bin]
         if qcd == 0 and ttj != 0: 
            log.warning('Category %s, bin %s cannot be reweitghted properly'
                        ' given that qcd has no events and tt does' % (category, bin))
         weight = ttj/qcd if qcd else 0.
         bin_yield += qcd
         corr_yield += qcd*weight
         cat_weights.append(weight)
         qcds.append(qcd)
         ttjs.append(ttj)

      #Make weights such that they do NOT alter the total number of events in the bin
      if corr_yield == 0 and bin_yield != 0: 
         log.warning(
            'Bin %s cannot be reweitghted properly '
            'given that qcd has no events and tt does' % bin)
      factor = bin_yield/corr_yield if corr_yield else 0
      corr_qcds = [i*j*factor for i, j in zip(qcds, cat_weights)]
      assert(corr_yield == 0 or abs(sum(corr_qcds) - sum(qcds)) < 10**-6)
      for cat, weight in zip(categories, cat_weights):
         cat_weight[flavour][cat][bin]  = weight*factor
         biased_qcd[flavour][cat][bin] *= weight*factor
      bias_qcds = [biased_qcd[flavour][i][bin] for i in categories]
      assert(ratios_are_ok(bias_qcds, ttjs))

total_biased_yield = sum( k for i in biased_qcd.itervalues() for j in i.itervalues() for k in j.itervalues() )
final_qcd  = copy.deepcopy(biased_qcd)
assert(abs(total_biased_yield - total_yield)/total_biased_yield < 10**-4) #allow minimal variations due to empty tt categories

##FLAV WEIGHTS
for flavour in flavours:
   flav_yield = sum( k for j in qcd_yields[flavour].itervalues() for k in j.itervalues() )
   corr_yield = 0
   for bin in bins:
      bin_yield = sum(biased_qcd[flavour][i][bin] for i in categories)
      for category in categories:
         bin_weight[flavour][category][bin] = 1./bin_yield if bin_yield else 0
         final_qcd[flavour][category][bin] *= 1./bin_yield if bin_yield else 0
         corr_yield += final_qcd[flavour][category][bin]
   
   factor = flav_yield/corr_yield
   for bin in bins:
      for category in categories:
         bin_weight[flavour][category][bin] *= factor
         final_qcd[flavour][category][bin]  *= factor

total_final_yield = sum( k for i in final_qcd.itervalues() for j in i.itervalues() for k in j.itervalues() )
log.info( "yields: %.1f --> %.1f --> %.1f" % (total_yield, total_biased_yield, total_final_yield))

#debugging helpers
def bin_yields(yields):
   ret = []
   for bin in bins:
      ret.append(
         sum(yields[i][bin] for i in categories)
         )
   return ret

def cat_yields(yields):
   ret = []
   for cat in categories:
      ret.append(
         sum(yields[cat][i] for i in bins)
         )
   return ret

def is_flat(distro):
   new = [i for i in distro if i] #zero suppress
   if len(new) == 1: return True
   val = new[0]
   for i in new[1:]:
      if abs(val - i)/val > 10**-6: return False
   return True

## many, many checks!
for flavour in flavours:
   assert(is_flat(bin_yields(final_qcd[flavour])))
   for bin in bins:
      bias_qcds = [final_qcd[flavour][i][bin] for i in categories]
      ttjs = [ttj_yields[flavour][i][bin] for i in categories]
      assert(ratios_are_ok(bias_qcds, ttjs))

##
##  STORE IN H2D and jsons
##

with open('data/qcd_bin_weights.json', 'w') as out:
   out.write(
      prettyjson.dumps(bin_weight)
      )   

with io.root_open('data/qcd_weights.root', 'w') as out:
   fweights = ROOT.TObjString(prettyjson.dumps(flav_weights))
   out.WriteTObject(fweights, 'flavour_weights')
   for flavour in flavours:
      fdir = out.mkdir(flavour)
      for category in categories:
         cdir = fdir.mkdir(category)
         h2d_category = Hist2D(binning.pt_bins, binning.eta_bins) #category bias weights
         h2d_bin      = Hist2D(binning.pt_bins, binning.eta_bins) #pt/eta bin weights        
         for cat_bin, bin_bin in zip(h2d_category, h2d_bin):
            cat_cut = binning.cut_from_bin(cat_bin)
            bin_cut = binning.cut_from_bin(bin_bin)
            assert(cat_cut == bin_cut)
            cat_bin.value = cat_weight[flavour][category][cat_cut]
            bin_bin.value = bin_weight[flavour][category][cat_cut]
         cdir.WriteTObject(h2d_category, 'bias')
         cdir.WriteTObject(h2d_bin     , 'kin' )
         
         
