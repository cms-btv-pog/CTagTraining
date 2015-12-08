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
 
  TString histos[] = {"B","C"};
  size_t size = 2;

  TFile* All = TFile::Open("./histos/AllHistograms.root");

  vector<TH1*> histograms(0);
  for (size_t i = 0; i<size; i++){
    histograms.push_back((TH1*)All->Get("histBDTG_"+histos[i]));
  }
  
  for (size_t i = 0; i<size; i++){
    histograms[i]->Scale(1/histograms[i]->Integral());
    histograms[i]->Rebin(8);
  }

  TCanvas* c = new TCanvas("c","Overlay Canvas",800,800);
  c->cd();
  c->SetLogy(1);
  c->SetLeftMargin(0.15);
  c->SetRightMargin(0.05);
  c->SetTopMargin(0.05);
  c->SetBottomMargin(0.15);
  TLegend* l = new TLegend(0.63,0.83,0.88,0.93);
  gStyle->SetOptStat("");
  
  for (size_t i = 0; i<histograms.size(); i++){
    if (i == 0) {histograms[i]->SetLineColor(kRed);}
    if (i == 1) {histograms[i]->SetLineColor(kBlue);}
    histograms[i]->SetLineWidth(2);
    histograms[i]->SetTitle("");
    histograms[i]->GetXaxis()->SetTitleOffset(1.3);
    histograms[i]->GetYaxis()->SetTitleOffset(1.3);
    histograms[i]->GetXaxis()->SetTitleSize(0.045);
    histograms[i]->GetYaxis()->SetTitleSize(0.045);
    histograms[i]->GetXaxis()->SetTitle("BDT discriminator value");
    histograms[i]->GetYaxis()->SetTitle("Normalised number of events");
    if (i==0){histograms[i]->Draw();}
    else {histograms[i]->Draw("same");}
    l->AddEntry(histograms[i],histos[i],"l");
  }
  
  l->Draw();
  c->SaveAs("BDTG_Overlay_13TeVSL.png");
   
}

void DrawROCOverlays(){
 
  TString ROC = "ROC_C_light_Inclusive";
  TString ROC_files[] = {"/user/smoortga/CTag/TMVActag_v1/TMVA_BDTSetup/CMSSW_7_5_1_Retraining/histos/AllHistograms.root",
  			 "/user/smoortga/CTag/testScikitLearn/histos_RFC/AllHistograms.root",
			 "/user/smoortga/CTag/testScikitLearn/histos/AllHistograms.root"};
			 
  TString LegendNames[] = {"TMVA BDT (2000 trees, all events, 76 variables)",
			   "sklearn RFC (2000 trees, 1% of events, 20 variables)",
			   "sklearn GB (2000 iter, 1% of events, 20 variables)"};
			 
  size_t size = 3;

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
    ROC_curves[i]->SetLineColor(i+2);
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
  mg->SetTitle(ROC+";C Efficiency; B Efficiency");
  mg->Draw("AL");
  l->Draw("same");
  c->Update();
  c->SaveAs(ROC + "_compareGBtoRC.png"); // + "_Overlay.png");
   
}

void DrawCategoryOverlays(){
 
  TString ROC[] = {"Inclusive","NoVertex","PseudoVertex","RecoVertex"};
  size_t size = 4;

  TFile* All = TFile::Open("./histos/AllHistograms.root");

  vector<TGraph*> ROC_curves(0);
  for (size_t i = 0; i<size; i++){
    ROC_curves.push_back((TGraph*)All->Get("ROC_C_light_"+ROC[i]));
  }
  
  /*for (size_t i = 0; i<size; i++){
    histograms[i]->Scale(1/histograms[i]->Integral());
    histograms[i]->Rebin(8);
  }*/

  TCanvas* c = new TCanvas("c","Overlay Canvas",700,700);
  c->SetLogy();
  c->SetGridx();
  c->SetGridy();
  TLegend* l = new TLegend(0.35,0.15,0.90,0.35);
  
  TMultiGraph* mg = new TMultiGraph();
  for (size_t i = 0; i<ROC_curves.size(); i++){
    ROC_curves[i]->SetLineColor(i+1);
    ROC_curves[i]->SetLineWidth(2);
    if (i>0){ROC_curves[i]->SetLineStyle(7);}
    //ROC_curves[i]->SetTitle("");
    mg->Add(ROC_curves[i]);
    l->AddEntry(ROC_curves[i],ROC[i],"l");
  }
  
  // Make Diagonal
  Int_t n_diag = 14;
  Float_t x[14] = {0.001,0.005,0.01,0.05,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9,1};
  TGraph* diag = new TGraph(n_diag,x,x);
  diag->SetLineColor(13); //gray
  diag->SetLineStyle(2); //dotted
  mg->Add(diag);
  
  c->cd();
  mg->SetTitle(";C Efficiency; DUSG Efficiency");
  mg->Draw("AL");
  l->Draw("same");
  c->Update();
  c->SaveAs("CompareCategories.png"); // + "_Overlay.png");
   
}


void DrawOverlays(){
  //DrawBDTGOverlays();
  DrawROCOverlays();
  //DrawCategoryOverlays();
}

