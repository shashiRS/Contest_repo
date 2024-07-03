.. This file explains RTA concept in ConTest

RTA
===
Please read this chapter to understand RTA Analysis Tool integration concept in ConTest.


What is RTA?
************
    RTA Analysis tool provides the functionality to measure runtime of any service utilizing the
    RTA service functions.
    RTA is developed by Ulrich Wagner team (Ulrich.Wagner@continental-corporation.com)


How RTA works?
**************
    RTA is an MO (Measurement Object) which can be loaded in MTS (Measurement Test Simulation)
    tool. RTA captures Measurement Freezes (specific information which SW application outputs
    with the help of a special piece of SW embedded into it).

    Measurement Freezes contains data regarding resource utilization (memory usage,
    core usage etc.). RTA provides APIs to register Core, Components etc. running on target or
    ECU. The Core, Components etc. information are saved in XML files for different projects.

    RTA opens up Python interpreter (2.7) inside it which allows to execute Python commands
    execution in MTS which potentially means Python scripts can be written to access RTA APIs
    for reporting etc. A specific Python script can be linked to RTA MO which can be executed
    once a recording (.rrec) file is loaded and started running.


How ConTest use RTA?
********************
    Since MTS doesn't provide APIs to control it during runtime flexibly therefore ConTest will use
    MTS CLI interface for automation.

    Idea is to provide APIs in order to take inputs from user(s) e.g. which recording file to
    run, which MTS configuration file to load etc. and trigger MTS via CLI options.

    ConTest will provide APIs to register Core, Component, Budgets, Report paths etc. and create a
    an MTS configuration which then will be loaded or triggered via MTS CLI.


What do I need to run RTA in ConTest (Installations)?
*****************************************************
    Following installations are required:
        - RTA sandbox from IMS checked-out on your local machine *(RTA sandbox also contains MTS)*
        - Install Python (2.7 32-bit) on your machine at C:/Python27 location *(required by RTA)*
        - ConTest


Pictorial Explanation
*********************
The concept of RTA running in ConTest is shown in following diagram.

.. image:: ../../../tools_utils/rta/RTA_Concept_In_PTF.JPG


TODOs
*****
A demo test has been written to show RTA running in ConTest.
However, following points need clarification:

- Locations for Core XML files ?
- Location of RTA ?
- Location of Budget files ?
- Who will provide Core XMLs, Budget CSVs, .rrec files ? or from where the information will come ?
- Is current ConTest APIs are sufficient or they need some modification(s) ?


.. |br| raw:: html

    <br />

