#include "TGraph.h"

void ROCoverlays() {
  TFile *TTbar = TFile::Open("ttbarEval/histos/AllHistograms.root");
  TFile *QCD = TFile::Open("qcdEval/histos/AllHistograms.root"); 

  for (Int_t i=0; i<9; i++){
    // Discriminators ttbar
    TH1F *ttbarC = (TH1F*)TTbar->Get(Form("histBDTG_C_Pt%i",i));
    TH1F *ttbarL = (TH1F*)TTbar->Get(Form("histBDTG_light_Pt%i",i));
    
    // Discriminators qcd
    TH1F *qcdC = (TH1F*)QCD->Get(Form("histBDTG_C_Pt%i",i));
    TH1F *qcdL = (TH1F*)QCD->Get(Form("histBDTG_light_Pt%i",i));
    
    //ROC CvLight
    TGraph *qcdCvL = (TGraph*)QCD->Get(Form("ROC_C_light_%i",i));
    TGraph *ttbarCvL = (TGraph*)TTbar->Get(Form("ROC_C_light_%i",i));
    

    // Normalize Discriminator Distributions
    ttbarC->Scale(1./ttbarC->Integral());
    ttbarL->Scale(1./ttbarL->Integral());
    qcdC->Scale(1./qcdC->Integral());
    qcdL->Scale(1./qcdL->Integral());
    
    //Set colors
    qcdCvL->SetLineColor(kBlack);
    qcdL->SetLineColor(kBlack);
    qcdC->SetLineColor(kBlack);
    
    ttbarCvL->SetLineColor(kBlue);
    ttbarC->SetLineColor(kBlue);
    ttbarL->SetLineColor(kBlue);
    
    qcdCvL->SetLineWidth(2); 
    ttbarCvL->SetLineWidth(2); 
    qcdC->SetLineWidth(2);
    qcdL->SetLineWidth(2);    
    ttbarL->SetLineWidth(2); 
    ttbarC->SetLineWidth(2);
    
    
    TCanvas *cv = 0;
    TLegend *l = 0;
    TLatex *tex = 0;
    // Discriminators QCD
    cv = new TCanvas("cv","cv",800,800);
    cv->SetGridx();
    cv->SetGridy();
    qcdL->SetLineColor(kBlue);
    qcdL->SetTitle("QCD Discriminators");
    qcdL->Draw();
    qcdC->Draw("same");
    gStyle->SetOptStat(0);
    l = new TLegend(0.55,0.75,0.90,0.9);
    l->AddEntry(qcdC,"C Discriminator","l");
    l->AddEntry(qcdL,"DUSG Discriminator","l");
    l->Draw();
    cv->Update();
    cv->SaveAs(Form("QCD_Discriminators_%i.png",i));
    qcdL->SetLineColor(kBlack);
    
    // ttbar Discriminators
    cv = new TCanvas("cv","Reco",800,800);
    cv->SetGridx();
    cv->SetGridy();
    ttbarC->SetLineColor(kBlack);
    ttbarL->SetTitle("ttbar Discriminators");
    ttbarL->Draw();
    ttbarC->Draw("same");
    gStyle->SetOptStat(0);
    l = new TLegend(0.55,0.8,0.90,0.9);
    l->AddEntry(ttbarC,"C Discriminator","l");
    l->AddEntry(ttbarL,"DUSG Discriminator","l");
    l->Draw();
    cv->Update();
    cv->SaveAs(Form("TTbar_Discriminators_%i.png",i));
    ttbarC->SetLineColor(kBlue);
    
    // C Discriminators
    cv = new TCanvas("cv","C",800,800);
    cv->SetGridx();
    cv->SetGridy();
    qcdC->Draw();
    qcdC->SetTitle("C Discriminators");
    ttbarC->Draw("same");
    gStyle->SetOptStat(0);
    l = new TLegend(0.55,0.8,0.90,0.9);
    l->AddEntry(ttbarC,"ttbar","l");
    l->AddEntry(qcdC,"QCD","l");
    l->Draw();
    cv->Update();
    cv->SaveAs(Form("C_Discriminators_%i.png",i));
    
    // DUSG Discriminators
    cv = new TCanvas("cv","DUSG",800,800);
    cv->SetGridx();
    cv->SetGridy();
    qcdL->SetTitle("DUSG Discriminators");
    qcdL->Draw();
    ttbarL->Draw("same");
    gStyle->SetOptStat(0);
    l = new TLegend(0.55,0.8,0.90,0.9);
    l->AddEntry(ttbarL,"ttbar","l");
    l->AddEntry(qcdL,"QCD","l");
    l->Draw();
    cv->Update();
    cv->SaveAs(Form("DUSG_Discriminators_%i.png",i));
    
    // CvL
    cv = new TCanvas("cv","Reco",800,800);
    cv->SetLogy();
    cv->SetGridx();
    cv->SetGridy();
    ttbarCvL->Draw();
    qcdCvL->Draw("same");
    l = new TLegend(0.15,0.8,0.40,0.9);
    l->AddEntry(ttbarCvL,"ttbar","l");
    l->AddEntry(qcdCvL,"QCD","l");
    l->Draw();
    cv->SaveAs(Form("CvL_%i.png",i));
  }
}
