#####
# @brief    Compare the effect of the optimization concerning -- context assessment (alternative danger)
#
# The script takes a dataset as input (i.e., base dataset, fault-induced
# dataset, or fault signature) and runs the modified dDCA with different
# calculation options concerning the context assessment. The results
# are plottet via matplotlib where the focus is on the aspect to compare
# like, in this case, the context assessment.
#
# The following options are compared:
# 1) single cell, lifetime = 1 (like min-dDCA)
# 2) N cells -> mean value
# 3) N cells -> voting
# 4) N cells -> context aggregation (total k value)
# 5) N cells -> context aggregation (mean k value)
# 
# @file     opt_dc_context_alt.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/20
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
# for plotting
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})
from matplotlib import rc
rc('mathtext', default='regular')
from matplotlib.ticker import (AutoLocator, AutoMinorLocator, MultipleLocator)
import matplotlib.dates as md


##### GLOBAL VARIABLES #####
# Output directory
OUT_DIR     = "plots/"

# dendritic cell lifetime/population
DC_M            = 5
# number of sensor values for std-dev evaluation
STDDEV_N        = 10
# sensitivity of safe indicator
SAFE_SENS       = 0.1

# Date/time format
fmt         = '%Y-%m-%d %H:%M:%S'


##### VISUALIZATION ####################
### Check input file
# Parameter given
if (len(sys.argv) < 2):
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

# Base SVG filename on input filename
SVG_OUTPUT = OUT_DIR+Path(CSV_INPUT).stem + "-opt_dc_context_alt-plot.svg"
# Use 2nd parameter for transparency
TRANSPARENT = None
if len(sys.argv) >= 3:
    TRANSPARENT = int(sys.argv[2])
else:
    TRANSPARENT = 0

### Get data from CSV file
csv_i = None
try:
    # Open CSV input file
    csv_f = open(CSV_INPUT, 'r')
    # Get a CSV reader
    csv_i = csv.reader(csv_f, delimiter=',')
except Exception as e:
    print("Cannot open the CSV input file \"%s\" ... aborting!" % CSV_INPUT)
    exit(-1)

##### READ THE INPUT DATA ######
index       = []
# general
snid        = []
tstmp       = []
time        = []
sntime      = []
# use case data
Tair        = []
Tsoil       = []
Hair        = []
Hsoil       = []
# fault indicator
Xnt         = []
Xvs         = []
Xbat        = []
Xart        = []
Xrst        = []
Xic         = []
Xadc        = []
Xusart      = []
# fault label
label       = []

# Iterate over entries
line_count = 0
i = 0
for row in csv_i:
    # ignore first line
    if line_count>0:
        index.append(i)
        i += 1
        
        ### META DATA ###
        snid.append(str(row[0]))
        tmp = int(row[1])
        tstmp.append(tmp)
        time.append(datetime.utcfromtimestamp(tmp))
        sntime.append(int(row[2]))
        
        ### USE CASE DATA ###
        Tair.append(round(float(row[3]),2))
        Tsoil.append(round(float(row[4]),2))
        Hair.append(round(float(row[5]),2))
        Hsoil.append(round(float(row[6]),2))
        
        ### FAULT INDICATOR ###
        Xnt.append(round(float(row[7]),2))
        Xvs.append(round(float(row[8]),2))
        Xbat.append(round(float(row[9]),2))
        Xart.append(round(float(row[10]),2))
        Xrst.append(round(float(row[11]),2))
        Xic.append(round(float(row[12]),2))
        Xadc.append(round(float(row[13]),2))
        Xusart.append(round(float(row[14]),2))
        
        ### FAULT LABEL ###
        label.append(int(row[15]))
    line_count = line_count + 1


###### SIMULATE DDCA WITH DIFFERENT SETTINGS #####
# use case data history
t_air_a     = []
t_soil_a    = []
h_air_a     = []
h_soil_a    = []
# DCA indicators
antigen     = []
danger      = []
safe        = []
# Fault context
context1    = []
context2    = []
context3    = []
context4    = []
context5    = []
# List of dendritic cells
dcs         = []

