#####
# @brief    Injected faults into pre-recorded dataset
#
# Python script to inject faults based on the provided fault signatures
# into a given dataset and save the resulting dataset.
# The input file (CSV) format expected is:
#   SNID, UNIX_timestamp, SNTIME,
#   Tair, Tsoil, Hair, Hsoil,
#   Xnt, Xvs, Xbat, Xart, Xrst, Xic, Xadc, Xusart,
#   fault_label
# Thereby, the first line contains the header and can be ignored.
#
# A dataset has to be given as parameter, for example:
# => $ python3 inject_faults.py datasets/asnx_base_data.csv
#
# @file     inject_faults.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/14
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
import glob
# To get filename without path and extension
from pathlib import Path
# CSV functionality
import csv
# For random number
from random import randint


##### GLOBAL VARIABLES #####
# Output directory
OUT_DIR     = "results/"

# Fault signatures directory
FAULT_DIR   = "fault_signatures/"
# Available fault signatures
FAULTS      = glob.glob(FAULT_DIR+"*.csv")


##### INJECT FAULTS ####################
### Check input file
# Parameter given
if (len(sys.argv) != 2):
    print("ERROR: the script needs the input CSV file as parameter!")
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
CSV_OUTPUT = OUT_DIR+Path(CSV_INPUT).stem + "-faulty.csv"


##################################
##### GET DATASET FROM FILE ######
##################################
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
        #time_t = datetime.utcfromtimestamp(tstmp_t)
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
        # Get indicator values
        x_nt_t = round(float(row[7]),2)
        x_nt.append(x_nt_t)
        x_vs_t = round(float(row[8]),2)
        x_vs.append(x_vs_t)
        x_bat_t = round(float(row[9]),2)
        x_bat.append(x_bat_t)
        x_art_t = round(float(row[10]),2)
        x_art.append(x_art_t)
        x_rst_t = round(float(row[11]),2)
        x_rst.append(x_rst_t)
        x_ic_t = round(float(row[12]),2)
        x_ic.append(x_ic_t)
        x_adc_t = round(float(row[13]),2)
        x_adc.append(x_adc_t)
        x_usart_t = round(float(row[14]),2)
        x_usart.append(x_usart_t)
        
        ### FAULT LABEL ###
        label_t = int(row[15])
        label.append(label_t)
        # Increment line counter
    line_count += 1


##################################
##### GET FAULTS FROM FILE  ######
##################################
faults = []
for i in range(len(FAULTS)):
    # Get data from CSV file
    # use case data
    f_t_air     = []    # index: 0
    f_t_soil    = []    # index: 1
    f_h_air     = []    # index: 2
    f_h_soil    = []    # index: 3
    # fault indicator
    f_x_nt      = []    # index: 4
    f_x_vs      = []    # index: 5
    f_x_bat     = []    # index: 6
    f_x_art     = []    # index: 7
    f_x_rst     = []    # index: 8
    f_x_ic      = []    # index: 9
    f_x_adc     = []    # index: 10
    f_x_usart   = []    # index: 11
    # fault label
    f_label     = []    # index: 12
    csv_fault = None
    try:
        # Open CSV input file
        csv_f_in = open(FAULTS[i], 'r')
        # Get a CSV reader
        csv_fault = csv.reader(csv_f_in, delimiter=',')
    except Exception as e:
        print("Cannot open the fault signature \"%s\" ... aborting!" % FAULTS[i])
        exit(-1)
    # Iterate over entries
    line_count = 0
    for row in csv_fault:
        if line_count>0:
            ### USE CASE DATA ###
            # Get sensor readings
            f_t_air_t = round(float(row[3]),2)
            f_t_air.append(f_t_air_t)
            f_t_soil_t = round(float(row[4]),2)
            f_t_soil.append(f_t_soil_t)
            f_h_air_t = round(float(row[5]),2)
            f_h_air.append(f_h_air_t)
            f_h_soil_t = round(float(row[6]),2)
            f_h_soil.append(f_h_soil_t)
            
            ### FAULT INDICATOR ###
            # Get indicator values
            f_x_nt_t = round(float(row[7]),2)
            f_x_nt.append(f_x_nt_t)
            f_x_vs_t = round(float(row[8]),2)
            f_x_vs.append(f_x_vs_t)
            f_x_bat_t = round(float(row[9]),2)
            f_x_bat.append(f_x_bat_t)
            f_x_art_t = round(float(row[10]),2)
            f_x_art.append(f_x_art_t)
            f_x_rst_t = round(float(row[11]),2)
            f_x_rst.append(f_x_rst_t)
            f_x_ic_t = round(float(row[12]),2)
            f_x_ic.append(f_x_ic_t)
            f_x_adc_t = round(float(row[13]),2)
            f_x_adc.append(f_x_adc_t)
            f_x_usart_t = round(float(row[14]),2)
            f_x_usart.append(f_x_usart_t)
            
            ### FAULT LABEL ###
            f_label_t = int(row[15])
            f_label.append(f_label_t)
            # Increment line counter
        line_count += 1
    # Add fault-data to fault list
    faults.append((f_t_air,f_t_soil,f_h_air,f_h_soil,f_x_nt,f_x_vs,f_x_bat,f_x_art,f_x_rst,f_x_ic,f_x_adc,f_x_usart,f_label))

