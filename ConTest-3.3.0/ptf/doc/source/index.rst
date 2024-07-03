.. ConTest Documentation documentation master file, created by
   sphinx-quickstart on Wed Oct 11 12:19:33 2017.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. image:: logo.png
   :scale: 50 %
   :align: center

ConTest
=======
**ConTest** (Continental Software Testing Tool) is a framework for software requirement and integration testing in HIL and SIL environment. |br|
ConTest release version : |version| |br|
Get ConTest latest release by reading :ref:`Getting Release`

.. raw:: html

  <iframe src="https://continental.sharepoint.com/teams/team_10058759/_layouts/15/embed.aspx?UniqueId=3944e912-9f36-4041-8e1b-65376448e354&embed=%7B%22ust%22%3Atrue%2C%22hv%22%3A%22CopyEmbedCode%22%7D&referrer=StreamWebApp&referrerScenario=EmbedDialog.Create" width="640" height="360" frameborder="0" scrolling="no" allowfullscreen title="What is ConTest.mp4"></iframe>

*Unfortunately the video via Microsoft Sharepoint is only accessible for internals which are members of* `TEPM TPT Trainng Group`_ |br|
*If you're not already a member of* `TEPM TPT Trainng Group`_, *you can request access.*


With the help of available automated tools APIs testers can write complex test cases with
proper documentation of each test step.

ConTest also supports writing and execution of tests which doesn't require hardware.

Following are some highlighting features:

    - Developed in Python 3.9
    - Write tests with well defined guidelines
    - Write tests in Ubuntu or Windows
    - Control of Automated tools/utilities via Setup-Teardown approach
    - Rated TCL1 on ISO26262 Tool Safety Standard
    - Tests multiple runs supported
    - Randomize Tests Execution
    - Parameterized tests supported
    - Tests Generator
    - Reports generation with complete test data (test details, steps, failures, traceability etc.)
    - Reports generated in HTML, TXT, JSON and XML (Junit and CatHat) formats
    - GUI and CLI interfaces
    - Documentation done in Sphinx
    - Code satisfying PyLint, PEP8 checks (Static Code Analysis tools for Python)


For more information read concerned chapters.

Details
=======

Details for setting up machine and using ConTest is explained in separate sections:

.. toctree::
   :maxdepth: 1

   installations
   ide_setup
   how_to_get_release
   how_to_run
   uim
   using_ptf/using_ptf
   ci_integration/ci_integration
   special_cases/special_cases
   global_param_auto
   tool_api_auto
   verify_api_auto
   create_request
   contribute/contribute
   tools_concept/tools_concept
   training
   release
   faq


.. |br| raw:: html

    <br />

.. _link: https://confluence-adas.zone2.agileci.conti.de/display/public/department0034/123.+UD+-+ConTest#id-123.UDConTest-DownloadingConTest
.. _TEPM TPT Trainng Group: https://teams.microsoft.com/l/channel/19%3aeBNePnEjFncYti61Q76hivQ5g-AHsQ6mSO5RmXP8-UE1%40thread.tacv2/General?groupId=5a025357-6a97-45a1-8d61-def802a4a3ed&tenantId=8d4b558f-7b2e-40ba-ad1f-e04d79e6265a


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

