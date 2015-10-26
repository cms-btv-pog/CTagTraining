#Targets:
# - weights   : makes weights
# - flat_tree : makes flat trees, with weights

# Working directory
BASE=$(CMSSW_BASE)/src
SCRIPTS=$(BASE)/CTagTraining/scripts
DATA=$(SCRIPTS)/data
INPUTS=$(DATA)/inputs

#weight tasks
$(DATA)/qcd_flavor_weights.json: $(INPUTS)/qcd.list $(SCRIPTS)/compute_weights.py
	./compute_weights.py qcd --compute-flavor

$(DATA)/ttjets_flavor_weights.json: $(INPUTS)/ttjets.list $(SCRIPTS)/compute_weights.py
	./compute_weights.py ttjets --compute-flavor

weights: $(DATA)/qcd_flavor_weights.json $(DATA)/ttjets_flavor_weights.json

#flat trees tasks
$(DATA)/flat_trees/qcd/.flat_trees_timestamp: $(SCRIPTS)/createNewTree.py $(DATA)/qcd_flavor_weights.json $(DATA)/ttjets_flavor_weights.json
	./createNewTree.py qcd --apply-pteta-weight --apply-category-weight --apply-flavor-weight && touch $@

#ttjets do not have weights
$(DATA)/flat_trees/ttjets/.flat_trees_timestamp: $(SCRIPTS)/createNewTree.py
  ./createNewTree.py ttjets && touch $@

trees: $(DATA)/flat_trees/qcd/.flat_trees_timestamp $(DATA)/flat_trees/ttjets/.flat_trees_timestamp