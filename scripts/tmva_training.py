import ROOT
import os
import multiprocessing
import array



# LR training variables
training_vars_float = [
  #"flavour",
  #"vertexCategory",
  #"vertexLeptonCategory",
  #"jetPt",
  #"trackJetPt",
  #"jetEta",
  "trackSip2dSig_0", "trackSip2dSig_1", "trackSip2dSig_2",
  "trackSip3dSig_0", "trackSip3dSig_1", "trackSip3dSig_2",
  "trackSip2dVal_0", "trackSip2dVal_1", "trackSip2dVal_2",
  "trackSip3dVal_0", "trackSip3dVal_1", "trackSip3dVal_2",
  "trackPtRel_0", "trackPtRel_1", "trackPtRel_2",
  "trackPPar_0", "trackPPar_1", "trackPPar_2",
  "trackEtaRel_0", "trackEtaRel_1", "trackEtaRel_2",
  "trackDeltaR_0", "trackDeltaR_1", "trackDeltaR_2",
  "trackPtRatio_0", "trackPtRatio_1", "trackPtRatio_2",
  "trackPParRatio_0", "trackPParRatio_1", "trackPParRatio_2",
  "trackJetDist_0","trackJetDist_1","trackJetDist_2",
  "trackDecayLenVal_0", "trackDecayLenVal_1", "trackDecayLenVal_2",
  "vertexMass_0",
  "vertexEnergyRatio_0",
  "trackSip2dSigAboveCharm_0",
  "trackSip3dSigAboveCharm_0",
  "flightDistance2dSig_0",
  "flightDistance3dSig_0",
  "flightDistance2dVal_0",
  "flightDistance3dVal_0",
  "trackSumJetEtRatio",
  "vertexJetDeltaR_0",
  "trackSumJetDeltaR",
  "trackSip2dValAboveCharm_0",
  "trackSip3dValAboveCharm_0",
  "vertexFitProb_0",
  #"chargedHadronEnergyFraction",
  #"neutralHadronEnergyFraction",
  #"photonEnergyFraction",
  #"electronEnergyFraction",
  #"muonEnergyFraction",
  "massVertexEnergyFraction_0",
  "vertexBoostOverSqrtJetPt_0",
  "leptonPtRel_0","leptonPtRel_1","leptonPtRel_2",
  "leptonSip3d_0","leptonSip3d_1","leptonSip3d_2",
  "leptonDeltaR_0","leptonDeltaR_1","leptonDeltaR_2",
  "leptonRatioRel_0","leptonRatioRel_1","leptonRatioRel_2",
  "leptonEtaRel_0","leptonEtaRel_1","leptonEtaRel_2",
  "leptonRatio_0","leptonRatio_1","leptonRatio_2",
  "vertexNTracks_0",
  "jetNSecondaryVertices",
  "jetNTracks",
  ]

training_vars_int = [
  #"vertexNTracks_0",
  #"jetNSecondaryVertices",
  #"jetNTracks",
  #"chargedHadronMultiplicity",
  #"neutralHadronMultiplicity",
  #"photonMultiplicity",
  #"electronMultiplicity",
  #"muonMultiplicity",
  #"hadronMultiplicity",
  #"hadronPhotonMultiplicity",
  #"totalMultiplicity",
  ]



