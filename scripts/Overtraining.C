#include "DrawOverlays.h"
#include <vector>
#include "TStyle.h"
#include "TGraph.h"
#include "TMultiGraph.h"
#include "TH1.h"
#include "TString.h"
#include "TCanvas.h"
#include "TLegend.h"
#include "TFile.h"


void DrawBDTGOverlays(){
 
  
  TFile* QCD_train = TFile::Open("./TMVA_classification.root");
  TFile* TTbar_val = TFile::Open("./histos/AllHistograms.root");

  TH1F* QCD_BDTG_C = (TH1F*)QCD_train->Get("Method_BDT/BDTG/MVA_BDTG_S");
  TH1F* QCD_BDTG_DUSG = (TH1F*)QCD_train->Get("Method_BDT/BDTG/MVA_BDTG_B");
  TH1F* TTbar_BDTG_C = (TH1F*)TTbar_val->Get("histBDTG_C");
  TH1F* TTbar_BDTG_DUSG = (TH1F*)TTbar_val->Get("histBDTG_light");
  

  // Change number of bins to match to 50
  Int_t final_nbins = 20.;
  QCD_BDTG_C->Rebin(QCD_BDTG_C->GetNbinsX()/final_nbins);
  QCD_BDTG_DUSG->Rebin(QCD_BDTG_DUSG->GetNbinsX()/final_nbins);
  TTbar_BDTG_C->Rebin(TTbar_BDTG_C->GetNbinsX()/final_nbins);
  TTbar_BDTG_DUSG->Rebin(TTbar_BDTG_DUSG->GetNbinsX()/final_nbins);
  
  // Normalize histograms
  QCD_BDTG_C->Scale(1./QCD_BDTG_C->Integral());
  QCD_BDTG_DUSG->Scale(1./QCD_BDTG_DUSG->Integral());
  TTbar_BDTG_C->Scale(1./TTbar_BDTG_C->Integral());
  TTbar_BDTG_DUSG->Scale(1./TTbar_BDTG_DUSG->Integral());

  TCanvas* c = new TCanvas("c","Overlay Canvas",1200,600);
  c->Divide(2,1);
  TLegend* l1 = new TLegend(0.10,0.8,0.40,0.9);
  TLegend* l2 = new TLegend(0.10,0.8,0.40,0.9);
  gStyle->SetOptStat("");
  
  c->cd(1);
  TTbar_BDTG_C->SetTitle("");
  TTbar_BDTG_C->SetLineColor(4);
  TTbar_BDTG_C->SetLineWidth(2);
  TTbar_BDTG_C->GetYaxis()->SetTitle("Normalized number of jets");
  TTbar_BDTG_C->Draw("hist");
  l1->AddEntry(TTbar_BDTG_C,"BDTG_C for TTbar","l");
  QCD_BDTG_C->SetLineColor(2);
  QCD_BDTG_C->SetLineWidth(2);
  QCD_BDTG_C->Draw("lsame");
  l1->AddEntry(QCD_BDTG_C,"BDTG_C for QCD","l");
  l1->Draw("same");
  
  c->cd(2);
  TTbar_BDTG_DUSG->SetTitle("");
  TTbar_BDTG_DUSG->SetLineColor(4);
  TTbar_BDTG_DUSG->SetLineWidth(2);
  TTbar_BDTG_DUSG->GetYaxis()->SetTitle("Normalized number of jets");
  TTbar_BDTG_DUSG->Draw("hist");
  l2->AddEntry(TTbar_BDTG_DUSG,"BDTG_DUSG for TTbar","l");
  QCD_BDTG_DUSG->SetLineColor(2);
  QCD_BDTG_DUSG->SetLineWidth(2);
  QCD_BDTG_DUSG->Draw("lsame");
  l2->AddEntry(QCD_BDTG_DUSG,"BDTG_DUSG for QCD","l");
  l2->Draw("same");
  
  c->SaveAs("Overtraining.png");
   
}

/*void DrawROCOverlays(){
 
  TString ROC = "ROC_C_light_Inclusive";
  TString ROC_files[] = {"/user/smoortga/CTag/TMVActag_v1/TMVA_BDTSetup/Optimal_BDTSettings_Training/histos/AllHistograms.root",
  			 "/user/smoortga/CTag/TMVActag_v1/NewWeightsCTaggingCvsDUSG/FullCTaggerSL/histos/AllHistograms.root"};
			 
  TString LegendNames[] = {"Optimal Settings",
  			   "Default Settings"};
			 
  size_t size = 2;

  vector<TFile*> Root_Files(0);
  for (size_t i = 0; i<size; i++){
    Root_Files.push_back((TFile*)TFile::Open(ROC_files[i]));
  }

  vector<TGraph*> ROC_curves(0);
  for (size_t i = 0; i<size; i++){
    ROC_curves.push_back((TGraph*)Root_Files[i]->Get(ROC));
  }

  TCanvas* c = new TCanvas("c","Overlay Canvas",800,800);
  c->SetLogy();
  c->SetGridx();
  c->SetGridy();
  TLegend* l = new TLegend(0.35,0.15,0.90,0.35);
  //gStyle->SetOptStat("");
  
  TMultiGraph* mg = new TMultiGraph();
  for (size_t i = 0; i<ROC_curves.size(); i++){
    ROC_curves[i]->SetLineColor(i+1);
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
  
  c->cd();
  mg->SetTitle(ROC+";C Efficiency; DUSG Efficiency");
  mg->Draw("AL");
  l->Draw("same");
  c->Update();
  c->SaveAs(ROC + "_DefaultVsOptimal.png"); // + "_Overlay.png");
   
}*/


void Overtraining(){
  DrawBDTGOverlays();
}