for i in range(len(snid)):
    ### ANTIGEN ###
    # use SNID as antigen
    # comment: does not allow spatial correlation of several nodes
    antigen_t = snid[i]
    # Store antigen
    antigen.append(antigen_t)
    
    ### DANGER ###
    # Use X_NT as danger1
    danger1_t = Xnt[i]
    # Use X_VS as danger2
    danger2_t = Xvs[i]
    # Use X_BAT as danger3
    danger3_t = Xbat[i]
    # Use X_ART as danger4
    danger4_t = Xart[i]
    # Use X_RST as danger5
    danger5_t = Xrst[i]
    # Use X_IC as danger6
    danger6_t = Xic[i]
    # Use X_ADC as danger7
    danger7_t = Xadc[i]
    # Use X_USART as danger8
    danger8_t = Xusart[i]
    # Calculate final danger indicators
    danger_t = round((danger1_t + danger2_t + danger3_t + danger4_t + danger5_t + danger6_t + danger7_t + danger8_t),2)
    danger.append(danger_t)
    
    ### SAFE ###
    # Store last N sensor values
    t_air_a.append(Tair[i])
    if len(t_air_a)>STDDEV_N:
        t_air_a.pop(0)
    t_soil_a.append(Tsoil[i])
    if len(t_soil_a)>STDDEV_N:
        t_soil_a.pop(0)
    h_air_a.append(Hair[i])
    if len(h_air_a)>STDDEV_N:
        h_air_a.pop(0)
    h_soil_a.append(Hsoil[i])
    if len(h_soil_a)>STDDEV_N:
        h_soil_a.pop(0)
    
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
    safe_sig  = round(math.exp(-max(safe1_t, safe2_t, safe3_t, safe4_t)*SAFE_SENS),2)
    safe.append(safe_sig)


    ### DC UPDATE ###
    context_t = danger_t - safe_sig
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


    ### CX ASSIGNMENT ###
    # option 1
    context1_t = 1 if dcs[-1]["context"]>=0 else 0
    context1.append(context1_t)
    # option 2
    state = 0
    for dc in dcs:
        state = state + 1 if dc["context"]>=0 else state
    state = state/len(dcs)
    context2_t = state
    context2.append(context2_t)
    # option 3
    state = 0
    for dc in dcs:
        state = state + 1 if dc["context"]>=0 else state
    state = state/len(dcs)
    context3_t = 1 if state>0.5 else 0
    context3.append(context3_t)
    # option 4
    k_sum = 0
    for dc in dcs:
        k_sum = k_sum + dc["context"]
    context4_t = 1 if k_sum>=0 else 0
    context4.append(context4_t)
    # option 5
    k_sum = 0
    for dc in dcs:
        k_sum = k_sum + dc["context"]
    k_sum = k_sum/len(dcs)
    context5_t = 1 if k_sum>=0 else 0
    context5.append(context5_t)


##### PLOT THE DATA VIA MATPLOTLIB ####
# get lowest (first) and highest (last) value of interest
x_first = index[0]
x_last  = index[-1]

# prepare figure
fig = plt.figure(figsize=(15,8), dpi=300, tight_layout=True)
ax1 = fig.add_subplot(311)
ax1b = ax1.twinx()
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)
ax3b = ax3.twinx()

### use case data ###
# grid
ax1.grid(which='major', color='#CCCCCC', linestyle=':')
# x-axis
ax1.set_xlim(x_first,x_last)
ax1.xaxis.set_major_locator(AutoLocator())
ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
ax1.set_xticklabels([])
ax1b.set_xlim(x_first,x_last)
ax1b.set_xticklabels([])
# y-axis
ax1.set_ylabel(r"temperature [$^{\circ}$C]")
ax1.set_ylim(0,50)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.yaxis.set_major_locator(MultipleLocator(10))
ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
ax1b.set_ylabel("relative humidity [%]")
ax1b.set_ylim(0,100)
ax1b.spines['top'].set_visible(False)
ax1b.spines['left'].set_visible(False)
ax1b.xaxis.set_ticks_position('bottom')
ax1b.spines['bottom'].set_position(('data',0))
ax1b.yaxis.set_ticks_position('right')
ax1b.yaxis.set_major_locator(MultipleLocator(20))
ax1b.yaxis.set_minor_locator(AutoMinorLocator(2))
# plot data
lns1 = ax1.plot(index, Tair, '-',  label=r"$T_{air}$", color="darkgreen")
lns2 = ax1.plot(index, Tsoil, '-',  label=r"$T_{soil}$", color="limegreen")
lns3 = ax1b.plot(index, Hair, '-.',  label=r"$H_{air}$", color="darkblue")
lns4 = ax1b.plot(index, Hsoil, '-.',  label=r"$H_{soil}$", color="dodgerblue")
lns = lns1+lns2+lns3+lns4
labs = [l.get_label() for l in lns]
ax1b.legend(lns, labs, ncol=4, loc='lower center', facecolor='white', framealpha=1)

