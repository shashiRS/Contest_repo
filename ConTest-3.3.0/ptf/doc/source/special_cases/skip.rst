Skip Decorator
==============

With the help of a skip decorator ``@skip_if`` users can skip the execution of a test case.
The skipping of test case will be decided with a help of a boolean condition given by user via ``@skip_if`` decorator.

.. note::
    The skipped test case verdict will be ``SKIPPED`` in all reports.

Usefulness
**********

This functionality is useful when users want to skip execution of a test case if some pre-conditions are not met, perhaps
to save time consumed during execution of test case etc.


In order to use this functionality, please check following examples:


Normal Test Usage
*****************

Skip via Statement
------------------

.. code-block:: python
    :emphasize-lines: 2, 5

    # importing skip decorator
    from ptf.ptf_utils.decorator.skip import skip_if

    # skip execution of `SWT_MY_AWESOME_TEST_1v1` test if system is linux
    @skip_if(sys.platform == 'linux', reason="This test shall only run on windows platform")
    def SWT_MY_AWESOME_TEST_1v1():
        ...


Skip via Function
-----------------

.. code-block:: python
    :emphasize-lines: 2, 7

    # importing skip decorator
    from ptf.ptf_utils.decorator.skip import skip_if

    # skip execution of `SWT_MY_AWESOME_TEST_2v1` test if `my_func` returns `True`
    # NOTE: any user specific implementation can be done in `my_func` but the return
    # value shall be either `True` or `False`
    @skip_if(my_func(), reason="My awesome skip reason")
    def SWT_MY_AWESOME_TEST_2v1():
        ...


Parameterized Test Usage
************************

.. code-block:: python
    :emphasize-lines: 2-3, 6-7

    # importing skip and parameterized decorators
    from ptf.ptf_utils.parameterized import parameterized
    from ptf.ptf_utils.decorator.skip import skip_if

    # skip execution of all parameters of `SWT_MY_AWESOME_PARAM_TESTv1` test if system is linux
    @skip_if(sys.platform == 'linux', reason="This test shall only run on windows platform")
    @parameterized(['hello', 'world'])
    def SWT_MY_AWESOME_PARAM_TESTv1(text):
        ...


.. |br| raw:: html

    <br />
