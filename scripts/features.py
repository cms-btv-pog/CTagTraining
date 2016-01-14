'''
central place to list the features to be used in training
'''

general = [
  #"flavour",
  #"vertexCategory",
  #"vertexLeptonCategory",
  #"jetPt",
  #"trackJetPt",
  #"jetEta",
  "trackSip2dSig_0", "trackSip2dSig_1",#"trackSip2dSig_2",
  "trackSip3dSig_0", "trackSip3dSig_1",#"trackSip3dSig_2",
  #"trackSip2dVal_0", "trackSip2dVal_1", "trackSip2dVal_2",
  #"trackSip3dVal_0", "trackSip3dVal_1", "trackSip3dVal_2",
  "trackPtRel_0", "trackPtRel_1",# "trackPtRel_2",
  "trackPPar_0", "trackPPar_1",# "trackPPar_2",
  "trackEtaRel_0","trackEtaRel_1",# "trackEtaRel_2",
  "trackDeltaR_0", "trackDeltaR_1",# "trackDeltaR_2",
  "trackPtRatio_0", "trackPtRatio_1",# "trackPtRatio_2",
  "trackPParRatio_0", "trackPParRatio_1",# "trackPParRatio_2",
  "trackJetDist_0","trackJetDist_1",# "trackJetDist_2",
  "trackDecayLenVal_0", "trackDecayLenVal_1",# "trackDecayLenVal_2",
  "jetNSecondaryVertices",
  "jetNTracks",
  "trackSumJetEtRatio",
  "trackSumJetDeltaR",
]

vertex = [
  "vertexMass_0",
  "vertexEnergyRatio_0",
  "trackSip2dSigAboveCharm_0",
  "trackSip3dSigAboveCharm_0",
  "flightDistance2dSig_0",
  "flightDistance3dSig_0",
  #"flightDistance2dVal_0",
  #"flightDistance3dVal_0",
  "vertexJetDeltaR_0",
  "vertexNTracks_0",
  #"trackSip2dValAboveCharm_0",
  #"trackSip3dValAboveCharm_0",
  #"vertexFitProb_0",
  #"chargedHadronEnergyFraction",
  #"neutralHadronEnergyFraction",
  #"photonEnergyFraction",
  #"electronEnergyFraction",
  #"muonEnergyFraction",
  "massVertexEnergyFraction_0",
  "vertexBoostOverSqrtJetPt_0",
]

leptons = [
  "leptonPtRel_0","leptonPtRel_1",#"leptonPtRel_2",
  "leptonSip3d_0","leptonSip3d_1",#"leptonSip3d_2",
  "leptonDeltaR_0","leptonDeltaR_1",#"leptonDeltaR_2",
  "leptonRatioRel_0","leptonRatioRel_1",#"leptonRatioRel_2",
  "leptonEtaRel_0","leptonEtaRel_1",#"leptonEtaRel_2",
  "leptonRatio_0","leptonRatio_1",#"leptonRatio_2",
  ]
