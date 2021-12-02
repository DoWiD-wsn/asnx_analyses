#####
# @brief    Assess the results of the modified dDCA
#
# Python script to assess the results obtained from the modified
# deterministic dendritic cell algorithm (dDCA) used for detecting
# node-level faults in wireless sensor networks. The script reads the
# CSV input file and compares the available fault labels with the
# obtained fault context (by the dDCA). Thereby, it counts the:
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
# A dataset has to be given as parameter, for example:
# => $ python3 assess_ddca_output.py results/base_-_indoor_-_stable-ddca.csv
#
# @file     assess_ddca_output.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/01
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
# To get filename without path and extension
from pathlib import Path
# CSV functionality
import csv


##### GLOBAL VARIABLES #####
# Output directory
OUT_DIR     = "results/"


##### SIMULATION #######################
### Check input file
# Parameter given
if (len(sys.argv) != 2):
    print("ERROR: the script needs at least the input CSV file as parameter!")
    exit(-1)
# Correct extension
if not (str(sys.argv[1]).endswith('.csv') or str(sys.argv[1]).endswith('.CSV')):
    print("ERROR: CSV file expected as input!")
    exit(-1)
# Use given file as input
CSV_INPUT = str(sys.argv[1])

# Check if output directory exists
if not os.path.exists(OUT_DIR):
    try:
        os.makedirs(OUT_DIR)
    except Exception as e:
        print("ERROR: Couldn't create directory for results ... aborting!")
        print(e)
        exit(-1)

# Get data from CSV file
csv_i = None
try:
    # Open CSV input file
    csv_f = open(CSV_INPUT, 'r')
    # Get a CSV reader
    csv_i = csv.reader(csv_f, delimiter=',')
except Exception as e:
    print("Cannot open the CSV input file \"%s\" ... aborting!" % CSV_INPUT)
    exit(-1)

# Get output CSV filename from input filename
CSV_OUTPUT = OUT_DIR+Path(CSV_INPUT).stem + "-result.csv"

# Prepare data variables
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

### CALCULATE METRICS ###
tpr     = round(tp / (tp + fn), 2) if (tp + fn)>0 else 1
tnr     = round(tn / (tn + fp), 2) if (tn + fp)>0 else 1
f_score = round(tp / (tp + (1/2) * (fp + fn)), 2) if (tp + (1/2) * (fp + fn))>0 else 1

# Try to open/create CSV output file
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
    csv_o.writerow(["input file", "measurements", "true positives (TP)", "true negatives (TN)", "false positives (FP)", "false negatives (FN)", "sensitivity (TPR)", "specificity (TNR)", "accuracy (F-score)"])
    csv_o.writerow([CSV_INPUT, lines, tp, tn, fp, fn, tpr, tnr, f_score])
except Exception as e:
    print("Writing initial data to the CSV file failed ... aborting!")
    print(e)
    exit(-1)

# Close CSV output file
try:
    # Try to close the CSV file
    csv_f.close()
except Exception as e:
    print("Couldn't close CSV output file ... aborting!")
    print(e)
