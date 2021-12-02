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
└── dcdc_converter      : Analysis of the DC/DC converter's efficiency
```


### Active Phase ###

The active phase was analyzed utilizing a [Joulescope](https://www.joulescope.com/).
We measured the energy consumption of the active phase with a sampling frequency of 2\,MHz and a reduction frequency of 2\,Hz.
The dataset (`active_phase-record.csv`) contains the measurements of the Joulescope in the format:  
`time [s] , current [A] , voltage [V]`

The dataset can be visualized using the provided Python3 script (`visualize_dataset.py`) with:  
  `python3 visualize_dataset.py active_phase-record.csv 1`  
To enhance the visibility of the resulting plot (`active_phase-plot.svg`) the mean average of `N` samples is first calculated to reduce the dataset size (e.g., with `N = 500`).
The resulting reduced dataset is then plotted.


### DC/DC Converter ###

Dataset recorded from indoor deployment (sensor node `41CC57CC` located in office) between 2021-11-22 00:00:00 and 2021-11-29 00:00:00 with several small events when the nearby windows were opened to air the room.
The update interval was 1 minute.
