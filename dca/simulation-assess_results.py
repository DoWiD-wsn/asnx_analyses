#####
# @brief    Assess the results of the fault-injection simulations
#
# Python script to assess the results obtained from the modified
# deterministic dendritic cell algorithm (dDCA) used for detecting
# node-level faults in wireless sensor networks. The script reads all
# available result files and compares the available fault labels with
# the obtained fault context (by the dDCA). Thereby, it counts the:
# *) true positives
# *) true negatives
# *) false positives
# *) false negatives
# to calculate the effectiveness metrics:
# *) sensitivity (true positives rate)
# *) specificity (true negatives rate)
# *) accuracy (F-score)
# The resulting numbers are written to a result report as a CSV file.
# The input file (CSV) format expected is:
#   SNID, UNIX_timestamp, SNTIME,
#   Tair, Tsoil, Hair, Hsoil,
#   Xnt, Xvs, Xbat, Xart, Xrst, Xic, Xadc, Xusart,
#   fault_label
#   antigen, danger indicator, safe indicator, fault context
# Thereby, the first line contains the header and can be ignored.
#
# Run the script with:
# => $ python3 simulation-assess_results.py
#
# @file     simulation-assess_results.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/02
#####


##### LIBRARIES ########################
# basic math
import math
# For date/time
from datetime import datetime
from datetime import timedelta
# To handle the command line parameter
import sys
# directory/file functionality
import os
# For directory and file functionality
import glob
from pathlib import Path
# CSV functionality
import csv


##### GLOBAL VARIABLES #####
# Output directory
OUT_DIR     = "sim_results/"
# Result file location
RESULT_DIR  = "results/"
# Assessment result output (CSV file)
CSV_OUTPUT  = "simulation_assessment_result.csv"


##### ASSESSMENT #######################
# Check if result directory exists
if not os.path.exists(RESULT_DIR):
    print("ERROR: Result directory does not exist ... aborting!")
    exit(-1)

# Get filenames of all result files
csv_files = []
for filename in glob.glob(RESULT_DIR+'*.csv'):
    csv_files.append(filename)
num_files = len(csv_files)

# Check if output directory exists
if not os.path.exists(OUT_DIR):
    try:
        os.makedirs(OUT_DIR)
    except Exception as e:
        print("ERROR: Couldn't create directory for results ... aborting!")
        print(e)
        exit(-1)
# Get result file name and path
CSV_OUTPUT  = OUT_DIR+CSV_OUTPUT

# Prepare data variables
lines_tot   = []
tp_tot      = []
tn_tot      = []
fp_tot      = []
fn_tot      = []
# Results
tpr_tot     = []
tnr_tot     = []
f_score_tot = []

# Read in all result files
for filename in csv_files:
    # Try to open the CSV file
    csv_i = None
    try:
        # Open CSV input file
        csv_f = open(filename, 'r')
        # Get a CSV reader
        csv_i = csv.reader(csv_f, delimiter=',')
    except Exception as e:
        print("Cannot open the CSV input file \"%s\" ... aborting!" % filename)
        exit(-1)
    # Prepare local data variables
    lines   = 0
    tp      = 0
    tn      = 0
    fp      = 0
    fn      = 0
    # Results
    tpr     = 0     # sensitivity
    tnr     = 0     # specificity
    f_score = 0     # accuracy
    # Iterate over entries
    for row in csv_i:
        # Ignore first line (header)
        if lines>0:
            ### GET DATAFIELDS ###
            # fault label
            label = int(row[15])
            # fault context
            context = int(row[19])
            ### COMPARE DATA ###
            # true positive
            if (label==1) and (context==1):
                tp = tp + 1
            # true negative
            elif (label==0) and (context==0):
                tn = tn + 1
            # false positive
            elif (label==0) and (context==1):
                fp = fp + 1
            # false negative
            elif (label==1) and (context==0):
                fn = fn + 1
            # that should never happen
            else:
                print("ERROR: encountered a label/context that was neither 0 nor 1 ... abort!")
                exit(-1)
        # Increment line counter
        lines += 1
    # Ignore first line
    lines -= 1
    # Close CSV input file
    try:
        # Try to close the CSV file
        csv_f.close()
    except Exception as e:
        print("Couldn't close CSV input file ... aborting!")
        print(e)
        exit(-1)
    ### CALCULATE METRICS ###
    tpr     = round(tp / (tp + fn), 2) if tp>0 else 1
    tnr     = round(tn / (tn + fp), 2) if tn>0 else 1
    f_score = round(tp / (tp + (1/2) * (fp + fn)), 2) if tp>0 else 1
    ### Append results to result lists
    lines_tot.append(lines)
    tp_tot.append(tp)
    tn_tot.append(tn)
    fp_tot.append(fp)
    fn_tot.append(fn)
    # Results
    tpr_tot.append(tpr)
    tnr_tot.append(tnr)
    f_score_tot.append(f_score)

