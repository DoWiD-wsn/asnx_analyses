#!/usr/bin/env python3

########################################################################
#   PLOT JOULESCOPE CSV                                                #
#                                                                      #
#   Author: Dominik Widhalm                                            #
#   Date:   2021-12-29                                                 #
#                                                                      #
#   Plot the data acquired with the Joulescope.                        #
#                                                                      #
########################################################################

##### LIBRARIES ########################
# basic math
import math
# To handle the command line parameter
import sys
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
from matplotlib.ticker import (AutoMinorLocator, MultipleLocator)


##### GLOBAL VARIABLES #####
# Number of consecutive values to average
N = 500
# Start index (set to 'None' if not used)
start = None
# End index (set to 'None' if not used)
end = None

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

# Cut values below zero (measurement errors)
for i in range(len(current)):
    if current[i]<0:
        current[i]=0.0
    # Convert A to mA
    current[i] *= 1000

# Calculate resulting power [mW]
power = []
for i in range(len(current)):
    power.append(current[i]*voltage[i])

# Get first and last time
x_first = min(time) if start is None else start
x_last = max(time) if end is None else end

### Average every N consecutive values
# time
npt = np.array(time)
npt_n = np.nanmean(np.pad(npt.astype(float), (0, N - npt.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)
# current
npi = np.array(current)
npi_n = np.nanmean(np.pad(npi.astype(float), (0, N - npi.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)
# voltage
npv = np.array(voltage)
npv_n = np.nanmean(np.pad(npv.astype(float), (0, N - npv.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)
# power
npp = np.array(power)
npp_n = np.nanmean(np.pad(npp.astype(float), (0, N - npp.size%N), mode='constant', constant_values=np.NaN).reshape(-1, N), axis=1)


##### PLOT DATA ######
# Create subplots
fig = plt.figure(figsize=(12,9), dpi=150, tight_layout=True)
ax1 = fig.add_subplot(311)
ax2 = fig.add_subplot(312)
ax3 = fig.add_subplot(313)

### current
ax1.grid(which='major', color='#CCCCCC', linestyle=':')
ax1.set_ylabel('current [mA]')
ax1.set_xlim(x_first,x_last)
ax1.set_ylim(0,(max(npi_n)*1.1))
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.xaxis.set_ticks_position('bottom')
ax1.spines['bottom'].set_position(('data',0))
ax1.yaxis.set_ticks_position('left')
ax1.spines['left'].set_position(('data',x_first))
ax1.set_xticklabels([])
# plot data
ax1.plot(npt_n, npi_n, '-',  label=r"$i(t)$", color="darkred")
# legend
ax1.legend(loc='upper right', facecolor='white', framealpha=1)

### voltage
ax2.grid(which='major', color='#CCCCCC', linestyle=':')
ax2.set_ylabel('voltage [V]')
ax2.set_xlim(x_first,x_last)
ax2.set_ylim(0,(max(npv_n)*1.1))
ax2.spines['top'].set_visible(False)
ax2.spines['right'].set_visible(False)
ax2.xaxis.set_ticks_position('bottom')
ax2.spines['bottom'].set_position(('data',0))
ax2.yaxis.set_ticks_position('left')
ax2.spines['left'].set_position(('data',x_first))
ax2.set_xticklabels([])
# plot data
ax2.plot(npt_n, npv_n, '-',  label=r"$v(t)$", color="darkblue")
# legend
ax2.legend(loc='upper right', facecolor='white', framealpha=1)

### power
ax3.grid(which='major', color='#CCCCCC', linestyle=':')
ax3.set_xlabel('time [ms]')
ax3.set_ylabel('power [mW]')
ax3.set_xlim(x_first,x_last)
ax3.set_ylim(0,(max(npp_n)*1.1))
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.xaxis.set_ticks_position('bottom')
ax3.spines['bottom'].set_position(('data',0))
ax3.yaxis.set_ticks_position('left')
ax3.spines['left'].set_position(('data',x_first))
# plot data
ax3.plot(npt_n, npp_n, '-',  label=r"$p(t)$", color="darkviolet")
# legend
ax3.legend(loc='upper right', facecolor='white', framealpha=1)

### Finish figure
if TRANSPARENT:
    plt.savefig(SVG_OUTPUT, transparent=True)
else:
    plt.savefig(SVG_OUTPUT, transparent=False)
plt.cla()
plt.clf()
plt.close()
