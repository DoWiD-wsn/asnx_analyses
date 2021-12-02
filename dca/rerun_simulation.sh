#!/bin/bash

#####
# @brief    Run a defined number of simulations per dataset
#
# Bash script to run several simulations of fault injections and
# subsequent dDCA assessment. The desired number is given as parameter.
# The script calls the respective Python scripts and analyses their
# results.
#
# Execution example:
# => $ ./rerun_simulation.sh 10
#
# @file     rerun_simulation.sh
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/02
#####

# Check if exactly one parameter was given
if [ "$#" -ne 1 ] ; then
    echo "No arguments supplied but one required"
    exit 1;
fi
# Get the desired number of runs
RUNS=$1

# Iterate over all available datasets
for dataset in base_datasets/* ; do
    # Run desired number of simulations per dataset
    echo "Run $RUNS simulations for dataset \"$dataset\""
    for (( run=0; run<$RUNS; run++ )); do
        # Call python script
        python3 simulate_ddca_inject_faults.py $dataset
        # Rename result file
        pathname=$(basename -- "$dataset")
        filename="${pathname%.*}"
        defname="results/${filename}-ddca_with_faults.csv"
        newname="results/${filename}-ddca_with_faults-${run}.csv"
        mv $defname $newname
    done
done
echo ""

# Generate plot for every result file in results/
echo "Generate plot for every result file"
for resultfile in results/* ; do
    python3 visualize_ddca_dataset.py $resultfile
done

# Run assessment script
echo "Run assessment script for all results"
python3 simulation-assess_results.py

echo ""
echo "DONE!"
echo ""

