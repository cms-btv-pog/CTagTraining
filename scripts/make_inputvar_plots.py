'''
make distribution plots of relevant input variables
'''

from rootpy.io import root_open
import rootpy
from rootpy.plotting import Hist1D, Profile1D
import os
from pdb import set_trace
from argparse import ArgumentParser
import multiprocessing
import uuid

parser = ArgumentParser()
parser.add_argument('input',  help='input txt with files (non-flat trees)')
parser.add_argument('out', help='output root file')
parser.add_argument('--pickEvery', type=int, default=1, help='output root file')
args = parser.parse_args()

inputs = args.input
dirpath = os.path.dirname(args.out)
if dirpath and not os.path.isdir(dirpath):
   os.makedirs(dirpath)

def process_file(infile, outfile, pick_every):
   with root_open(outfile, 'w') as outtfile:
      flavdirs = {}
      name = infile #name.strip()
      print 'analyzing %s' % name
      base = os.path.basename(name).replace('.root','')
      split = base.split('_')
      category = split[-2]
      flavour  = split[-1]
      with root_open(name) as tfile:
         tree = tfile.Get(category)
         tree.SetBranchStatus('*', 0)
         tree.SetBranchStatus('jetPtD', 1)
         tree.SetBranchStatus('relConcentricEnergyAroundJetAxis', 1)

         njets = 0.
         mean = []
         hists = {}
         #rings
         for i in range(8):
            hists['ring%d' % i] = Hist1D(101, 0, 1.01, title='Energy deposit ring %d' % i)
            mean.append(0)
         
         for i in range(1,7):
            hists['ring_sum_%d' % i] = Hist1D(101, 0, 1.01, title='Energy deposit ring [0,%d]' % i)
            
         hists['ring_profile'] = Profile1D(8, 0, 8, title='Energy deposits in rigs')
         hists['ptD'] = Hist1D(101, 0, 1.01, title='p_{TD}')
         if 'RecoVertex' in category:
            hists['svmass'] = Hist1D(100, 0, 20, title='M(SV)')
            hists['svmass_corrected'] = Hist1D(100, 0, 20, title='M_{corr}(SV)')
            tree.SetBranchStatus('vertexMass', 1)
            tree.SetBranchStatus('correctedSVMass', 1)
         if 'NoSoftLepton' not in category:
            hists['ratiolpt'] = Hist1D(101, 0, 1.01)
            tree.SetBranchStatus('leptonRatio', 1)

         for idx, entry in enumerate(tree):
            if idx % pick_every: continue
            #if idx % 10000 == 0: print 'processing entry %i' % idx
            #if 'NoSoftLepton' not in category and 0.6 <= entry.leptonRatio[0] < 0.9: continue
            njets+=1.
            hists['ptD'].fill(entry.jetPtD[0])
            for i in range(8):
               mean[i]+=entry.relConcentricEnergyAroundJetAxis[i]
               hists['ring%d' % i].fill(entry.relConcentricEnergyAroundJetAxis[i])
               hists['ring_profile'].Fill(i, entry.relConcentricEnergyAroundJetAxis[i])
            for i in range(1,7):
               hists['ring_sum_%d' % i].fill(sum(entry.relConcentricEnergyAroundJetAxis[:i+1]))
            if 'RecoVertex' in category:
               hists['svmass'].fill(entry.vertexMass[0])
               hists['svmass_corrected'].fill(entry.correctedSVMass[0])
            if 'NoSoftLepton' not in category:
               hists['ratiolpt'].fill(entry.leptonRatio[0])
         flavdir = flavdirs[flavour] if flavour in flavdirs else outtfile.mkdir(flavour)
         flavdirs[flavour] = flavdir
         outdir = flavdir.mkdir(category)
         for name, hist in hists.iteritems():
            outdir.WriteTObject(hist, name)


infiles = [i.strip() for i in open(args.input)]
partials = ['%s.root' % str(uuid.uuid1()) for _ in infiles]
parallelProcesses = multiprocessing.cpu_count()/2
pool = multiprocessing.Pool(parallelProcesses)
for infile, outfile in zip(infiles, partials):
   pool.apply_async(
      process_file, 
      args=(infile, outfile, args.pickEvery)
      )
pool.close()
pool.join()
print "processing done"
os.system('hadd -O -f %s %s' % (args.out, ' '.join(partials)))
os.system('rm %s' % ' '.join(partials))

