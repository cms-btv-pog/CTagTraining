import sys
import os
import ROOT
from array import array
import time
import multiprocessing
import thread
import subprocess
import math

ROOT.gROOT.SetBatch(True)

flavourCutsDict = {}
flavourCutsDict["B"] = "flavour == 5"
flavourCutsDict["C"] = "flavour == 4"
flavourCutsDict["light"] = "flavour !=4 && flavour !=5"
flavourCutsDict["non-C"] = "flavour !=4"
flavourCutsDict["non-B"] = "flavour !=5"

# also add vertexCategory
categoryCutsDict = {}
categoryCutsDict["NoVertex"] = "vertexCategory == 2"
categoryCutsDict["PseudoVertex"] = "vertexCategory == 1"
categoryCutsDict["RecoVertex"] = "vertexCategory == 0"

categories = []
categories.append("NoVertex")
categories.append("PseudoVertex")
categories.append("RecoVertex")
categories.append("Inclusive")

flavours = []
flavours.append("B")
flavours.append("C")
flavours.append("light")
flavours.append("non-C")
flavours.append("non-B")

PtBins = []
PtBins = []
PtBins.append("jetPt > 15")
PtBins.append("15 < jetPt and jetPt <= 40")
PtBins.append("40 < jetPt and jetPt <= 60")
PtBins.append("60 < jetPt and jetPt <= 90")
PtBins.append("90 < jetPt and jetPt <= 150")
PtBins.append("150 < jetPt and jetPt <=400")
PtBins.append("jetPt > 400")
PtBins.append("jetPt > 30")
PtBins.append("jetPt > 150")


etaPtBins = []
etaPtBins.append("15 < jetPt and jetPt <= 40 and abs(jetEta) <= 1.2")
etaPtBins.append("15 < jetPt and jetPt <= 40 and 1.2 < abs(jetEta) and abs(jetEta) <= 2.1")
etaPtBins.append("15 < jetPt and jetPt <= 40 and abs(jetEta) > 2.1")
etaPtBins.append("40 < jetPt and jetPt <= 60 and abs(jetEta) <= 1.2")
etaPtBins.append("40 < jetPt and jetPt <= 60 and 1.2 < abs(jetEta) and abs(jetEta) <= 2.1")
etaPtBins.append("40 < jetPt and jetPt <= 60 and abs(jetEta) > 2.1")
etaPtBins.append("60 < jetPt and jetPt <= 90 and abs(jetEta) <= 1.2")
etaPtBins.append("60 < jetPt and jetPt <= 90 and 1.2 < abs(jetEta) and abs(jetEta) <= 2.1")
etaPtBins.append("60 < jetPt and jetPt <= 90 and abs(jetEta) > 2.1")
etaPtBins.append("90 < jetPt and jetPt <= 150 and abs(jetEta) <= 1.2")
etaPtBins.append("90 < jetPt and jetPt <= 150 and 1.2 < abs(jetEta) and abs(jetEta) <= 2.1")
etaPtBins.append("90 < jetPt and jetPt <= 150 and abs(jetEta) > 2.1")
etaPtBins.append("150 < jetPt and jetPt <= 400 and abs(jetEta) <= 1.2")
etaPtBins.append("150 < jetPt and jetPt <= 400 and 1.2 < abs(jetEta) and abs(jetEta) <= 2.1")
etaPtBins.append("150 < jetPt and jetPt <= 400 and abs(jetEta) > 2.1")
etaPtBins.append("400 < jetPt and jetPt <= 600 and abs(jetEta)<= 1.2")
etaPtBins.append("400 < jetPt and jetPt <= 600 and abs(jetEta) > 1.2")
etaPtBins.append("jetPt > 600 and abs(jetEta) <= 1.2")
etaPtBins.append("jetPt > 600 and abs(jetEta) > 1.2")
  


