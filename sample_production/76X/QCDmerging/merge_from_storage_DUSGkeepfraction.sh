##!/bin/bash

maindirec=/pnfs/iihe/cms/store/user/smoortga/BTagServiceWork/BtagExtractor_76X/CSVSLctag_trial2_CvsL/

dirs_to_merge=(QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_15to30_CvsL/151221_141301/0000/)
# QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_30to50_CvsL/150819_200359/0000/ QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_50to80_CvsL/150819_200524/0000/ QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_80to120_CvsL/150819_200610/0000/ IgnoreLocality_QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_120to170_CvsL_IgnoreLocality/150820_162152/0000/ QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_170to300_CvsL/150819_200734/0000/ resub1_QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_300to470_CvsL_resub1/150821_003203/0000/ QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_470to600_CvsL/150819_200904/0000/ QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3_AODSIM/QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_600to800_CvsL/150819_200953/0000/ QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_800to1000_CvsL/150819_201033/0000/ QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_1000to1400_CvsL/150819_201118/0000/ QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_1400to1800_CvsL/150819_201202/0000/ QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_1800to2400_CvsL/150819_201248/0000/ QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM/QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8/crab_VariableExtraction75X_Spring15Sample_QCD_Pt_2400to3200_CvsL/150819_201535/0000/)

homedirec=/user/smoortga/CTag/SampleProduction/76X/NewVariables/MergedSamples/

#CAT=(CombinedSVNoVertexNoSoftLepton)
CAT=(CombinedSVRecoVertexNoSoftLepton)

FLAV=(D U S G)
#FLAV=(D U S G)

mkdir $homedirec/QCD_training_RecoVertexNoSoftLeptonDUSGkeepfraction
cd $homedirec/QCD_training_RecoVertexNoSoftLeptonDUSGkeepfraction

for l in ${dirs_to_merge[@]} ;
do
	for k in ${CAT[@]} ;
	do
		for j in $( ls $maindirec/$l/${k}_B*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Bfiles.txt; done
		for j in $( ls $maindirec/$l/${k}_C*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Cfiles.txt; done
		if [ $k=="CombinedSVNoVertexNoSoftLepton" ]
		then
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_D*); do
				echo "at file number $countfiles" 
				((countfiles++))
				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 10 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/10 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Dfiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_U*); do 
				echo "at file number $countfiles" 
				((countfiles++))
				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 10 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/10 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Ufiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_S*); do 
				echo "at file number $countfiles" 
				((countfiles++))
				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 10 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/10 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Sfiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_G*); do 
				echo "at file number $countfiles" 
				((countfiles++))
				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 10 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/10 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Gfiles.txt
			done
		else
			for j in $( ls $maindirec/$l/${k}_D*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Dfiles.txt; done
			for j in $( ls $maindirec/$l/${k}_U*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Ufiles.txt; done
			for j in $( ls $maindirec/$l/${k}_S*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Sfiles.txt; done
			for j in $( ls $maindirec/$l/${k}_G*); do printf "dcap://maite.iihe.ac.be/$j " >> ${k}Gfiles.txt; done			
		fi
	done
done	

for k in ${CAT[@]} ;
do
	for i in ${FLAV[@]} ;
	do
#		echo cat ${k}${i}files.txt
		rootfiles=`cat ${k}${i}files.txt`
		hadd tmp.root $rootfiles
		mv tmp.root ${k}_${i}.root
	done
done

