"""
    Copyright 2019 Continental Corporation

    :file: test_cli_options.py
    :platform: Windows, Linux
    :synopsis:
        File containing release test. Checking all CLI options is working as expected.
    :author:
        - Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""
# disabling import error as they are installed at start of framework
# pylint: disable=import-error
import os
import sys
import subprocess
import shutil
import unittest
import glob
import json
import re
import pytest

try:
    SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
    BASE_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", ".."))
    sys.path.append(os.path.abspath(os.path.join(BASE_DIR, "..")))
    from ptf.tests.release_testing import format_helper
finally:
    pass


@pytest.mark.skipif(sys.platform != "win32", reason="Executed only on Windows platform")
class TestCLIOptions(unittest.TestCase):
    """Test Class for checking working of CLI options"""

    @classmethod
    def setUpClass(cls):
        """
        Initialize the class with variables, objects etc., for testing
        """
        cls.app_run_dict = {
            "config_file": os.path.join(SCRIPT_DIR, "PTF_Config_report_gen.ini"),
            "contest_app": os.path.join(SCRIPT_DIR, "..", "..", "..", "main.py"),
            "setup_file_success_1": os.path.join(SCRIPT_DIR, "sample_test", "setup_for_cli_test.pytest"),
            "setup_file_success_2": "setup_for_cli_test",
            "setup_file_error": SCRIPT_DIR,
        }

        if sys.platform == "linux":
            cls.set_shell = False
        else:
            cls.set_shell = True

    def test_cli_arg_help(self):
        """
        Method for checking help CLI option
        """
        h_run_output = []
        # Checking argument -h
        h_run = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-h"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        h_run_output.append((h_run.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if h_run.returncode:
            h_run_again = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-h"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            h_run_output.append((h_run_again.stdout.decode("utf-8")).replace("\r", ""))
            # Remove line added by __ini__.py from 'contest_verify' API when running for build check
            # When running locally line will not be added to output
            pattern = r"'contest_verify' package version: '\d+.\d+.\d+'\n"
            h_run_output[1] = re.sub(pattern, "", h_run_output[1])
        self.assertEqual(format_helper.HELP_PRINT, "".join(h_run_output))

    def test_cli_args_success(self):
        """
        Method for checking CLI options like config file, base location, run mode success run
        """
        arg_run_output = []
        # Checking arguments -c -l -r
        arg_run = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        arg_run_output.append((arg_run.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if arg_run.returncode:
            arg_run_again = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            arg_run_output.append((arg_run_again.stdout.decode("utf-8")).replace("\r", ""))

        # Check if config file loaded successfully
        self.assertIn(format_helper.CFG_SUCCESS, "".join(arg_run_output))
        # Check if base location updated successfully
        self.assertIn(format_helper.BASE_LOC_SUCCESS, "".join(arg_run_output))
        # Check if auto run has successfully executed
        for expected_print in format_helper.AUTO_RUN_SUCCESS:
            self.assertIn(expected_print, "".join(arg_run_output))
        # No. of iterations read from config file as 1 and test case executed only once
        self.assertIn(format_helper.NO_OF_LOOPS_SUCCESS[0], "".join(arg_run_output))
        self.assertIn(format_helper.NO_OF_LOOPS_SUCCESS[1], "".join(arg_run_output))

    def test_cli_cfg_error(self):
        """
        Method for checking config file option while expecting error
        """
        cfg_run_1_output = []
        cfg_run_2_output = []
        # Check when config file not given
        cfg_run_1 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-c"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        cfg_run_1_output.append((cfg_run_1.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if cfg_run_1.returncode:
            cfg_run_again_1 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-c"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            cfg_run_1_output.append((cfg_run_again_1.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.CFG_ERROR[0], "".join(cfg_run_1_output))

        # Check when wrong config file given
        cfg_run_2 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-c", "path_to_error"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        cfg_run_2_output.append((cfg_run_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if cfg_run_2.returncode:
            cfg_run_again_2 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-c", "path_to_error"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            cfg_run_2_output.append((cfg_run_again_2.stdout.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.CFG_ERROR[1], "".join(cfg_run_2_output))

    def test_cli_run_mode_error(self):
        """
        Method for checking run mode option while expecting error
        """
        run_mode_1_output = []
        run_mode_2_output = []
        # Check when argument not given
        run_mode_1 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-r"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        run_mode_1_output.append((run_mode_1.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if run_mode_1.returncode:
            run_mode_again_1 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-r"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            run_mode_1_output.append((run_mode_again_1.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.RUN_ERROR[0], "".join(run_mode_1_output))

        # Check when wrong argument given
        run_mode_2 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-r", "man"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        run_mode_2_output.append((run_mode_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if run_mode_2.returncode:
            run_mode_again_2 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-r", "man"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            run_mode_2_output.append((run_mode_again_2.stdout.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.RUN_ERROR[1], "".join(run_mode_2_output))

    def test_cli_timestamp_on_off_check(self):
        """
        Method for checking timestamp is on or off
        """
        time_stamp_1_output = []
        time_stamp_2_output = []
        # Check when timestamp argument by default 'on'
        time_stamp_1 = subprocess.run(
            [
                "python",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        time_stamp_1_output.append((time_stamp_1.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if time_stamp_1.returncode:
            time_stamp_again_1 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            time_stamp_1_output.append((time_stamp_again_1.stdout.decode("utf-8")).replace("\r", ""))

        timestamp_match_obj = re.search(r"(\d+:\d+:\d+,\d+)", "".join(time_stamp_1_output))

        self.assertIsNotNone(timestamp_match_obj)
        # Check when timestamp argument is 'off'
        time_stamp_2 = subprocess.run(
            [
                "python",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "--timestamp",
                "off",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        time_stamp_2_output.append((time_stamp_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if time_stamp_2.returncode:
            time_stamp_again_2 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "--timestamp",
                    "off",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            time_stamp_2_output.append((time_stamp_again_2.stdout.decode("utf-8")).replace("\r", ""))

        timestamp_match_obj = re.search(r"(\d+:\d+:\d+,\d+)", "".join(time_stamp_2_output))

        self.assertIsNone(timestamp_match_obj)

    def test_cli_no_of_loops_error(self):
        """
        Method for checking no_of_loops option while expecting error
        """
        no_of_loops_1_output = []
        no_of_loops_2_output = []
        # Check when argument not given
        no_of_loops_1 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-n"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        no_of_loops_1_output.append((no_of_loops_1.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if no_of_loops_1.returncode:
            no_of_loops_again_1 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-n"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            no_of_loops_1_output.append((no_of_loops_again_1.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.NO_OF_LOOPS_ERROR[0], "".join(no_of_loops_1_output))

        # Check when wrong argument given
        no_of_loops_2 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-n", "abc"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        no_of_loops_2_output.append((no_of_loops_2.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if no_of_loops_2.returncode:
            no_of_loops_again_2 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-n", "abc"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            no_of_loops_2_output.append((no_of_loops_again_2.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.NO_OF_LOOPS_ERROR[1], "".join(no_of_loops_2_output))

    def test_cli_no_of_loops_success(self):
        """
        Method for checking number of iterations the test cases executed provided from CLI
        """
        no_of_loops_output = []
        no_of_loops = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "-n",
                "3",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        no_of_loops_output.append((no_of_loops.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if no_of_loops.returncode:
            arg_run_again = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "-n",
                    "3",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            no_of_loops_output.append((arg_run_again.stdout.decode("utf-8")).replace("\r", ""))

        # checking the number of iterations the testcase executed as 3 times
        for index in range(1, 4):
            # checking PASS Testcase
            self.assertIn(format_helper.NO_OF_LOOPS_SUCCESS[0] + "-testrun__" + str(index), "".join(no_of_loops_output))
            # checking FAIL Testcase
            self.assertIn(format_helper.NO_OF_LOOPS_SUCCESS[1] + "-testrun__" + str(index), "".join(no_of_loops_output))

    def test_cli_base_loc_error(self):
        """
        Method for checking base location option while expecting error
        """
        set_base_loc_1_output = []
        set_base_loc_2_output = []
        # Check when base location not given
        set_base_loc_1 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-l"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_base_loc_1_output.append((set_base_loc_1.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_base_loc_1.returncode:
            set_base_loc_again_1 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-l"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_base_loc_1_output.append((set_base_loc_again_1.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.BASE_LOC_ERROR[0], "".join(set_base_loc_1_output))

        # Check when wrong base location given
        set_base_loc_2 = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "-l", "path_to_error"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_base_loc_2_output.append((set_base_loc_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_base_loc_2.returncode:
            set_base_loc_again_2 = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "-l", "path_to_error"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_base_loc_2_output.append((set_base_loc_again_2.stdout.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.BASE_LOC_ERROR[1], "".join(set_base_loc_2_output))

    def test_cli_setup_file_success(self):
        """
        Method for checking the CLI option setup file success run
        """
        set_setup_file_1 = []
        set_setup_file_2 = []
        # Check custom setup file
        set_setup_file_run_1 = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "--setup-file",
                self.app_run_dict["setup_file_success_1"],
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_setup_file_1.append((set_setup_file_run_1.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_setup_file_run_1.returncode:
            set_setup_file_run_again_1 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "--setup-file",
                    self.app_run_dict["setup_file_success_1"],
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_setup_file_1.append((set_setup_file_run_again_1.stdout.decode("utf-8")).replace("\r", ""))

        for expected_print in format_helper.SETUP_FILE_SUCCESS:
            self.assertIn(expected_print, "".join(set_setup_file_1))

        # Check custom setup file by just filename (without extn .pytest)
        set_setup_file_run_2 = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "--setup-file",
                self.app_run_dict["setup_file_success_2"],
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_setup_file_2.append((set_setup_file_run_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_setup_file_run_2.returncode:
            set_setup_file_run_again_2 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "--setup-file",
                    self.app_run_dict["setup_file_success_2"],
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_setup_file_2.append((set_setup_file_run_again_2.stdout.decode("utf-8")).replace("\r", ""))

        for expected_print in format_helper.SETUP_FILE_SUCCESS:
            self.assertIn(expected_print, "".join(set_setup_file_2))

    def test_cli_setup_file_error(self):
        """
        Method for checking the CLI option setup file success run
        """
        set_setup_file_1 = []
        set_setup_file_2 = []
        # Check when no setup file given
        set_setup_file_run_1 = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "--setup-file",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_setup_file_1.append((set_setup_file_run_1.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_setup_file_run_1.returncode:
            set_setup_file_run_again_1 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "--setup-file",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_setup_file_1.append((set_setup_file_run_again_1.stderr.decode("utf-8")).replace("\r", ""))

        self.assertIn(format_helper.SETUP_FILE_ERROR[0], "".join(set_setup_file_1))

        # Check when wrong path given
        set_setup_file_run_2 = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "-r",
                "auto",
                "--setup-file",
                self.app_run_dict["setup_file_error"],
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        set_setup_file_2.append((set_setup_file_run_2.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if set_setup_file_run_2.returncode:
            set_setup_file_run_again_2 = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "-r",
                    "auto",
                    "--setup-file",
                    self.app_run_dict["setup_file_error"],
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            set_setup_file_2.append((set_setup_file_run_again_2.stdout.decode("utf-8")).replace("\r", ""))

        self.assertIn(format_helper.SETUP_FILE_ERROR[1], "".join(set_setup_file_2))

    def test_filter_error(self):
        """
        Method for checking CLI options for missing arguments after --filter
        """
        filter_output = []
        filter_run = subprocess.run(
            ["python3", self.app_run_dict["contest_app"], "--filter"],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        filter_output.append((filter_run.stderr.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if filter_run.returncode:
            filter_run_again = subprocess.run(
                ["python", self.app_run_dict["contest_app"], "--filter"],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            filter_output.append((filter_run_again.stderr.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.FILTER_ERROR[0], "".join(filter_output))

    def test_incorrect_filter_via_cli(self):
        """
        Test method to give error message if all wrong tag/tags given via cli
        """
        filter_output = []
        filter_run = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "--filter",
                "tag",
                "x",
                "-r",
                "auto",
                "--timestamp",
                "off",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        filter_output.append((filter_run.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if filter_run.returncode:
            filter_run_again = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "--filter",
                    "tag",
                    "x",
                    "-r",
                    "auto",
                    "--timestamp",
                    "off",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            filter_output.append((filter_run_again.stdout.decode("utf-8")).replace("\r", ""))
        self.assertIn(format_helper.WRONG_FILTER[0], "".join(filter_output))

    def test_multiple_correct_filters_via_cli(self):
        """
        Test method for multiple correct tags given via cli
        """
        new_report_folder_path = None
        filter_output = []
        filter_run = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "--filter",
                "tag",
                "hil",
                "sil",
                "tag_1",
                "-r",
                "auto",
                "--timestamp",
                "off",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        filter_output.append((filter_run.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if filter_run.returncode:
            filter_run_again = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "--filter",
                    "tag",
                    "hil",
                    "sil",
                    "tag_1",
                    "-r",
                    "auto",
                    "--timestamp",
                    "off",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            filter_output.append((filter_run_again.stdout.decode("utf-8")).replace("\r", ""))
        for line in filter_output[-1].split("\n"):
            if "[ConTest TEST_RUNNER] TXT Reports at : " in line:
                new_report_folder_path = line.replace("[ConTest TEST_RUNNER] TXT Reports at : ", "")
        test_result_json_report = os.path.join(new_report_folder_path, "TEST_RESULT.json")
        expected_tests = [
            "global_setup",
            "SWT_SAMPLE_TESTv1__each",
            "SWT_SAMPLE_TESTv2",
            "SWT_SAMPLE_TESTv3",
            "SWT_SAMPLE_TESTv4",
            "global_teardown",
        ]
        executed_test = []
        with open(test_result_json_report, "r", encoding="utf-8") as file:
            data = json.load(file)
            for i in range(len(data["tests"])):
                executed_test.append(data["tests"][i]["test_name"])
        self.assertSetEqual(
            set(expected_tests), set(executed_test), "All the expected tests are not found in the json report "
        )

    def test_correct_filter_via_cli(self):
        """
        Test method for correct tag given via cli
        """
        new_report_folder_path = None
        filter_output = []
        filter_run = subprocess.run(
            [
                "python3",
                self.app_run_dict["contest_app"],
                "-c",
                self.app_run_dict["config_file"],
                "-l",
                os.path.join(SCRIPT_DIR, "sample_test"),
                "--filter",
                "tag",
                "hil",
                "-r",
                "auto",
                "--timestamp",
                "off",
            ],
            stderr=subprocess.PIPE,
            stdout=subprocess.PIPE,
            shell=self.set_shell,
            check=False,
        )
        filter_output.append((filter_run.stdout.decode("utf-8")).replace("\r", ""))
        # If python3 has error, try with python
        if filter_run.returncode:
            filter_run_again = subprocess.run(
                [
                    "python",
                    self.app_run_dict["contest_app"],
                    "-c",
                    self.app_run_dict["config_file"],
                    "-l",
                    os.path.join(SCRIPT_DIR, "sample_test"),
                    "--filter",
                    "tag",
                    "hil",
                    "-r",
                    "auto",
                    "--timestamp",
                    "off",
                ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE,
                shell=self.set_shell,
                check=False,
            )
            filter_output.append((filter_run_again.stdout.decode("utf-8")).replace("\r", ""))
        for line in filter_output[-1].split("\n"):
            if "[ConTest TEST_RUNNER] TXT Reports at : " in line:
                new_report_folder_path = line.replace("[ConTest TEST_RUNNER] TXT Reports at : ", "")
        test_result_json_report = os.path.join(new_report_folder_path, "TEST_RESULT.json")
        expected_tests = ["global_setup", "SWT_SAMPLE_TESTv1__each", "SWT_SAMPLE_TESTv2", "global_teardown"]
        executed_test = []
        with open(test_result_json_report, "r", encoding="utf-8") as file:
            data = json.load(file)
            for i in range(len(data["tests"])):
                executed_test.append(data["tests"][i]["test_name"])
        self.assertSetEqual(
            set(expected_tests), set(expected_tests), "All the expected tests are not found in the json report "
        )

    @classmethod
    def tearDownClass(cls):
        """
        Terminates or deletes the open files and folders after running unittests
        """
        # delete all report folders
        folders = glob.iglob(os.path.join(SCRIPT_DIR, "sample_test", "reports_*"))
        for folder in folders:
            if os.path.isdir(folder):
                shutil.rmtree(folder)


if __name__ == "__main__":
    unittest.main(verbosity=2)
