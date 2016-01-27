import sys
import os
import ROOT
import numpy as np
import math
from argparse import ArgumentParser


parser = ArgumentParser()
parser.add_argument('--min', type=float, default=0, help='lower bound of the discriminator')
parser.add_argument('--max',  type=float, default=1, help='upper bound of the discriminator')
parser.add_argument('--ncuts', type=int, default=200, help='number of cuts/bins to make the plots (i.e. the refinement of the calculation)')
parser.add_argument('--outdir', default=os.getcwd(), help='directory of the output file')
parser.add_argument('--indirCvsDUSG', default=os.getcwd(), help='directory of the input files of the CvsDUSG training (trainPlusBDTG_...)')
parser.add_argument('--indirCvsB', default=os.getcwd(), help='directory of the input files of the CvsDUSG training (trainPlusBDTG_...)')
parser.add_argument('--pickEvery', type=int, default=1, help='pick one event every so many events')

args = parser.parse_args()


# PREPARE ALL FILES

indir_CvsDUSG = args.indirCvsDUSG #"/user/smoortga/CTag/76X_Retraining_Sklearn/src/CTagTraining/scripts/tested_files/76X_CvsDUSG_AllVariables"
indir_CvsB = args.indirCvsB #"/user/smoortga/CTag/76X_Retraining_Sklearn/src/CTagTraining/scripts/tested_files/76X_CvsB_AllVariables"#

os.system('hadd ' + os.getcwd() + '/CvsDUSG_C_tmp.root ' + indir_CvsDUSG + '/trainPlusBDTG_CombinedSV*_C.root')
os.system('hadd ' + os.getcwd() + '/CvsDUSG_B_tmp.root ' + indir_CvsDUSG + '/trainPlusBDTG_CombinedSV*_B.root')
os.system('hadd ' + os.getcwd() + '/CvsDUSG_DUSG_tmp.root ' + indir_CvsDUSG + '/trainPlusBDTG_CombinedSV*_DUSG.root')

os.system('hadd ' + os.getcwd() + '/CvsB_C_tmp.root ' + indir_CvsB + '/trainPlusBDTG_CombinedSV*_C.root')
os.system('hadd ' + os.getcwd() + '/CvsB_B_tmp.root ' + indir_CvsB + '/trainPlusBDTG_CombinedSV*_B.root')
os.system('hadd ' + os.getcwd() + '/CvsB_DUSG_tmp.root ' + indir_CvsB + '/trainPlusBDTG_CombinedSV*_DUSG.root')


Eff_vs_Disc_2D_B = ROOT.TGraph2D()
Eff_vs_Disc_2D_C = ROOT.TGraph2D()
Eff_vs_Disc_2D_DUSG = ROOT.TGraph2D()

disc_min = args.min
disc_max = args.max
ncuts = args.ncuts

CvsDUSG_Disc = np.arange(disc_min,disc_max,(disc_max-disc_min)/ncuts)
CvsB_Disc = np.arange(disc_min,disc_max,(disc_max-disc_min)/ncuts)

Plot_2D_B = ROOT.TH2D("Plot_2D_B"," ;#Delta CvsDUSG;#Delta CvsB",ncuts,disc_min,disc_max,ncuts,disc_min,disc_max)
Plot_2D_C = ROOT.TH2D("Plot_2D_C"," ;#Delta CvsDUSG;#Delta CvsB",ncuts,disc_min,disc_max,ncuts,disc_min,disc_max)
Plot_2D_DUSG = ROOT.TH2D("Plot_2D_DUSG"," ;#Delta CvsDUSG;#Delta CvsB",ncuts,disc_min,disc_max,ncuts,disc_min,disc_max)

CvsDUSG_Disc_bin = []
CvsB_Disc_bin = []
for idx,i in enumerate(CvsDUSG_Disc):
	CvsDUSG_Disc_bin.insert(idx,Plot_2D_B.GetXaxis().FindBin(i))
	CvsB_Disc_bin.insert(idx,Plot_2D_B.GetXaxis().FindBin(i))


