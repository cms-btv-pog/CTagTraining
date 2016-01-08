##!/bin/bash

maindirec=/pnfs/iihe/cms/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/

dirs_to_merge=(TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/crab_VariableExtraction75X_Spring15Sample_TTJets_CvsL/160106_161345/0000/)

homedirec=/user/smoortga/CTag/SampleProduction/76X/NewVariables/MergedSamples

CAT=(CombinedSVRecoVertexNoSoftLepton CombinedSVPseudoVertexNoSoftLepton CombinedSVNoVertexNoSoftLepton CombinedSVRecoVertexSoftElectron CombinedSVPseudoVertexSoftElectron CombinedSVNoVertexSoftElectron CombinedSVRecoVertexSoftMuon CombinedSVPseudoVertexSoftMuon CombinedSVNoVertexSoftMuon)

FLAV=(B C D U S G)
#FLAV=(D U S G)

mkdir $homedirec/TTJets_trial2
cd $homedirec/TTJets_trial2

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
#				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 20 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/12 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Dfiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_U*); do 
				echo "at file number $countfiles" 
				((countfiles++))
#				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 20 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/12 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Ufiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_S*); do 
				echo "at file number $countfiles" 
				((countfiles++))
#				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 20 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/12 files is used!
				printf "dcap://maite.iihe.ac.be/$j " >> ${k}Sfiles.txt
			done
			let countfiles=0
			for j in $( ls $maindirec/$l/${k}_G*); do 
				echo "at file number $countfiles" 
				((countfiles++))
#				if [ $countfiles -ne 1 ] ; then if [ $countfiles -eq 20 ] ; then countfiles=0 ; fi ; continue ; fi #this makes sure that only 1/12 files is used!
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

