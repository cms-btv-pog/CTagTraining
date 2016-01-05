#! /bin/env bash

#
# Gets the output of an optimization cycle (condor only, for the moment) and creates all the ROC
# plots in a sub-directory called ROCs
#

indir=$1
mkdir -p $indir/ROCs
cfgs=`grep Arguments $indir/condor.jdl | awk '{print $3}'`
NPROCS=0
for cfg_hash in $cfgs; do
    echo $cfg_hash
    python make_roc.py $indir/ $indir/ROCs --filter=$cfg_hash --tag=$cfg_hash --quiet &
    NPROC=$(($NPROC+1))
    if [ "$NPROC" -ge 10 ]; then
        wait
        NPROC=0
    fi
done