CvsDUSG_B = ROOT.TFile("CvsDUSG_B_tmp.root");
CvsDUSG_C = ROOT.TFile("CvsDUSG_C_tmp.root");
CvsDUSG_DUSG = ROOT.TFile("CvsDUSG_DUSG_tmp.root");
CvsB_B = ROOT.TFile("CvsB_B_tmp.root");
CvsB_C = ROOT.TFile("CvsB_C_tmp.root");
CvsB_DUSG = ROOT.TFile("CvsB_DUSG_tmp.root");

CvsDUSG_B_tree = CvsDUSG_B.Get("tree");
CvsDUSG_C_tree = CvsDUSG_C.Get("tree");
CvsDUSG_DUSG_tree = CvsDUSG_DUSG.Get("tree");
CvsB_B_tree = CvsB_B.Get("tree");
CvsB_C_tree = CvsB_C.Get("tree");
CvsB_DUSG_tree = CvsB_DUSG.Get("tree");





# FOR B
CvsDUSG_B_nen = CvsDUSG_B_tree.GetEntries();
CvsB_B_nen = CvsB_B_tree.GetEntries();
assert(CvsDUSG_B_nen == CvsB_B_nen)

for i in xrange(CvsDUSG_B_nen):
	if (i%args.pickEvery)!=0:
		continue
	CvsDUSG_B_tree.GetEntry(i);
	CvsB_B_tree.GetEntry(i);
	Plot_2D_B.Fill(CvsDUSG_B_tree.BDTG,CvsB_B_tree.BDTG)
	
Total_Integral_B = Plot_2D_B.Integral(0,ncuts,0,ncuts);
for idx,i in enumerate(CvsDUSG_Disc):
	for jdx,j in enumerate(CvsB_Disc):
		Eff_vs_Disc_2D_B.SetPoint(jdx+(ncuts*idx),i,j,Plot_2D_B.Integral(CvsDUSG_Disc_bin[idx],ncuts,CvsB_Disc_bin[jdx],ncuts) / Total_Integral_B)

# FOR C
CvsDUSG_C_nen = CvsDUSG_C_tree.GetEntries();
CvsB_C_nen = CvsB_C_tree.GetEntries();
assert(CvsDUSG_C_nen == CvsB_C_nen)

for i in xrange(CvsDUSG_C_nen):
	if (i%args.pickEvery)!=0:
		continue
	CvsDUSG_C_tree.GetEntry(i);
	CvsB_C_tree.GetEntry(i);
	Plot_2D_C.Fill(CvsDUSG_C_tree.BDTG,CvsB_C_tree.BDTG)
	
Total_Integral_C = Plot_2D_C.Integral(0,ncuts,0,ncuts);
for idx,i in enumerate(CvsDUSG_Disc):
	for jdx,j in enumerate(CvsB_Disc):
		Eff_vs_Disc_2D_C.SetPoint(jdx+(ncuts*idx),i,j,Plot_2D_C.Integral(CvsDUSG_Disc_bin[idx],ncuts,CvsB_Disc_bin[jdx],ncuts) / Total_Integral_C)
		
# FOR DUSG
CvsDUSG_DUSG_nen = CvsDUSG_DUSG_tree.GetEntries();
CvsB_DUSG_nen = CvsB_DUSG_tree.GetEntries();
assert(CvsDUSG_DUSG_nen == CvsB_DUSG_nen)

for i in xrange(CvsDUSG_DUSG_nen):
	if (i%args.pickEvery)!=0:
		continue
	CvsDUSG_DUSG_tree.GetEntry(i);
	CvsB_DUSG_tree.GetEntry(i);
	Plot_2D_DUSG.Fill(CvsDUSG_DUSG_tree.BDTG,CvsB_DUSG_tree.BDTG)
	
