.. This file describes how maintenance of contest is done in CI

Maintenance
===========

In this chapter you find information how to maintain bricks support for ConTest.

.. note::
    This chapter is only intended for ConTest developers.

Release a new docker image
**************************

A new docker image for ConTest version can be released and uploaded to artifactory for usage via
`docker-builder-configs`_ repository. |br|

Please check a reference `Pull Request`_ regarding where to make changes for creating a docker image. |br|
Just change the version and add any new python modules (if any) which can be seen in the Pull Request.


Add additional tool configurations
**********************************

To add new tool configurations for Bricks, copy one of the existing configurations in `github`_
and adapt it for your needs. |br|
Documentation about the structure can be found in `confluence`_. |br|
After the new configuration is merged to master branch, a new release of the tools repository is
required before the new configuration can be used in Bricks. Please check with CIP team how to do this.

.. _github: http://github-am.geo.conti.de/ADCU-CIP/cip_build_system_tools/blob/master/tools/contest/
.. _confluence: https://confluence-adas.zone2.agileci.conti.de/display/department0034/113.+UD+-+%28v4.1.6%29+Use+cases+for+Bricks+developers
.. _docker-builder-configs: https://github-am.geo.conti.de/ADCU-CIP/docker-builder-configs
.. _Pull Request: https://github-am.geo.conti.de/ADCU-CIP/docker-builder-configs/pull/258

.. |br| raw:: html

    <br />
