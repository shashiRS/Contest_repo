.. This file explains how to get ConTest release

.. _Getting Release:

How To Get Release
==================

Users can get specific release of ConTest in following ways:


Via Artifactory (Recommended)
*****************************
Download ConTest specific release version from `artifactory link`_


Via GitHub
**********
You can download latest release (zip file) from `GitHub link`_


Via Git
*******
- Get access to Continental GitHub and install Git → `Install Git`_
- Setup Git → `Setting Up Git`_
- Clone repository and move to release tag as below

  .. code-block:: bash

        git clone git@github-am.geo.conti.de:ADAS/ConTest.git
        # check all release tags
        git tag --list
        # checkout to a specific or latest release tag
        # replace x, y, z in command below with specific release tag version
        git checkout vx.y.z


.. _artifactory link: https://eu.artifactory.conti.de/artifactory/c_adas_astt_generic_prod_eu_l/ConTest/
.. _GitHub link: https://github-am.geo.conti.de/ADAS/ConTest/releases/latest
.. _Install Git: https://confluence-adas.zone2.agileci.conti.de/display/ASTT/Installations+and+Access
.. _Setting Up Git: https://confluence-adas.zone2.agileci.conti.de/display/ASTT/Setting+Up+Git
.. _Cloning Repository: https://confluence-adas.zone2.agileci.conti.de/pages/viewpage.action?pageId=15450178

.. |br| raw:: html


    <br />




