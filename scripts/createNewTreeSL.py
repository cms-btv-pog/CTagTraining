import sys
import os
sys.argv.append( '-b-' )
from ROOT import *
from array import array
import time
import math
import multiprocessing
import thread
import subprocess


def processNtuple(inFileName, outDirName, startEntry, endEntry, variables):
  
  print "Starting to process events %i to %i" %(startEntry, endEntry)
  # retrieve the ntuple of interest
  inFile = TFile( inFileName )
  inTreeName = inFileName.rsplit("/",1)[1].replace("skimmed_", "").split("_",1)[0]
  mychain = gDirectory.Get( inTreeName )
  branchList = mychain.GetListOfBranches()
  
  # output
  outFileName = "%s/%s_%i-%i.root" %(outDirName, inFileName.rsplit("/",1)[1].rsplit(".",1)[0], startEntry, endEntry)
  print outFileName
  outFile = TFile( outFileName, 'recreate' )
  outTree = TTree( 'tree', 'c-tagging training tree with SL information' )


  # loop over variable sets and create new branches
  outVariables = {}
  for varSet in variables:
    if (len(varSet) == 3):
        #print "%s: %f" %(varSet[0], float(getattr(mychain, varSet[0])))
        outVariables[varSet[0]] = array( varSet[1], [ 0 ] )
        outTree.Branch( varSet[0], outVariables[varSet[0]], '%s/%s'%(varSet[0], varSet[1].upper()) )
        # print outVariables[varSet[0]]
    elif (len(varSet) == 4):
      for vecIndex in range(varSet[3]):
        #print "%s[%i]: %f" %(varSet[0], vecIndex, float(varVector[vecIndex]))
        varName = "%s_%i"%(varSet[0],vecIndex)
        outVariables[varName] = array( varSet[1], [ 0 ] )
        # print outVariables[varName]
        outTree.Branch( varName, outVariables[varName], '%s/%s'%(varName, varSet[1].upper()) )


  ### actual loop ###
  print "%s: Starting event loop" %(multiprocessing.current_process().name)
  startTime = time.time()
  for jentry in xrange(startEntry, endEntry):
  # get the next tree in the chain and verify
    ientry = mychain.LoadTree( jentry )
    if ientry < 0:
      print "%s: Problem loading tree for event: %i" %(multiprocessing.current_process().name, ientry)
      break

    # timing
    if (ientry%10000==0):
      if (ientry != startEntry):
        print "%s: Progress: %3.1f%%" %(multiprocessing.current_process().name, float(ientry-startEntry)/(endEntry-startEntry)*100)
        endTime = time.time()
        deltaTime = endTime - startTime
        rate = 10000./deltaTime
        print "%s: current rate: %5.2f Hz" %(multiprocessing.current_process().name, rate)
        startTime = time.time()

   # copy next entry into memory and verify
    nb = mychain.GetEntry( jentry )
    if nb <= 0:
      print "%s: Problem getting entry %i" %(multiprocessing.current_process().name, jentry)
      continue

    # loop over variables
    # use the values directly from the tree
    for varSet in variables:
      # non-vector variable
      if (len(varSet) == 3):
        if varSet[0] not in branchList:
          # assign default value
          outVariables[varSet[0]][0] = varSet[2]
        elif (varSet[1] == "f"):
          #print "%s: %f" %(varSet[0], float(getattr(mychain, varSet[0])))
          outVariables[varSet[0]][0] = float(getattr(mychain, varSet[0]))
          # print outVariables[varSet[0]]
        elif (varSet[1] == "i"):
          # print "%s: %i" %(varSet[0], int(getattr(mychain, varSet[0])))
          outVariables[varSet[0]][0] = int(getattr(mychain, varSet[0]))
          # print outVariables[varSet[0]]
        else:
          print "ERROR: %s type not known for variables %s" %(varSet[1], varSet[0])
      # vector variable to be decomposed
      elif (len(varSet) == 4):
        if varSet[0] not in branchList:
          for vecIndex in range(varSet[3]):
            varName = "%s_%i"%(varSet[0],vecIndex)
            outVariables[varName][0] = varSet[2]
        else:
           varVector = getattr(mychain, varSet[0])
           for vecIndex in range(varSet[3]):
            # print "%s[%i]: %f" %(varSet[0], vecIndex, float(varVector[vecIndex]))
            varName = "%s_%i"%(varSet[0],vecIndex)
            var_value = varVector[vecIndex] if len(varVector) > vecIndex else varSet[2]
            if (varSet[1] == "f"):
              outVariables[varName][0] = float(var_value)
            elif (varSet[1] == "i"):
              outVariables[varName][0] = int(var_value)
            elif (varSet[1] == "l"):
              outVariables[varName][0] = long(var_value)
            else:
              print "ERROR: %s type not known for variables %s" %(varSet[1], varSet[0])
            if (math.isnan(outVariables[varName][0])):
              outVariables[varName][0] = varSet[2]
    outTree.Fill()
  
  outFile.Write()
  outFile.Close()
  inFile.Close()
  print "%s: Total time: %5.2f s" %(multiprocessing.current_process().name, time.clock())



