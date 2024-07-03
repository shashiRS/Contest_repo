.. This file explains coding guidelines of ConTest

Coding Guidelines
=================

In this chapter coding guidelines have been explained. |br|
In order to code in clean and explanatory form we follow some guidelines which not only increase our
code readability but also makes code maintainable.


File Header
***********

We use reST (reStructuredText) format for comments or docstrings in our Python code. |br|
An example of file header is shown below:

Example::

    """
        Module for ...
        Copyright 2018 Continental Corporation

        :file: my_file.py
        :platform: Linux, Windows
        :synopsis: This file contains code for ...

        :author:
            - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    """


Importing Modules
*****************

Always do import of custom modules as below:

Example::

    # standard imports
    import time
    import os

    # always do custom imports as relative e.g. below we are importing contest_asserts
    from contest_verify.verify import contest_asserts


Function Docstrings
*******************

Example::

    def add(a, b):
        """
        Method for adding 2 numbers

        :param int a: First number to add
        :param int b: Second number to add

        :returns: The added value
        :rtype: int
        """
        c = a + b
        return c



Examples In Function Docstrings
*******************************

If your function is an API (i.e. it's intended to be used in tests) then write an example for it's
use case in function docstrings.


Example::

    def add(a, b):
        """
        Function for adding 2 numbers

        :param int a: First number to add
        :param int b: Second number to add

        :returns: The added value
        :rtype: int

        Example::

            # adding 2+3
            print(add(2, 3))

        """
        c = a + b
        return c


Class Development and Docstrings
********************************

It's recommended to develop feature(s) as a Python class. |br|
The formatting and coding of class is normal Python coding, however following are some guidelines: |br|

    - Docstring are mandatory for methods and for class
    - Write comments before each important code line
    - Class methods intended to be used as APIs should be public methods
    - Write examples in docstrings for APIs
    - Class methods not intended as APIs should be protect methods
    - Class should consist of a protected method for prints with PTF tag
    - Use **contest_asserts** module for verification of values
    - Don't use "print()" to show debugging output, but use the python logging framework


Example::

    # Create a logger for the calculator class
    import logging  # In your final implementation, move to standard imports
    LOG = logging.getLogger('Calculator')

    class Calculator:
        """
        Class for addition and subtraction actions
        """

        def __init__(self):
            """
            Constructor
            """
            pass

        def add(self, a, b):
            """
            Method for adding 2 numbers

            :param int a: First number to add
            :param int b: Second number to add

            :returns: The added value
            :rtype: int

            Example::

                print(add(3, 2))

            """
            c = a + b
            LOG.debug("Addition value is: %s", c)
            return c

        def subtract(a, b):
            """
            Method for subtracting 2 numbers

            :param int a: First number
            :param int b: Second number

            :returns: The subtracted value
            :rtype: int

            Example::

                print(subtract(3, 2))

            """
            c = a - b
            LOG.debug("Subtraction value is: %s", c)
            return c


Static Code Analysis
********************

In order to follow static coding standards for Python, make sure coding is done with PyLint and PEP8
checks in mind. |br|
You can set your IDE (PyCharm) by reading PyCharm_Setup_ |br|


For enthusiasts, feel free to read more from following links:

    - PEP8_
    - PyLint_

We have some scripts (batch and shell) which automatically checks code against PEP8 and PyLint rules. |br|
Location of these scripts are mentioned below: |br|

Code Analysis Scripts Location: **ConTest/code_analyzer**



.. _PyCharm_Setup: ../ide_setup.html
.. _PEP8: https://www.python.org/dev/peps/pep-0008/
.. _PyLint: https://docs.pylint.org/en/1.6.0/tutorial.html

.. |br| raw:: html

    <br />




