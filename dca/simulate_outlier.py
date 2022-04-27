#####
# @brief    Perform a outlier detection on a pre-recorded dataset
#
# Script to perform a variance-based outlier detection on the previously
# generated test datasets. The script reads all datasets fro the given
# "RESULT_DIR", performs specified models to detect anomalies
# (outliers), and store the data in a new dataset with a respective
# postfix (e.g., "-stdev") in the "RESULT_DIR".
#
# Call example:
# => $ python3 simulate_outlier.py
#
# @file     simulate_outlier.py
# @author   Dominik Widhalm
# @version  1.1.0
# @date     2022/04/27
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
# Result file location
RESULT_DIR  = "results/"

# Window size for outlier detection (None for no window)
WINDOW_SIZE = 15
# Detection threshold (multiples of sigma)
THRESHOLD   = 3
# Include node-level diagnostics (danger indicator) in detection
INC_DIAG    = 0         # 0 ... exclude / 1 ... include

##### CLASS FOR WELFORD'S ALGORITHM ####
class Welford:
    def __init__(self, window=None):
        self.mean = 0
        self.variance = 0
        self.cnt = 0
        self.val = []
        self.window = window
    
    def add(self, element):
        mean_old = self.mean
        self.cnt += 1
        self.mean += (element - self.mean) / self.cnt
        self.variance += (element - self.mean) * (element - mean_old)
    
    def remove(self, element):
        if(self.cnt == 0):
            return
        if(self.cnt == 1):
            self.mean = 0
            self.variance = 0
            self.cnt = 0
            self.val = []
        mean_old = (self.cnt * self.mean - element) / (self.cnt - 1)
        self.variance -= (element - self.mean) * (element - mean_old)
        self.mean = mean_old
        self.cnt -= 1
    
    def replace(self, old, new):
        self.remove(old)
        self.add(new)
    
    def get_mean(self):
        return self.mean
    
    def get_variance(self):
        return (abs(self.variance) / self.cnt)
    
    def get_stdev(self):
        var = self.get_variance()
        if var != 0:
            return math.sqrt(var)
        else:
            return 0
        
    def update(self, element):
        self.val.append(element)
        # Check window size
        if((self.window is not None) and (self.cnt>=self.window)):
            old = self.val.pop(0)
            self.replace(old,element)
        else:
            self.add(element)
        # Check for outlier (3*sigma)
        if abs(self.get_stdev()) >= THRESHOLD:
            return 1
        else:
            return 0

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
    extension = None
    if INC_DIAG:
        extension = "-stdev_ext.csv"
    else:
        extension = "-stdev.csv"
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
    # Welford instance
    t_air_inst  = Welford(window=WINDOW_SIZE)
    t_soil_inst = Welford(window=WINDOW_SIZE)
    h_air_inst  = Welford(window=WINDOW_SIZE)
    h_soil_inst = Welford(window=WINDOW_SIZE)
    if INC_DIAG:
        d_inst  = Welford(window=WINDOW_SIZE)
    
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
            danger_t = round(float(row[17]),2)
            if INC_DIAG:
                danger.append(danger_t)
            else:
                danger.append(0.0)
            
            ### FAULT LABEL ###
            label_t = int(row[15])
            label.append(label_t)


    ##########################################
    ##### Step 2 - Run Outlier detection #####
    ##########################################
            
            # Update Welford instances
            t_air_cx = t_air_inst.update(t_air_t)
            t_soil_cx = t_soil_inst.update(t_soil_t)
            h_air_cx = h_air_inst.update(h_air_t)
            h_soil_cx = h_soil_inst.update(h_soil_t)
            
            if INC_DIAG:
                # Correct indicator sensibility factor (0.1 -> x10)
                d_cx = d_inst.update(danger_t*10.0)
            
            # Outlier if at least one data element is an outlier
            if INC_DIAG:
                context.append(max(t_air_cx,t_soil_cx,h_air_cx,h_soil_cx,d_cx))
            else:
                context.append(max(t_air_cx,t_soil_cx,h_air_cx,h_soil_cx))

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