def processNtuple(inFileName, inDirName, outDirName,):
  
  print "Starting to process %s" %inFileName
  # retrieve the ntuple of interest
  inFile = ROOT.TFile( "%s/%s" %(inDirName, inFileName) )
  inTreeName = "tree"
  mychain = ROOT.gDirectory.Get( inTreeName )
  
  # output
  outFileName = "%s/%s_Histograms.root" %(outDirName, inFileName.rsplit(".",1)[0])
  print "Writing to %s" %outFileName
  outFile = ROOT.TFile( outFileName, 'recreate' )

  discriminantHistos = []
  nBins = 1000
  
  for flav in flavourCutsDict.keys():
    discriminantHisto = ROOT.TH1D("histBDTG_%s"%flav, "BDTG output for %s;BDTG value"%flav, nBins, -1, 1)
    mychain.Draw("BDTG >> +histBDTG_%s"%flav, flavourCutsDict[flav], "")
    discriminantHisto.Write()
    discriminantHistos.append(discriminantHisto)
    for i in range(len(etaPtBins)):
      discriminantHisto = ROOT.TH1D("histBDTG_%s_EtaPt%i"%(flav, i), "BDTG output for %s and %s;BDTG value"%(flav, etaPtBins[i]), nBins, -1, 1)
      mychain.Draw("BDTG >> +histBDTG_%s_EtaPt%i"%(flav, i), "(%s) && (%s)" %(flavourCutsDict[flav], etaPtBins[i].replace("and","&&")), "")
      discriminantHisto.Write()
      discriminantHistos.append(discriminantHisto)
    for cat in categoryCutsDict.keys():
      discriminantHisto = ROOT.TH1D("histBDTG_%s_%s"%(flav, cat), "BDTG output for %s and %s;BDTG value"%(flav, cat), nBins, -1, 1)
      mychain.Draw("BDTG >> +histBDTG_%s_%s"%(flav, cat), "%s && %s"%(flavourCutsDict[flav], categoryCutsDict[cat]), "")
      discriminantHisto.Write()
      discriminantHistos.append(discriminantHisto)
    for j in range(len(PtBins)):
      discriminantHisto = ROOT.TH1D("histBDTG_%s_Pt%i"%(flav, j), "BDTG output for %s and %s;BDTG value"%(flav, PtBins[j]), nBins, -1, 1)
      mychain.Draw("BDTG >> +histBDTG_%s_Pt%i"%(flav, j), "(%s) && (%s)" %(flavourCutsDict[flav], PtBins[j].replace("and","&&")), "")
      discriminantHisto.Write()
      discriminantHistos.append(discriminantHisto)
  
  outFile.Close()
  inFile.Close()