def main():

  ROOT.gROOT.SetBatch(True)
  parallelProcesses = multiprocessing.cpu_count()
  
  outDirName = '/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1/TTbar/'
  #outMergedDirName = '/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL/MergedQCD/'
  if not os.path.exists(outDirName):
    print "Creating new output directory: ", outDirName
    os.makedirs(outDirName)
  eventsPerJob = 250000
  
  # QCD sample
  #inFileList = [
  # NoVertex
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexNoSoftLepton_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexNoSoftLepton_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexNoSoftLepton_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftElectron_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftElectron_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftElectron_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftMuon_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftMuon_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVNoVertexSoftMuon_DUSG.root',
  # PseudoVertex
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexNoSoftLepton_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexNoSoftLepton_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexNoSoftLepton_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftElectron_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftElectron_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftElectron_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftMuon_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftMuon_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVPseudoVertexSoftMuon_DUSG.root',
 # RecoVertex
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexNoSoftLepton_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexNoSoftLepton_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexNoSoftLepton_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftElectron_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftElectron_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftElectron_DUSG.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftMuon_B.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftMuon_C.root',
    #'/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/QCD_training/skimmed_20k_eachptetabin_CombinedSVRecoVertexSoftMuon_DUSG.root']

  
  
  # TTbar sample
  inFileList = [
  # NoVertex
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexNoSoftLepton_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexNoSoftLepton_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexNoSoftLepton_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftElectron_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftElectron_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftElectron_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftMuon_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftMuon_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVNoVertexSoftMuon_DUSG.root',
  # PseudoVertex
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexNoSoftLepton_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexNoSoftLepton_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexNoSoftLepton_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftElectron_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftElectron_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftElectron_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftMuon_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftMuon_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVPseudoVertexSoftMuon_DUSG.root',
 # RecoVertex
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexNoSoftLepton_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexNoSoftLepton_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexNoSoftLepton_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftElectron_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftElectron_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftElectron_DUSG.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftMuon_B.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftMuon_C.root',
    '/user/smoortga/CTag/TMVActag_v1/Non_Flat_TrainingTrees/CMSSW_7_5_1/TTJets/skimmed_CombinedSVRecoVertexSoftMuon_DUSG.root']
               
                


                
  variables = [ 
  # define as ["variable name", "variable type (f/i)", default value, in case of vector: max. length]
                ["flavour", "f", -1],
                ["jetPt", "f", -1],
                ["trackJetPt", "f", -1],
                ["jetEta", "f", -3],
                ["vertexCategory", "f", -1],
		["vertexLeptonCategory", "f", -1],
          			["trackSip2dSig", "f", -10, 3], # centered around 0
          			["trackSip3dSig", "f", -10, 3], # centered around 0
          			["trackSip2dVal", "f", -0.1, 3], # centered around 0
          			["trackSip3dVal", "f", -0.1, 3], # centered around 0
          			["trackPtRel", "f", -1, 3], # exponentially falling from 0 to ~450
          			["trackPPar", "f", -1, 3], # exponentially falling from 0 to ~10000
          			["trackEtaRel", "f", -1, 3], # distribution from 1 to 10
          			["trackDeltaR", "f", -0.1, 3], # distribution from 0 to 0.3
          			["trackPtRatio", "f", -0.1, 3], # distribution from 0 to 0.3
          			["trackPParRatio", "f", 1.1, 3], # from 0.95 increasing exponentially to peak at 1
          			["trackJetDist", "f", -0.1, 3], # exponentially rising distribution from -0.07 to peak at 0
          			["trackDecayLenVal", "f", -0.1, 3], # exponentially falling from 0 to ~5
          			["vertexMass", "f", -0.1, 1], # exponentially falling from 0 to ~450
          			["vertexNTracks", "f", 0, 1], # at least two tracks make a vertex
          			["vertexEnergyRatio", "f", -0.1, 1], # positive values, larger than zero (can get large, but mostly < 2)
          			["trackSip2dSigAboveCharm", "f", -999, 1], # peaks at zero
          			["trackSip3dSigAboveCharm", "f", -999, 1], # peaks at zero
          			["flightDistance2dSig", "f", -1, 1], # exponentially falling from 0 up to ~200
          			["flightDistance3dSig", "f", -1, 1], # exponentially falling from 0 up to ~300
          			["flightDistance2dVal", "f", -0.1, 1], # exponentially falling from 0 up to ~2.5
          			["flightDistance3dVal", "f", -0.1, 1], # exponentially falling from 0 up to ~14
          			["trackSumJetEtRatio", "f", -0.1], # 0 to ~8
          			["jetNSecondaryVertices", "f", 0],
          			["vertexJetDeltaR", "f", -0.1, 1], # 0 to 0.5
          			["trackSumJetDeltaR", "f", -0.1], # exponentially falling from 0 up to ~3
          			["jetNTracks", "f", -0.1], # from 0 to 1
          			["trackSip2dValAboveCharm", "f", -0.1, 1], # default -0.1 in case not reached
          			["trackSip3dValAboveCharm", "f", -0.1, 1], # default -0.1 in case not reached
          			["vertexFitProb", "f", -1, 1], # largely from 0 to ~10, but some outliers
          			["chargedHadronEnergyFraction", "f", -0.1], # 0 to 1
          			["neutralHadronEnergyFraction", "f", -0.1], # 0 to 1
          			["photonEnergyFraction", "f", -0.1], # 0 to 1
          			["electronEnergyFraction", "f", -0.1], # 0 to 1
          			["muonEnergyFraction", "f", -0.1], # 0 to 1
          			["chargedHadronMultiplicity", "f", -1],
          			["neutralHadronMultiplicity", "f", -1],
          			["photonMultiplicity", "f", -1],
          			["electronMultiplicity", "f", -1],
          			["muonMultiplicity", "f", -1],
          			["hadronMultiplicity", "f", -1],
          			["hadronPhotonMultiplicity", "f", -1],
          			["totalMultiplicity", "f", -1],
          			["massVertexEnergyFraction", "f", -0.1, 1], # distribution from 0 to ~5 with peak at 0
          			["vertexBoostOverSqrtJetPt", "f", -0.05, 1], # distribution from 0 to 1 with peak at 0
				["leptonPtRel", "f", -1, 3],
				["leptonSip3d", "f", -1000, 3], # has very long tails, so default at very low value
				["leptonDeltaR", "f", -0.1, 3],
				["leptonRatioRel", "f", -0.05, 3],
				["leptonEtaRel", "f", -0.1, 3],
				["leptonRatio", "f", -0.1, 3],
               ]
                
  for inFileName in inFileList:

    #inFileName = '/scratch/clange/CSV_AK5_JT5/QCD_training/CombinedSVV2RecoVertex_B.root'

    # retrieve the ntuple of interest to determine number of events
    inFile = TFile( inFileName )
    # inTreeName = inFileName.rsplit("/",1)[1].replace("skimmed_20k_eachptetabin_", "").split("_",1)[0]
    inTreeName = inFileName.rsplit("/",1)[1].replace("skimmed_", "").split("_",1)[0]
    print "Using tree with name: ", inTreeName 
    mychain = gDirectory.Get( inTreeName )
    branchList = mychain.GetListOfBranches()
    entries = mychain.GetEntriesFast()
    inFile.Close()
  
    # create Pool
    p = multiprocessing.Pool(parallelProcesses)
    print "Using %i parallel processes" %parallelProcesses
  
    # create jobs based on number of events
    eventsList = []
    startEvent = 0
    while (startEvent < entries):
      eventsList.append(startEvent)
      startEvent += eventsPerJob
    eventsList.append(entries+1)
    print "%i jobs to run" %(len(eventsList)-1)

    # debug
    # processNtuple(inFileName, outDirName, eventsList[0], eventsList[1]-1, variables)
    # run jobs
    for i in range(len(eventsList)-1):
      p.apply_async(processNtuple, args = (inFileName, outDirName, eventsList[i], eventsList[i+1]-1, variables,))
    p.close()
    p.join()
  
  
  # loop over all output files of one category and flavour and hadd them : hadd -f skimmed_20k_eachptetabin_CombinedSVNoVertex_B.root skimmed_20k_eachptetabin_CombinedSVNoVertex*_B_*.root
  finalOutFiles = ['NoVertex_B','NoVertex_C','NoVertex_DUSG','PseudoVertex_B','PseudoVertex_C','PseudoVertex_DUSG','RecoVertex_B','RecoVertex_C','RecoVertex_DUSG']
  outDirName = os.path.join(os.path.abspath(sys.path[0]), outDirName) # absolute path to be safe
  print "hadding key files"
  for fileName in finalOutFiles:
   #for QCD:
   #haddCommand = "pwd && hadd -f skimmed_20k_eachptetabin_CombinedSV%s.root skimmed_20k_eachptetabin_CombinedSV%s*_%s_*.root" %(fileName,fileName.split("_",1)[0],fileName.split("_",1)[1])
   #for TTbar
   haddCommand = "pwd && hadd -f CombinedSV%s.root skimmed_CombinedSV%s*_%s_*.root" %(fileName,fileName.split("_",1)[0],fileName.split("_",1)[1])
   print haddCommand
   lock=thread.allocate_lock()
   lock.acquire()
   haddProcess=subprocess.Popen(haddCommand, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True, cwd=outDirName)
   haddProcess.wait()
   lock.release()
   errors = haddProcess.stderr.read()
   if ( len(errors) > 0):
     print "WARNING, there has been an error!"
     print errors
   print haddProcess.stdout.read()
   # delete split files
   # for fileName in fileList:
   #   print "deleting %s/%s"%(outDirName, fileName)
   #   os.remove("%s/%s"%(outDirName, fileName))
  print "hadding is finished"
  
  
  print "done"  


if __name__ == "__main__":
  main()

#  LocalWords:  inFileList
