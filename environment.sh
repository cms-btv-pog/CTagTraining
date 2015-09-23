#!/bin/bash                                                                                                                                  

# Setup the environment for the framework                                                                                                    
export CTRAIN=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd -P)
echo "Setting variable \$CTRAIN=$CTRAIN"

eval `scramv1 runtime -sh`
vpython=$CTRAIN/external/vpython
echo "Activating python virtualenv from $vpython"
if [ -d "$vpython" ]; then
    echo "Activating python virtual environment"
    export VIRTUAL_ENV_DISABLE_PROMPT=1
    pushd $vpython
    # See https://github.com/pypa/virtualenv/issues/150
    source bin/activate
    popd
else
    echo "$vpython does not exist! run ./install.sh to install python virtualenv and additional packages."
fi

# Put the PWD into the PYTHONPATH
# Make sure we prefer our virtualenv packages
export PYTHONPATH=$vpython/lib/python2.7/site-packages/:$PYTHONPATH