def makeROCCurves(outDirName):
  
  nBins = 100
  xBins = array("d")
  xBinsPlot = array("d")
  yBinsPlot = array("d")
  for i in range(0,nBins+2):
    xBins.append(float(i)/nBins)
  outFileName = "%s/AllHistograms.root" %(outDirName)
  print "Updating %s" %outFileName
  outFile = ROOT.TFile.Open(outFileName, "update")
  histDictFlav = [[0 for x in range(len(PtBins))] for y in range(len(flavours))]
  histDictFlavEffs = [[0 for x in range(len(PtBins))] for y in range(len(flavours))]
  histDictFlavEffsError = [[0 for x in range(len(PtBins))] for y in range(len(flavours))]
  histDictFlavCat = [[0 for x in range(len(categories))] for y in range(len(flavours))]
  histDictFlavCatEffs = [[0 for x in range(len(categories))] for y in range(len(flavours))]
  histDictFlavCatEffsError = [[0 for x in range(len(categories))] for y in range(len(flavours))]
  for flav in range(len(flavours)):
    for j in range(len(PtBins)):
      histDictFlav[flav][j] = outFile.Get("histBDTG_%s_Pt%i"%(flavours[flav],j))
      histDictFlavEffs[flav][j] = array("d")
      histDictFlavEffsError[flav][j] = array("d")
      integral = histDictFlav[flav][j].Integral(0, histDictFlav[flav][j].GetNbinsX()+1)
      for xbin in range(0, histDictFlav[flav][j].GetNbinsX()+2):
        histDictFlavEffs[flav][j].append(histDictFlav[flav][j].Integral(xbin, histDictFlav[flav][j].GetNbinsX()+1)/integral) # Eff = Sum(binx --> end) / Sum(begin --> end)
	histDictFlavEffsError[flav][j].append(math.sqrt(histDictFlav[flav][j].Integral(xbin, histDictFlav[flav][j].GetNbinsX()+1))/integral)
    for c in range(len(categories)):
      if c < (len(categories)-1):
        histDictFlavCat[flav][c] = outFile.Get("histBDTG_%s_%s"%(flavours[flav],categories[c]))
      else:
        histDictFlavCat[flav][c] = outFile.Get("histBDTG_%s"%(flavours[flav]))
      histDictFlavCatEffs[flav][c] = array("d")
      histDictFlavCatEffsError[flav][c] = array("d")
      integral = histDictFlavCat[flav][c].Integral(0, histDictFlavCat[flav][c].GetNbinsX()+1)
      for xbin in range(0, histDictFlavCat[flav][c].GetNbinsX()+2):
        histDictFlavCatEffs[flav][c].append(histDictFlavCat[flav][c].Integral(xbin, histDictFlavCat[flav][c].GetNbinsX()+1)/integral)
	histDictFlavCatEffsError[flav][c].append(math.sqrt(histDictFlavCat[flav][c].Integral(xbin, histDictFlavCat[flav][c].GetNbinsX()+1))/integral)


  # Create Efficiency v. Discriminator bin plots
  canvas1 = ROOT.TCanvas("c0","Eff",800,800)
  XbinEff = array("d")
  YbinEff = array("d")
  XbinEffError = array("d") # dummy
  YbinEffError = array("d")
  for flav in range(len(flavours)):
    for cat in range(len(categories)):
      del XbinEff[:]
      del YbinEff[:]
      del XbinEffError[:] # dummy
      del YbinEffError[:]
      for Xbin in range(0,histDictFlavCat[flav][cat].GetNbinsX()+1):
        YbinEff.append(histDictFlavCatEffs[flav][cat][Xbin])
	YbinEffError.append(histDictFlavCatEffsError[flav][cat][Xbin])
        XbinEff.append(histDictFlavCat[flav][cat].GetBinCenter(Xbin))
	XbinEffError.append(0) # dummy
        #XbinEff.append(histDictFlavCat[flav][cat].Integral(Xbin,histDictFlavCat[flav][cat].GetNbinsX()+1))
        #XbinEff.append(Xbin)
      EffCurve = ROOT.TGraphErrors(len(XbinEff),XbinEff,YbinEff,XbinEffError,YbinEffError)
      EffCurve.GetXaxis().SetTitle("%s Discriminant"%(flavours[flav]))
      EffCurve.GetYaxis().SetTitle("%s efficiency"%(flavours[flav]))
      EffCurve.SetTitle("%s efficiency, %s"%(flavours[flav],categories[cat]))
      EffCurve.SetName("Efficiency_%s_discrim_%s"%(flavours[flav],categories[cat]))
      EffCurve.Draw("al")
      ROOT.gPad.SetGridx(1)
      ROOT.gPad.SetGridy(1)
      #canvas1.SaveAs("%s/%s.png" %(outDirName, EffCurve.GetName()))
      EffCurve.Write()

  # Create ROC curves for vertex categories
  canvas2 = ROOT.TCanvas("c2","ROC",800,800);
  for flav1 in range(len(flavours)):
    for flav2 in range(len(flavours)):
      for cat in range(len(categories)):
        del xBinsPlot[:]
        del yBinsPlot[:]
        yBins = array("d")
        for i in range(0,nBins+2):
          yBins.append(0.)
        integral1 = histDictFlavCat[flav1][cat].Integral(0, histDictFlavCat[flav1][cat].GetNbinsX()+1)
        discrimBin = histDictFlavCat[flav1][cat].GetNbinsX()+1 
        for currentBin in range(0,nBins+2):
          currentEff = histDictFlavCatEffs[flav1][cat][discrimBin]
          yBins[currentBin] = histDictFlavCatEffs[flav2][cat][discrimBin]
          while currentEff < xBins[currentBin] and discrimBin > 0:
            discrimBin -= 1
            currentEff = histDictFlavCatEffs[flav1][cat][discrimBin]
            yBins[currentBin] = histDictFlavCatEffs[flav2][cat][discrimBin]
          if (currentBin < (nBins+1) and currentEff < xBins[currentBin+1]):
            xBinsPlot.append(xBins[currentBin])
            yBinsPlot.append(yBins[currentBin])

        rocCurve = ROOT.TGraph(len(xBinsPlot),xBinsPlot,yBinsPlot)
        rocCurve.GetXaxis().SetTitle("%s efficiency"%flavours[flav1])
        rocCurve.GetYaxis().SetTitle("%s efficiency"%flavours[flav2])
        rocCurve.SetTitle("%s vs. %s, %s"%(flavours[flav1], flavours[flav2], categories[cat]))
        rocCurve.SetName("ROC_%s_%s_%s"%(flavours[flav1], flavours[flav2],categories[cat]))
        rocCurve.GetYaxis().SetRangeUser(0.0001,1.0);
        rocCurve.GetXaxis().SetLimits(0.,1.0);
        rocCurve.Draw("al")
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)
        ROOT.gPad.SetLogy()
        #canvas2.SaveAs("%s/%s.png" %(outDirName, rocCurve.GetName()))
        rocCurve.Write()
        
  # Create ROC curves
  canvas = ROOT.TCanvas("c1","ROC",800,800);
  for flav1 in range(len(flavours)):
    for flav2 in range(len(flavours)):
      for n in range(len(PtBins)):
        del xBinsPlot[:]
        del yBinsPlot[:]
        yBins = array("d")
        for i in range(0,nBins+2):
          yBins.append(0.)
        integral1 = histDictFlav[flav1][n].Integral(0, histDictFlav[flav1][n].GetNbinsX()+1)
        #del xBinsPlot[:]
        #del yBinsPlot[:]
        #print "ROC curve for flavor %s %s" %(flav1,flav2)
        # loop over efficiency values starting at 0 (i.e. highest bin)
        discrimBin = histDictFlav[flav1][n].GetNbinsX()+1
        for currentBin in range(0,nBins+2):
          # get discriminant bin for signal
          currentEff = histDictFlavEffs[flav1][n][discrimBin]
          yBins[currentBin] = histDictFlavEffs[flav2][n][discrimBin]
        #print "%i - %i: %f - %f - %f" %(currentBin, discrimBin, xBins[currentBin], currentEff, yBins[currentBin])
          while currentEff < xBins[currentBin] and discrimBin > 0:
            discrimBin -= 1
            currentEff = histDictFlavEffs[flav1][n][discrimBin]
            yBins[currentBin] = histDictFlavEffs[flav2][n][discrimBin]
            #print "while %i - %i: %f - %f - %f" %(currentBin, discrimBin, xBins[currentBin], currentEff, yBins[currentBin])
          #print "--------------"
          if (currentBin < (nBins+1) and currentEff < xBins[currentBin+1]):
            xBinsPlot.append(xBins[currentBin])
            yBinsPlot.append(yBins[currentBin])

        
        #print yBins
        #print len(yBins)

        #print "eff vs eff"
        #for i in range (0, len(xBinsPlot)):
        #  print "%f %f" %(xBinsPlot[i], yBinsPlot[i])

        #rocCurve = TGraph(len(xBins),xBins,yBins)
        rocCurve = ROOT.TGraph(len(xBinsPlot),xBinsPlot,yBinsPlot)
        rocCurve.GetXaxis().SetTitle("%s efficiency"%flavours[flav1])
        rocCurve.GetYaxis().SetTitle("%s efficiency"%flavours[flav2])
        rocCurve.SetTitle("%s vs. %s, %s"%(flavours[flav1], flavours[flav2], PtBins[n]))
        rocCurve.SetName("ROC_%s_%s_%i"%(flavours[flav1], flavours[flav2],n))
        rocCurve.GetYaxis().SetRangeUser(0.0001,1.0);
        rocCurve.GetXaxis().SetLimits(0.,1.0);
        #TH1D("ROC_%s_%s"%(flav1, flav2), "ROC curve for %s vs. %s;%s efficiency;%s efficiency"%(flav1, flav2, flav1, flav2), 100, -1, 1)
        rocCurve.Draw("al")
        ROOT.gPad.SetGridx(1)
        ROOT.gPad.SetGridy(1)
        ROOT.gPad.SetLogy()
        #canvas.SaveAs("%s/%s.png" %(outDirName, rocCurve.GetName()))
        rocCurve.Write()
      #break
  outFile.Close()        
  


