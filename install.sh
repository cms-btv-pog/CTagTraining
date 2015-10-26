#!/usr/bin/env bash

set -o errexit
set -o nounset

: ${CMSSW_BASE:?"CMSSW_BASE is not set!  Run cmsenv before install.sh"}

########################
# Python customization #
########################

fwk_location=$CMSSW_BASE/src/CTagTraining
external=$fwk_location/external
vpython=$external/vpython
vpython_src=$external/src/virtualenv

pushd $vpython_src

echo "Creating virtual python environment in $vpython"
if [ ! -d "$vpython" ]; then
  ./virtualenv.py --distribute $vpython
else
  echo "...virtual environment already setup."
fi

popd

echo "Activating virtual python environment"
pushd $vpython
export VIRTUAL_ENV_DISABLE_PROMPT=1
source bin/activate

echo "Installing yolk -- python package management"
pip install -U yolk
echo "Installing rootpy -- pyRoot done right"
pip install -e $external/src/rootpy
echo "Installing root_numpy -- connection between ROOT and numpy"
pip install -e $external/src/root_numpy
echo "Installing scikit-learn -- python machine learning"
pip install -U scikit-learn

popd