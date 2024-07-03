"""
    Copyright 2019 Continental Corporation

    :file: data_reporter.py
    :platform: Windows, Linux
    :synopsis:
        Script containing implementation for sharing information (errors, warnings etc.) to user
        either on console or GUI

    :author:
        - M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
"""

# standard python modules
from datetime import datetime
import logging


# custom imports
from .helper import InfoLevelType


LOG = logging.getLogger('DATA_REPORTER')


# pylint: disable=too-few-public-methods
class DataReporter:
    """
    Class for sharing information (errors, warnings etc.) with user by printing it on console and or
    displaying on GUI
    """

    def __init__(self, gui=None):
        """
        Constructor

        :param object gui: Object of GUI which helps to communicate information (errors, warnings
            etc.) with GUI. This parameter will only be used when data preparation is requested from
            GUI otherwise the information will only be directed to console. Default value is None.
        """
        # saving object og gui of giving
        self.gui = gui

    def log(self, info, info_level=InfoLevelType.INFO):
        """
        Method for printing information on console for user convenience and optionally on GUI as
        well if required

        :param string info: Information to share or print
        :param enum info_level: Enum value for information type (INFO, ERR, WARN)
        """
        def report_error_to_gui(info_to_pass):
            """
            Local function to print information and pass to GUI (if required)

            :param string info_to_pass: Information to print on console and pass to GUI
                (if required)
            """
            self.gui.report_error_from_data_reporter(info_to_pass)
        if info_level == InfoLevelType.INFO:
            info_str = "[{}@{}] {}".format(
                InfoLevelType.INFO.name, datetime.now().strftime('%H:%M.%S'), info)
            LOG.info(info_str)
        elif info_level == InfoLevelType.WARN:
            info_str = "[{}@{}] {}".format(
                InfoLevelType.WARN.name, datetime.now().strftime('%H:%M.%S'), info)
            LOG.warning(info_str)
        elif info_level == InfoLevelType.ERR:
            info_str = "[{}@{}] {}".format(
                InfoLevelType.ERR.name, datetime.now().strftime('%H:%M.%S'), info)
            LOG.warning(info_str)
            if self.gui:
                report_error_to_gui(info_str)
            raise RuntimeError(info)
