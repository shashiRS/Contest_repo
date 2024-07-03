.. This file explains how to run ConTest

.. _How To Run:

How To Run
==========

.. raw:: html

  <iframe src="https://continental.sharepoint.com/teams/team_10058759/_layouts/15/embed.aspx?UniqueId=e1e49292-225a-466d-a48f-2a2e209285b2&embed=%7B%22ust%22%3Atrue%2C%22hv%22%3A%22CopyEmbedCode%22%7D&referrer=StreamWebApp&referrerScenario=EmbedDialog.Create" width="640" height="360" frameborder="0" scrolling="no" allowfullscreen title="Command Line Options.mp4"></iframe>

*Unfortunately the video via Microsoft Sharepoint is only accessible for internals which are members of* `TEPM TPT Trainng Group`_ |br|
*If you're not already a member of* `TEPM TPT Trainng Group`_, *you can request access.*

ConTest can be started with a simple command

Command On Windows::

    cd <contest_repository_path>
    <python_exe_absolute_path> main.py


Command On Ubuntu::

    cd <contest_repository_path>
    python main.py

.. note::
    Please use the Python interpreter to run the framework in which all required Python modules have been installed.

.. note::
    If above command is executed then framework will be in manual mode. |br|
    In manual mode user has to select options by itself with the help of information messages
    displayed on message area.

Positional Argument ``run_exec_record``
***************************************

In order to re-run an older execution record, the ``run_exec_record`` positional argument can be used. |br| |br|
ConTest will save a complete execution record of a test run in a yaml file ``exec_record.yml`` in the timestamp report folder. |br|

The absolute or full path to the ``exec_record.yml`` can be given as input to the ``run_exec_record`` positional argument
in order to re-run specific tests based on their verdicts in the given previous execution.

.. note::
    Once the ``run_exec_record`` positional argument is given the other default arguments will be ignored !

Following are **mandatory** sub-arguments for ``run_exec_record``.

+-------------------------+------------------------+----------------------------------------------------+
| Arguments               |      Desc.             |                   Detail                           |
+=========================+========================+====================================================+
| ``-y``                  | Execution Record File  | Old execution record yaml file                     |
+-------------------------+------------------------+----------------------------------------------------+
| ``-v``                  |    Test Verdict(s)     | Test verdicts to re-run from old execution record  |
+-------------------------+------------------------+----------------------------------------------------+

Execution Record File ``-y``
----------------------------

Full path to the ``exec_record.yml`` file which shall be residing in report folder of previous execution run.

Verdicts of Tests ``-v``
------------------------

Selection of a single or multiple verdicts which shall be filtered when selecting test cases for re-execution.

.. note::
    Currently supported args for ``-v`` are ``"pass", "fail", "skip", "inconclusive"``

Example::

    # re-run failed tests from an old execution record saved in D:\my_report\reports_20240419_110559\exec_record.yml
    <python_exe> main.py run_exec_record -v fail -y D:\my_report\reports_20240419_110559\exec_record.yml

    # re-run failed and skipped tests from an old execution record saved in D:\my_report\reports_20240419_110559\exec_record.yml
    <python_exe> main.py run_exec_record -v fail skip -y D:\my_report\reports_20240419_110559\exec_record.yml


Command Line Options
********************

.. note::
    Following arguments are default arguments