def train(bdtoptions):
  
  TMVA_tools = ROOT.TMVA.Tools.Instance()

  tree = ROOT.TChain('tree')

 
  files = [
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVNoVertex_C.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVPseudoVertex_C.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVRecoVertex_C.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVNoVertex_B.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVPseudoVertex_B.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVRecoVertex_B.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVNoVertex_DUSG.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVPseudoVertex_DUSG.root",
    "/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1_WithNewWeights/QCD/skimmed_20k_eachptetabin_CombinedSVRecoVertex_DUSG.root"
    ]
  
  for f in files:
      print 'Opening file %s' %f
      tree.Add('%s' %f)
  
  signal_selection = 'flavour==4' # c
  background_selection = 'flavour==5' # b

  num_pass = tree.GetEntries(signal_selection)
  num_fail = tree.GetEntries(background_selection)

  print 'N events signal', num_pass
  print 'N events background', num_fail
  outFile = ROOT.TFile('TMVA_classification.root', 'RECREATE')

  factory = ROOT.TMVA.Factory(
                               "TMVAClassification", 
                               outFile, 
                               "!V:!Silent:Color:DrawProgressBar:Transformations=I"
                             ) 

  for var in training_vars_float:
    factory.AddVariable(var, 'F') # add float variable
  for var in training_vars_int:
    factory.AddVariable(var, 'I') # add integer variable

  factory.SetWeightExpression('weight')

  factory.AddSignalTree(tree, 1.)
  factory.AddBackgroundTree(tree, 1.)

  # import pdb; pdb.set_trace()

  factory.PrepareTrainingAndTestTree( ROOT.TCut(signal_selection), ROOT.TCut(background_selection),
                                      "nTrain_Signal=0:nTest_Background=0:SplitMode=Random:NormMode=NumEvents:!V" )

  
  factory.BookMethod( ROOT.TMVA.Types.kBDT,
                      "BDTG",
                      # "!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.05:UseBaggedGrad:GradBaggingFraction=0.9:SeparationType=GiniIndex:nCuts=500:NNodesMax=5"
                      ":".join(bdtoptions)
                    )

  factory.TrainAllMethods()

  # factory.OptimizeAllMethods()

  factory.TestAllMethods()

  factory.EvaluateAllMethods()

  outFile.Close()

##   ROOT.gROOT.LoadMacro('$ROOTSYS/tmva/test/TMVAGui.C')
##   ROOT.TMVAGui('TMVA_classification.root')
##   raw_input("Press Enter to continue...")


def trainMultiClass():

  classes = [
    ('flavour==5', 'B'),
    ('flavour==4', 'C'),
    ('flavour!=5 && flavour!=4', 'DUSG')
  ]

  for cl in classes:
    print 'N events', cl[1], tree.GetEntries(cl[0])

  outFile = ROOT.TFile('TMVA_multiclass.root', 'RECREATE')

  factory = ROOT.TMVA.Factory(
        "TMVAClassification", 
        outFile, 
        "!V:!Silent:Color:DrawProgressBar:Transformations=I:AnalysisType=Multiclass" ) 

  for var in training_vars_float:
    factory.AddVariable(var, 'F') # add float variable
  for var in training_vars_int:
    factory.AddVariable(var, 'I') # add integer variable

  # factory.SetWeightExpression('')

  for cl in classes:
    factory.AddTree(tree, cl[1], 1., ROOT.TCut(cl[0]))
  # factory.AddSignalTree(tree, 1.)
  # factory.AddBackgroundTree(tree, 1.)

  # import pdb; pdb.set_trace()

  factory.PrepareTrainingAndTestTree( ROOT.TCut(''), ROOT.TCut(''),  "SplitMode=Random:NormMode=NumEvents:!V")

  factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDTG","!H:!V:NTrees=1000:BoostType=Grad:Shrinkage=0.05:UseBaggedGrad:GradBaggingFraction=0.9:SeparationType=GiniIndex:nCuts=500:NNodesMax=5" )

  # factory.BookMethod(ROOT.TMVA.Types.kBDT, "BDT_ADA", "!H:!V:NTrees=400:BoostType=AdaBoost:SeparationType=GiniIndex:nCuts=50:AdaBoostBeta=0.2:MaxDepth=2:MinNodeSize=6")

  factory.TrainAllMethods()

  # factory.OptimizeAllMethods()

  factory.TestAllMethods()

  factory.EvaluateAllMethods()

  outFile.Close()

 #ROOT.gROOT.LoadMacro('$ROOTSYS/tmva/test/TMVAMultiClassGui.C')
 #ROOT.TMVAMultiClassGui('TMVA_multiclass.root')
 #raw_input("Press Enter to continue...")



