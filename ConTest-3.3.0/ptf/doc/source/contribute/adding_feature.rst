.. This file explains how a user can add a tool feature

Adding Tools
============

In this chapter guidelines have been given for user who want to contribute to ConTest Tools Utilities. |br|
**Tool Utilities** component is developed or designed independently to act as a feature which can be used
outside ConTest. |br| |br|


Important ConTest Locations
***************************

+---------------------------+-----------------------------------------------------------------------+
|      Location             |                                Description                            |
+===========================+=======================================================================+
| ConTest/gui               | GUI Code                                                              |
+---------------------------+-----------------------------------------------------------------------+
| ConTest/code_analyzer     | Scripts for static code analysis checks                               |
+---------------------------+-----------------------------------------------------------------------+
| ConTest/gui/gui_utils     | GUI data model and helping scripts for ConTest                        |
+---------------------------+-----------------------------------------------------------------------+
| ConTest/ptf/ptf_utils     | Core scripts                                                          |
+---------------------------+-----------------------------------------------------------------------+
| ConTest/ptf/tools_utils   | Automated tools utilities **(Contribution Location)**                 |
+---------------------------+-----------------------------------------------------------------------+


.. note::
    If you want to contribute in core functionalities apart from **tool_utils** then please get in touch with ConTest
    team.


Getting Code
************

In order to get ConTest code to work on it **clone ConTest repository**. |br|
For getting all information about following points: |br|

    - Installing git and accessing GitHub
    - Setting up git
    - Cloning ConTest repository
    - GitHub workflow


See this link_

.. note::
    Also contact ConTest team to get access to the repository for pushing the changes.


Contributing
************

After cloning the repository and understanding the **Git** and **GitHub** workflow user can  take existing
utilities as an example and create a new one following those as example. |br|

But following are some rules:

    - Each feature shall be in a separate folder **ConTest/ptf/tools_utils/my_feature**
    - **__init__.py** file shall be included in new feature folder
    - Read Coding_Guidelines_ chapter for creating feature scripts and for documentation
    - Whole feature folder should pass PEP8 and PyLint checks
    - Write documentation of your feature at **ConTest/ptf/doc/source/tools_concept**
    - Unit Tests shall be created for your feature at **ConTest/ptf/tests**


.. _Coding_Guidelines: coding_guide.html
.. _link: http://confluence-adas.conti.de:8090/display/ASTT/Git

.. |br| raw:: html

    <br />

