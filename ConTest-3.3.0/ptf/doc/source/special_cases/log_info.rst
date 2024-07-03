Adjust Logging Verbosity
========================

ConTest uses the `python 3 logging framework <https://docs.python.org/3/library/logging.html>`_
for all internal and tools logging. By default, all log prints with level "INFO", "WARNING",
"ERROR" and "CRITICAL" are printed and the prints with level "DEBUG" are ignored. |br|
If you want to change this, e.g. to debug a specific tool, please place the following logging
configuration as ``logging.conf`` in the root directory of your contest installation (next to your
main.py). Then add/adapt the loggers for your needs. |br|
E.g. to only show messages with the level "WARNING" or higher, change the level for the root logger
in line 21 from INFO to WARNING. |br|
For extended documentation how to adapt the loggers, please check the
`logging file format documentation <https://docs.python.org/3/library/logging.config.html#logging-config-fileformat>`_.

.. literalinclude:: logging.conf.template
    :linenos:

.. |br| raw:: html

    <br />
