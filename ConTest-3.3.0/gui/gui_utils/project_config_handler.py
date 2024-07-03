"""
    Copyright 2019 Continental Corporation

    :file: project_config_handler.py
    :platform: Windows, Linux
    :synopsis:
        This file handles the project configurations. It contains functions to persist and load
        configurations and provides validation functions to make sure the configuration fulfills
        our requirements.

    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
import ast
import configparser
import logging
import os
import sys
from enum import Enum
import copy

import global_vars
from gui import ui_helper
from data_handling import helper

LOG = logging.getLogger('Project config handler')


class Sections(Enum):
    """
    The configuration sections. The order is the same as it is then in the stored configuration
    file.
    """
    INFO = 'INFO'
    FRAMEWORK = 'Framework'
    PTF_CONFIG = 'ptf_cfg_section'
    PTF_REPORT = 'ptf_report_section'
    PTF_T32 = 'ptf_t32_section'
    MISCELLANEOUS = 'miscellaneous'
    GUI_SETTINGS = 'gui_settings'


class ProjectConfigHandler:
    """
    This handler provides the possibility to work with persisted user configurations.
    Each property defined in this class will be persisted on writes. Also each property returns
    a default value if it was never written.
    """

    # The error message to be shown if the selected path is not in base path.
    __PATH_NOT_IN_BASEPATH_ERROR = "The {} path needs to be within base path.\n\n" \
                                   "Given path: {}.\nBase path: {}"

    def __init__(self, path=None):
        """
        Initialize the configuration handler. By default, no configuration file is loaded,
        but for each configuration property a default value will be provided.

        :param str path: Optional config file that should be loaded on initialisation
        """
        self.__config = configparser.ConfigParser(comment_prefixes='/', allow_no_value=True)

        # Init sections
        self.__init_sections()

        # Stores the config path that is currently loaded
        self.loaded_config = None

        # The original base path after loading a configuration
        # Will be set once after loading a configuration
        self.__original_basepath = None

        if path:
            self.load_config(path)

    def load_config(self, path):
        """
        Load configuration from given file.
        To check the configuration for consistency, please use `:func:post_load_config` function

        :param str path: The file path to load.
        """
        if os.path.exists(path):
            self.__config.read(path)
            self.loaded_config = path
            self.__original_basepath = self.base_path
        else:
            raise FileNotFoundError(
                "Could not load project configuration {}. File not found.".format(path))

    def post_load_config(self):
        """
        This method can be called after a configuration file is loaded. It will verify that
        all configured paths exist and are properly configured.
        Additionally, it will append additional paths to system path and create the reporting
        directory if it does not exist.
        """
        # disable pylint check since the verification is still quite straightforward and rewriting
        # the code would only make it worse.
        # pylint: disable=too-many-branches
        LOG.info("Verifying paths in config file ...")

        errors = []

        # First check base path
        if not self.base_path or not os.path.exists(self.base_path):
            errors.append("Base path '{}' does not exist.".format(self.base_path))

        # Now check other paths that should be in base path
        for path in [self.ptf_test_path, self.cmm_test_path, self.canoe_cfg_path,
                     self.cte_cfg, self.cte_location]:
            if path and path != 'None':
                if not os.path.exists(path):
                    errors.append("Path '{}' does not exist.".format(path))
                elif not path.startswith(self.base_path):
                    errors.append("Path '{}' not located in base path.".format(path))

        # The report directory will be created if it does not exist, therefore we
        # need to handle it separately
        if self.report_path and self.report_path != 'None' \
                and not os.path.exists(self.report_path) and not errors:
            LOG.info("Report directory %s does not exist. Creating it.", self.report_path)
            try:
                os.makedirs(self.report_path)
            except PermissionError as err:
                raise RuntimeError("Report directory path error while creating it.\n{}".format(err))

        # Finally verify the additional paths.
        # If they exist, add them to system path
        for path in self.additional_paths:
            if not os.path.exists(path):
                errors.append("Additional path '{}' does not exist".format(path))
            elif path not in sys.path:
                sys.path.append(path)
                LOG.info("%s added to sys.path", path)

        # Check verification result. If there are errors, log them and raise an exception
        if errors:
            for error in errors:
                LOG.error(error)
            raise RuntimeError("\n".join(errors))

        LOG.info("Verification succeeded.")

    def pre_save_verify_config(self):
        """
        Verifies that the configuration structure is consistent and all required
        values are properly set before saving it to disk.
        """
        # removing capl test path entry in ptf_cfg_section since this will not be required after
        # v2.0.0 release in which we take canoe cfg path directly from user
        self.__config.remove_option(Sections.PTF_CONFIG.value, 'capl tests path')
        if not self.base_path or not self.ptf_test_path:
            raise RuntimeError("Please give following mandatory paths:\n\n"
                               "- Base Path\n"
                               "- Python Tests")
        if self.use_cte_checkbox == "True":
            if not self.cte_location or not self.cte_cfg:
                raise RuntimeError("Please give CTF Paths:\n\n"
                                   "- CTF Location\n"
                                   "- CTF Cfg")
            if not self.canoe_cfg_path:
                raise RuntimeError("Please give CANoe Cfg Path Required For CTF Execution:\n\n"
                                   "- CANoe Cfg")
        if self.report_path == "":
            self.report_path = self.base_path
            msg = "Report path not given\nReports will be saved in Base Path"
            ui_helper.pop_up_msg(helper.InfoLevelType.INFO, msg_str=msg)

    def save_config(self, path=None):
        """
        Saves the configuration to given path.

        :param str path: The path to store the file. If not given, the last loaded file path will
                         be used.
        """
        # First priority is the given path
        save_to_path = path
        # If this is not given, fallback to already stored path
        if not save_to_path:
            save_to_path = self.loaded_config
        # If this is again not given, raise error
        if not save_to_path:
            raise ValueError("Please provide a path to the file to save or load a configuration "
                             "before saving.")

        # Make sure that the configuration is in proper shape
        self.pre_save_verify_config()

        # writing information on top of configuration file
        for option in self.__config.options(Sections.INFO.value):
            self.__config.remove_option(Sections.INFO.value, option)
        self.__config.set(Sections.INFO.value,
                          '; Please do not change this file manually. This file should '
                          'only be created from ' + global_vars.FW_NAME, None)

        # adding a FW section
        self.__config[Sections.FRAMEWORK.value]['name'] = global_vars.TEST_ENVIRONMENT

        # Finally save the configuration
        with open(save_to_path, 'w') as configfile:
            self.__config.write(configfile)

    def __init_sections(self, reset=False):
        """
        Initialize the sections in the configuration
        :param bool reset: If only non-existing sections should be created or all sections should
                           be reset
        """
        for section in Sections:
            if reset or section.value not in self.__config.sections():
                self.__config[section.value] = {}

    # This is a getter, so we need to provide the 'self' parameter
    # pylint: disable=no-self-use
    def __get_framework_name(self):
        """
        Returns the test framework name.

        :return: The framework name
        :rtype: str
        """
        return global_vars.TEST_ENVIRONMENT

    def __get_basepath(self):
        """
        Returns the base path.

        :return: The stored basepath. Can be None.
        :rtype: str
        """
        return self.__config.get(Sections.PTF_CONFIG.value, 'base path', fallback=None)

    def __set_basepath(self, basepath):
        """
        Sets the base path and updates all related other paths (like ptf test path or report path).

        :param str basepath: The basepath to store
        """
        old_base_path = self.base_path
        self.__config[Sections.PTF_CONFIG.value]['base path'] = basepath if basepath else None
        # Update other paths, if set
        for update_path in ['ptf_test_path', 'cmm_test_path', 'canoe_cfg_path', 'report_path',
                            'cte_location', 'cte_cfg']:
            update_path_value = getattr(self, update_path)
            if update_path_value and update_path_value.startswith(old_base_path):
                setattr(self, update_path, update_path_value.replace(old_base_path, basepath))

    def __get_original_basepath(self):
        """
        Returns the original basepath that was stored in the last loaded configuration.
        """
        return self.__original_basepath

    def __get_ptf_test_path(self):
        """
        Returns the ptf test path.

        :return: The stored ptf test path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'ptf tests path', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __set_ptf_test_path(self, ptf_test_path):
        """
        Stores the ptf test path. Verifies that the path is in base path.

        :param str ptf_test_path: The ptf test path to store.
        """
        if not ptf_test_path.startswith(self.base_path):
            raise RuntimeError(
                self.__PATH_NOT_IN_BASEPATH_ERROR.format('Python', ptf_test_path, self.base_path))
        self.__config[Sections.PTF_CONFIG.value]['ptf tests path'] = ptf_test_path

    def __get_cmm_test_path(self):
        """
        Returns the cmm test path.

        :return: The stored cmm test path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'cmm tests path', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __set_cmm_test_path(self, cmm_test_path):
        """
        Stores the cmm test path. Verifies that the path is in base path.

        :param str cmm_test_path: The cmm test path to store.
        """
        if cmm_test_path and not cmm_test_path.startswith(self.base_path):
            raise RuntimeError(
                self.__PATH_NOT_IN_BASEPATH_ERROR.format('cmm', cmm_test_path, self.base_path))
        self.__config[Sections.PTF_CONFIG.value]['cmm tests path'] = cmm_test_path

    def __get_capl_test_path(self):
        """
        Returns the capl test path.
        NOTE: This method is kept to detect and inform user that user has saved CAPL tests in old
        contest version and how user can make change in cfg to take advantage of new way of CANoe
        cfg tests handling which is easier than before.
        :return: The stored capl test path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'capl tests path', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __get_canoe_cfg_path(self):
        """
        Returns the CANoe cfg path.

        :return: The stored CANoe cfg path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'canoe cfg path', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __set_canoe_cfg_path(self, canoe_cfg_path):
        """
        Stores the CANoe cfg path. Verifies that the path is in base path.

        :param str canoe_cfg_path: The ptf test path to store.
        """
        if canoe_cfg_path and not canoe_cfg_path.startswith(self.base_path):
            raise RuntimeError(
                self.__PATH_NOT_IN_BASEPATH_ERROR.format(
                    'CANoe Cfg', canoe_cfg_path, self.base_path))
        self.__config[Sections.PTF_CONFIG.value]['canoe cfg path'] = canoe_cfg_path

    def __get_cte_cfg(self):
        """
        Returns the CTF (CANoe Test Environment) cfg path.

        :return: The stored CTF (CANoe Test Environment) cfg path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'cte cfg', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __set_cte_cfg(self, cte_cfg_path):
        """
        Stores the CTF (CANoe Test Framework) cfg path. Verifies that the path is in base path.

        :param str cte_cfg_path: The CTF (CANoe Test Framework) cfg path to store.
        """
        if cte_cfg_path and not cte_cfg_path.startswith(self.base_path):
            raise RuntimeError(
                self.__PATH_NOT_IN_BASEPATH_ERROR.format(
                    'CTF Cfg', cte_cfg_path, self.base_path))
        self.__config[Sections.PTF_CONFIG.value]['cte cfg'] = cte_cfg_path

    def __get_cte_location(self):
        """
        Returns the CTF zip path.

        :return: The stored CTF zip path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_CONFIG.value, 'cte zip', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __set_cte_location(self, cte_zip_path):
        """
        Stores the CTF zip path. Verifies that the path is in base path.

        :param str cte_zip_path: The CTF exe path to store.
        """
        if cte_zip_path and not cte_zip_path.startswith(self.base_path):
            raise RuntimeError(
                self.__PATH_NOT_IN_BASEPATH_ERROR.format(
                    'CTF Zip', cte_zip_path, self.base_path))
        self.__config[Sections.PTF_CONFIG.value]['cte zip'] = cte_zip_path

    def __get_use_cte_checkbox(self):
        """
        Returns the CTF usage flag.

        :return: The stored CTF usage flag. Can be None.
        :rtype: bool
        """
        use_cte = self.__config.get(Sections.PTF_CONFIG.value, 'use cte', fallback=None)
        # For backwards compatibility
        return None if use_cte == 'None' else use_cte

    def __set_use_cte_checkbox(self, use_cte):
        """
        Stores the CTF usage flag.

        :param bool use_cte: The CTF usage flag to store.
        """
        self.__config[Sections.PTF_CONFIG.value]['use cte'] = str(use_cte)

    def __get_t32_executable_name(self):
        """
        Returns the trace32 executable name.

        :return: The stored trace32 executable name. Can be None.
        :rtype: str
        """
        name = self.__config.get(Sections.PTF_T32.value, 'executable name', fallback=None)
        # For backwards compatibility
        return None if name == 'None' else name

    def __get_t32_source_code_path(self):
        """
        Returns the trace32 source code path.

        :return: The stored trace32 source code path. Can be None.
        :rtype: str
        """
        path = self.__config.get(Sections.PTF_T32.value, 'source code path', fallback=None)
        # For backwards compatibility
        return None if path == 'None' else path

    def __get_report_path(self):
        """
        Returns the report path.

        :return: The stored report path. Can be None.
        :rtype: str
        """
        return self.__config.get(Sections.PTF_REPORT.value, 'report path', fallback=None)

    def __set_report_path(self, report_path):
        """
        Stores the report path. Verifies that the path is in base path.

        :param str report_path: The report path to store.
        """
        self.__config[Sections.PTF_REPORT.value]['report path'] = report_path

    def __get_additional_paths(self):
        """
         Returns additional paths.

         :return: The additional paths. Might return an empty array, never None.
         :rtype: list
         """
        additional_paths = self.__config.get(Sections.MISCELLANEOUS.value, 'additional paths', fallback=None)
        if additional_paths and additional_paths != 'None':
            # removing spaces if user added them in additional path text editor box
            return [path.strip() for path in additional_paths.split(';')]
        return []

    def __set_additional_paths(self, additional_paths):
        """
        Stores additional paths. Verifies that paths exist.

        :param list additional_paths: The additional paths to store
        """
        if additional_paths:
            # Filter out empty entries
            additional_paths = list(filter(None, additional_paths))
            for path in additional_paths:
                if not os.path.exists(path):
                    raise FileNotFoundError(
                        "Additional path '{}' does not exist. Please remove or change.".format(
                            path))

        self.__config[Sections.MISCELLANEOUS.value]['additional paths'] = \
            ";".join(additional_paths)

    def __get_selected_tests(self):
        """
         Returns selected tests of different types (python, cmm, capl)

         :return: The selected tests (python, cmm, capl)
         :rtype: dictionary
         """
        to_return = copy.copy(ui_helper.TESTS_FOR_CFG)
        python_tests = ast.literal_eval(
            self.__config.get(Sections.GUI_SETTINGS.value, 'selected_tests', fallback=None))
        # this block is added for supporting configurations stored with old versions (v1.0 to v1.4)
        # since they do not contain such sections (cmm and capl sections)
        try:
            cmm_tests = ast.literal_eval(
                self.__config.get(Sections.GUI_SETTINGS.value, 'cmm_tests', fallback=None))
        except ValueError:
            cmm_tests = list()
            LOG.warning("CMM tests section not found in cfg file. Please save your CMM"
                        " tests with new version (if required).")
        try:
            capl_tests = ast.literal_eval(
                self.__config.get(Sections.GUI_SETTINGS.value, 'capl_tests', fallback=None))
        except ValueError:
            capl_tests = dict()
            LOG.warning("CAPL tests section not found in cfg file. Please save your CAPL"
                        " tests with new version (if required).")

        if python_tests:
            to_return["selected_tests"] = python_tests
        if cmm_tests:
            to_return["cmm_tests"] = cmm_tests
        if capl_tests:
            to_return["capl_tests"] = capl_tests
        # if there is None value for selected tests then return empty dictionary
        return to_return

    def __set_selected_tests(self, tests_in_cfg):
        """
        Sets the selected tests to store into different test categories (python, cmm, capl).
        It is to be noted that 'selected_tests' can be treated as python category for backward
        compatibility.

        :param dictionary selected_tests: Dictionary containing tests categories as key and their
            values as saved tests in cfg
        """
        if not tests_in_cfg:
            tests_in_cfg = None
        self.__config[Sections.GUI_SETTINGS.value]['selected_tests'] = \
            str(tests_in_cfg["selected_tests"])
        self.__config[Sections.GUI_SETTINGS.value]['cmm_tests'] = str(tests_in_cfg["cmm_tests"])
        self.__config[Sections.GUI_SETTINGS.value]['capl_tests'] = str(tests_in_cfg["capl_tests"])

    def __get_num_loops(self):
        """
        Returns the number of iterations how often the testcases should be executed.

        :return: The number of iterations. Default value of 1. Never None.
        :rtype: int
        """
        # Fallback for backwards compatibility
        if self.__config.get(Sections.GUI_SETTINGS.value, 'no. of loops', fallback=1) != 'None':
            return self.__config.getint(Sections.GUI_SETTINGS.value, 'no. of loops', fallback=1)
        return 1

    def __set_num_loops(self, num_loops):
        """
        Set the number of iterations how often the testcases should be executed.

        :param int num_loops: The number of loops to store.
        """
        self.__config[Sections.GUI_SETTINGS.value]['no. of loops'] = str(num_loops)

    def reset(self):
        """
        Resets the configuration to default values.
        """
        self.__init_sections(True)

    # Property definition block
    fw_name = property(__get_framework_name)
    base_path = property(__get_basepath, __set_basepath)
    original_base_path = property(__get_original_basepath)
    ptf_test_path = property(__get_ptf_test_path, __set_ptf_test_path)
    cmm_test_path = property(__get_cmm_test_path, __set_cmm_test_path)
    capl_test_path = property(__get_capl_test_path)
    canoe_cfg_path = property(__get_canoe_cfg_path, __set_canoe_cfg_path)
    cte_location = property(__get_cte_location, __set_cte_location)
    cte_cfg = property(__get_cte_cfg, __set_cte_cfg)
    use_cte_checkbox = property(__get_use_cte_checkbox, __set_use_cte_checkbox)
    t32_executable_name = property(__get_t32_executable_name)
    t32_source_code_path = property(__get_t32_source_code_path)
    report_path = property(__get_report_path, __set_report_path)
    additional_paths = property(__get_additional_paths, __set_additional_paths)
    selected_tests = property(__get_selected_tests, __set_selected_tests)
    num_loops = property(__get_num_loops, __set_num_loops)
