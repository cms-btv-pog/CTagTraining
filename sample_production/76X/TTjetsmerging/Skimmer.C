#include <string>         // std::string
#include "TTree.h"
#include "TString.h"
#include "TFile.h"

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
#include "TLegend.h"
#include "TLine.h"
#include "TArrow.h"
#include "TLatex.h"
#include "TGraph.h"
#include "TGraphErrors.h"
#include "TFormula.h"
#include "TAxis.h"
#include "TRandom3.h"
#include "TMath.h"

#include <cmath>
#include <iostream>
#include <stdio.h>
#include <fstream>
#include <sstream>
#include <vector>

//int main() {
void Skimmer() {
//void Filter(TString filename, TString treename) {
// Example of Root macro based on $ROOTSYS/tutorials/tree/copytree3.C
   
//  gSystem->Load("$ROOTSYS/test/libEvent");
//  gSystem->Load("$ROOTSYS/lib/libEve.so");

	string filename[27]={"CombinedSVNoVertexNoSoftLepton_B.root","CombinedSVNoVertexNoSoftLepton_C.root","CombinedSVNoVertexNoSoftLepton_DUSG.root","CombinedSVPseudoVertexNoSoftLepton_B.root","CombinedSVPseudoVertexNoSoftLepton_C.root","CombinedSVPseudoVertexNoSoftLepton_DUSG.root","CombinedSVRecoVertexNoSoftLepton_B.root","CombinedSVRecoVertexNoSoftLepton_C.root","CombinedSVRecoVertexNoSoftLepton_DUSG.root","CombinedSVNoVertexSoftElectron_B.root","CombinedSVNoVertexSoftElectron_C.root","CombinedSVNoVertexSoftElectron_DUSG.root","CombinedSVPseudoVertexSoftElectron_B.root","CombinedSVPseudoVertexSoftElectron_C.root","CombinedSVPseudoVertexSoftElectron_DUSG.root","CombinedSVRecoVertexSoftElectron_B.root","CombinedSVRecoVertexSoftElectron_C.root","CombinedSVRecoVertexSoftElectron_DUSG.root","CombinedSVNoVertexSoftMuon_B.root","CombinedSVNoVertexSoftMuon_C.root","CombinedSVNoVertexSoftMuon_DUSG.root","CombinedSVPseudoVertexSoftMuon_B.root","CombinedSVPseudoVertexSoftMuon_C.root","CombinedSVPseudoVertexSoftMuon_DUSG.root","CombinedSVRecoVertexSoftMuon_B.root","CombinedSVRecoVertexSoftMuon_C.root","CombinedSVRecoVertexSoftMuon_DUSG.root"};
	TString treename[27]={"CombinedSVNoVertexNoSoftLepton","CombinedSVNoVertexNoSoftLepton","CombinedSVNoVertexNoSoftLepton","CombinedSVPseudoVertexNoSoftLepton","CombinedSVPseudoVertexNoSoftLepton","CombinedSVPseudoVertexNoSoftLepton","CombinedSVRecoVertexNoSoftLepton","CombinedSVRecoVertexNoSoftLepton","CombinedSVRecoVertexNoSoftLepton","CombinedSVNoVertexSoftElectron","CombinedSVNoVertexSoftElectron","CombinedSVNoVertexSoftElectron","CombinedSVPseudoVertexSoftElectron","CombinedSVPseudoVertexSoftElectron","CombinedSVPseudoVertexSoftElectron","CombinedSVRecoVertexSoftElectron","CombinedSVRecoVertexSoftElectron","CombinedSVRecoVertexSoftElectron","CombinedSVNoVertexSoftMuon","CombinedSVNoVertexSoftMuon","CombinedSVNoVertexSoftMuon","CombinedSVPseudoVertexSoftMuon","CombinedSVPseudoVertexSoftMuon","CombinedSVPseudoVertexSoftMuon","CombinedSVRecoVertexSoftMuon","CombinedSVRecoVertexSoftMuon","CombinedSVRecoVertexSoftMuon"};
//	string filename[54]={"CombinedSVPseudoVertexSoftElectron_B.root","CombinedSVPseudoVertexSoftElectron_C.root","CombinedSVPseudoVertexSoftElectron_DUSG.root","CombinedSVPseudoVertexSoftMuon_B.root","CombinedSVPseudoVertexSoftMuon_C.root","CombinedSVPseudoVertexSoftMuon_DUSG.root"};
//	TString treename[54]={"CombinedSVPseudoVertexSoftElectron","CombinedSVPseudoVertexSoftElectron","CombinedSVPseudoVertexSoftElectron","CombinedSVPseudoVertexSoftMuon","CombinedSVPseudoVertexSoftMuon","CombinedSVPseudoVertexSoftMuon"};
//	string filename[3]={"CombinedSVNoVertexSoftElectron_B.root","CombinedSVNoVertexSoftElectron_C.root","CombinedSVNoVertexSoftElectron_DUSG.root"};
//	TString treename[3]={"CombinedSVNoVertexSoftElectron","CombinedSVNoVertexSoftElectron","CombinedSVNoVertexSoftElectron"};

	double fraction = 0.1;
	double rdmnr = -999;
	gRandom->Uniform();

	for(int k = 0; k<27; k++)
	{  
		//Get old file, old tree and set top branch address
  	TString name = filename[k].c_str();
		TFile *oldfile = new TFile(name);
  	TTree *oldtree = (TTree*)oldfile->Get(treename[k]); //CombinedSVNoVertex, CombinedSVRecoVertex, CombinedSVPseudoVertex
  	Int_t nentries = (Int_t)oldtree->GetEntries();

		cout << "There are " << nentries << " jets in the file " << filename[k] << " will select " << 100*fraction << " percent of events in a random way" << endl;
   
  	Int_t flavour;
  	Double_t jetpt, jeteta, trackSumJetEtRatio, trackSumJetDeltaR;
    	std::vector <double>  *trackSip3dSig, *trackSip2dSig, *trackPtRel, *trackDeltaR, *trackPtRatio, *trackJetDist, *trackDecayLenVal, *trackSip2dSigAboveCharm, *trackSip3dSigAboveCharm, *leptonPtRel, *leptonSip3d, *leptonDeltaR, *leptonRatioRel;
  	oldtree->SetBranchAddress("flavour",&flavour);
  	oldtree->SetBranchAddress("jetPt",&jetpt);
  	oldtree->SetBranchAddress("jetEta",&jeteta);
  	oldtree->SetBranchAddress("trackPtRel",&trackPtRel);

  	//Create a new file + a clone of old tree in new file
  	TFile *newfile = new TFile("skimmed_"+name,"recreate");
  	TTree *newtree = oldtree->CloneTree(0);
		
//cout<<"TEST1"<<endl;
		for (Int_t i=0;i<nentries; i++)
		{
	    	 oldtree->GetEntry(i);
//cout<<"TEST2"<<endl;
         bool Skipevent = false;
         if(trackPtRel != 0)
				 {
		       for(Int_t iVect = 0; iVect < trackPtRel->size(); iVect ++)
					 {
			         if(trackPtRel->at(iVect) != trackPtRel->at(iVect) )
			         {
			          	cout << "trackPtRel[" << iVect << "]: " << trackPtRel->at(iVect) << endl; 
			           	Skipevent = true;
			         }
		       }		
		     }

				 if(gRandom->Uniform() > fraction) Skipevent = true;
				 
		     if(Skipevent == true) continue;
				 
				 newtree->Fill();
		}
		
		newtree->Print();
	  newtree->AutoSave();

	  delete oldfile;
  	delete newfile;
	}
}
