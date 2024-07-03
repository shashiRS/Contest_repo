.. This file describes how the reporting and traceability can be done


Tests Reporting and Traceability
================================

Reporting and Traceability of Test Cases can be triggered by following steps mentioned below:

#. Tests configured to run in Bricks :ref:`Contest in bricks` |br|

#. Activate Pre and Post reporting in ``conf/build.yml`` file ``tools:`` section. |br|
   **Pre-Reporting** step crawls the test scripts for fetching data e.g. requirement IDs, test names, tags etc. |br|
   **Post-Reporting** steps links the test cases with the requirements on `CIP Reporting Web Interface`_ for tests
   traceability. |br|

   .. code-block:: yaml
       :linenos:

       ...
       tools:
         specs:
           # Reporting run relevant before compilation
           - tool_spec: reporting/reporting/pre_reporting.yml
           # Reporting run relevant after compilation
           - tool_spec: reporting/reporting/post_reporting.yml

#. Activate ConTest reporting crawler in ``conf/build.yml`` file ``reporting:`` section. |br|
   Details can be found at `CIP ConTest reporting Crawler`_.

   .. code-block:: yaml
       :linenos:

       ...
       reporting:
         crawler:
           contest_result_report:


.. _CIP Reporting Web Interface: https://report-overview.cmo.conti.de/?project_id=ACDC2
.. _CIP ConTest reporting Crawler: https://readthedocs.cmo.conti.de/docs/reporting-user-doc/en/stable/configuration/configuration.html#contest-crawler

.. |br| raw:: html

    <br />
