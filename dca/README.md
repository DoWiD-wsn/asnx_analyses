# DCA Analyses #

In this directory, analyses concerning our modified deterministic dendritic cell algorithm (dDCA)-based fault detection approach are located.
This approach detects node level faults by combining node-level diagnostic information with sensor data-related metrics to improve the overall fault detectability and to enable the distinction between rare but proper events in the sensed physical phenomena from fault-induced data distortion.

Correspondingly, we provide pre-recorded sensor data (from current and previous deployments), node fault signatures (from previous and current experiments), and Python scripts to:

* **Visualize a given dataset** (see `visualize_dataset.py`):  
  Example call: `python3 visualize_dataset.py datasets/asnx_base_data.csv 1`  
  Default output filename: input filename ending with `-plot.svg`  
  Default output directory: `plots/`
* **Visualize a given fault** (see `visualize_fault.py`):  
  Example call: `python3 visualize_fault.py fault_signatures/fault-bad_connection.csv 1`  
  Default output filename: input filename ending with `-plot.svg`  
  Default output directory: `plots/`
* **Simulate the modified dDCA on a given dataset** (see `simulate_ddca.py`)  
  Example call: `python3 simulate_ddca.py datasets/asnx_base_data.csv`  
  Default output filename: input filename ending with `-ddca.csv`  
  Default output directory: `results/`
* **Visualize a given dDCA-extended dataset** (see `visualize_ddca_dataset.py`)  
  Example call: `python3 visualize_ddca_dataset.py results/base_-_indoor_-_stable-ddca.csv 1`  
  Default output filename: input filename ending with `-plot.svg`  
  Default output directory: `plots/`
* **Analyze and compare the output of the dDCA simulation** (see `assess_ddca_output.py`)  
  Example call: `python3 assess_ddca_output.py results/base_-_indoor_-_stable-ddca.csv`  
  Default output filename: input filename ending with `-result.csv`  
  Default output directory: `results/`

Information on the single base datasets and the fault signatures are provided below.
In addition, we added example plots of the base datasets and fault signature for visual inspection.


## Directory structure ##

```
.
├── base_datasets       : Base datasets as described below
├── fault_signatures    : Fault signatures as described below
└── plots               : Example plots of base datasets and fault signatures
```


## Base Datasets ##

```
./base_datasets/
├── base_-_indoor_-_stable.csv      : Indoor deployment with stable environmental conditions
├── base_-_indoor_-_room_airing.csv : Indoor deployment with several events (open windows to air the room)
└── base_-_outdoor_-_heavy_rain.csv : Outdoor deployment with heavy rain in second half
```

### base - indoor - stable ###

Dataset recorded from indoor deployment (sensor node `41B9FD22` located in living space) between 2021-07-04 06:00:00 and 2021-07-11 06:00:00 with no noticeable occurrences.
The update interval was 10 minutes.


### base - indoor - room airing ###

Dataset recorded from indoor deployment (sensor node `41CC57CC` located in office) between 2021-11-22 00:00:00 and 2021-11-29 00:00:00 with several small events when the nearby windows were opened to air the room.
The update interval was 1 minute.


### base - outdoor - heavy rain ###

Dataset recorded from outdoor deployment (sensor node `41CC57CC` located in Lower Austria) between 2021-08-12 04:00:00 and 2021-08-19 04:00:00 with heavy rain starting from 2021-08-16 morning.
The update interval was 10 minutes.


## Fault Signatures ##

```
./fault_signatures/
├── fault_-_bad_connection.csv      : Node fault caused by bad sensor connection
└── tba                             : Fault signatures well be added soon
```
