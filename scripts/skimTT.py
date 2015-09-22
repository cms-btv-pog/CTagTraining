import sys
import os
sys.argv.append( '-b-' )
from ROOT import *
from array import array
import time
import math
import multiprocessing


def processNtuple(categoryName, inFileList, inDirName, outDirName, nEvents):
  
  print "Starting to process %i events for %s" %(nEvents, categoryName)
  
  chain = TChain('tree')
  
  for f in inFileList:
    print 'Opening file %s/%s' %(inDirName, f)
    chain.Add('%s/%s' %(inDirName, f))
  
  # output
  outFileName = "%s/%s.root" %(outDirName, categoryName)
  print "Storing to ", outFileName
  outFile = TFile( outFileName, 'recreate' )

  subTree = chain.CloneTree(nEvents)
  subTree.AutoSave()
  
  outFile.Write()
  outFile.Close()

  return


def main():

  ROOT.gROOT.SetBatch(True)
  parallelProcesses = multiprocessing.cpu_count()
  
  inDirName = '/scratch/clange/CSV_AK5_JT5/TT_bias_flat/'
  outDirName = '/scratch/clange/CSV_AK5_JT5/TT_bias_flat_skim/'
  if not os.path.exists(outDirName):
    print "Creating new output directory: ", outDirName
    os.makedirs(outDirName)
  sampleFraction = 0.10
  
  categoryDictMax = {}
  categoryDictMin = {}
  categoryInFileList = {}
  
  for inFileName in os.listdir(inDirName):
    if inFileName.endswith(".root") and not (inFileName.find("Eta") >= 0):
      category = inFileName.rsplit("_",1)[0]
      eventRange = inFileName.replace(".root","").rsplit("_",1)[1]
      if category not in categoryDictMax.keys():
        categoryDictMin[category] = int(eventRange.split("-")[0])
        categoryDictMax[category] = int(eventRange.split("-")[1])
        categoryInFileList[category] = []
      else:
        thisMin = int(eventRange.split("-")[0])
        thisMax = int(eventRange.split("-")[1])
        if (thisMin < categoryDictMin[category]):
          categoryDictMin[category] = thisMin
        if (thisMax > categoryDictMax[category]):
          categoryDictMax[category] = thisMax
      categoryInFileList[category].append(inFileName)

  print categoryDictMax
  print categoryDictMin
  for category in categoryDictMax.keys():
    categoryDictMax[category] = int(sampleFraction*(categoryDictMax[category]-categoryDictMin[category]))

  print categoryDictMax

  # create Pool
  p = multiprocessing.Pool(parallelProcesses)
  print "Using %i parallel processes" %parallelProcesses

  for category in categoryInFileList.keys():
    
    # debug
    # processNtuple(category, categoryInFileList[category], inDirName, outDirName, categoryDictMax[category])
    # break
    # run jobs
    p.apply_async(processNtuple, args = (category, categoryInFileList[category], inDirName, outDirName, categoryDictMax[category],))

  p.close()
  p.join()

  print "done"  


if __name__ == "__main__":
  main()
