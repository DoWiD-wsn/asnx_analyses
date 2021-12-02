#####
# @brief    Run the modified dDCA on a pre-recorded dataset
#
# Python script to simulate the functioning of the modified
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
# => $ python3 simulate_ddca.py datasets/asnx_base_data.csv
#
# @file     simulate_ddca.py
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

# dendritic cell lifetime/population
DC_M            = 3
# number of sensor values for std-dev evaluation
STDDEV_N        = 10
# sensitivity of safe indicator
SAFE_SENS       = 0.1


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
CSV_OUTPUT = OUT_DIR+Path(CSV_INPUT).stem + "-ddca.csv"

# Prepare data arrays/lists/etc.
snid        = []
tstmp       = []
sntime      = []
# use case data
t_air       = []
t_soil      = []
h_air       = []
h_soil      = []
t_air_a     = []
t_soil_a    = []
h_air_a     = []
h_soil_a    = []
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
# Fault context
context     = []
# List of dendritic cells
dcs         = []


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
        # Store last N sensor values
        t_air_a.append(t_air_t)
        if len(t_air_a)>STDDEV_N:
            t_air_a.pop(0)
        t_soil_a.append(t_soil_t)
        if len(t_soil_a)>STDDEV_N:
            t_soil_a.pop(0)
        h_air_a.append(h_air_t)
        if len(h_air_a)>STDDEV_N:
            h_air_a.pop(0)
        h_soil_a.append(h_soil_t)
        if len(h_soil_a)>STDDEV_N:
            h_soil_a.pop(0)
        
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


##################################
##### Step 2 - signal update #####
##################################
    
        ### ANTIGEN ###
        # use SNID as antigen
        # comment: does not allow spatial correlation of several nodes
        antigen_t = snid[-1]
        
        # Store antigen
        antigen.append(antigen_t)
        
        ### DANGER ###
        # Use X_NT as danger1
        danger1_t = x_nt_t
        # Use X_VS as danger2
        danger2_t = x_vs_t
        # Use X_BAT as danger3
        danger3_t = x_bat_t
        # Use X_ART as danger4
        danger4_t = x_art_t
        # Use X_RST as danger5
        danger5_t = x_rst_t
        # Use X_IC as danger6
        danger6_t = x_ic_t
        # Use X_ADC as danger7
        danger7_t = x_adc_t
        # Use X_USART as danger8
        danger8_t = x_usart_t
        # Calculate final danger indicators
        danger_t = round(min(1, (danger1_t + danger2_t + danger3_t + danger4_t + danger5_t + danger6_t + danger7_t + danger8_t)),2)
        danger.append(danger_t)
        
        ### SAFE ###
        # Safe1 - T_air relative difference
        safe1_mu = 0
        for val in t_air_a:
            safe1_mu = safe1_mu + val
        safe1_mu = safe1_mu / len(t_air_a)
        safe1_dev = 0
        for val in t_air_a:
            safe1_dev = safe1_dev + ((val-safe1_mu)**2)
        safe1_dev = safe1_dev / len(t_air_a)
        safe1_dev = math.sqrt(safe1_dev)
        safe1_t = safe1_dev
        # Safe2 - T_soil relative difference
        safe2_mu = 0
        for val in t_soil_a:
            safe2_mu = safe2_mu + val
        safe2_mu = safe2_mu / len(t_soil_a)
        safe2_dev = 0
        for val in t_soil_a:
            safe2_dev = safe2_dev + ((val-safe2_mu)**2)
        safe2_dev = safe2_dev / len(t_soil_a)
        safe2_dev = math.sqrt(safe2_dev)
        safe2_t = safe2_dev
        # Safe3 - H_air relative difference
        safe3_mu = 0
        for val in h_air_a:
            safe3_mu = safe3_mu + val
        safe3_mu = safe3_mu / len(h_air_a)
        safe3_dev = 0
        for val in h_air_a:
            safe3_dev = safe3_dev + ((val-safe3_mu)**2)
        safe3_dev = safe3_dev / len(h_air_a)
        safe3_dev = math.sqrt(safe3_dev)
        safe3_t = safe3_dev
        # Safe4 - H_soil relative difference
        safe4_mu = 0
        for val in h_soil_a:
            safe4_mu = safe4_mu + val
        safe4_mu = safe4_mu / len(h_soil_a)
        safe4_dev = 0
        for val in h_soil_a:
            safe4_dev = safe4_dev + ((val-safe4_mu)**2)
        safe4_dev = safe4_dev / len(h_soil_a)
        safe4_dev = math.sqrt(safe4_dev)
        safe4_t = safe4_dev
        # Calculate final safe indicator
        safe_t  = round(math.exp(-max(safe1_t, safe2_t, safe3_t, safe4_t)*SAFE_SENS),2)
        safe.append(safe_t)


##########################################
##### Step 3 - dendritic cell update #####
##########################################
    
        context_t = danger_t - safe_t
        # Update previous DCs
        for dc in dcs:
            dc["context"] = dc["context"] + context_t
        # Create new DC
        dcs.append({
            "antigen"   : antigen_t,
            "context"   : context_t,
        })
        # If population is full, delete oldest DC
        if len(dcs)>DC_M:
            dcs.pop(0)
    

#######################################
##### Step 4 - context assignment #####
#######################################
    
        state = 0
        for dc in dcs:
            state = state + 1 if dc["context"]>=0 else state
        state = state/len(dcs)
        context_t = 1 if state>0.5 else 0
        context.append(context_t)

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