def read(inDirName, inFileName):
  
  print "Reading", inFileName
  
  TMVA_tools = ROOT.TMVA.Tools.Instance()

  tree = ROOT.TChain('tree')

  tree.Add('%s/%s' %(inDirName, inFileName))

  reader = ROOT.TMVA.Reader('TMVAClassification_BDTG')

  varDict = {}
  for var in training_vars_float:
    varDict[var] = array.array('f',[0])
    reader.AddVariable(var, varDict[var])
  for var in training_vars_int:
    varDict[var] = array.array('f',[0])
    reader.AddVariable(var, varDict[var])


  reader.BookMVA("BDTG","weights/TMVAClassification_BDTG.weights.xml")

  bdtOuts = []
  flavours = []
  categories = []
  jetPts = []
  jetEtas = []

  for jentry in xrange(tree.GetEntries()):

    ientry = tree.LoadTree(jentry)
    nb = tree.GetEntry(jentry)

    for var in varDict:
      varDict[var][0] = getattr(tree, var)

    bdtOutput = reader.EvaluateMVA("BDTG")
    flavour = tree.flavour
    bdtOuts.append(bdtOutput)
    flavours.append(flavour)
    categories.append(tree.vertexCategory)
    jetPts.append(tree.jetPt)
    jetEtas.append(tree.jetEta)

    if jentry%10000 == 0:
      print jentry, bdtOutput, flavour

  writeSmallTree = True

  if writeSmallTree:
    print "Writing small tree"

    BDTG = array.array('f',[0])
    flav = array.array('f',[0])
    cat = array.array('f',[0])
    jetPt = array.array('f',[0])
    jetEta = array.array('f',[0])

    fout = ROOT.TFile('trainPlusBDTG_%s.root'%(inFileName.replace(".root","")), 'RECREATE')
    outTree = ROOT.TTree( 'tree', 'b-tagging training tree' )
    outTree.Branch('BDTG', BDTG, 'BDTG/F')
    outTree.Branch('flavour', flav, 'flavour/F')
    outTree.Branch('vertexCategory', cat, 'vertexCategory/F')
    outTree.Branch('jetPt', jetPt, 'jetPt/F')
    outTree.Branch('jetEta', jetEta, 'jetEta/F')


    for i in range(len((bdtOuts))):
      BDTG[0] = bdtOuts[i]
      flav[0] = flavours[i]
      cat[0] = categories[i]
      jetPt[0] = jetPts[i]
      jetEta[0] = jetEtas[i]
      if i%10000==0:
        print i, bdtOuts[i], flavours[i]
      outTree.Fill()
      # treeout.Write()
    fout.Write()
    fout.Close()
  print "done", inFileName

def readParallel():

  print "start readParallel()"
  ROOT.gROOT.SetBatch(True)
  parallelProcesses = multiprocessing.cpu_count()
  
  #inDirName="dcap://t3se01.psi.ch:22125//pnfs/psi.ch/cms/trivcat/store/user/vlambert/TMVA/ctag_CSVMLP_IVFadapv1/Weighted/"
  inDirName="/user/smoortga/CTag/TMVActag_v1/FlatTrees_SL_7_5_1/MergedTTbar"
  files = [
    "CombinedSVNoVertex_B.root",
    "CombinedSVNoVertex_C.root",
    "CombinedSVNoVertex_DUSG.root",
    "CombinedSVPseudoVertex_B.root",
    "CombinedSVPseudoVertex_C.root",
    "CombinedSVPseudoVertex_DUSG.root",
    "CombinedSVRecoVertex_B.root",
    "CombinedSVRecoVertex_C.root",
    "CombinedSVRecoVertex_DUSG.root"
    ]
  #files ["CombinedSVNoVertex_B.root"]

  #for inFileName in os.listdir(inDirName):
  #  if inFileName.endswith(".root") and not (inFileName.find("Eta") >= 0):
  #    files.append(inFileName)

  # create Pool
  p = multiprocessing.Pool(parallelProcesses)
  print "Using %i parallel processes" %parallelProcesses

  for f in files:
    # debug
     read(inDirName, f)
    # break
    # run jobs
    #p.apply_async(read, args = (inDirName, f,))

  p.close()
  p.join()
    


if __name__ == '__main__':
    bdtoptions = [ "!H",
                                 "!V",
                                 "NTrees=1000",
                                 "MinNodeSize=1.5%",
                                 "BoostType=Grad",
                                 "Shrinkage=0.10",
                                 "UseBaggedGrad",
                                 "GradBaggingFraction=0.5",
                                 "nCuts=80",
                                 "MaxDepth=2",
                               ]
    train(bdtoptions)
    # trainMultiClass()
    readParallel()

