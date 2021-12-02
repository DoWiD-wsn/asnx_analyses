#####
# @brief    Visualize the DC/DC efficiency based on given datasets
#
# Python script to generate a SVG graph of the data of a given
# from two datasets, one for the actual consumption and the second
# providing reference measurements.
# The input files (CSV) format expected is:
#   voltage [dec], voltage [V], current [mA], power [mW]
#
# The transparency of the SVG output can be adjsuted via a parameter:
# => $ python3 visualize_dataset.py 1
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
# Measurement record
CSV_INPUT     = "dcdc_idle-record.csv"
# Reference measurements
CSV_INPUT_REF = "dcdc_idle_ref.csv"


##### VISUALIZATION ####################
# Base SVG filename on input filename
SVG_OUTPUT = Path(CSV_INPUT).stem + "-plot.svg"
# Use 2nd parameter for transparency
TRANSPARENT = None
if len(sys.argv) == 2:
    TRANSPARENT = int(sys.argv[1])
else:
    TRANSPARENT = 0

### Get data from CSV file
# Reference measurement (directly supplied 3.3 V)
dec,volt,current,power = np.loadtxt(CSV_INPUT_REF, unpack=True, delimiter=',', skiprows=1)
i_sum = 0
for value in current:
    i_sum += value
i_ref = round(i_sum / len(current),3)
p_ref = round((i_ref * 3.3),3)
# clear lists
dec = []
volt = []
current = []
power = []

# Power measurement (externally supplied via DC/DC converter)
dec,volt,current,power = np.loadtxt(CSV_INPUT, unpack=True, delimiter=',', skiprows=1)
for i in range(len(current)):
    # Cut values below zero (measurement errors)
    if current[i]<0:
        current[i]=0.0
# intermediate storage
cnt_d  = dict()
v_dict = dict()
i_dict = dict()
v_mean = []
i_min  = []
i_mean = []
i_max  = []
p_min  = []
p_mean = []
p_max  = []
p_eff  = []
# prepare dictionaries with measurements ordered by decimal voltage input
for i in range(len(dec)):
    output = int(dec[i])
    if output not in cnt_d:
        cnt_d[output] = 0
        v_dict[output] = []
        i_dict[output] = []
    cnt_d[output] += 1
    v_dict[output].append(volt[i])
    i_dict[output].append(current[i])
# calculate min/mean/max
for step in sorted(cnt_d.keys()):
    # get mean voltage at step level
    v_sum = 0
    for value in v_dict[step]:
        v_sum += value
    v_mean.append(round(v_sum/cnt_d[step], 3))
    # get min/mean/max currents at step level
    i_sum = 0
    i_min_step  = 9999
    i_max_step  = 0
    for value in i_dict[step]:
        i_sum += value
        if value < i_min_step:
            i_min_step = value
        if value > i_max_step:
            i_max_step = value
    i_min.append(i_min_step)
    i_mean.append(round(i_sum/cnt_d[step], 3))
    i_max.append(i_max_step)
# calculate power values
for i in range(len(v_mean)):
    p_min.append(round(v_mean[i] * i_min[i],3))
    p_mean.append(round(v_mean[i] * i_mean[i],3))
    p_max.append(round(v_mean[i] * i_max[i],3))
# calculate power efficiency
for i in range(len(v_mean)):
    # Check for non-working region
    if(i_mean[i] < 1.0):
        p_eff.append(0.0)
    else:
        # useful power / total power
        p_eff.append((p_ref/p_mean[i]) * 100)
# prepare line data for reference measurement
i_ref_t = [i_ref for i in range(len(cnt_d))]
p_ref_t = [p_ref for i in range(len(cnt_d))]


##### PLOT DATA ######
# get lowest (first) and highest (last) voltage
x_first = round(min(v_mean),1)
x_last = round(max(v_mean),1)

# prepare figure
fig = plt.figure(figsize=(12,4), dpi=150, tight_layout=True)
ax1 = fig.add_subplot(111)
ax2 = ax1.twinx()

# grid
ax1.grid(which='major', color='#CCCCCC', linestyle=':')
# x-axis
ax1.set_xlabel('supply voltage [V]')
ax1.set_xlim(x_first,x_last)
ax1.xaxis.set_major_locator(MultipleLocator(0.25))
ax1.xaxis.set_minor_locator(AutoMinorLocator(2))
ax1.xaxis.set_ticks_position('bottom')
# y-axis 1 - power axis
ax1.set_ylabel('power consumption [mW]')
ax1.set_ylim(0,65)
ax1.spines['top'].set_visible(False)
ax1.spines['right'].set_visible(False)
ax1.spines['bottom'].set_position(('data',0))
ax1.yaxis.set_ticks_position('left')
ax1.spines['left'].set_position(('data',x_first))
ax1.yaxis.set_major_locator(MultipleLocator(10))
ax1.yaxis.set_minor_locator(AutoMinorLocator(4))
# y-axis 2 - efficiency axis
ax2.set_ylabel("power efficiency [%]")
ax2.set_ylim(0,97.5)
ax2.spines['top'].set_visible(False)
ax2.spines['left'].set_visible(False)
ax2.xaxis.set_ticks_position('bottom')
ax2.spines['bottom'].set_position(('data',0))
ax2.yaxis.set_ticks_position('right')
ax2.spines['right'].set_position(('data',x_last))
ax2.yaxis.set_major_locator(MultipleLocator(10))
ax2.yaxis.set_minor_locator(AutoMinorLocator(2))
# plot data
lns1 = ax1.plot(v_mean, p_mean, '--',  label=r"$\overline{P_{in}(v)}$", linewidth=1, color="darkviolet")
ax1.fill_between(v_mean, p_min, p_max, alpha=0.2, antialiased=True, color="darkviolet")
lns2 = ax1.plot(v_mean, p_ref_t, '-.',  label=r"$\overline{P_{ref}}$", linewidth=1, color="magenta")
lns3 = ax2.plot(v_mean, p_eff, '-',  label=r"$\overline{\eta}$", linewidth=1, color="green")

# Prepare legend
lns = lns1+lns2+lns3
labs = [l.get_label() for l in lns]
ax2.legend(lns, labs, loc='center right', facecolor='white', framealpha=1)

### Finish figure
if TRANSPARENT:
    plt.savefig(SVG_OUTPUT, transparent=True)
else:
    plt.savefig(SVG_OUTPUT, transparent=False)
plt.cla()
plt.clf()
plt.close()
