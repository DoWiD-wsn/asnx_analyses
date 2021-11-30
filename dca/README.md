# DCA Analyses #

In this directory, analyses concerning our modified deterministic dendritic cell algorithm (dDCA)-based fault detection approach are located.
This approach detects node level faults by combining node-level diagnostic information with sensor data-related metrics to improve the overall fault detectability and to enable the distinction between rare but proper events in the sensed physical phenomena from fault-induced data distortion.

Correspondingly, we provide pre-recorded sensor data (from current and previous deployments), node fault signatures (from previous and current experiments), and Python scripts to:

* visualize a given dataset (see `visualize_dataset.py`)
* simulate the modified dDCA on a given dataset (see `simulate_ddca.py`)
* analyze and compare the output of the dDCA simulation (see `assess_ddca_output.py`)

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


## Fault Signatures ##

```
./fault_signatures/
└── tba     : Fault signatures well be added soon
```
