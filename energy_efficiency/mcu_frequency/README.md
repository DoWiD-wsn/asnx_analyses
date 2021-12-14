# MCU Frequency Analyses #

The clock frequency has an impact on two operational aspects:

1. the (dynamic) power dissipation
2. the speed of operation

Therefore, the clock frequency needs to be chosen in such a way, that the operations are as fast as needed, but as slow as reasonably possible to keep the power consumption down.
The sensor node, however, spends only a short time in an active state and remains sleeping the rest of the time.
Consequently, the question arose whether a higher clock frequency (than 4 MHz) is beneficial as the node would perform its tasks faster and will be put back to sleeping sooner.
In other words, is the energy saved from spending less time in an active state greater than the energy surplus required for faster operation.

To answer this question, we performed several experiments, both with and without sensor attached, in which we measured the time the node stayed active and the total energy consumed during a defined period.
In the case of the experiments with a sensor attached, a DS18B20 temperature sensor (one-wire interface) was used.
However, in all experiments, a sensor measurement update interval of 2 minutes was used.
All experiments are based on the `005-dca_centralized` source code available in the ASN(x) repository's `dca` branch.
We performed the experiments with the following clock sources:

* 4 MHz external quartz crystal oscillator
* 8 MHz internal RC oscillator
* 16 MHz external quartz crystal oscillator


### Experiments with sensor ###

When clocked with the 4 MHz external quartz crystal oscillator, the sensor node stayed around 1.72 s active.
It consumed about 43.5 µAh per 10 minutes (including 5 sensor updates).

Clocked with the 8 MHz internal RC oscillator, on the other hand, the active time was insignificantly reduced to 1.71 s while the energy consumed during 10 minutes increased to 50.1 µAh.


### Experiments without sensor ###

When clocked with the 4 MHz external quartz crystal oscillator, the sensor node was active for about 637 ms.
It consumed around 18.9 µAh per 10 minutes (including 5 sensor updates).

In contrast, when clocked with the 16 MHz external quartz crystal oscillator, the active time was still about 617 ms but the energy consumption increased to 27.0 µAh.


### Conclusion ###

Our experiments confirmed that 4 MHz is a good choice for the sensor node as it provides sufficient processing speed required by, for example, the communication interfaces such as UART, but does not increase the energy consumption unnecessarily.
The results show that increasing the clock frequency insignificantly reduced the processing time, but significantly increased the energy consumption.
This was especially true in the case of the experiments with the sensor which prolonged the active time notably.