Total_Integral_DUSG = Plot_2D_DUSG.Integral(0,ncuts,0,ncuts);
for idx,i in enumerate(CvsDUSG_Disc):
	for jdx,j in enumerate(CvsB_Disc):
		Eff_vs_Disc_2D_DUSG.SetPoint(jdx+(ncuts*idx),i,j,Plot_2D_DUSG.Integral(CvsDUSG_Disc_bin[idx],ncuts,CvsB_Disc_bin[jdx],ncuts) / Total_Integral_DUSG)



## DRAW 2D DISCRIMINATOR DISTRIBUTIONS AND SCATTER PLOT

cc = ROOT.TCanvas("cc","cc",1100,700)
cc.Divide(2,2)
l = ROOT.TLegend(0.73,0.7,0.93,0.93)
l.SetFillColor(0)


Plot_2D_B.GetYaxis().SetTitleOffset(0.9)
Plot_2D_B.GetYaxis().SetTitleSize(0.065)
Plot_2D_B.GetYaxis().SetLabelSize(0.055)
Plot_2D_B.GetXaxis().SetTitleSize(0.065)
Plot_2D_B.GetXaxis().SetLabelSize(0.055)
Plot_2D_B.GetZaxis().SetLabelSize(0.055)
Plot_2D_C.GetYaxis().SetTitleOffset(0.9)
Plot_2D_C.GetYaxis().SetTitleSize(0.065)
Plot_2D_C.GetYaxis().SetLabelSize(0.055)
Plot_2D_C.GetXaxis().SetTitleSize(0.065)
Plot_2D_C.GetXaxis().SetLabelSize(0.055)
Plot_2D_C.GetZaxis().SetLabelSize(0.055)
Plot_2D_DUSG.GetYaxis().SetTitleOffset(0.9)
Plot_2D_DUSG.GetYaxis().SetTitleSize(0.065)
Plot_2D_DUSG.GetYaxis().SetLabelSize(0.055)
Plot_2D_DUSG.GetXaxis().SetTitleSize(0.065)
Plot_2D_DUSG.GetXaxis().SetLabelSize(0.055)
Plot_2D_DUSG.GetZaxis().SetLabelSize(0.055)

Plot_2D_B.SetMarkerColor(ROOT.kGreen)
Plot_2D_B.SetFillColor(ROOT.kGreen)
Plot_2D_B.SetMarkerStyle(6)
l.AddEntry(Plot_2D_B,"B","f")
cc.cd(4)
ROOT.gPad.SetMargin(0.13,0.07,0.13,0.07)
Plot_2D_B.Draw()	
cc.cd(1)
ROOT.gStyle.SetOptStat(0)
l_B = ROOT.TLegend(0.73,0.8,0.85,0.9)
l_B.AddEntry(Plot_2D_B,"B","p")
ROOT.gPad.SetMargin(0.13,0.12,0.13,0.07)
Plot_2D_B.Scale(1/Plot_2D_B.Integral())
Plot_2D_B.SetMinimum(0.00001)
Plot_2D_B.SetMaximum(0.2)
ROOT.gPad.SetLogz(1)
Plot_2D_B.Draw("COLZ")
l_B.Draw("same")

Plot_2D_C.SetMarkerColor(ROOT.kBlue)
Plot_2D_C.SetFillColor(ROOT.kBlue)
Plot_2D_C.SetMarkerStyle(6)
l.AddEntry(Plot_2D_C,"C","f")
cc.cd(4)
Plot_2D_C.Draw("same")	
cc.cd(2)
ROOT.gStyle.SetOptStat(0)
l_DUSG = ROOT.TLegend(0.73,0.8,0.85,0.9)
l_DUSG.AddEntry(Plot_2D_DUSG,"DUSG","p")
ROOT.gPad.SetMargin(0.13,0.12,0.13,0.07)
Plot_2D_DUSG.Scale(1/Plot_2D_DUSG.Integral())
Plot_2D_DUSG.SetMinimum(0.00001)
Plot_2D_DUSG.SetMaximum(0.2)
ROOT.gPad.SetLogz(1)
Plot_2D_DUSG.Draw("COLZ")
l_DUSG.Draw("same")

