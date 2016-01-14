#from WMCore.Configuration import Configuration
#config = Configuration()
from CRABClient.UserUtilities import config
config = config()

config.section_("General")
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_15to30_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_30to50_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_50to80_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_80to120_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_120to170_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_170to300_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_300to470_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_470to600_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_600to800_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_800to1000_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_1000to1400_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_1400to1800_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_1800to2400_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_2400to3200_CvsL'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_3200toInf_CvsL'
config.General.requestName = 'VariableExtraction75X_Spring15Sample_TTJets_CvsL'

#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_300to470_CvsL_resub1'
#config.General.requestName = 'VariableExtraction75X_Spring15Sample_QCD_Pt_470to600_CvsL_resub1'

#config.General.workArea = 'crab_projects'
#config.General.workArea = 'crab_projects_CvsL' 
##trial2 = with 'hacked' JetTagMVAExtractor such that empty files are produced instead of not produced which gives problems with crab if you ask them to stage out
config.General.workArea = 'crab_projects_trial2TTJets_CvsL' 

#config.General.transferOutputs=True
config.General.transferLogs=True

config.section_("JobType")

#cfg Command Line parameters
#config.JobType.pyCfgParams = ['isTTBar=True']

config.JobType.pluginName = 'Analysis'
config.JobType.psetName = 'varextractor_ctag_CvsL_cfg.py'
#config.JobType.inputFiles = 'MVAJetTags.db'
config.JobType.outputFiles = ['CombinedSVRecoVertexNoSoftLepton_B.root','CombinedSVRecoVertexNoSoftLepton_C.root','CombinedSVRecoVertexNoSoftLepton_D.root','CombinedSVRecoVertexNoSoftLepton_U.root','CombinedSVRecoVertexNoSoftLepton_S.root','CombinedSVRecoVertexNoSoftLepton_G.root','CombinedSVPseudoVertexNoSoftLepton_B.root','CombinedSVPseudoVertexNoSoftLepton_C.root','CombinedSVPseudoVertexNoSoftLepton_D.root','CombinedSVPseudoVertexNoSoftLepton_U.root','CombinedSVPseudoVertexNoSoftLepton_S.root','CombinedSVPseudoVertexNoSoftLepton_G.root','CombinedSVNoVertexNoSoftLepton_B.root','CombinedSVNoVertexNoSoftLepton_C.root','CombinedSVNoVertexNoSoftLepton_D.root','CombinedSVNoVertexNoSoftLepton_U.root','CombinedSVNoVertexNoSoftLepton_S.root','CombinedSVNoVertexNoSoftLepton_G.root','CombinedSVRecoVertexSoftMuon_B.root','CombinedSVRecoVertexSoftMuon_C.root','CombinedSVRecoVertexSoftMuon_D.root','CombinedSVRecoVertexSoftMuon_U.root','CombinedSVRecoVertexSoftMuon_S.root','CombinedSVRecoVertexSoftMuon_G.root','CombinedSVPseudoVertexSoftMuon_B.root','CombinedSVPseudoVertexSoftMuon_C.root','CombinedSVPseudoVertexSoftMuon_D.root','CombinedSVPseudoVertexSoftMuon_U.root','CombinedSVPseudoVertexSoftMuon_S.root','CombinedSVPseudoVertexSoftMuon_G.root','CombinedSVNoVertexSoftMuon_B.root','CombinedSVNoVertexSoftMuon_C.root','CombinedSVNoVertexSoftMuon_D.root','CombinedSVNoVertexSoftMuon_U.root','CombinedSVNoVertexSoftMuon_S.root','CombinedSVNoVertexSoftMuon_G.root','CombinedSVRecoVertexSoftElectron_B.root','CombinedSVRecoVertexSoftElectron_C.root','CombinedSVRecoVertexSoftElectron_D.root','CombinedSVRecoVertexSoftElectron_U.root','CombinedSVRecoVertexSoftElectron_S.root','CombinedSVRecoVertexSoftElectron_G.root','CombinedSVPseudoVertexSoftElectron_B.root','CombinedSVPseudoVertexSoftElectron_C.root','CombinedSVPseudoVertexSoftElectron_D.root','CombinedSVPseudoVertexSoftElectron_U.root','CombinedSVPseudoVertexSoftElectron_S.root','CombinedSVPseudoVertexSoftElectron_G.root','CombinedSVNoVertexSoftElectron_B.root','CombinedSVNoVertexSoftElectron_C.root','CombinedSVNoVertexSoftElectron_D.root','CombinedSVNoVertexSoftElectron_U.root','CombinedSVNoVertexSoftElectron_S.root','CombinedSVNoVertexSoftElectron_G.root']
#config.JobType.allowUndistributedCMSSW = True

config.section_("Data")
#config.Data.inputDataset = '/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
#config.Data.inputDataset = '/QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1/AODSIM'
config.Data.inputDataset = '/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2/AODSIM'


config.Data.inputDBS = 'global'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_15to30_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_50to80_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_80to120_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_120to170_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_170to300_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_600to800_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v3_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_800to1000_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_1000to1400_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_1400to1800_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_1800to2400_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_2400to3200_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/QCD_Pt_3200toInf_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
config.Data.outLFNDirBase = '/store/user/smoortga/BTagServiceWork/BTagExtractor_76X/CSVSLctag_trial2_CvsL/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'

#config.Data.outLFNDirBase = '/store/user/gvonsem/BTagServiceWork/BtagExtractor_75X/CSVSLctag_trial2_CvsL/resub1_QCD_Pt_300to470_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v1_AODSIM'
#config.Data.outLFNDirBase = '/store/user/gvonsem/BTagServiceWork/BtagExtractor_75X/CSVSLctag_trial2_CvsL/resub1_QCD_Pt_470to600_TuneCUETP8M1_13TeV_pythia8_RunIISpring15DR74-Asympt25ns_MCRUN2_74_V9-v2_AODSIM'


config.Data.splitting = 'FileBased'
#config.Data.unitsPerJob = 10
config.Data.unitsPerJob = 4
config.Data.totalUnits = 100
config.Data.publication = False
#config.Data.Data.publishDBS = 'phys03'
#config.Data.publishDataName = 'TEST'
#config.Data.ignoreLocality = True #activate this line if you want to run remotely (i.e xroot)

config.section_("Site")
config.Site.storageSite = 'T2_BE_IIHE' # to be adapted according to your network  

config.section_("User") # to be adapted according to your network
config.User.voGroup = 'becms' # to be adapted according to your network
