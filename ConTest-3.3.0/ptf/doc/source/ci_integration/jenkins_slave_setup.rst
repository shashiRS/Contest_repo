.. In this file it is described how to setup contest on a jenkins node to use it in CI for Bricks.

Jenkins slave setup
===================

On physical nodes
-----------------
To be able to use ConTest on a physical jenkins node, you need to install it in the correct location. |br|
On windows nodes, ConTest needs to be installed in ``D:\\tools\\contest\\<version>\\``. |br|
Please agree with ConTest team where the tool has been installed on jenkins node because the same location can be
mentioned in ConTest tool configuration file.

.. note::
    There is currently no automated installation if ConTest is missing. So make sure you prepared
    your node before test execution. Same applies for additional external tools that are required
    for your test execution.


In the cloud (Docker Linux)
---------------------------

Select ConTest version which you want to use for tests execution and check with ConTest team if a docker image is
available for that version and request for a ConTest tool configuration file from ConTest team which then you can
call in your ``conf/build.yml`` file ``tool:`` section.

.. |br| raw:: html

    <br />
