"""
    Copyright 2019 Continental Corporation

    :file: user_config_handler.py
    :platform: Windows, Linux
    :synopsis:
        This file contains handlers for user specific configuration. User specific configuration
        is all configuration that is not project specific, e.g. if the user enabled 'dark mode' on
        the UI. For project specific configuration handler, see config_handler.py.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import configparser
import platform
import os
from enum import Enum
from ast import literal_eval

from PyQt5 import QtCore
from PyQt5.QtCore import QStandardPaths, QObject

# The amount of most recent configurations to store
MOST_RECENT_CONFIGURATIONS_COUNT = 5


class Sections(Enum):
    """
    The configuration sections
    """

    UI = "ui"
    PROJECT_CONFIG = "project-config"
    UI_POSITION = "UI_position"
    UI_SIZE = "UI_size"


class UserConfigSignalHandler(QObject):
    """
    The signal handler for user configuration signals.
    This is needed since the user config signal handler should exist as singleton.
    If we moved this into the UserConfigHandler, the signals would be disconnected once
    a UserConfigHandler instance is deleted, resulting in python crashing with core dumps.
    """

    last_configurations_changed = QtCore.pyqtSignal()


# pylint: disable=unsubscriptable-object, unsupported-assignment-operation
# This is a config handler which doesn't need public methods, only public attributes
class UserConfigHandler:
    """
    This handler provides the possibility to work with persisted user configurations.
    Each property defined in this class will be persisted on writes. Also each property returns
    a default value if it was never written.
    """

    # The configuration to be handled by this config handler. Will be initialized on first call
    # of constructor. Needs to be class variable to have consistent values even for multiple
    # instances.
    __config = None

    # Store the signal handler instance to keep it alive until python is closed.
    __signal_handler = None

    # Public signals
    # The signal that is emitted once the recently opened configurations changed.
    last_configurations_changed = None

    def __init__(self):
        if platform.system() == "Linux" and "WORKSPACE" in os.environ:
            # if this file is running on linux platform and in jenkins environment i.e. docker image running in a
            # container then instead create 'userconfig.ini' in current working directory in order to avoid
            # permission denied issues due to Kyverno changes
            self.user_config_path = os.path.join(os.getcwd(), "userconfig.ini")
        else:
            # Default configuration path as defined for the OS.
            # See QStandardPaths documentation for details.
            # Can not be created as module variable to use proper location in tests.
            self.user_config_path = os.path.join(
                QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation), "userconfig.ini"
            )

        if not UserConfigHandler.__config:
            # Load existing configuration. Ignores non existing files.
            UserConfigHandler.__config = configparser.ConfigParser()
            UserConfigHandler.__config.read(self.user_config_path)

            # Make our signal publicly accessible in an singleton like behavior.
            # See USerConfigSignalHandler implementation for description of this weird
            # implementation.
            UserConfigHandler.__signal_handler = UserConfigSignalHandler()
            UserConfigHandler.last_configurations_changed = (
                UserConfigHandler.__signal_handler.last_configurations_changed
            )

            # Init sections
            self.__init_sections()

    def __init_sections(self, reset=False):
        """
        Initialize the sections in the configuration
        :param bool reset: If only non-existing sections should be created or all sections should
                           be reset
        """
        for section in Sections:
            if reset or section.value not in self.__config.sections():
                self.__config[section.value] = {}

    def __save_config(self):
        """
        Persists the configuration on storage.
        """
        try:
            os.makedirs(os.path.dirname(self.user_config_path))
        except FileExistsError:
            pass

        with open(self.user_config_path, "w", encoding="utf-8") as configfile:
            self.__config.write(configfile)

    def __set_darkmode(self, dark_mode_enabled):
        """
        Write the dark mode setting.

        :param bool dark_mode_enabled: If dark mode is enabled.
        """
        self.__config[Sections.UI.value]["darkmode"] = str(dark_mode_enabled)
        self.__save_config()

    def __get_darkmode(self):
        """
        Returns the dark mode setting.

        :return: The dark mode setting value
        :rtype: bool
        """
        return self.__config.getboolean(Sections.UI.value, "darkmode", fallback=False)

    def __set_line_wrap(self, line_wrap):
        """
        Write the line wrap for log output window setting

        :param line_wrap: If automatic line wrap in log output should be enabled
        """
        self.__config[Sections.UI.value]["linewrap"] = str(line_wrap)
        self.__save_config()

    def __get_line_wrap(self):
        """
        Returns if the lines in the log output window should be automatically wrapped.

        :return: The line wrap setting
        :rtype: bool
        """
        return self.__config.getboolean(Sections.UI.value, "linewrap", fallback=True)

    def __set_reopen_last_configuration(self, reopen):
        """
        Sets if last loaded configuration should be reopened on next start

        :param bool reopen: If the last configuration should be reopened.
        """
        self.__config[Sections.PROJECT_CONFIG.value]["reopen"] = str(reopen)
        self.__save_config()

    def __get_reopen_last_configuration(self):
        """
        Returns if the last loaded configuration should be reopened on next start

        :return: If the last configuration should be reopened.
        :rtype: bool
        """
        return self.__config.getboolean(Sections.PROJECT_CONFIG.value, "reopen", fallback=False)

    def __get_last_configurations(self):
        """
        Returns a tuple of recently opened configurations.

        :return: The recently opened configurations.
        :rtype: tuple
        """
        last_configurations_str = self.__config.get(Sections.PROJECT_CONFIG.value, "last_config", fallback="")

        # If we use split(";") on an empty string, we will the following list [''].
        # Therefore we check here for an empty string and return an empty tuple instead.
        if last_configurations_str:
            return tuple(last_configurations_str.split(";"))
        return ()

    def __set_last_configurations(self, configurations):
        """
        Sets the last opened configurations to given list.
        Length limits for the amount of configurations is still applied.
        Also, the last_configurations_changed signal will be emited.

        :param list configurations: The configurations to set
        """

        self.__config[Sections.PROJECT_CONFIG.value]["last_config"] = ""
        for configuration in configurations:
            self.add_configuration(configuration)

    def __set_last_ui_position(self, position):
        """
        sets the last position coordinates of the UI main window

        :param tuple position: position coordinates of the UI main window
        """
        self.__config[Sections.UI_POSITION.value]["position"] = str(position)
        self.__save_config()

    def __get_last_ui_position(self):
        """
        Returns the last position coordinates of the UI main window

        :return: position coordinates of the UI main window
        :rtype: tuple
        """
        return literal_eval(self.__config.get(Sections.UI_POSITION.value, "position", fallback="(-9, -9)"))

    def __set_last_ui_size(self, size):
        """
        sets the last size coordinates of the UI main window

        :param tuple size: size coordinates of the UI main window
        """
        self.__config[Sections.UI_SIZE.value]["size"] = str(size)
        self.__save_config()

    def __set_what_is_new_variable(self, what_is_new_value):
        """
        Write the what_is_new value.
        :param bool what_is_new_value: If what_is_new variable value is True.
        """
        self.__config[Sections.UI.value]["show_whats_new"] = str(what_is_new_value)
        self.__save_config()

    def __get_what_is_new_value(self):
        """
        Returns the what_is_new variable value.
        :return: The what_is_new value
        :rtype: bool
        """
        return self.__config.getboolean(Sections.UI.value, "show_whats_new", fallback=False)

    def __get_last_ui_size(self):
        """
        Returns the last size coordinates of the UI main window

        :return: size coordinates of the UI main window
        :rtype: tuple
        """
        return literal_eval(self.__config.get(Sections.UI_SIZE.value, "size", fallback="(1042, 868)"))

    def __get_contest_version(self):
        """
        Returns the version of ConTest
        :return: The version of ConTest
        :rtype: string
        """
        return self.__config.get(Sections.UI.value, "version", fallback="1.10.0")

    def __set_contest_version(self, version):
        """
        Write version of ConTest
        :param str version: The version of Contest
        """
        self.__config[Sections.UI.value]["version"] = str(version)
        self.__save_config()

    def add_configuration(self, new_configuration):
        """
        Adds a new configuration to recently opened configuration list.
        Will limit the list length to MOST_RECENT_CONFIGURATIONS_COUNT.
        Will emit the last_configurations_changed signal.

        :param str new_configuration: The new configuration to add to list
        """
        # Unify path separators before adding to user config
        new_configuration = new_configuration.replace("/", os.path.sep)
        new_configuration = new_configuration.replace("\\", os.path.sep)

        configurations = list(self.__get_last_configurations())
        if new_configuration in configurations:
            configurations.remove(new_configuration)

        configurations.append(new_configuration)
        configurations = configurations[-MOST_RECENT_CONFIGURATIONS_COUNT:]
        self.__config[Sections.PROJECT_CONFIG.value]["last_config"] = ";".join(configurations)
        self.__save_config()
        UserConfigHandler.last_configurations_changed.emit()

    def reset(self):
        """
        Resets the configuration to default values
        """
        self.__init_sections(True)

    # Property definition block
    darkmode = property(__get_darkmode, __set_darkmode)
    line_wrap = property(__get_line_wrap, __set_line_wrap)
    reopen_last_configuration = property(__get_reopen_last_configuration, __set_reopen_last_configuration)
    last_configurations = property(__get_last_configurations, __set_last_configurations)
    last_position = property(__get_last_ui_position, __set_last_ui_position)
    last_size = property(__get_last_ui_size, __set_last_ui_size)
    show_whats_new = property(__get_what_is_new_value, __set_what_is_new_variable)
    version = property(__get_contest_version, __set_contest_version)
