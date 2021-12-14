# Energy Efficiency Analyses #

In this directory, analyses concerning the energy efficiency of our ASN(x) are located.
In this context, we particularly analyzed:

* **the efficiency of the components**
* **the efficiency of the entire node**

Regarding the former, we especially analyzed the power consumption of the diagnostic measures and the efficiency of the used DC/DC converter (i.e., TPS63031DSKR).
For the latter, the overall consumption of the entire sensor node is analyzed.
We measured the power consumption in the active states as well as in power-down mode.
Thereby, we included the lengths of the particular phases in our measurements to get the resulting energy consumption.
This information was in turn used to estimate the expected battery life.

Information on the single analyses is provided below.
In addition, we added example plots of the acquired data for visual inspection.


## Directory structure ##

```
.
├── active_phase        : Detailed analysis of the ASN(x)' active phase
├── dcdc_converter      : Analysis of the DC/DC converter's efficiency
└── mcu_frequency       : Analysis of the effect of F_CPU on energy efficiency
```


### Active Phase ###

The active phase was analyzed utilizing a [Joulescope](https://www.joulescope.com/).
We measured the energy consumption of the active phase with a sampling frequency of 2\,MHz and a reduction frequency of 2\,Hz.
The dataset (`active_phase-record.csv`) contains the measurements of the Joulescope in the format:  
`time [s] , current [A] , voltage [V]`

The dataset can be visualized using the provided Python3 script (`visualize_dataset.py`) with:  
  `python3 visualize_dataset.py active_phase-record.csv 1`  
To enhance the visibility of the resulting plot the mean average of `N` samples is first calculated to reduce the dataset size (e.g., with `N = 500`).
The resulting reduced dataset is then plotted.
An example plot of the provided dataset is available in `active_phase-record-plot.svg`.


### DC/DC Converter ###

The efficiency of the used DC/DC converter (i.e., TPS63031DSKR) was measured using the `supply_voltage_sweep.py` example script of our [embedded testbench (ETB](https://github.com/DoWiD-wsn/embedded_testbench).
During this analysis, the ASN(x) was put to an active mode where it stayed idling in an endless loop.
The resulting measurements of the current consumption at a decreasing supply voltage (from 3.5 down to 1.5 V) are available in `dcdc_idle-record.csv`.
Reference measurements of the power consumption of a directly supplied ASN(x), by bypassing the DC/DC converter, are available in `dcdc_idle_ref.csv`.
Both datasets contain the measurements in the format:  
`voltage [dec] , voltage [V] , current [mA] , power [mW]`
where the first voltage is the value written to the ETB's DC/DC converter used to control the ASN(x)' supply voltage.

The datasets can be visualized using the provided Python3 script (`visualize_dataset.py`) with:  
  `python3 visualize_dataset.py 1`  
An example plot of the provided dataset is available in `dcdc_idle-record-plot.svg`.


### MCU Frequency ###

Currently, the ASN(x) is clocked by a 4 MHz external quartz crystal.
The clock frequency has, aside from the supply voltage, an impact on the dynamic power dissipation and, thus, the total energy consumption of the sensor node.
To confirm the choice of the oscillator frequency, several experiments were conducted.
In this context, a [Joulescope](https://www.joulescope.com/) was used for the measurements.
The results and findings are collected in this directory.
