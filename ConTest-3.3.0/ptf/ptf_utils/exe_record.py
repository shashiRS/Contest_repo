"""
    Copyright Continental Corporation and subsidiaries. All rights reserved.
    :platform: Windows and Linux
    :synopsis:
        This file contains functionality to save  configuration information  and test case verdicts for the latest
        finished test execution run.
"""

# standard python imports
from os import path
from datetime import datetime
import re

# Disabling import error, environment should support yaml
# pylint: disable=import-error
import logging
import os
import yaml

# framework related imports
from ptf.ptf_utils.global_params import get_cfg_paths
from ptf.ptf_utils.global_params import _PROJECT_SPECS, _Test_Verdict
from global_vars import PYTHON_PATH, TestVerdicts, PYTHON_BIT_ARCH, BASE_PYTHON_VERSION, TEST_ENVIRONMENT
from data_handling import helper

# Create logger object for this file
LOG = logging.getLogger("EXEC_RECORD")

# Disabling warnings  as current implementation is required as per logic
# pylint: disable=too-many-locals, too-many-branches


def save_exe_record():
    """
    Function to extract the latest test case verdicts and framework configuration data and saving it into yaml file
    """
    # extracting txt and base report locations from paths dictionary
    report_file = [path.join(get_cfg_paths(helper.EXEC_RECORD_DIR), "exec_record.yml")]
    external_report_dir = _PROJECT_SPECS["ext_report_dir_with_timestamp"]
    # if report directory was given via cli then add it to above list
    if external_report_dir:
        report_file.append(path.join(external_report_dir, "exec_record.yml"))

    # Initialize test case list for each type of test verdict
    passed_tests = []
    inconclusive_tests = []
    failed_tests = []
    skipped_tests = []
    unknown_tests = []

    for test, verdict in _Test_Verdict.items():
        # Remove parameterized duplicates
        if "(index:" in test:
            test = test.split("(index:")[0]
        if "-testrun" in test:
            test = test.split("-testrun")[0]
        # Generate list of test cases
        if test not in helper.SETUP_TEARDOWN_METHOD_NAMES:
            if verdict == TestVerdicts.PASS.name:
                passed_tests.append(test)
            elif verdict == TestVerdicts.INCONCLUSIVE.name:
                inconclusive_tests.append(test)
            elif verdict == TestVerdicts.FAIL.name:
                failed_tests.append(test)
            elif verdict == TestVerdicts.SKIP.name:
                skipped_tests.append(test)
            elif verdict == TestVerdicts.UNKNOWN.name:
                unknown_tests.append(test)

    # Getting abs path just so all paths have the same format
    external_paths = [os.path.abspath(ep) for ep in _PROJECT_SPECS["additional_paths"]]
    # Eliminate duplicated paths if same path was given in CLI and cfg.ini.
    external_paths = list(set(external_paths))

    # Get values for test_config data dict
    test_config = {
        "config_path": _PROJECT_SPECS["cfg_file_path"],
        "setup_path": _PROJECT_SPECS["setup_file_path"],
        "base_loc_path": _PROJECT_SPECS["paths"]["basePath"],
        "report_dir": _PROJECT_SPECS["paths"]["externalReport"],
        "external_loc": external_paths,
        "timestamp": _PROJECT_SPECS["timestamp"],
        "python_exe_path": PYTHON_PATH,
        "base_python_ver": BASE_PYTHON_VERSION,
        "python_bit_arch": PYTHON_BIT_ARCH,
        "test_environment": TEST_ENVIRONMENT,
    }
    # Convert to set to remove duplicates in each verdict category for param test cases and/or multiple runs
    # For test cases that have different verdicts for multiple runs and/or parameters, it will be saved only one record
    # in each corresponding verdict list
    test_verdicts = {
        "passed_tests": list(set(passed_tests)),
        "failed_tests": list(set(failed_tests)),
        "skipped_tests": list(set(skipped_tests)),
        "inconclusive_tests": list(set(inconclusive_tests)),
        "unknown_test": list(set(unknown_tests)),
    }
    run_options = {
        "randomize": _PROJECT_SPECS["randomize"],
        "tests_frequency": _PROJECT_SPECS["tests_frequency"],
        "run_mode": _PROJECT_SPECS["run_mode"],
    }
    execution_data = {
        "execution_date": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S"),
    }

    for exec_path in report_file:
        with open(exec_path, "w", encoding="utf-8") as file:
            file.write("# Test configuration data\n")
            yaml.dump(test_config, file)
            file.write("\n# Test verdict lists\n")
            yaml.dump(test_verdicts, file)
            file.write("\n# Run Options\n")
            yaml.dump(run_options, file)
            file.write("\n# Execution Information\n")
            yaml.dump(execution_data, file)


