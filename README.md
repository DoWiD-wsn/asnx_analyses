# ASN(x) Analyses #

The **A**VR-based **S**ensor **N**ode with **X**bee, short **ASN(x)**, is a low-cost platform for low-power sensor nodes specifically for (environmental) monitoring applications, both indoor and outdoor.
In this repository, information and data acquired by the analyses of its functioning as well as ASN(x)-based use cases and approaches are collected.
For example, this repository includes datasets recorded from our wireless sensor network (WSN) deployments, the results of our ETB-based experiments, and automated result extraction/visualization Python scripts used in the course of academic dissemination.

For more information on the ASN(x) (and its design) refer to [AVR-based Sensor Node](https://github.com/DoWiD-wsn/avr-based_sensor_node).
Details on the cluster head and sink node used in our testbed can be found in [RPi-based Cluster Head](https://github.com/DoWiD-wsn/RPi_cluster_head) and [RPi-based Sink Node](https://github.com/DoWiD-wsn/RPi_sink_node), respectively.
Additionally, information on the embedded testbench (short *ETB*) that was used for the majority of our lab experiments is given in [Embedded Testbench](https://github.com/DoWiD-wsn/embedded_testbench).

## Contents ##

```
.
├── dca                 : DCA-based fault detection
└── energy_efficiency   : General energy efficiency
```

### DCA ###

In the ``dca`` directory, data related to our modified deterministic dendritic cell algorithm (dDCA)-based fault detection approach are located.
This approach detects node level faults by combining node-level diagnostic information with sensor data-related metrics to improve the overall fault detectability and to enable the distinction between rare but proper events in the sensed physical phenomena from fault-induced data distortion.


### Energy-Efficiency ###

the ``energy_efficiency`` directory contains data used for the analysis of the ASN(x)' energy efficiency, that is, how much energy the node requires in (1) sleep mode, (2) active mode, and (3) for the implemented fault diagnostics.


## Contributors ##

* **Dominik Widhalm** - [***DC-RES***](https://informatics.tuwien.ac.at/doctoral/resilient-embedded-systems/) - [*UAS Technikum Wien*](https://embsys.technikum-wien.at/staff/widhalm/)

Contributions of any kind or feedback are highly welcome.
For coding bugs (i.e., in the Python scripts) or minor improvements simply use pull requests.
However, for major changes or general discussions please contact [Dominik Widhalm](mailto:widhalm@technikum-wien.at?subject=ASN(x)%20Analyses%20on%20GitHub).


## Related Publications ##

- Dominik Widhalm, Karl M. Goeschka, and Wolfgang Kastner, "*An open-source wireless sensor node platform with active node-level reliability for monitoring applications*", Sensors 21, no. 22: 7613, 2021, DOI: [10.3390/s21227613](https://doi.org/10.3390/s21227613)
- Dominik Widhalm, Karl M. Goeschka, and Wolfgang Kastner, "*Undervolting on wireless sensor nodes: a critical perspective*", in The 23rd International Conference on Distributed Computing and Networking (ICDCN 2022), January 4-7, 2022, DOI: [10.1145/3491003.3491018O](https://doi.org/10.1145/3491003.3491018O)
- Dominik Widhalm, Karl M. Goeschka, and Wolfgang Kastner, "*Is Arduino a suitable platform for sensor nodes?*", in The 47th Annual Conference of the IEEE Industrial Electronics Society (IECON 2021), October 13-16, 2021, DOI: [10.1109/IECON48115.2021.9589479](https://doi.org/10.1109/IECON48115.2021.9589479)
- Dominik Widhalm, Karl M. Goeschka, and Wolfgang Kastner, "*Node-level indicators of soft faults in wireless sensor networks*", in The 40th International Symposium on Reliable Distributed Systems (SRDS 2021), September 20-23, 2021, DOI: [10.1109/SRDS53918.2021.00011](https://doi.org/10.1109/SRDS53918.2021.00011)


## License

The material contained in this repository is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
