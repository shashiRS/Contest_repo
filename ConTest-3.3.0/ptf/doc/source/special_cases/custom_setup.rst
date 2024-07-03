Custom Setup & Teardown Decorator
=================================

With the help of a custom setup decorator ``@custom_setup`` users can specify particular functions to be executed before and
after the execution of a test case.

Usefulness
**********

This functionality is useful when users want to replace the standard ``setup`` and ``teardown`` functions with their
own custom functions for a particular test case function.

The custom pre and post functions must be implemented in default ``setup.pytest`` file or custom setup file ``setup_*.pytest``.

In order to use this functionality, the ``custom_setup`` decorator class can be imported and used as below:


Normal Test Usage
*****************

.. code-block:: python
    :emphasize-lines: 2, 4-6, 10-12, 16-18

    # importing custom setup decorator
    from ptf.ptf_utils.decorator.custom_setup import custom_setup

    # specifying the framework to run `my_setup` function before and `my_teardown`
    # function after `SWT_MY_AWESOME_TEST_1v1` test
    @custom_setup(setup="my_setup", teardown="my_teardown")
    def SWT_MY_AWESOME_TEST_1v1():
        ...

    # specifying the framework to run `my_setup` function before and standard
    # `teardown` function after `SWT_MY_AWESOME_TEST_2v1` test
    @custom_setup(setup="my_setup")
    def SWT_MY_AWESOME_TEST_2v1():
        ...

    # specifying the framework to run standard `setup` function before and `my_teardown`
    # function after `SWT_MY_AWESOME_TEST_3v1` test
    @custom_setup(teardown="my_teardown")
    def SWT_MY_AWESOME_TEST_3v1():
        ...


Parameterized Test Usage
************************

.. code-block:: python
    :emphasize-lines: 2, 5-7, 12-14, 19-21

    # importing custom setup decorator
    from ptf.ptf_utils.decorator.custom_setup import custom_setup
    from ptf.ptf_utils.parameterized import parameterized

    # specifying the framework to run `my_setup` function before and `my_teardown`
    # function after each set of `SWT_MY_AWESOME_PARAM_TEST_1v1` test
    @custom_setup(setup="my_setup", teardown="my_teardown")
    @parameterized(['hello', 'world'])
    def SWT_MY_AWESOME_PARAM_TEST_1v1(text):
        ...

    # specifying the framework to run `my_setup` function before and standard
    # `teardown` function after each set of `SWT_MY_AWESOME_PARAM_TEST_2v1` test
    @custom_setup(setup="my_setup")
    @parameterized(['hello', 'world'])
    def SWT_MY_AWESOME_PARAM_TEST_2v1(text):
        ...

    # specifying the framework to run standard `setup` function before and
    # `my_teardown` function after each set of `SWT_MY_AWESOME_PARAM_TEST_3v1` test
    @custom_setup(teardown="my_teardown")
    @parameterized(['hello', 'world'])
    def SWT_MY_AWESOME_PARAM_TEST_3v1(text):
        ...


.. |br| raw:: html

    <br />
