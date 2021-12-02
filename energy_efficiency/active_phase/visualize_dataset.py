#####
# @brief    Visualize a given Joulescope record (dataset)
#
# Python script to generate a SVG graph of the data of a given
# Joulescope record via matplotlib. It generates one figure where
# every N datapoints are reduced to their mean value for better
# visibility. This is necessary as the Joulescope record was captured
# with a sampling frequency of 2 MHz and, thus, contains many values.
# The input file (CSV) format expected is:
#   time [s], current [A], voltage [V]
#
# The Joulescope record has to be given as parameter, for example:
# => $ python3 visualize_dataset.py active_phase-record.csv 1
# where the 2nd parameter defines the transparency of the SVG output
#
# @file     visualize_dataset.py
# @author   Dominik Widhalm
# @version  1.0.0
# @date     2021/12/02
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
# CSV and number conversion functionality
import numpy as np
from scipy.interpolate import interp1d
# for plotting
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 12})
from matplotlib import rc
rc('mathtext', default='regular')
from matplotlib.ticker import (AutoLocator, AutoMinorLocator, MultipleLocator)
import matplotlib.dates as md


##### GLOBAL VARIABLES #################
# Average every N samples
N = 500


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

# Base SVG filename on input filename
SVG_OUTPUT = Path(CSV_INPUT).stem + "-plot.svg"
# Use 2nd parameter for transparency
TRANSPARENT = None
if len(sys.argv) >= 3:
    TRANSPARENT = int(sys.argv[2])
else:
    TRANSPARENT = 0

### Get data from CSV file
time,current,voltage = np.loadtxt(CSV_INPUT, unpack=True, delimiter = ',')
for i in range(len(time)):
    # Convert s to ms
    time[i] *= 1000

# Pre-process data
for i in range(len(current)):
    # Cut values below zero (measurement errors)
    if current[i]<0:
        current[i]=0.0
    # Convert A to mA
    current[i] *= 1000

# average every N consecutive values
npt = np.array(time)
npi = np.array(current)
npv = np.array(voltage)
npt_n = np.nanmean(np.pad(npt.astype(float), (0, N-npt.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)
npi_n = np.nanmean(np.pad(npi.astype(float), (0, N-npi.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)
npv_n = np.nanmean(np.pad(npv.astype(float), (0, N-npv.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)

##### Calculate power from current and voltage #####
npp_n = []
for i in range(len(npi_n)):
    npp_n.append(npi_n[i] * npv_n[i])


##### PLOT DATA ######
# Get first and last time
x_first = min(time)
x_last = max(time)

# prepare figure
fig = plt.figure(figsize=(12,4), dpi=150, tight_layout=True)
ax1 = fig.add_subplot(111)

# grid
ax1.grid(which='major', color='#CCCCCC', linestyle=':')
# x-axis
ax1.set_xlabel('time [ms]')
ax1.set_xlim(x_first,x_last)
ax1.xaxis.set_major_locator(MultipleLocator(200))
ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
ax1.xaxis.set_ticks_position('bottom')
# y-axis
ax1.set_ylabel('power consumption [mW]')
ax1.set_ylim(0,105)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_position(('data',0))
ax1.yaxis.set_ticks_position('left')
ax1.spines['left'].set_position(('data',x_first))
ax1.yaxis.set_major_locator(MultipleLocator(10))
ax1.yaxis.set_minor_locator(AutoMinorLocator(2))
# plot data
ax1.plot(npt_n, npp_n, '-',  label=r"$p(t)$", linewidth=1, color="darkviolet")

# Prepare legend
ax1.legend(loc='upper right', facecolor='white', framealpha=1)

### Finish figure
if TRANSPARENT:
    plt.savefig(SVG_OUTPUT, transparent=True)
else:
    plt.savefig(SVG_OUTPUT, transparent=False)
plt.cla()
plt.clf()
plt.close()