def load_exec_record(exec_dir_path=None):
    """
    Function to load test case verdicts and framework configuration data from exec_record,yml file

    :param str exec_dir_path: Path to execution record file (exec_record,yml)

    :returns: execution record data
    :rtype: dictionary
    """
    # Safely open exec_record.yml
    exec_info = []
    with open(exec_dir_path, "r", encoding="utf-8") as stream:
        try:
            exec_info = yaml.safe_load(stream)
        except yaml.YAMLError as e:
            raise RuntimeError(
                f"Unable to parse the execution record .yml file. Error when reading {exec_info}."
            ) from e
    return exec_info


def process_exec_data(args):
    """
    Function to change CLI args data based on data provided in execution record file (exec_record.yml).
    In case CLI args were given by user they will be used instead of execution record values.

    :param obj args: Run configuration args to be filled with information from exec_record.yml

    :returns: Selected test cases that needs to be run based on selected verdict
    :rtype: list
    """
    # check if verdict option was given
    if args.v is None:
        raise RuntimeError(
            "Verdict option argument, -v, must be provided to enable run_exec_record. Please provide -v  value"
        )

    # check if execution record path was given and if path is valid
    if args.y is not None:
        # Check if full path to a valid exec_record.yml file was provided
        reg_compile = re.compile(r".*exec_record.yml")
        report_name = reg_compile.match(args.y)
        if report_name:
            # Check if path to exec_record.yml exists
            if not path.exists(args.y):
                raise RuntimeError(
                    "Wrong -y option detected: "
                    "\nLocation (" + args.y + ") doesn't exist. Please check if execution record file exists"
                )
        else:
            raise RuntimeError("Wrong -y value detected: \nPlease provide full path to execution record yml file")
    # Exit execution and ask user to give path to exec_record.yml file if not given
    else:
        raise RuntimeError(
            "exec_record_yml argument, -y, must be provided to enable run_exec_record. Please provide -y  value"
        )

    # Load exec_record.yml data
    exec_data = load_exec_record(args.y)

    # Copy exec_data to args
    # Verify if path to cfg.ini in exec_record.yml is valid
    if not path.exists(exec_data["config_path"]):
        raise RuntimeError(
            "Wrong value detected: "
            "\nLocation (" + exec_data["config_path"] + ") doesn't exist. Please check if cfg.ini file exists"
        )
    args.c = exec_data["config_path"]
    # Verify if path to setup in exec_record.yml is valid
    if not path.exists(exec_data["setup_path"]):
        raise RuntimeError(
            "Wrong value detected: "
            "\nLocation (" + exec_data["setup_path"] + ") doesn't exist. Please check if setup file exists"
        )
    args.setup_file = exec_data["setup_path"]
    # Verify if path to base location in exec_record.yml is valid
    if not path.exists(exec_data["base_loc_path"]):
        raise RuntimeError(
            "Wrong value detected: "
            "\nLocation (" + exec_data["base_loc_path"] + ") doesn't exist. Please check if base location exists"
        )
    args.l = exec_data["base_loc_path"]
    # Verify external path exists
    if exec_data["external_loc"]:
        for loc in exec_data["external_loc"]:
            # Verify if external path is valid
            if not path.exists(loc):
                raise RuntimeError(
                    "Wrong value detected: "
                    "\nLocation (" + loc + ") doesn't exist. Please check if external path exists"
                )
    args.e = [exec_data["external_loc"]]
    # Verify if path to report dir in exec_record.yml is valid
    if exec_data["report_dir"]:
        if not path.exists(exec_data["report_dir"]):
            raise RuntimeError(
                "Wrong value detected: "
                "\nLocation (" + exec_data["report_dir"] + ") doesn't exist. Please check if report directory exists"
            )
        args.report_dir = exec_data["report_dir"]

    # Get random_execution flag, number of loops, run mode and timestamp enabled status
    args.random_execution = exec_data["randomize"]
    args.n = exec_data["tests_frequency"]
    args.r = exec_data["run_mode"]
    args.timestamp = exec_data["timestamp"]

    # Get list of selected test cases
    selected_test_cases = []
    [verdicts] = args.v
    for verdict in verdicts:
        if verdict == TestVerdicts.PASS.name.lower():
            selected_test_cases.extend(exec_data["passed_tests"])
        if verdict == TestVerdicts.INCONCLUSIVE.name.lower():
            selected_test_cases.extend(exec_data["inconclusive_tests"])
        if verdict == TestVerdicts.FAIL.name.lower():
            selected_test_cases.extend(exec_data["failed_tests"])
        if verdict == TestVerdicts.SKIP.name.lower():
            selected_test_cases.extend(exec_data["skipped_tests"])
        if verdict == TestVerdicts.UNKNOWN.name.lower():
            selected_test_cases.extend(exec_data["unknown_tests"])

    return selected_test_cases
