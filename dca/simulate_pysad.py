#####
# @brief    Run the models of PySAD on a pre-recorded dataset
#
# Script to perform the models available in PySAD on the previously
# generated test datasets. The script reads all datasets fro the given
# "RESULT_DIR", performs specified models to detect anomalies
# (outliers), and store the data in a new dataset with a respective
# postfix (e.g., "-rrfc") in the "RESULT_DIR".
#
# Call example:
# => $ python3 simulate_pysad.py
#
# @file     simulate_pysad.py
# @author   Dominik Widhalm
# @version  1.1.0
# @date     2022/04/16
# @see      https://pysad.readthedocs.io/en/latest/examples.html
#
# @todo     Optimize model parameters for better detection results
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
# PySAD (models and calibrator)
from pysad.models import *
from pysad.transform.probability_calibration import ConformalProbabilityCalibrator
from pysad.transform.postprocessing import RunningAveragePostprocessor
from pysad.transform.preprocessing import InstanceUnitNormScaler
import numpy as np
# Silence VisibleDeprecationWarning in NumPy
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


##### GLOBAL VARIABLES #####
# Result file location
RESULT_DIR  = "results/"

# Threshold for calibrated anomaly score
THRESHOLD   = 0.95      # probability of being normal is less than 5%.
# Window size for anomaly score calibration
WINDOW_SIZE = 140

##### SIMULATION #######################
# Check if result directory exists
if not os.path.exists(RESULT_DIR):
    print("ERROR: Result directory does not exist ... aborting!")
    exit(-1)
# Get filenames of all result files
csv_files = []
for filename in glob.glob(RESULT_DIR+'*-ddca.csv'):
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
    print("=> CSV input file \"%s\"" % CSV_INPUT)
              
    # Models available in PySAD (and applicable to our data)
    models = [
        ##### Models running and producing results #####
        
        ## Exact-STORM method ##
        # https://pysad.readthedocs.io/en/latest/generated/pysad.models.ExactStorm.html#pysad.models.ExactStorm
        # Default: (window_size=10000, max_radius=0.1)
        ["storm", ExactStorm(window_size=WINDOW_SIZE, max_radius=0.1)],
        
        ## Isolation Forest Algorithm for Streaming Data ##
        # https://pysad.readthedocs.io/en/latest/generated/pysad.models.IForestASD.html#pysad.models.IForestASD
        # Default: (initial_window_X=None, window_size=2048)
        ["iforest", IForestASD(initial_window_X=None, window_size=WINDOW_SIZE)],
        
        ## RobustRandomCutForest ##
        # https://pysad.readthedocs.io/en/latest/generated/pysad.models.RobustRandomCutForest.html#pysad.models.RobustRandomCutForest
        # Default: (num_trees=4, shingle_size=4, tree_size=256)
        ["rrcf", RobustRandomCutForest(num_trees=10, shingle_size=5, tree_size=200)],
        
        ## xStream ##
        # https://pysad.readthedocs.io/en/latest/generated/pysad.models.xStream.html#pysad.models.xStream
        # Default: (num_components=100, n_chains=100, depth=25, window_size=25)
        ["xstream", xStream(num_components=200, n_chains=50, depth=10, window_size=WINDOW_SIZE)],
    ]
    # Init probability calibrator.
    # Probability calibrators convert module scores into true probabilities for decision-making on anomalousness.
    calibrator = ConformalProbabilityCalibrator(windowed=True, window_size=WINDOW_SIZE)
    # Init normalizer.
    preprocessor = InstanceUnitNormScaler()
    # Init running average postprocessor.
    postprocessor = RunningAveragePostprocessor(window_size=WINDOW_SIZE)
    
    # Iterate over all models of PySAD
    for (name, model) in models:
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
        extension = "-%s.csv" % (name)
        CSV_OUTPUT = RESULT_DIR+(Path(CSV_INPUT).stem).replace('-ddca','') + extension
        print("    Write to file \"%s\"" % CSV_OUTPUT)

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
                danger.append(0.0)
                
                ### FAULT LABEL ###
                label_t = int(row[15])
                label.append(label_t)


        ####################################
        ##### Step 2 - Run PySAD model #####
        ####################################
                
                # Concatenate sensor measurements
                point = np.array([t_air_t, t_soil_t, h_air_t, h_soil_t])
                # Fit preprocessor to and transform the instance.
                point = preprocessor.fit_transform_partial(point)
                
                # Fit to an instance x and score it.
                anomaly_score = model.fit_score_partial(point)
                # Xstream delivers an array of scores with size 1
                if(name == "xstream"):
                    anomaly_score = anomaly_score[0]
                
                # Apply running averaging to the score.
                #anomaly_score = postprocessor.fit_transform_partial(anomaly_score)
                
                # Fit & calibrate score.
                calibrated_score = calibrator.fit_transform_partial(anomaly_score)
                
                # Check if anomaly score exceeds the defined threshold
                if calibrated_score > THRESHOLD:
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
    
    # Done with this dataset
    print()