+-------------------------+------------------------+----------------------------------------------------+
| Arguments               |      Desc.             |                   Detail                           |
+=========================+========================+====================================================+
| ``-c``                  |     Config. file       | configuration file to be loaded in framework       |
+-------------------------+------------------------+----------------------------------------------------+
| ``-r``                  |       Run Mode         | auto (load and run config) or manual (load config) |
|                         |                        | or auto_gui (load and run config with GUI)         |
+-------------------------+------------------------+----------------------------------------------------+
| ``-l``                  |    Base Location       | used in-case config has wrong base location        |
+-------------------------+------------------------+----------------------------------------------------+
| ``-n``                  |   No. of Iterations    | Run the test cases with given no of iterations     |
+-------------------------+------------------------+----------------------------------------------------+
| ``-e``                  |     Ext. Mod. Loc.     | for ext. python module path addition in sys.path   |
+-------------------------+------------------------+----------------------------------------------------+
| ``--rest-port``         |    REST Client Port    | Opening REST Client with particular port number    |
+-------------------------+------------------------+----------------------------------------------------+
| ``--random``            |    Random execution    | Execute the tests in random order                  |
+-------------------------+------------------------+----------------------------------------------------+
| ``--dark-mode``         |    Enable Dark Mode    | Starts the gui with dark mode enabled              |
+-------------------------+------------------------+----------------------------------------------------+
| ``--setup-file``        |    Custom setup file   | Provide the custom setup file to be used           |
+-------------------------+------------------------+----------------------------------------------------+
| ``--check-pip-mods``    |    Check PIP Modules   | Check if modules req. to run tool are installed    |
+-------------------------+------------------------+----------------------------------------------------+
| ``--report-dir``        |    Report Directory    | Provide report directory for reports generation    |
+-------------------------+------------------------+----------------------------------------------------+
| ``--filter``            |    Test case filter    | Filters testcases to be executed                   |
+-------------------------+------------------------+----------------------------------------------------+
| ``--timestamp``         |    Timestamp On/Off    | Turn timestamp print on/off in log                 |
+-------------------------+------------------------+----------------------------------------------------+
| ``--reverse_selection`` | Reverse test selection | Test selection will be reversed based on the       |
|                         |                        | user selected tests.                               |
+-------------------------+------------------------+----------------------------------------------------+
| ``-h``                  |          Help          | to see help descriptions of above mentioned args   |
+-------------------------+------------------------+----------------------------------------------------+


Configuration File Argument ``-c``
----------------------------------

User can load a configuration file using ``-c`` option. |br|
If only ``-c`` option is provided then framework will **only** load cfg file.

Example::

    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file>


Run Mode Argument ``-r`` (optional with ``-c``)
-----------------------------------------------

User can execute tests mentioned in configuration file using ``-r`` option. |br|
This option only works with ``-c`` option. |br|
The default value for ``-r`` is manual.

Example::

    # load configuration file and execute test cases in configuration file
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -r auto

    # load configuration file and execute test cases in configuration file with ConTest GUI
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -r auto_gui

Base Location Argument ``-l`` (optional with ``-c``)
----------------------------------------------------

User can change the base location in-case location of scripts are different from the one mentioned
in configuration file using ``-l`` option. |br|
This option only works with ``-c`` option. |br|

.. note::
    Base location is the place where all user tests and helping scripts are placed. |br|
    The original base location in configuration file will not be changed if this option is used.


Example::

    # load configuration file with different base location
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -l <correct_base_location>
    # load configuration file with different base location and execute tests
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -r auto -l <correct_base_location>


No. of Tests Execution Iterations ``-n`` (optional with ``-c``)
---------------------------------------------------------------

With this option user can provide number of times the test cases can be executed from the one mentioned
in configuration file using ``-n`` option. |br|
This option only works with ``-c`` option. |br|

Example::

    # load configuration file and execute tests
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -r auto -n <no_of_loops>


External Path Argument ``-e`` (optional with ``-c``)
----------------------------------------------------

With this option user can provide paths where some external (modules not in python test location) python modules are
located which are used inside python scripts in python test location.
This option only works with ``-c`` option. |br|

.. note::
    If paths given doesn't exist then an error will be raised.


Example::

    # load configuration file and add ext paths in sys.path
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> -e <ext_path_1> <ext_path_2> -r auto


REST Client Argument ``--rest-port``
------------------------------------

Option to start ConTest with rest client. A Rest Client is provided with port number. |br|
The port must be used equal to rest server port, which is running independently on same machine. |br|

Example::

    # starting contest with its REST service client with a particular port
    <python_exe_absolute_path> main.py --rest-port 5001


Random Test Execution Argument ``--random``
-------------------------------------------

If this flag is given, the tests will be executed in random order. |br|

Example::

    # Run tests in random order
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --random


GUI Dark Mode Argument ``--dark-mode``
-------------------------------------------

If this flag is given, GUI will be started in dark mode. |br|