### indicator plot ###
# grid
ax2.grid(which='major', color='#CCCCCC', linestyle=':')
# x-axis
ax2.set_xlim(x_first,x_last)
ax2.xaxis.set_major_locator(AutoLocator())
ax2.xaxis.set_minor_locator(AutoMinorLocator(2))
ax2.set_xticklabels([])
# y-axis
ax2.set_ylabel("fault indicators")
ax2.set_ylim(0,1.1)
ax2.yaxis.set_major_locator(MultipleLocator(0.2))
ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
# plot data
ax2.plot(index, Xnt, '-',  label=r"$\chi_{NT}$", color="midnightblue")
ax2.plot(index, Xvs, '-',  label=r"$\chi_{VS}$", color="darkgreen")
ax2.plot(index, Xbat, '-',  label=r"$\chi_{BAT}$", color="rosybrown")
ax2.plot(index, Xart, '-',  label=r"$\chi_{ART}$", color="orangered")
ax2.plot(index, Xrst, '-',  label=r"$\chi_{RST}$", color="fuchsia")
ax2.plot(index, Xic, '-',  label=r"$\chi_{IC}$", color="lime")
ax2.plot(index, Xadc, '-',  label=r"$\chi_{ADC}$", color="aqua")
ax2.plot(index, Xusart, '-',  label=r"$\chi_{USART}$", color="gold")
ax2.legend(framealpha=1, ncol=8, loc='upper center')

### DCA plot ###
# grid
ax3.grid(which='major', color='#CCCCCC', linestyle=':')
# x-axis
ax3.set_xlim(x_first,x_last)
ax3.xaxis.set_major_locator(AutoLocator())
ax3.xaxis.set_minor_locator(AutoMinorLocator(2))
ax3.set_xlabel('sensor updates')
ax3b.set_xlim(x_first,x_last)
ax3b.xaxis.set_major_locator(AutoLocator())
ax3b.xaxis.set_minor_locator(AutoMinorLocator(2))
# y-axis
ax3.set_ylabel("danger/fault indicators")
ax3.set_ylim(0,1.1)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.yaxis.set_major_locator(MultipleLocator(0.2))
ax3.yaxis.set_minor_locator(AutoMinorLocator(2))
ax3b.set_ylabel("fault context")
ax3b.set_ylim(0,1.1)
ax3b.spines['top'].set_visible(False)
ax3b.spines['left'].set_visible(False)
ax3b.xaxis.set_ticks_position('bottom')
ax3b.spines['bottom'].set_position(('data',0))
ax3b.yaxis.set_ticks_position('right')
ax3b.yaxis.set_major_locator(MultipleLocator(0.2))
ax3b.yaxis.set_minor_locator(AutoMinorLocator(2))
# plot data
lns1 = ax3.plot(index, danger, '--',  label="danger", color="red")
lns2 = ax3.plot(index, safe, '-.',  label="safe", color="green")
###
lns3 = ax3.plot(index, context1, '-',  label="Cx 1", color="thistle")
lns4 = ax3.plot(index, context2, '-',  label="Cx 2", color="violet")
lns5 = ax3.plot(index, context3, '-',  label="Cx 3", color="fuchsia")
lns6 = ax3b.plot(index, context4, '-',  label="Cx 4", color="darkorchid")
lns7 = ax3b.plot(index, context5, '-',  label="Cx 5", color="indigo")
###
lns8 = ax3b.plot(index, label, ':',  label="fault label", color="cornflowerblue")
lns = lns1+lns2+lns3+lns4+lns5+lns6+lns7+lns8
labs = [l.get_label() for l in lns]
ax3b.legend(lns, labs, loc='center right', facecolor='white', framealpha=1)

### Finish figure
if TRANSPARENT:
    plt.savefig(SVG_OUTPUT, transparent=True)
else:
    plt.savefig(SVG_OUTPUT, transparent=False)
plt.cla()
plt.clf()
plt.close()
