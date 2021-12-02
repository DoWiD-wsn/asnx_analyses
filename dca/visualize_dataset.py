#####
# @brief    Visualize a given base dataset
#
# Python script to generate a SVG graph of the data of a given base
# dataset via matplotlib. It generates one figure with two subplots:
# 1.) use case-related data (air/soil temperature/humidity)
# 2.) self-diagnostic data (fault indicators) & fault label
# The input file (CSV) format expected is:
#   SNID, UNIX_timestamp, SNTIME,
#   Tair, Tsoil, Hair, Hsoil,
#   Xnt, Xvs, Xbat, Xart, Xrst, Xic, Xadc, Xusart,
#   fault_label
# Thereby, the first line contains the header and can be ignored.
#
# The base dataset has to be given as parameter, for example:
# => $ python3 visualize_dataset.py datasets/asnx_base_data.csv 1
# where the 2nd parameter defines the transparency of the SVG output
#
# @file     visualize_dataset.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/11/30
#####


##### LIBRARIES ########################
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

# Date/time format
fmt         = '%Y-%m-%d %H:%M:%S'
xfmt        = md.DateFormatter('%H:%M\n%m/%d')


##### METHODS ##########################
# See https://www.codegrepper.com/code-examples/python/python+datetime+round+to+nearest+hour
def hour_rounder(t):
    # Rounds to nearest hour by adding a timedelta hour if minute >= 30
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
               +timedelta(hours=t.minute//30))


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
SVG_OUTPUT = OUT_DIR+Path(CSV_INPUT).stem + "-plot.svg"
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

### Prepare data arrays/lists/etc.
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
for row in csv_i:
    # ignore first line
    if line_count>0:
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

### Plot the data via matplotlib
# get lowest (first) and highest (last) time
x_first = hour_rounder(time[0])
x_last  = hour_rounder(time[-1])

# prepare figure
fig = plt.figure(figsize=(15,8), dpi=300, tight_layout=True)
ax1 = fig.add_subplot(211)
ax1b = ax1.twinx()
ax2 = fig.add_subplot(212)
ax2b = ax2.twinx()

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
lns1 = ax1.plot(time, Tair, '-',  label=r"$T_{air}$", color="darkgreen")
lns2 = ax1.plot(time, Tsoil, '-',  label=r"$T_{soil}$", color="limegreen")
lns3 = ax1b.plot(time, Hair, '-',  label=r"$H_{air}$", color="darkblue")
lns4 = ax1b.plot(time, Hsoil, '-',  label=r"$H_{soil}$", color="dodgerblue")
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
ax2b.set_xlim(x_first,x_last)
ax2b.xaxis.set_major_locator(AutoLocator())
ax2b.xaxis.set_minor_locator(AutoMinorLocator(2))
ax2b.set_xlabel('time [H:M]')
ax2b.xaxis.set_major_formatter(xfmt)
# y-axis
ax2.set_ylabel("fault indicator")
ax2.set_ylim(0,1.0)
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.yaxis.set_major_locator(MultipleLocator(0.2))
ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
ax2b.set_ylabel("fault label")
ax2b.set_ylim(0,1.0)
ax2b.spines['top'].set_visible(False)
ax2b.spines['left'].set_visible(False)
ax2b.xaxis.set_ticks_position('bottom')
ax2b.spines['bottom'].set_position(('data',0))
ax2b.yaxis.set_ticks_position('right')
ax2b.yaxis.set_major_locator(MultipleLocator(0.2))
ax2b.yaxis.set_minor_locator(AutoMinorLocator(2))
# plot data
lns1 = ax2.plot(time, Xnt, '-',  label=r"$\chi_{NT}$", color="midnightblue")
lns2 = ax2.plot(time, Xvs, '-',  label=r"$\chi_{VS}$", color="darkgreen")
lns3 = ax2.plot(time, Xbat, '-',  label=r"$\chi_{BAT}$", color="rosybrown")
lns4 = ax2.plot(time, Xart, '-',  label=r"$\chi_{ART}$", color="orangered")
lns5 = ax2.plot(time, Xrst, '-',  label=r"$\chi_{RST}$", color="fuchsia")
lns6 = ax2.plot(time, Xic, '-',  label=r"$\chi_{IC}$", color="lime")
lns7 = ax2.plot(time, Xadc, '-',  label=r"$\chi_{ADC}$", color="aqua")
lns8 = ax2.plot(time, Xusart, '-',  label=r"$\chi_{USART}$", color="gold")
lns9 = ax2b.plot(time, label, '-',  label="fault label", linewidth=1, color="cornflowerblue")
lns = lns1+lns2+lns3+lns4+lns5+lns6+lns7+lns8+lns9
labs = [l.get_label() for l in lns]
ax2b.legend(lns, labs, ncol=9, loc='upper center', facecolor='white', framealpha=1)

### Finish figure
if TRANSPARENT:
    plt.savefig(SVG_OUTPUT, transparent=True)
else:
    plt.savefig(SVG_OUTPUT, transparent=False)
plt.cla()
plt.clf()
plt.close()
