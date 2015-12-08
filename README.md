# CTagTraining
Training and Validation of the CMS charm tagger.
This repository is used to make changes to the standalone TMVA based charm tagger. 
Not for CMSSW integrated charm tagger.

============
Installation
============

Run the following commands

```
#create new CMSSW dev area
areaname=WHATEVER
scram pro -n $areaname CMSSW CMSSW_7_6_0_pre7 #or cmsrel CMSSW_7_6_0_pre7
cd $areaname/src
cmsenv
git cms-init
git clone --recursive https://github.com/cms-btv-pog/CTagTraining.git
cd CTagTraining
./install.sh
```

The install command will install all the necessary CMSSW and python packages (rootpy, scikit-learn, etc..)

When entering the dev area run:

```
source environment.sh
```

To activate the customization. Must be run at each login (just like cmsenv)