# Calculated mean, min, and max values
lines_mean   = 0
tp_mean      = 0
tn_mean      = 0
fp_mean      = 0
fn_mean      = 0
tpr_mean     = 0
tnr_mean     = 0
f_score_mean = 0
lines_min    = 999
tp_min       = 999
tn_min       = 999
fp_min       = 999
fn_min       = 999
tpr_min      = 999
tnr_min      = 999
f_score_min  = 999
lines_max    = 0
tp_max       = 0
tn_max       = 0
fp_max       = 0
fn_max       = 0
tpr_max      = 0
tnr_max      = 0
f_score_max  = 0
for i in range(len(lines_tot)):
    ### mean sum ###
    lines_mean   += lines_tot[i]
    tp_mean      += tp_tot[i]
    tn_mean      += tn_tot[i]
    fp_mean      += fp_tot[i]
    fn_mean      += fn_tot[i]
    tpr_mean     += tpr_tot[i]
    tnr_mean     += tnr_tot[i]
    f_score_mean += f_score_tot[i]
    ### min values ###
    if (lines_tot[i]<lines_min):
        lines_min = lines_tot[i]
    if (tp_tot[i]<tp_min):
        tp_min = tp_tot[i]
    if (tn_tot[i]<tn_min):
        tn_min = tn_tot[i]
    if (fp_tot[i]<fp_min):
        fp_min = fp_tot[i]
    if (fn_tot[i]<fn_min):
        fn_min = fn_tot[i]
    if (tpr_tot[i]<tpr_min):
        tpr_min = tpr_tot[i]
    if (tnr_tot[i]<tnr_min):
        tnr_min = tnr_tot[i]
    if (f_score_tot[i]<f_score_min):
        f_score_min = f_score_tot[i]
    ### max values ###
    if (lines_tot[i]>lines_max):
        lines_max = lines_tot[i]
    if (tp_tot[i]>tp_max):
        tp_max = tp_tot[i]
    if (tn_tot[i]>tn_max):
        tn_max = tn_tot[i]
    if (fp_tot[i]>fp_max):
        fp_max = fp_tot[i]
    if (fn_tot[i]>fn_max):
        fn_max = fn_tot[i]
    if (tpr_tot[i]>tpr_max):
        tpr_max = tpr_tot[i]
    if (tnr_tot[i]>tnr_max):
        tnr_max = tnr_tot[i]
    if (f_score_tot[i]>f_score_max):
        f_score_max = f_score_tot[i]
### mean final ###
lines_mean   = round(lines_mean/len(lines_tot), 2)
tp_mean      = round(tp_mean/len(lines_tot), 2)
tn_mean      = round(tn_mean/len(lines_tot), 2)
fp_mean      = round(fp_mean/len(lines_tot), 2)
fn_mean      = round(fn_mean/len(lines_tot), 2)
tpr_mean     = round(tpr_mean/len(lines_tot), 2)
tnr_mean     = round(tnr_mean/len(lines_tot), 2)
f_score_mean = round(f_score_mean/len(lines_tot), 2)


# Try to open/create TXT output file
csv_o = None
try:
    # Open CSV file
    csv_f = open(CSV_OUTPUT, 'w')
    # Get a CSV writer
    csv_o = csv.writer(csv_f)
except Exception as e:
    print("Cannot open the CSV output file/reader ... aborting!")
    print(e)
    exit(-1)

# Write initial rows into the CSV file
try:
    csv_o.writerow(["dataset", "value", "measurements", "true positives (TP)", "true negatives (TN)", "false positives (FP)", "false negatives (FN)", "sensitivity (TPR)", "specificity (TNR)", "accuracy (F-score)"])
except Exception as e:
    print("Writing initial data to the CSV file failed ... aborting!")
    print(e)
    exit(-1)

# Write total results into the CSV file
try:
    tot_string = "total (%d datasets)" % (num_files)
    csv_o.writerow([tot_string, "mean", lines_mean, tp_mean, tn_mean, fp_mean, fn_mean, tpr_mean, tnr_mean, f_score_mean])
    csv_o.writerow([tot_string, "min", lines_min, tp_min, tn_min, fp_min, fn_min, tpr_min, tnr_min, f_score_min])
    csv_o.writerow([tot_string, "max", lines_max, tp_max, tn_max, fp_max, fn_max, tpr_max, tnr_max, f_score_max])
except Exception as e:
    print("Writing total data to the CSV file failed ... aborting!")
    print(e)
    exit(-1)

# Write particular results into the CSV file
for i in range(len(lines_tot)):
    try:
        csv_o.writerow([csv_files[i], "-", lines_tot[i], tp_tot[i], tn_tot[i], fp_tot[i], fn_tot[i], tpr_tot[i], tnr_tot[i], f_score_tot[i]])
    except Exception as e:
        print("Writing dataset %d data to the CSV file failed ... aborting!" % (i))
        print(e)
        exit(-1)

# Close CSV output file
try:
    # Try to close the CSV file
    csv_f.close()
except Exception as e:
    print("Couldn't close CSV output file ... aborting!")
    print(e)