Plot_2D_DUSG.SetMarkerColor(ROOT.kRed)
Plot_2D_DUSG.SetFillColor(ROOT.kRed)
Plot_2D_DUSG.SetMarkerStyle(6)
l.AddEntry(Plot_2D_DUSG,"DUSG","f")
cc.cd(4)
Plot_2D_DUSG.Draw("same")	
cc.cd(3)
ROOT.gStyle.SetOptStat(0)
l_C = ROOT.TLegend(0.73,0.8,0.85,0.9)
l_C.AddEntry(Plot_2D_C,"C","p")
ROOT.gPad.SetMargin(0.13,0.12,0.13,0.07)
Plot_2D_C.Scale(1/Plot_2D_C.Integral())
Plot_2D_C.SetMinimum(0.00001)
Plot_2D_C.SetMaximum(0.2)
ROOT.gPad.SetLogz(1)
Plot_2D_C.Draw("COLZ")
l_C.Draw("same")

cc.cd(4)
l.Draw("same")	
cc.SaveAs(args.outdir+'/2D_BDTG_Plot.png')





#DRAW 2D EFFICIENCY CURVES

mg = ROOT.TMultiGraph()
mg.SetMinimum(1)
mg.SetMaximum(200)
ll = ROOT.TLegend(0.7,0.6,0.90,0.90)

Const_C_eff = [0.2,0.25,0.3,0.35,0.4,0.45,0.5]
Colors = [1,2,3,4,6,7,8]
Styles = [24,25,26,27,28,30,32]
npoints = Eff_vs_Disc_2D_C.GetN()
npoints_B = Eff_vs_Disc_2D_B.GetN()
npoints_DUSG = Eff_vs_Disc_2D_DUSG.GetN()
C_points = Eff_vs_Disc_2D_C.GetZ()
B_points = Eff_vs_Disc_2D_B.GetZ()
DUSG_points = Eff_vs_Disc_2D_DUSG.GetZ()
assert(npoints == npoints_B and npoints == npoints_DUSG)
graphs = []

for jdx,j in enumerate(Const_C_eff):
	graphs.insert(jdx, ROOT.TGraph())
	point_number = 0
	for idx in xrange(npoints-1): 
		if math.fabs(C_points[idx]-j)<0.002 and B_points[idx] > 0.001 and DUSG_points[idx] > 0.001 and B_points[idx] < 1 and DUSG_points[idx] < 1:
			graphs[jdx].SetPoint(point_number,1./B_points[idx],1./DUSG_points[idx])
			point_number+=1
	
	graphs[jdx].SetMarkerColor(Colors[jdx])
	graphs[jdx].SetMarkerStyle(Styles[jdx])
	graphs[jdx].SetLineColor(Colors[jdx])
	graphs[jdx].SetLineWidth(2)
	ll.AddEntry(graphs[jdx],"#epsilon^{C} = " + str(j),"p")
	mg.Add(graphs[jdx])

ROOT.gStyle.SetOptStat(0)
c = ROOT.TCanvas("c","c",800,700)
c.cd()
ROOT.gPad.SetLogx(1)
ROOT.gPad.SetLogy(1)
ROOT.gPad.SetGrid(1,1)
mg.Draw("ALP")
mg.GetYaxis().SetTitle("Light Rejection (1/#epsilon^{light})")
mg.GetXaxis().SetTitle("B Rejection (1/#epsilon^{B})")
mg.GetXaxis().SetLimits(1.,40.)
ROOT.gPad.Modified()
ll.Draw("same")

c.SaveAs(args.outdir+'/Eff_BvsDUSG_Cte_C.png')

os.system('rm ' + os.getcwd() + '/*CvsDUSG_*_tmp.root')
os.system('rm ' + os.getcwd() + '/*CvsB_*_tmp.root')