def main():
  from argparse import ArgumentParser

  parser = ArgumentParser()
  parser.add_argument('inputdir')
  parser.add_argument('outputdir')
  args = parser.parse_args()

  ROOT.gROOT.SetBatch(True)
  parallelProcesses = multiprocessing.cpu_count()
  
  # create Pool
  p = multiprocessing.Pool(parallelProcesses)
  print "Using %i parallel processes" %parallelProcesses
    
  #outDirName = './histos_witherror'
  outDirName = args.outputdir
  inDirName = args.inputdir

  if not os.path.isdir(outDirName):
    os.makedirs(outDirName)
  
  fileList = []

  for inFileName in os.listdir(inDirName):
    if inFileName.endswith(".root") and inFileName.startswith("trainPlusBDTG_"):
      category = inFileName.replace("trainPlusBDTG_", "").split("_",1)[0]
      flavour = inFileName.replace("trainPlusBDTG_", "").split("_",2)[1]
      key = "%s_%s" %(category, flavour)
      print key
      fileList.append(inFileName.replace(".root", "_Histograms.root"))
      # processNtuple(inFileName, inDirName, outDirName)
      # break
      p.apply_async(processNtuple, args = (inFileName, inDirName, outDirName,))

  p.close()
  p.join()


  # loop over all output files of one category and flavour and hadd them
  outDirName = os.path.join(os.path.abspath(sys.path[0]), outDirName) # absolute path to be safe
  print "hadding key files"
  haddList = ""
  for fileName in fileList:
    haddList += "%s " %fileName
  haddCommand = "pwd && hadd -f AllHistograms.root %s" %(haddList)
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
  # for fileName in fileList:
  #   print "deleting %s/%s"%(outDirName, fileName)
  #   os.remove("%s/%s"%(outDirName, fileName))
  
  makeROCCurves(outDirName)
  

if __name__ == "__main__":
  main()
