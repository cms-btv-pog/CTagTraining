import FWCore.ParameterSet.Config as cms
from pdb import set_trace
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')

options.register(
   'isTTBar', False,
   VarParsing.multiplicity.singleton,
   VarParsing.varType.bool,
   "Run this on a TTBar sample"
)
options.parseArguments()

process = cms.Process("CSVTrainer")

process.load("FWCore.MessageLogger.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100

process.load("RecoBTau.JetTagComputer.jetTagRecord_cfi")

# load the full reconstruction configuration, to make sure we're getting all needed dependencies
process.load("Configuration.StandardSequences.MagneticField_cff")
process.load("Configuration.Geometry.GeometryIdeal_cff") #new one
process.load("Configuration.StandardSequences.FrontierConditions_GlobalTag_cff")

process.options   = cms.untracked.PSet(
    wantSummary = cms.untracked.bool(False)
)
process.maxEvents = cms.untracked.PSet(
    input = cms.untracked.int32(1000)
)

process.GlobalTag.globaltag = cms.string("MCRUN2_74_V9D")

from PhysicsTools.PatAlgos.tools.helpers import massSearchReplaceAnyInputTag, loadWithPostfix, applyPostfix
process.load("CommonTools.ParticleFlow.PFBRECO_cff")
process.pfNoMuonJMEPFBRECO.enable = options.isTTBar
process.pfNoElectronJMEPFBRECO.enable = options.isTTBar
del process.loadRecoTauTagMVAsFromPrepDB

# for the PU ID
# Select GenJets with Pt>8 GeV
process.ak4GenJetsMCPUJetID = cms.EDFilter("GenJetSelector",
    src    = cms.InputTag("ak4GenJets"), #, '', 'CSVTrainer'),
    cut    = cms.string('pt > 8.0'),
    filter = cms.bool(False)             # in case no GenJets pass the selection, do not filter events, just produce an empty GenJet collection
)

# Match selected GenJets to RecoJets
process.ak4PFJetsGenJetMatchMCPUJetID = cms.EDProducer("GenJetMatcher",  # cut on deltaR; pick best by deltaR
    src                   = cms.InputTag("pfJetsPFBRECO", '', 'CSVTrainer'),           # RECO jets (any View<Jet> is ok)
    matched               = cms.InputTag("ak4GenJetsMCPUJetID"), # GEN jets  (must be GenJetCollection)
    mcPdgId               = cms.vint32(),                        # N/A
    mcStatus              = cms.vint32(),                        # N/A
    checkCharge           = cms.bool(False),                     # N/A
    maxDeltaR             = cms.double(0.25),                    # Minimum deltaR for the match
    resolveAmbiguities    = cms.bool(True),                      # Forbid two RECO objects to match to the same GEN object
    resolveByMatchQuality = cms.bool(False),
)


#input for softLeptonTagInfos
process.load('RecoBTag.SoftLepton.softPFElectronTagInfos_cfi')# import *
process.softPFElectronsTagInfos.primaryVertex = 'offlinePrimaryVertices' #cms.InputTag('goodOfflinePrimaryVertices')
process.softPFElectronsTagInfos.jets = cms.InputTag("pfJetsPFBRECO", '', 'CSVTrainer')
process.softPFElectronsTagInfos.useMCpromptElectronFilter = cms.bool(True)
process.load('RecoBTag.SoftLepton.softPFMuonTagInfos_cfi')# import *
process.softPFMuonsTagInfos.primaryVertex = 'offlinePrimaryVertices' #cms.InputTag('goodOfflinePrimaryVertices')
process.softPFMuonsTagInfos.jets = cms.InputTag("pfJetsPFBRECO", '', 'CSVTrainer')
process.softPFMuonsTagInfos.useMCpromptMuonFilter = cms.bool(True)

#process.combinedSecondaryVertexSoftLepton.trackMultiplicityMin = cms.uint32(2)

#load custom tag info
process.load('RecoBTag.CTagging.RecoCTagging_cff') # import pfInclusiveSecondaryVertexFinderCvsLTagInfos
process.load('RecoBTag.ImpactParameter.pfImpactParameterTagInfos_cfi')
process.customTagInfos = cms.Sequence(
    ( process.inclusiveCandidateVertexingCvsL *
      process.pfInclusiveSecondaryVertexFinderCvsLTagInfos
    )
)

#for Inclusive Vertex Finder
process.load('RecoVertex.AdaptiveVertexFinder.inclusiveVertexing_cff')
process.load('RecoBTag.SecondaryVertex.inclusiveSecondaryVertexFinderTagInfos_cfi')
process.load('RecoBTag.SecondaryVertex.candidateCombinedSecondaryVertexSoftLeptonComputer_cfi')
process.inclusiveVertexFinder.primaryVertices = 'offlinePrimaryVertices' #cms.InputTag("goodOfflinePrimaryVertices")
process.trackVertexArbitrator.primaryVertices = 'offlinePrimaryVertices' #cms.InputTag("goodOfflinePrimaryVertices")

#for the flavour matching
from PhysicsTools.JetMCAlgos.HadronAndPartonSelector_cfi import selectedHadronsAndPartons
process.selectedHadronsAndPartons = selectedHadronsAndPartons.clone()

from PhysicsTools.JetMCAlgos.AK4PFJetsMCFlavourInfos_cfi import ak4JetFlavourInfos
process.jetFlavourInfosAK4PFJets = ak4JetFlavourInfos.clone()
process.jetFlavourInfosAK4PFJets.jets = cms.InputTag("pfJetsPFBRECO", '', 'CSVTrainer')
process.jetFlavourInfosAK4PFJets.hadronFlavourHasPriority = True

process.source = cms.Source(
   "PoolSource",
   fileNames = cms.untracked.vstring(
#      'file:/uscms_data/d3/verzetti/RelValTTbar_13_sample.root',
      '/store/relval/CMSSW_7_6_0/RelValTTbar_13_HS/GEN-SIM-RECO/PU25ns_76X_mcRun2_asymptotic_v11_TSGstudy-v1/00000/0489299E-7B89-E511-9947-0025905B858E.root'
			#'root://cms-xrd-global.cern.ch//store/mc/RunIISpring15DR74/QCD_Pt_30to50_TuneCUETP8M1_13TeV_pythia8/AODSIM/Asympt25ns_MCRUN2_74_V9-v2/00000/022C94E2-5F0F-E511-B8BA-7845C4FC3C98.root'
      ),
   ## eventsToProcess = cms.untracked.VEventRange([
   ##       '1:33:3209',
   ##       '1:33:3294',
   ##       '1:36:3512'
   ##       ])
)


process.combinedSVMVATrainer = cms.EDAnalyzer("JetTagMVAExtractor",
	variables = cms.untracked.VPSet(
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexNoSoftLepton"), variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexNoSoftLepton"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexNoSoftLepton"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)), # no trackEtaRel!!!???!!!
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexSoftMuon"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)), # no trackEtaRel!!!???!!!,"vertexNTracks"
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVRecoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","flightDistance2dSig","flightDistance3dSig","flightDistance2dVal","flightDistance3dVal","trackSumJetEtRatio","jetNSecondaryVertices","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","vertexFitProb","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVPseudoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackEtaRel","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","vertexMass","correctedSVMass","vertexNTracks","vertexEnergyRatio","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","vertexJetDeltaR","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","massVertexEnergyFraction","vertexBoostOverSqrtJetPt","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)),
		cms.untracked.PSet( label = cms.untracked.string("CombinedSVNoVertexSoftElectron"),  variables=cms.untracked.vstring(
"jetPt","jetEta","trackJetPt","vertexCategory","vertexLeptonCategory","trackSip2dSig","trackSip3dSig","trackSip2dVal","trackSip3dVal","trackMomentum","trackEta","trackPtRel","trackPPar","trackDeltaR","trackPtRatio","trackPParRatio","trackJetDist","trackDecayLenVal","trackSip2dSigAboveCharm","trackSip3dSigAboveCharm","trackSumJetEtRatio","trackSumJetDeltaR","jetNTracks","trackSip2dValAboveCharm","trackSip3dValAboveCharm","leptonPtRel","leptonSip3d","leptonDeltaR","leptonRatioRel","leptonEtaRel","leptonRatio","chargedHadronEnergyFraction","neutralHadronEnergyFraction","photonEnergyFraction","electronEnergyFraction","muonEnergyFraction","chargedHadronMultiplicity","neutralHadronMultiplicity","photonMultiplicity","electronMultiplicity","muonMultiplicity","hadronMultiplicity","hadronPhotonMultiplicity","totalMultiplicity","relConcentricEnergyAroundJetAxis","jetPtD"
)) # no trackEtaRel!!!???!!!

	),
  jetTagComputer = cms.string('candidateCombinedSecondaryVertexSoftLeptonComputer'),
  ipTagInfos = cms.InputTag("pfImpactParameterTagInfos", '', 'CSVTrainer'),
	svTagInfos =cms.InputTag("pfInclusiveSecondaryVertexFinderCvsLTagInfos", '', 'CSVTrainer'),
	muonTagInfos =cms.InputTag("softPFMuonsTagInfos", '', 'CSVTrainer'),
	elecTagInfos =cms.InputTag("softPFElectronsTagInfos", '', 'CSVTrainer'),
	
	
	minimumTransverseMomentum = cms.double(15.0),
	maximumTransverseMomentum = cms.double(9999999.),
	useCategories = cms.bool(True),
  calibrationRecords = cms.vstring(
		'CombinedSVRecoVertexNoSoftLepton', 
		'CombinedSVPseudoVertexNoSoftLepton', 
		'CombinedSVNoVertexNoSoftLepton',
		'CombinedSVRecoVertexSoftMuon', 
		'CombinedSVPseudoVertexSoftMuon', 
		'CombinedSVNoVertexSoftMuon',
		'CombinedSVRecoVertexSoftElectron', 
		'CombinedSVPseudoVertexSoftElectron', 
		'CombinedSVNoVertexSoftElectron'),
	categoryVariableName = cms.string('vertexLeptonCategory'), # vertexCategory = Reco,Pseudo,No
	maximumPseudoRapidity = cms.double(2.4),
	signalFlavours = cms.vint32(5, 7),
	minimumPseudoRapidity = cms.double(0.0),
	jetFlavourMatching = cms.InputTag("jetFlavourInfosAK4PFJets", '', 'CSVTrainer'),
	matchedGenJets = cms.InputTag("ak4PFJetsGenJetMatchMCPUJetID", '', 'CSVTrainer'),
	ignoreFlavours = cms.vint32(0) #, 11, 13, -11, -13)
)

process.seq = cms.Sequence(
   process.PFBRECO *
   process.ak4GenJetsMCPUJetID *
   process.ak4PFJetsGenJetMatchMCPUJetID *
   process.inclusiveVertexing * 
   process.pfImpactParameterTagInfos * 
   process.softPFMuonsTagInfos *
   process.softPFElectronsTagInfos *
   process.selectedHadronsAndPartons *
   process.jetFlavourInfosAK4PFJets *
   process.customTagInfos *
   process.combinedSVMVATrainer 
   )

massSearchReplaceAnyInputTag(
   process.seq,
   cms.InputTag("ak4PFJetsCHS"),
   cms.InputTag("pfJetsPFBRECO", '', 'CSVTrainer'),
   True
)

process.p = cms.Path(process.seq)

