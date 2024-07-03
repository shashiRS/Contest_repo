Prioritize Tests
=================

Test cases priority can be set for Python test cases.
This helps in-cases when user want to execute some test(s) before other tests.
Priority (HIGH, MEDIUM, LOW) can be set using ``priority`` decorator.

Example:

.. code:: python

    # to be done in custom import section on top of script
    from ptf.ptf_utils.decorator.prioritization import priority, Priority

    # @priority(Priority.LOW)     --> for setting test case priority as LOW
    # @priority(Priority.MEDIUM)  --> for setting test case priority as MEDIUM
    @priority(Priority.HIGH)
    def SWT_DEMO_TEST_PRIORITYv1():
        DETAILS("Demo test to show priority use case")

        PRECONDITION("Fill in testcase Precondition")

        VERIFIES("L3SW_xxxx")

        TESTTAG("requirement")

        TESTSTEP("Check addition")
        EXPECTED("Check Passed")
        contest_asserts.verify(1 + 2, 3, "1 + 2 != 3")

This testcase will be executed before all other selected test cases.

.. |br| raw:: html

    <br />
