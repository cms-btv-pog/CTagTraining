#include "TH1.h"
#include "TH2F.h"
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TSystem.h"
#include "TF1.h"
#include "TKey.h"
#include "TH1F.h"
#include "TStyle.h"
#include "TProfile.h"
#include "TStyle.h"
#include "TLegend.h"
#include "TLine.h"
#include "TArrow.h"
#include "TLatex.h"
#include "TMinuit.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TFormula.h"
#include "TAxis.h"
#include "TMultiGraph.h"
#include "TColor.h"

#include <iostream.h>
#include <stdio.h>
#include <fstream.h>
#include <vector.h>
//#include "./tdrstyle.C"

void CompareCMSSWtoTMVA(){

 // **************** CMSSW ********************************
 TString fileName1 = "/user/gvonsem/BTagServiceWork/MVA/gitrecipe/SuperCTagger/CMSSW_7_0_9/src/RecoBTau/JetTagMVALearning/test/ctag_CSVSL/Validation/70XCSVSLctagtraining_PUid/DQM_V0001_R000000001__POG__BTAG__ttincl.root";
 TFile* file1 = TFile::Open(fileName1);

 TH1F* CSVIVFV2_effC = (TH1F*) file1->Get("DQMData/Run 1/Btag/Run summary/CSVIVFSLctag_GLOBAL/effVsDiscrCut_discr_CSVIVFSLctag_GLOBALC");
 TH1F* CSVIVFV2_effDUSG = (TH1F*) file1->Get("DQMData/Run 1/Btag/Run summary/CSVIVFSLctag_GLOBAL/effVsDiscrCut_discr_CSVIVFSLctag_GLOBALDUSG");

 const Int_t n = 100;
 Double_t CSVSLctag_C[n],CSVSLctag_L[n],CSVSLctag_eC[n],CSVSLctag_eL[n];

 for(int bin = 0; bin<n; bin++){
	CSVSLctag_C[bin] = CSVIVFV2_effC->GetBinContent(bin+1);
	CSVSLctag_L[bin] = CSVIVFV2_effDUSG->GetBinContent(bin+1);
	CSVSLctag_eC[bin] = CSVIVFV2_effC->GetBinError(bin+1);
	CSVSLctag_eL[bin] = CSVIVFV2_effDUSG->GetBinError(bin+1);
 }

 TGraphErrors* CSVSLctag_CvsDUSG = new TGraphErrors(n,CSVSLctag_C,CSVSLctag_L,CSVSLctag_eC,CSVSLctag_eL);
 
 
 
 // ***************** TMVA *******************************
  TString ROC = "ROC_C_light_Inclusive";
  TString ROC_files[] = {"/user/smoortga/CTag/TMVActag_v1/NewWeightsCTaggingCvsDUSG/FullCTaggerSL/histos/AllHistograms.root",
  			 "/user/smoortga/CTag/TMVActag_v1/TMVA_BDTSetup/Optimal_BDTSettings_Training/histos/AllHistograms.root"};
			 
  TString LegendNames[] = {"TMVA (13 TeV with SL) Default",
  			   "TMVA (13 TeV with SL) Optimized"};
			 
  size_t size = 2;

  vector<TFile*> Root_Files(0);
  for (size_t i = 0; i<size; i++){
    Root_Files.push_back((TFile*)TFile::Open(ROC_files[i]));
  }

  vector<TGraph*> ROC_curves(0);
  for (size_t i = 0; i<size; i++){
    ROC_curves.push_back((TGraph*)Root_Files[i]->Get(ROC));
  }

  TCanvas* c = new TCanvas("c","Overlay Canvas",700,700);
  c->SetLogy();
  c->SetGridx();
  c->SetGridy();
  TLegend* l = new TLegend(0.35,0.15,0.90,0.35);
  //gStyle->SetOptStat("");
  
  
  TMultiGraph* mg = new TMultiGraph();
  for (size_t i = 0; i<ROC_curves.size(); i++){
    if (i == 0) {ROC_curves[i]->SetLineColor(kGreen + 2);}
    else {ROC_curves[i]->SetLineColor(kCyan + 1);}
    ROC_curves[i]->SetLineWidth(2);
    //ROC_curves[i]->SetTitle("");
    mg->Add(ROC_curves[i]);
    l->AddEntry(ROC_curves[i],LegendNames[i],"l");
  }
  
  // Make Diagonal
  Int_t n_diag = 14;
  Float_t x[14] = {0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1};
  TGraph* diag = new TGraph(n_diag,x,x);
  diag->SetLineColor(13); //gray
  diag->SetLineStyle(2); //dotted
  mg->Add(diag);
  
  // Add CMSSWS graph to multigraph
  CSVSLctag_CvsDUSG->SetLineColor(6);
  CSVSLctag_CvsDUSG->SetLineWidth(2);
  CSVSLctag_CvsDUSG->SetMarkerSize(0);
  mg->Add(CSVSLctag_CvsDUSG);
  l->AddEntry(CSVSLctag_CvsDUSG,"CMSSW (13 TeV with SL)","l");
  
  c->cd();
  mg->SetTitle(" ;C Efficiency; DUSG Efficiency");
  mg->Draw("AL");
  l->Draw("same");
  c->Update();
  c->SaveAs(ROC + "_TMVA_vs_OptimizedTMVA_vs_CMSSW.png"); // + "_Overlay.png");

}
