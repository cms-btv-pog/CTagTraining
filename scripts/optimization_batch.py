#! /bin/env python

'''
creates a batch task configuration that submits multiple training configurations, configure by modifying options_to_scan variable 
'''

import os
import itertools
from argparse import ArgumentParser
from pdb import set_trace
import hashlib
import localsettings as site

parser = ArgumentParser()
parser.add_argument('batchdir', help='where to dump batch jobs info')
args = parser.parse_args()

if not os.path.isdir(args.batchdir):
   os.makedirs(args.batchdir)

options_to_scan = [
  ('pickEvery',[10]),
  ('testEvery',[1]),
  ('ntrees',[250, 500, 1000]),
  ('relativeSplit',[0.006]),
  ('maxDepth',[-1, 5, 8, 15, 25]),
  ('algo',['GBC']),
  ('learningRate',[0.05, 0.1]),
  ('bkg',['B']),
##   ('pickEvery',[10]),
##   ('testEvery',[10]),
##   ('ntrees',[500]),
##   ('relativeSplit',[0.006]),
##   ('maxDepth',[15]),
##   ('algo',['GBC']),
##   ('learningRate',[0.05]),
##   ('category', ['*NoVertexNoSoftLepton*','*NoVertexSoftElectron*','*NoVertexSoftMuon*','*PseudoVertexNoSoftLepton*','*PseudoVertexSoftElectron*','*PseudoVertexSoftMuon*','*RecoVertexNoSoftLepton*','*RecoVertexSoftElectron*','*RecoVertexSoftMuon*']),
#   ('',),
#   ('',),
]

scripts_dir = os.path.join(os.environ['CTRAIN'], 'scripts')
batch_template = '''#! /bin/env bash

WORKINGDIR=$PWD
cd %s
echo 'sourcing anaconda'
source anaconda.sh
cd $WORKINGDIR
export XDG_CONFIG_HOME=$WORKINGDIR/.config
export XDG_CACHE_HOME=$WORKINGDIR/.cache

PA=$@
#PA=${PA#* }

pwd
ls -lht

echo "CLI Args"
echo $PA

echo "python"
echo `which python`

$CTRAIN/scripts/sklearn_training_trees.py $PA 

exitcode=$? 
echo "exit code: "$exitcode
exit $exitcode 

''' % scripts_dir
with open(os.path.join(args.batchdir, 'jobscript.sh'), 'w') as out:
   out.write(batch_template)

#
# batch submission template
#
condor_header = site.batch_header.format(BASHSCRIPT='jobscript.sh')
condor_job = site.batch_job

hashes = set()
with open(os.path.join(args.batchdir, 'condor.jdl'), 'w') as out: 
   out.write(condor_header)
   optnames = [i for i, _ in options_to_scan]
   scan_points = [i for _, i in options_to_scan]
   #set_trace()
   for idx, optset in enumerate(itertools.product(*scan_points)):
      opts = ' '.join(['--%s=%s' % i for i in zip(optnames, optset)])
      opts += ' --batch'
      hasher = hashlib.md5(opts)
      hh = hasher.hexdigest()[:10]
      if hh in hashes:
         raise RuntimeError()
      else:
         hashes.add(hh)
      opts = ' '.join([hh, opts])
      out.write(
         condor_job.format(jobidx=hh, cliArgs=opts)
         )

print "Created %d testing points" % (idx+1)
