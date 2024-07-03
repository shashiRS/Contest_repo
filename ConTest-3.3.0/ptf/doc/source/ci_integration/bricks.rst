.. This file describes how the integration into Bricks is done

.. _Contest in bricks:

Use ConTest in a project built with Bricks
##########################################

To integrate ConTest execution into your Bricks project, please follow these steps:

#. Make sure that your project is built with Bricks_ build system. |br|
   Check that you have a file ``conf/build.yml`` in your project's repository and check with your
   integrator that your project is running on Bricks.

   .. note::
      Build systems other than Bricks are currently not supported.

#. Add your testcases to the project's repository. |br|
   Check the `Github repository structure`_ page where to place the testcases for your project type.

#. Save your contest configuration in the project's repository. |br|
   The contest configuration should contain the testcases you want to execute. It is recommended
   to place it in the ``conf`` directory of your project, but you can place it anywhere you like.

#. Add ``conf/contest.yml`` to your project's repository. |br|
   You can use the following file as template:

   .. literalinclude:: contest.yml
       :language: yaml
       :linenos:
       :caption: conf/contest.yml

   In ``line 10``, you need to point to the configuration you created in ``step 3``.

#. Enable contest execution in ``conf/build.yml``. |br|
   Add an entry into the ``tools/specs`` block like this:

   .. code-block:: yaml
       :linenos:

       ...
       tools:
         specs:
           - tool_spec: contest/contest_cloud.yml
             # Run contest only in non-test, non-documentation generic linux64 build block
             match_attributes:
               "/testing/enabled": null
               "/documentation/enabled": null
               "/variant/name": generic
               "/build_platform/name": linux64

   With the `match_attributes` you can define for which binary build you want to execute ConTest.
   For a full list of available contest execution configurations, please check the
   `tools configuration repository`_ in github.

   .. note::
       If you need a new ConTest tool configuration for your project then please contact ConTest team.
       This configuration will contain information on which jenkins slave node or docker image test cases shall run and
       some additional steps required for the test cases e.g. stashing artifacts, uploading generated reports to
       artifactory, user defined steps etc.

#. Commit your code to github and try the execution. |br|
   That's it, you are ready to run your tests. |br|

Additional links
----------------

You can find additional information in the following links:

Bricks information: Bricks_ |br|
Recommended repository structure for github: `Github repository structure`_ |br|
Tools configurations: `tools configuration repository`_ |br|
Sample project: arith_add_

.. _Bricks: https://confluence-adas.zone2.agileci.conti.de/display/public/department0034/113.+UD+-+Bricks+Build+System
.. _Github repository structure: https://confluence-adas.zone2.agileci.conti.de/display/public/department0034/112.+UD+-+GitHub+Service#id-112.UD-GitHubService-GitHubRepositoryStructureGitHubRepositoryStructure
.. _tools configuration repository: http://github-am.geo.conti.de/ADCU-CIP/cip_build_system_tools/tree/master/tools/contest
.. _arith_add: http://github-am.geo.conti.de/ADAS-CIP-WaTSEn/arith_add/

.. |br| raw:: html

    <br />