##################################
##### INJECT FAULTS ##############
##################################
# Get random number of faults
F_NUM = randint(0,10)
# Inject faults
for i in range(F_NUM):
    # Get fault signature index
    F_IND = randint(0,len(FAULTS)-1)
    # Do until fault matches
    repeat = True
    while repeat:
        # Get random start location
        F_START = randint(0,len(snid)-1)
        # Get corresponding end position based on fault signature length
        F_END = F_START + len(faults[F_IND][0])
        # Check if fault fits into dataset
        if F_END>(len(snid)-1):
            # Try again
            continue
        # Check if there is already a fault in the given range
        is_fault = False
        for j in range(len(faults[F_IND][0])):
            # Check label of the data point
            if label[F_START+j] == 1:
                # There is already an active fault
                is_fault = True
                continue
        # Check if fault was found
        if is_fault == True:
            # Try again
            continue
        # Fault location is acceptable
        repeat = False
    # Insert fault in dataset
    for j in range(len(faults[F_IND][0])):
        # use case data
        t_air[F_START+j]    = t_air[F_START+j]  + faults[F_IND][0][j]
        t_soil[F_START+j]   = t_soil[F_START+j] + faults[F_IND][1][j]
        h_air[F_START+j]    = h_air[F_START+j]  + faults[F_IND][2][j]
        h_soil[F_START+j]   = h_soil[F_START+j] + faults[F_IND][3][j]
        # fault indicator
        x_nt[F_START+j]     = faults[F_IND][4][j]
        x_vs[F_START+j]     = faults[F_IND][5][j]
        x_bat[F_START+j]    = faults[F_IND][6][j]
        x_art[F_START+j]    = faults[F_IND][7][j]
        x_rst[F_START+j]    = faults[F_IND][8][j]
        x_ic[F_START+j]     = faults[F_IND][9][j]
        x_adc[F_START+j]    = faults[F_IND][10][j]
        x_usart[F_START+j]  = faults[F_IND][11][j]
        # fault label
        label[F_START+j]    = faults[F_IND][12][j]

# Close CSV input file
try:
    # Try to close the CSV file
    csv_f.close()
except Exception as e:
    print("Couldn't close CSV input file ... aborting!")
    print(e)


####################################
##### STORE RESULTS ################
####################################
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
    csv_o.writerow(["snid", "timestamp [UNIX]", "sntime", "T_air [°C]", "T_soil [°C]", "H_air [%RH]", "H_soil [%RH]", "x_nt", "x_vs", "x_bat", "x_art", "x_rst", "x_ic", "x_adc", "x_usart", "fault"])
except Exception as e:
    print("Writing initial data to the CSV file failed ... aborting!")
    print(e)
    exit(-1)

# Iterate over all data
for i in range(len(snid)):
    try:
        # Write a row to the CSV file
        csv_o.writerow([snid[i], tstmp[i], sntime[i], t_air[i], t_soil[i], h_air[i], h_soil[i], x_nt[i], x_vs[i], x_bat[i], x_art[i], x_rst[i], x_ic[i], x_adc[i], x_usart[i], label[i]])
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
