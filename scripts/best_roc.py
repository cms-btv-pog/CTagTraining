#! /bin/env python

'''
returns the most efficient ROC out of the ones in the root files provided
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
log = rootpy.log["/best_roc.py"]
log.setLevel(rootpy.log.DEBUG)

parser = ArgumentParser()
parser.add_argument('rocname')
parser.add_argument('inputfiles', nargs='+')

args = parser.parse_args()

def binary_search(xval, graph):
   'get the two closest points in x in a graph'
   m, M = 0, len(graph)-1
   while (M-m)>1:
      idx = (M-m)/2+m
      if graph[idx][0] > xval:
         M = idx
      else:
         m = idx
   return graph[m], graph[M]

def is_better(this, other):
   'returns if "this" roc is better than "other"'
   above, below = 0, 0
   for sig, bkg in this:
      p1, p2 = binary_search(sig, other)
      #interpolate
      slope = (p2[1]-p1[1])/(p2[0]-p1[0])
      offset = p1[1] - slope*p1[0]
      interpolation = slope*sig+offset
      if bkg > interpolation:
         above +=1
      else:
         below +=1
   return below > above

## best_file = None
## best_roc = None
wpoints = [(float('inf'), None) for _ in range(5, 95)]

## worst_file = None
## worst_roc = None

#infiles = ['CvsL_GBC_17Dec/ROCs/bf129208a8_ROCs.root', 'CvsL_GBC_17Dec/ROCs/7aa4de24d8_ROCs.root']#args.inputfiles
for infile in args.inputfiles:
   #log.debug('inspecting %s' % infile)
   tfile = root_open(infile)
   roc = tfile.Get(args.rocname)
   for idx, i in enumerate(range(5, 95)):
      xpoint = i/100.
      val = roc.Eval(xpoint)
      if val < wpoints[idx][0]:
         wpoints[idx] = (val, infile)
   ## if best_roc is None or is_better(roc, best_roc):
   ##    log.debug('new best! %s' % infile)
   ##    best_roc = roc
   ##    best_file = tfile
   ## if worst_roc is None or not is_better(roc, worst_roc):
   ##    worst_roc = roc
   ##    worst_file = tfile

ranks = {}
for _, v in wpoints:
   if v not in ranks:
      ranks[v]=0
   ranks[v]+=1
ranks = ranks.items()
ranks.sort(key=lambda x: x[1], reverse=True)

print "Ranks: "
for i, info in enumerate(ranks):
   print ' -->', i, ')', info[0]
#print ' --> WORST:', worst_file.name
