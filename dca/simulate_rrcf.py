#####
# @brief    Run the Robust Random Cut Forest Algorithm (rrcf) on a pre-recorded dataset
#
# Script to perform the RRCF on the previously generated test datasets.
# The script reads all datasets fro the given "RESULT_DIR", performs
# the RRCF to detect anomalies (outliers), and store the data in a new
# dataset with the postfix "-rrfc" in the "RESULT_DIR".
#
# Call example:
# => $ python3 simulate_rrcf.py
#
# @file     simulate_rrcf.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2022/04/05
# @see      https://klabum.github.io/rrcf/streaming.html
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
# RRCF
import rrcf


##### GLOBAL VARIABLES #####
# Result file location
RESULT_DIR  = "results/"

# Threshold for anomaly score (empirically derived)
threshold   = 50

# Number of trees
num_trees   = 40
# Tree size
tree_size   = 256


##### SIMULATION #######################
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
if not os.path.exists(RESULT_DIR):
    try:
        os.makedirs(RESULT_DIR)
    except Exception as e:
        print("ERROR: Couldn't create directory for results ... aborting!")
        print(e)
        exit(-1)

# Read in all result files
for CSV_INPUT in csv_files:
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
    print("Reading CSV input file \"%s\"" % CSV_INPUT)

    # Get output CSV filename from input filename
    CSV_OUTPUT = RESULT_DIR+Path(CSV_INPUT).stem + "-rrcf.csv"
    print("Write to file \"%s\"" % CSV_OUTPUT)

    # Prepare data arrays/lists/etc.
    snid        = []
    tstmp       = []
    sntime      = []
    # use case data
    t_air       = []
    t_soil      = []
    h_air       = []
    h_soil      = []
    # fault indicator
    x_nt        = []
    x_vs        = []
    x_bat       = []
    x_art       = []
    x_rst       = []
    x_ic        = []
    x_adc       = []
    x_usart     = []
    # fault label
    label       = []
    # DCA indicators
    antigen     = []
    danger      = []
    safe        = []


    # anomaly score
    context     = []

    #######################################
    ##### Step 0 - initialization     #####
    #######################################

    # Create a forest of empty trees for each sensor measurement
    forest_t_air    = []
    forest_t_soil   = []
    forest_h_air    = []
    forest_h_soil   = []
    for _ in range(num_trees):
        tree = rrcf.RCTree()
        forest_t_air.append(tree)
        tree = rrcf.RCTree()
        forest_t_soil.append(tree)
        tree = rrcf.RCTree()
        forest_h_air.append(tree)
        tree = rrcf.RCTree()
        forest_h_soil.append(tree)
    # Create dicts to store anomaly score of each point
    avg_codisp_t_air  = {}
    avg_codisp_t_soil = {}
    avg_codisp_h_air  = {}
    avg_codisp_h_soil = {}

    #######################################
    ##### Step 1 - sensor node update #####
    #######################################

    # Iterate over entries
    line_count = 0
    for row in csv_i:
        if line_count>0:
            ### GENERAL ###
            # Get snid
            snid_t = str(row[0])
            snid.append(snid_t)
            # Get date/time
            tstmp_t = int(row[1])
            tstmp.append(tstmp_t)
            # Get sntime
            sntime_t = int(row[2])
            sntime.append(sntime_t)
            
            ### USE CASE DATA ###
            # Get sensor readings
            t_air_t = round(float(row[3]),2)
            t_air.append(t_air_t)
            t_soil_t = round(float(row[4]),2)
            t_soil.append(t_soil_t)
            h_air_t = round(float(row[5]),2)
            h_air.append(h_air_t)
            h_soil_t = round(float(row[6]),2)
            h_soil.append(h_soil_t)
            
            ### FAULT INDICATOR ###
            # Ignore indicator values
            x_nt.append(0.0)
            x_vs.append(0.0)
            x_bat.append(0.0)
            x_art.append(0.0)
            x_rst.append(0.0)
            x_ic.append(0.0)
            x_adc.append(0.0)
            x_usart.append(0.0)
            # Ignore DCA values
            antigen.append("-")
            safe.append(0.0)
            
            ### FAULT LABEL ###
            label_t = int(row[15])
            label.append(label_t)


    ##############################
    ##### Step 2 - Run RRFC  #####
    ##############################

            # For each tree in the t_air forest
            for tree in forest_t_air:
                # If tree is above permitted size
                if len(tree.leaves) > tree_size:
                    # Drop the oldest point (FIFO)
                    tree.forget_point((line_count-1) - tree_size)
                # Insert the new measurement into the tree
                tree.insert_point(t_air_t, index=(line_count-1))
                # Compute codisp on the new point
                new_codisp = tree.codisp((line_count-1))
                # And take the average over all trees
                if not (line_count-1) in avg_codisp_t_air:
                    avg_codisp_t_air[(line_count-1)] = 0
                avg_codisp_t_air[(line_count-1)] += new_codisp / num_trees
                context_t_air = avg_codisp_t_air[(line_count-1)]

            # For each tree in the t_air forest
            for tree in forest_t_soil:
                # If tree is above permitted size
                if len(tree.leaves) > tree_size:
                    # Drop the oldest point (FIFO)
                    tree.forget_point((line_count-1) - tree_size)
                # Insert the new measurement into the tree
                tree.insert_point(t_soil_t, index=(line_count-1))
                # Compute codisp on the new point
                new_codisp = tree.codisp((line_count-1))
                # And take the average over all trees
                if not (line_count-1) in avg_codisp_t_soil:
                    avg_codisp_t_soil[(line_count-1)] = 0
                avg_codisp_t_soil[(line_count-1)] += new_codisp / num_trees
                context_t_soil = avg_codisp_t_soil[(line_count-1)]

            # For each tree in the h_air forest
            for tree in forest_h_air:
                # If tree is above permitted size
                if len(tree.leaves) > tree_size:
                    # Drop the oldest point (FIFO)
                    tree.forget_point((line_count-1) - tree_size)
                # Insert the new measurement into the tree
                tree.insert_point(h_air_t, index=(line_count-1))
                # Compute codisp on the new point
                new_codisp = tree.codisp((line_count-1))
                # And take the average over all trees
                if not (line_count-1) in avg_codisp_h_air:
                    avg_codisp_h_air[(line_count-1)] = 0
                avg_codisp_h_air[(line_count-1)] += new_codisp / num_trees
                context_h_air = avg_codisp_h_air[(line_count-1)]

            # For each tree in the t_air forest
            for tree in forest_h_soil:
                # If tree is above permitted size
                if len(tree.leaves) > tree_size:
                    # Drop the oldest point (FIFO)
                    tree.forget_point((line_count-1) - tree_size)
                # Insert the new measurement into the tree
                tree.insert_point(h_soil_t, index=(line_count-1))
                # Compute codisp on the new point
                new_codisp = tree.codisp((line_count-1))
                # And take the average over all trees
                if not (line_count-1) in avg_codisp_h_soil:
                    avg_codisp_h_soil[(line_count-1)] = 0
                avg_codisp_h_soil[(line_count-1)] += new_codisp / num_trees
                context_h_soil = avg_codisp_h_soil[(line_count-1)]
            
            # Get the maximum anomaly score
            context_t = max(context_t_air,context_t_soil,context_h_air,context_h_soil)
            # Store the score as "danger" value
            danger.append(min(1,context_t/threshold))
            # Decide if anomalous or not
            if context_t > threshold:
                context.append(1)
            else:
                context.append(0)

        # Increment line counter
        line_count += 1

    ####################################
    ##### Step 1.2 - result output #####
    ####################################

    # Close CSV input file
    try:
        # Try to close the CSV file
        csv_f.close()
    except Exception as e:
        print("Couldn't close CSV input file ... aborting!")
        print(e)

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
        csv_o.writerow(["snid", "timestamp [UNIX]", "sntime", "T_air [°C]", "T_soil [°C]", "H_air [%RH]", "H_soil [%RH]", "x_nt", "x_vs", "x_bat", "x_art", "x_rst", "x_ic", "x_adc", "x_usart", "fault", "antigen",  "danger",  "safe", "fault label"])
    except Exception as e:
        print("Writing initial data to the CSV file failed ... aborting!")
        print(e)
        exit(-1)

    # Iterate over all data
    for i in range(len(snid)):
        try:
            # Write a row to the CSV file
            csv_o.writerow([snid[i], tstmp[i], sntime[i], t_air[i], t_soil[i], h_air[i], h_soil[i], x_nt[i], x_vs[i], x_bat[i], x_art[i], x_rst[i], x_ic[i], x_adc[i], x_usart[i], label[i], antigen[i], danger[i], safe[i], context[i]])
        except Exception as e:
            print("Writing measurement data to the CSV file failed ... aborting!")
            print(e)
            exit(-1)

    # Close CSV output file
    try:
        # Try to close the CSV file
        csv_f.close()
    except Exception as e:
        print("Couldn't close CSV output file ... aborting!")
        print(e)
    
    print("DONE!")
    print()
