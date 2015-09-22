#include "TH1.h"
#include "TFile.h"
#include "TTree.h"
#include "TCanvas.h"
#include "TStyle.h"
#include "TDirectory.h"

void DrawVariablePDFs_TMVA(){
  
  TString var_name = "jetEta";
  //TString flavours[] = {"C","DUSG"};
  
  
  
  //Define the root files
  TFile* TMVA_file = TFile::Open("./TMVA_classification.root");
  
  
  Int_t nbins = 50;
  Float_t binmin = -3;
  Float_t binmax = 3;
  
  TH1F* signal_histo = new TH1F("signal_histo","Signal Vs Background from TMVA: " + var_name + ";" + var_name + ";Entries (normalized)",nbins,binmin,binmax);
  gDirectory->GetObject("InputVariables_Id/" + var_name +"__Signal_Id",signal_histo);
  TH1F* bckgr_histo = new TH1F("bckgr_histo","Signal Vs Background from TMVA: " + var_name + ";" + var_name + ";Entries (normalized)",nbins,binmin,binmax);
  gDirectory->GetObject("InputVariables_Id/" + var_name + "__Background_Id",bckgr_histo);
  
  signal_histo->Scale(1./signal_histo->Integral());
  bckgr_histo->Scale(1./bckgr_histo->Integral());
  
  TCanvas* c = new TCanvas("c","PDF canvas TMVA",800,800);
  TLegend* l = new TLegend(0.20,0.78,0.65,0.9);
  gStyle->SetLegendBorderSize(0);
  
  signal_histo->SetLineColor(2);
  signal_histo->SetLineWidth(2);
  signal_histo->Draw();
  l->AddEntry(signal_histo,var_name + " C Inclusive TMVA","l");
  bckgr_histo->SetLineColor(4);
  bckgr_histo->SetLineWidth(2);
  bckgr_histo->Draw("same");
  l->AddEntry(bckgr_histo,var_name + " DUSG Inclusive TMVA","l");
  
  l->Draw("same");
  c->SaveAs(var_name + "_ComparisonCvsDUSG_TMVA.png");

}