Example::

    # Start GUI in dark mode
    <python_exe_absolute_path> main.py --dark-mode


Custom Setup File Argument ``--setup-file`` (optional with ``-c``)
------------------------------------------------------------------

If you don't want to use the default setup.pytest file for (global) setup/teardown definition,
you can use the ``--setup-file`` option. |br|
You can provide the file name either with or without extension. |br|
This option only works with ``-c`` option. |br|

.. note::
    If the provided file can not be found in your base location, the default setup.pytest will be used.

Example::

    # Run tests with configuration and custom setup_2.pytest
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --setup-file setup_2.pytest
    # You can even leave away the file extension
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --setup-file setup_2


Check PIP Modules Installations ``--check-pip-mods``
----------------------------------------------------

Boolean argument to check if all python pip modules are installed in python interpreter used to run ``main.py``  |br|
After check has been performed, the application will exit as this argument is just for pip modules check . |br|

Example::

    # check if all python pip modules are installed in python interpreter used to run main.py
    # after checking framework will not start but exit with success, if all ok
    <python_exe_absolute_path> main.py --check-pip-mods


Report Directory Argument ``--report-dir`` (optional with ``-c``)
-----------------------------------------------------------------

If you want ConTest to generate reports at a specific location then you can use this
option. |br|
This path can be outside your Base Location. |br|
This option only works with ``-c`` option. |br|

.. note::
    If report directory doesn't exist then it will be created.


Filter argument ``--filter`` (optional with ``-c``)
---------------------------------------------------

Filters are a quite powerful mechanism to define which tests to execute. |br|
In general, the structure for each filter looks like this: |br|
`... --filter FILTER_TYPE FILTER_VALUE(s) --filter FILTER_2_TYPE FILTER_2_VALUE ...` |br|
So for each filter you provide the type of the filter and the value to filter for. |br|

In the following table you find some information about supported filter types and how to use them:

+----------------+----------------------+------------------------------------------------------+
| Filter Type    | Short description    |                Filter Values                         |
+================+======================+======================================================+
|      tag       | Filter for test tags | | With the tag filter, you can filter for a single   |
|                |                      | | test tag, like 'hil' or 'sil'. If multiple filters |
|                |                      | | are defined, only the last filter will be active   |
|                |                      | | in GUI mode but given filter values will be applied|
|                |                      | | in CLI auto mode.                                  |
+----------------+----------------------+------------------------------------------------------+

Example::

    # Run tests with given configuration and 'each' test tag
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --filter tag each
    # Run tests with given configuration and 'integration' test tag
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --filter tag integration

    # This will run sil and hil tagged tests in auto mode
    # NOTE: The multiple filters can be given and will take affect in auto mode
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --filter tag sil hil -r auto


Timestamp On/Off Argument ``--timestamp``
-----------------------------------------

Turn On/Off timestamp prints in output logs via this argument.
Default value is ``on``. |br|

Example::

    # turn off timestamp prints in output logs
    <python_exe_absolute_path> main.py --timestamp off


Reverse test selection Argument ``--reverse_selection``
-------------------------------------------------------

With this option, it is possible to reverse the test selection. i.e. user selected tests will be deselected and
unselected tests will be selected and executed. |br|

.. note::
    This option will be ignored if it's used with ``--filter`` option

Example::

    # enable reverse selection for test execution in gui mode
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --reverse_selection
    # use-case in auto mode: run all tests which are not mentioned in cfg file i.e. previously saved in cfg file
    <python_exe_absolute_path> main.py -c <path_to_your_configuration_file> --reverse_selection -r auto


Jenkins Run
***********

See :doc:`this documentation <./ci_integration/bricks>` how to use ConTest in your Jenkins build.

.. _Training section: training.html
.. _TEPM TPT Trainng Group: https://teams.microsoft.com/l/channel/19%3aeBNePnEjFncYti61Q76hivQ5g-AHsQ6mSO5RmXP8-UE1%40thread.tacv2/General?groupId=5a025357-6a97-45a1-8d61-def802a4a3ed&tenantId=8d4b558f-7b2e-40ba-ad1f-e04d79e6265a

.. |br| raw:: html


    <br />




