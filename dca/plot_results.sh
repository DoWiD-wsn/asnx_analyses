#!/bin/bash

#####
# @brief    Plot all data available in the results directory
#
# Bash script to plot all datasets contained in the results directory.
# With an optional argument, the transparency of the generated plots
# can be configured (i.e., 0 for not transparent; 1 for transparent).
#
# Execution example:
# => $ ./plot_results.sh 0
#
# @file     plot_results.sh
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2022/04/16
#####

# Check if a parameter was given
TRANSPARENT=0
if [ "$#" -ne 1 ] ; then
    TRANSPARENT=0
else
    TRANSPARENT=$1
fi

# Generate plot for every dataset in results/
echo "Generate plot for every result file"
for resultfile in results/* ; do
    python3 visualize_ddca_dataset.py $resultfile $TRANSPARENT
done
echo ""

echo ""
echo "DONE!"
echo ""

