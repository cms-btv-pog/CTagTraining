#Targets:
# - weights   : makes weights
# - flat_tree : makes flat trees, with weights

# Working directory
## BASE=$(CMSSW_BASE)/src
## SCRIPTS=$(BASE)/CTagTraining/scripts
SCRIPTS=./
DATA=$(SCRIPTS)/data
INPUTS=$(DATA)/inputs

#yields tasks
$(DATA)/qcd_yields.json: $(INPUTS)/qcd.list $(SCRIPTS)/compute_yields.py
	./compute_yields.py qcd

$(DATA)/ttjets_yields.json: $(INPUTS)/ttjets.list $(SCRIPTS)/compute_yields.py
	./compute_yields.py ttjets

yields: $(DATA)/qcd_yields.json $(DATA)/ttjets_yields.json

#weight tasks
$(DATA)/qcd_weights.root: $(DATA)/qcd_yields.json $(DATA)/ttjets_yields.json $(SCRIPTS)/compute_weights.py
	./compute_weights.py

weights: $(DATA)/qcd_weights.root

#flat trees tasks
$(DATA)/flat_trees/qcd_flat.list: $(SCRIPTS)/createNewTree.py $(DATA)/qcd_weights.root
	./createNewTree.py qcd --apply-pteta-weight --apply-category-weight --apply-flavor-weight

#ttjets do not have weights
$(DATA)/flat_trees/ttjets_flat.list: $(SCRIPTS)/createNewTree.py
	./createNewTree.py ttjets

trees: $(DATA)/flat_trees/qcd_flat.list $(DATA)/flat_trees/ttjets_flat.list
