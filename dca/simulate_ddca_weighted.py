#####
# @brief    Run the weighted dDCA on a pre-recorded dataset
#
# Python script to simulate the functioning of the weighted
# deterministic dendritic cell algorithm (dDCA) used for detecting
# node-level faults in wireless sensor networks. The script runs the
# algorithm on pre-recorded data, calculates the interim data (i.e.,
# danger and safe indicators), and determines the final classification
# result, that is, whether the data is considered normal or faulty.
# The input data extended with the dDCA data is written to a CSV file.
# The input file (CSV) format expected is:
#   SNID, UNIX_timestamp, SNTIME,
#   Tair, Tsoil, Hair, Hsoil,
#   Xnt, Xvs, Xbat, Xart, Xrst, Xic, Xadc, Xusart,
#   fault_label
# Thereby, the first line contains the header and can be ignored.
#
# A dataset has to be given as parameter, for example:
# => $ python3 simulate_ddca_weighted.py datasets/asnx_base_data.csv
#
# @file     simulate_ddca_weighted.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2022/09/06
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
from pysad.transform.probability_calibration import *
from pysad.transform.postprocessing import RunningAveragePostprocessor
from pysad.transform.preprocessing import InstanceUnitNormScaler
import numpy as np
# Silence VisibleDeprecationWarning in NumPy
import warnings
warnings.filterwarnings("ignore", category=np.VisibleDeprecationWarning)


##### GLOBAL VARIABLES #####
# Result file location
RESULT_DIR  = "results/"

# dendritic cell lifetime/population
DC_M            = 3
# number of sensor values for std-dev evaluation
STDEV_N         = 10
# sensitivity of safe indicator
SAFE_SENS       = 0.1

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
    CSV_OUTPUT = RESULT_DIR+(Path(CSV_INPUT).stem).replace('-ddca','') + '-ddca_weight.csv'
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
    # List of dendritic cells
    dcs         = []

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
            x_nt.append(round(float(row[7]),2))
            x_vs.append(round(float(row[8]),2))
            x_bat.append(round(float(row[9]),2))
            x_art.append(round(float(row[10]),2))
            x_rst.append(round(float(row[11]),2))
            x_ic.append(round(float(row[12]),2))
            x_adc.append(round(float(row[13]),2))
            x_usart.append(round(float(row[14]),2))
            ### FAULT LABEL ###
            label_t = int(row[15])
            label.append(label_t)
            ### DCA VALUES
            antigen_t = str(row[16])
            antigen.append(antigen_t)
            danger_t = round(float(row[17]),2)
            danger.append(danger_t)
            safe_t = round(float(row[18]),2)
            safe.append(safe_t)


            #################################
            ##### dendritic cell update #####
            #################################
    
            context_t = danger_t - safe_t
            # Update previous DCs
            for dc in dcs:
                dc["context"] = dc["context"] + context_t
            # Create new DC
            dcs.append({
                "antigen"   : antigen_t,
                "context"   : context_t,
                "age"       : (line_count-1)
            })
            # If population is full, delete oldest DC
            if len(dcs)>DC_M:
                dcs.pop(0)
            
            ##############################
            ##### context assignment #####
            ##############################
            
            oldest = dcs[0]["age"]
            state = 0
            sum_w = 0
            for dc in dcs:
                weight = dc["age"]-(oldest)+1
                sum_w += weight
                state = state + weight if dc["context"]>=0 else state
            state = state/sum_w
            context_t = 1 if state>0.5 else 0
            context.append(context_t)

        # Increment line counter
        line_count += 1

    #########################
    ##### result output #####
    #########################

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

print()
print("DONE!")
