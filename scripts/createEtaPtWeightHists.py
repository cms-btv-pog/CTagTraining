import sys
sys.argv.append( '-b-' )
import os
import shutil
from ROOT import *
from array import array
import time
import multiprocessing
import thread
import subprocess


def processNtuple(inFileName, inDirName, outDirName,category):
  
  print "Starting to process %s" %inFileName
  # retrieve the ntuple of interest
  inFile = TFile( "%s/%s" %(inDirName, inFileName) )
  inTreeName = "tree"
  #inTreeName = category
  mychain = gDirectory.Get( inTreeName )
  
  # output
  outFileName = "%s/%s_EtaPtWeightHisto.root" %(outDirName, inFileName.rsplit(".",1)[0])
  print "Writing to %s" %outFileName
  outFile = TFile( outFileName, 'recreate' )

  histo = TH2D("jets", "jets", 50, -2.5, 2.5, 40, 4.17438727, 6.95654544315); # pt starting from 15 and until 1000
  #mychain.Draw("log(jetPt+50):jetEta >> +jets", "", "Lego goff");
  mychain.Draw("log(jetPt+50):jetEta >> +jets", "weight_norm*weight_category", "Lego goff");   #after adding normalization and category weight branches
  bins = range(0,1020,20);
  #bins[1] = 15;
  nbins = len(bins) -1;
  histo_lin = TH2D("jets_lin", "jets_lin", 50, -2.5, 2.5, 50,0,1000); # pt starting from 15 and until 1000  , default nbins was 40
  #mychain.Draw("jetPt:jetEta >> +jets_lin", "","Lego goff")
  mychain.Draw("jetPt:jetEta >> +jets_lin", "weight_norm*weight_category", "Lego goff")  # after adding normalization and category weight branches

  outFile.cd()
  histo.Write()
  histo_lin.Write()
  outFile.Close()
  inFile.Close()

def combineHist(inDirName,flavour):
  weightHistName = "jets_lin"
  print "Accessing file %s/skimmed_20k_eachptetabin_CombinedSVRecoVertex_%s_EtaPtWeightHisto.root"%(inDirName,flavour)
  RecoFileName = "%s/skimmed_20k_eachptetabin_CombinedSVRecoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  PseudoFileName = "%s/skimmed_20k_eachptetabin_CombinedSVPseudoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  NoVtxFileName = "%s/skimmed_20k_eachptetabin_CombinedSVNoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  #RecoFileName = "%s/CombinedSVRecoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  #PseudoFileName = "%s/CombinedSVPseudoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  #NoVtxFileName = "%s/CombinedSVNoVertex_%s_EtaPtWeightHisto.root" %(inDirName, flavour) 
  RecoFile = TFile( "%s" %( RecoFileName) )
  PseudoFile = TFile( "%s" %( PseudoFileName) )
  NoVtxFile = TFile( "%s" %( NoVtxFileName) )
  
  RecoHist = RecoFile.Get(weightHistName)
  PseudoHist = PseudoFile.Get(weightHistName)
  NoVtxHist = NoVtxFile.Get(weightHistName)
  #print RecoHist.ClassName()
  RecoHist.Add(PseudoHist)
  RecoHist.Add(NoVtxHist)
  
  HistoutFileName = "%s/skimmed_20k_eachptetabin_CombinedSVInclusive_%s_EtaPtWeightHisto.root" %(inDirName, flavour)
  print "Writing Combined Histograms to %s"%HistoutFileName
  HistoutFile = TFile( HistoutFileName, 'recreate' )
  HistoutFile.cd()
  RecoHist.Write()
  HistoutFile.Close()


def main():

  ROOT.gROOT.SetBatch(True)
  parallelProcesses = multiprocessing.cpu_count()
  # create Pool
  p = multiprocessing.Pool(parallelProcesses)
  print "Using %i parallel processes" %parallelProcesses
  
  outDirName = '/user/smoortga/CTag/TMVActag_v1/EtaPtWeightHistos_SL_7_5_1/QCD'     # for individual category histograms
  combDirName = '/user/smoortga/CTag/TMVActag_v1/EtaPtWeightHistos_SL_7_5_1/QCD'    # for combined histograms
  inDirName = "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithWeights_NonPtEtaFlat/QCD"
  
  flavourCategoryDict = {}

  for inFileName in os.listdir(inDirName):
    if inFileName.endswith(".root"):
      # processNtuple(inFileName, inDirName, outDirName)
      # break
      category = inFileName.replace("skimmed_20k_eachptetabin_", "").split("_",1)[0]
      flavour = inFileName.replace("skimmed_20k_eachptetabin_", "").split("_",2)[1]
      flavour = flavour.replace(".root","")
      key = "%s_%s" %(category, flavour)
      print key
      if key not in flavourCategoryDict:
        flavourCategoryDict[key] = []
      flavourCategoryDict[key].append(inFileName.replace(".root", "_EtaPtWeightHisto.root"))
      p.apply_async(processNtuple, args = (inFileName, inDirName, outDirName, category))

  p.close()
  p.join()

  # loop over all output files of one category and flavour and hadd them
  outDirName = os.path.join(os.path.abspath(sys.path[0]), outDirName) # absolute path to be safe

  
  for key in flavourCategoryDict.keys():
    #hadd only of there's something to hadd
    if (len(flavourCategoryDict[key]) > 1):
      print "hadding key files"
      haddList = ""
      for fileName in flavourCategoryDict[key]:
        haddList += "%s " %fileName
      haddCommand = "pwd && hadd -f %s_EtaPtWeightHisto.root %s" %(key, haddList)
      if (haddList.find("skimmed_20k_eachptetabin_") >= 0):
        haddCommand = "pwd && hadd -f skimmed_20k_eachptetabin_%s_EtaPtWeightHisto.root %s" %(key, haddList)
      # print haddCommand
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
      for fileName in flavourCategoryDict[key]:
        print "deleting %s/%s"%(outDirName, fileName)
        os.remove("%s/%s"%(outDirName, fileName))
    else: # if nothing to hadd just move file
      if (flavourCategoryDict[key][0].find("skimmed_20k_eachptetabin_") >= 0):
        print "moving %s/%s to %s/%s_EtaPtWeightHisto.root" %(outDirName, flavourCategoryDict[key][0], outDirName, key)
	#shutil.copy2("%s/%s" %(outDirName, flavourCategoryDict[key][0]), "%s/skimmed_20k_eachptetabin_%s_EtaPtWeightHisto.root"%(outDirName, key))
        os.rename("%s/%s" %(outDirName, flavourCategoryDict[key][0]), "%s/skimmed_20k_eachptetabin_%s_EtaPtWeightHisto.root"%(outDirName, key))
      else:
        print "moving %s/%s to %s/%s_EtaPtWeightHisto.root" %(outDirName, flavourCategoryDict[key][0], outDirName, key)
        os.rename("%s/%s" %(outDirName, flavourCategoryDict[key][0]), "%s/%s_EtaPtWeightHisto.root"%(outDirName, key))

  print  "Combining files"     
  # Combine vertex categories for histograms
  flavours = ["C","B","DUSG"]
  for flav in flavours:
    combineHist(combDirName, flav)  


if __name__ == "__main__":
  main()
