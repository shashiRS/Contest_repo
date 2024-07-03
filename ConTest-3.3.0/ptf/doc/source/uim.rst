Utility Install Manager (UIM)
=============================

**Utility Install Manager** (UIM) allows users to install ConTest Tool Libraries Python Packages. |br|
From ConTest release ``v3.0.0`` this feature has been activated.

Available ConTest Python Libraries
**********************************

`Available ConTest Python Libraries`_

UIM Motivation
**************

- Fast release cycles for ConTest tool libraries
- Open for users contribution

Pre-Requisite
*************

- Connection to Continental network.
- Python ``3.9.x`` installed on user machine via Employee Self Service.

GUI Usage
*********

UIM feature can be used via **GUI** by navigating to ``UIM->Install Manager`` in ``Title Bar``. |br|
**Install Manager** allows users to install all available Python packages (libraries or modules) release by ConTest team.

.. note::

    Please note that the features in ``Install Manager`` will be improved in future. Users can also request additional
    options which shall be useful for all.

CLI Usage
*********

UIM feature can be used via **CLI** (Command Line Interface) also via following commands.

Get All Latest Libraries
------------------------

With following command users can automatically install latest version of all available Python libraries from ConTest team.

.. code:: batch

    # automatically install latest version of all available libraries
    <python_exe> main.py --uim latest


Get Specific Libraries
----------------------

With following command users can install Python libraries given via requirements file.

.. code:: batch

    # install libraries mentioned in given requirements file
    <python_exe> main.py --uim my_pip_reqs.txt

.. note::
    Please read `pip requirements file format`_ for understanding the syntax of requirements file


Backward Compatibility
**********************

It has been ensured that there is no need to make changes in existing test scripts. |br|
Users test scripts shall work as before.

For test script using libraries which are available as Python package, the installation those will be done automatically
in background if not found already or not already available in Python environment used to run ConTest tool.

Recommendation
**************

Although backward compatibility is ensured, however it's recommended to adapt importing of ConTest tool libraries in
following manner once installation of library is done.

``from contest_<lib_name> import <lib_name>``


.. _pip requirements file format: https://pip.pypa.io/en/stable/reference/requirements-file-format/
.. _Available ConTest Python Libraries: https://github-am.geo.conti.de/ADAS/contest_tools_utils#available-contest-python-libraries

.. |br| raw:: html

    <br />
