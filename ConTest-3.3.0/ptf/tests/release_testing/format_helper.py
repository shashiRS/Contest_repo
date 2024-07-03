"""
    Copyright 2019 Continental Corporation

    :file: format_helper.py
    :platform: Windows, Linux
    :synopsis:
        Helper file containing reports' reference(or expected) format templates for comparing with
        the generated ones
    :author:
        - Christopher Mirajkar <Christopher.Charles.Mirajkar@continental-corporation.com>
"""

import os
import io
import socket
import platform
import global_vars
import main
from ptf.ptf_utils.global_params import get_reporting_parameter
from ptf.ptf_utils.common import _get_user

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_SCRIPT = os.path.join(SCRIPT_DIR, "sample_test", "swt_report_generating_test.pytest")
REPORT_TEST_CASE_NAME_PASS = "SWT_SAMPLE_REPORT_GEN_TEST_PASSv1__each"
REPORT_TEST_CASE_NAME_FAIL = "SWT_SAMPLE_REPORT_GEN_TEST_FAILv1__each"
XML_FAILURE_MSG = (
    "[FATAL ERROR] &#10;&#09;--&gt;  File &quot;"
    + os.path.abspath(os.path.join(SCRIPT_DIR, "sample_test", "swt_report_generating_test.pytest"))
    + "&quot; line 40"
)
# expected json report format
JSON_TEMPLATE = {
    "$schema": "https://cip-config.cmo.conti.de/v2/configuration/contest/"
    "json_report_schema/1.0/schemas/test_report_schema.json",
    "summary": {
        "Runtime": "",
        "Total_Tests": 9,
        "Failed_Tests": 6,
        "Inconclusive_Tests": 0,
        "Skipped_Tests": 0,
        "Passed_Tests": 3,
        "Ignored_Tests": 0,
        "Missing_Tests": 0,
        "Test_Run_Result": False,
        "Test_Environment": global_vars.TEST_ENVIRONMENT,
        "Machine": socket.gethostname(),
        "User": _get_user(),
        "Reporting_Parameters": get_reporting_parameter(),
    },
    "tests": [
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "global_setup",
            "test_duration": "",
            "test_date": "",
            "test_status": "PASSED",
            "test_verifies": [],
            "automates_id": [],
            "test_tags": [],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": None,
            "test_skip_reason": None,
        },
        {
            "test_execution": [" Test Step : Generate report", " Expected : Report generated"],
            "test_type": "python",
            "test_details": ["This testcase is used for testing the report generation"],
            "precondition": [],
            "test_name": REPORT_TEST_CASE_NAME_PASS,
            "test_duration": "",
            "test_date": "",
            "test_status": "PASSED",
            "test_verifies": ["ASTT-968"],
            "automates_id": ["ID_1"],
            "test_tags": ["each", "python", "report_generating_test"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": None,
            "test_skip_reason": None,
        },
        {
            "test_execution": [" Test Step : Generate report", " Expected : Report generated"],
            "test_type": "python",
            "test_details": ["This testcase is used for testing the report generation"],
            "precondition": [],
            "test_name": REPORT_TEST_CASE_NAME_FAIL,
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": ["ASTT-968"],
            "automates_id": ["ID_2"],
            "test_tags": ["each", "python", "report_generating_test"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": f'[FATAL ERROR] \n\t-->  File "{TEST_SCRIPT}" line 44',
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "SWT_PTF_ASSERTS_FAIL_FOR_JUNIT_FAILUREv1",
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": [],
            "automates_id": ["ID_3"],
            "test_tags": ["python"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            # disable consider-using-f-string due to testing purpose
            # pylint: disable=C0209
            "test_failure": '1 != 2 this is contest specific exception \n\t-->  File "{}" '
            "line 50".format(TEST_SCRIPT),
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "SWT_PTF_EXPECTS_FAIL_FOR_JUNIT_ERRORv1",
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": [],
            "automates_id": ["ID_4"],
            "test_tags": ["python"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": "['1 != 2 this is contest expects specific exception \\n\\t-->  File "
            "\"{}\" line 54', '3 != 4 this is contest expects specific exception "
            '\\n\\t-->  File "{}" line 57\']'.format(
                TEST_SCRIPT.replace("\\", "\\\\"), TEST_SCRIPT.replace("\\", "\\\\")
            ),
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "SWT_GENERAL_FAIL_FOR_JUNIT_ERRORv1",
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": [],
            "automates_id": [],
            "test_tags": ["python"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": "this is forced Runtimeerror via python",
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "SWT_PARAM_ADD_JUNIT_TESTv1(index: 0)",
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": [],
            "automates_id": ["ID_5"],
            "test_tags": ["parameterized", "python"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": f'1 + 2 != 4 \n\t-->  File "{TEST_SCRIPT}" line 73',
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "SWT_PARAM_ADD_JUNIT_TESTv1(index: 1)",
            "test_duration": "",
            "test_date": "",
            "test_status": "FAILED",
            "test_verifies": [],
            "automates_id": ["ID_5"],
            "test_tags": ["parameterized", "python"],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": "(4, 5, '2 + 2 != 5')",
            "test_skip_reason": None,
        },
        {
            "test_execution": [],
            "test_type": "python",
            "test_details": [],
            "precondition": [],
            "test_name": "global_teardown",
            "test_duration": "",
            "test_date": "",
            "test_status": "PASSED",
            "test_verifies": [],
            "automates_id": [],
            "test_tags": [],
            "canoe_test_case_details": [],
            "meta_data_files": [],
            "test_warnings": [],
            "test_failure": None,
            "test_skip_reason": None,
        },
    ],
}

# reference text format expecting the words in report
TEST_CASE_PASS_TXT_TEMPLATE = "Hello there!" "\nExecuted in" "\n[PASSED]" "\nend " + REPORT_TEST_CASE_NAME_PASS
TEST_CASE_FAIL_TXT_TEMPLATE = (
    "Testcase failed with Failure(s):  [FATAL ERROR]" "\nExecuted in" "\n[FAILED]" "\nend " + REPORT_TEST_CASE_NAME_FAIL
)
SETUP_TXT_TEMPLATE = "Executed in\n[PASSED]\nend global_setup"
TEAR_DOWN_TXT_TEMPLATE = "Executed in\n[PASSED]\nend global_teardown"
SUMMARY_TXT_TEMPLATE = (
    "\nTEST REPORT LOG"
    "\n[Total Tests]        : 9"
    "\n[Running Tests]      : 9"
    "\n[Passed Tests]       : 3"
    "\n[Failed Tests]       : 6"
    "\n[Passed Tests]       :"
    "\nglobal_setup"
    "\n" + REPORT_TEST_CASE_NAME_PASS + "\nglobal_teardown"
    "\n[Failing Tests] :"
    "\n"
    + REPORT_TEST_CASE_NAME_FAIL
    + "\n SWT_PTF_ASSERTS_FAIL_FOR_JUNIT_FAILUREv1"
    + "\n SWT_PTF_EXPECTS_FAIL_FOR_JUNIT_ERRORv1"
    + "\n SWT_GENERAL_FAIL_FOR_JUNIT_ERRORv1"
    + "\n SWT_PARAM_ADD_JUNIT_TESTv1(index: 0)"
    + "\n SWT_PARAM_ADD_JUNIT_TESTv1(index: 1)"
    + "\n[TestEnvironment] : "
    + global_vars.TEST_ENVIRONMENT
)
# disable consider-using-f-string due to testing purpose
# pylint: disable=C0209
XML_SCHEMA = (
    """
<xs:schema attributeFormDefault="unqualified" elementFormDefault="qualified"
xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="testsuite">
    <xs:complexType>
      <xs:sequence>
        <xs:element name="testcase" maxOccurs="9" minOccurs="0">
          <xs:complexType>
            <xs:sequence>
              <xs:element name="error" maxOccurs="2" minOccurs="0">
                <xs:complexType>
                  <xs:simpleContent>
                    <xs:extension base="xs:string">
                      <xs:attribute type="xs:string" name="message"/>
                    </xs:extension>
                  </xs:simpleContent>
                </xs:complexType>
              </xs:element>
              <xs:element name="failure" maxOccurs="4" minOccurs="0">
                <xs:complexType>
                  <xs:simpleContent>
                    <xs:extension base="xs:string">
                      <xs:attribute type="xs:string" name="message"/>
                    </xs:extension>
                  </xs:simpleContent>
                </xs:complexType>
              </xs:element>
              <xs:element type="xs:string" name="system-out"/>
            </xs:sequence>
            <xs:attribute type="xs:string" name="classname" fixed="Tests"/>
            <xs:attribute name="name" use="required">
              <xs:simpleType>
                <xs:restriction base="xs:string">
                  <xs:enumeration value="global_setup" />
                  <xs:enumeration value="SWT_SAMPLE_REPORT_GEN_TEST_PASSv1__each"/>
                  <xs:enumeration value="SWT_SAMPLE_REPORT_GEN_TEST_FAILv1__each"/>
                  <xs:enumeration value="SWT_PTF_ASSERTS_FAIL_FOR_JUNIT_FAILUREv1"/>
                  <xs:enumeration value="SWT_PTF_EXPECTS_FAIL_FOR_JUNIT_ERRORv1"/>
                  <xs:enumeration value="SWT_GENERAL_FAIL_FOR_JUNIT_ERRORv1"/>
                  <xs:enumeration value="SWT_PARAM_ADD_JUNIT_TESTv1(index: 0)"/>
                  <xs:enumeration value="SWT_PARAM_ADD_JUNIT_TESTv1(index: 1)"/>
                  <xs:enumeration value="global_teardown" />
                </xs:restriction>
              </xs:simpleType>
            </xs:attribute>
            <xs:attribute type="xs:float" name="time"/>
          </xs:complexType>
        </xs:element>
      </xs:sequence>
      <xs:attribute type="xs:byte" name="failures" fixed="6"/>
      <xs:attribute type="xs:string" name="machine" fixed="{}"/>
      <xs:attribute type="xs:string" name="name" fixed="{}"/>
      <xs:attribute type="xs:byte" name="skipped" fixed="0"/>
      <xs:attribute type="xs:byte" name="tests" fixed="3"/>
      <xs:attribute type="xs:float" name="time"/>
      <xs:attribute type="xs:string" name="user" fixed="{}"/>
    </xs:complexType>
  </xs:element>
</xs:schema>
"""
).format(socket.gethostname(), global_vars.TEST_ENVIRONMENT, _get_user())
XSD_FILE_OBJECT = io.StringIO(XML_SCHEMA)
EXEC_RECORD_STRING = "{run_exec_record}"
HELP_PRINT = f"""usage: main.py [-h] [-c cfg_file] [-r run_mode] [--uim uim] [-l base_loc]
               [-n no_of_loops] [-e ext_loc [ext_loc ...]] [--random]
               [--dark-mode] [--setup-file setup_file] [--check-pip-mods]
               [--report-dir report_dir]
               [--filter filter_type [filter_values ...]]
               [--rest-port rest_port] [--timestamp time_stamp]
               [--reverse_selection]
               {EXEC_RECORD_STRING} ...\n\n{main.DESC_STRING}\n
positional arguments:
  {EXEC_RECORD_STRING}     Run test cases with given verdict from a previous test execution run

optional arguments:
  -h, --help            show this help message and exit
  -c cfg_file           Enter path of configuration (.ini) file
  -r run_mode           Enter Run Mode (manual or auto or auto_gui). Default is manual
  --uim uim             ConTest Utility Install Manager (UIM)
  -l base_loc           Enter base location if it's different from location in config file
  -n no_of_loops        Enter integer value to run the test cases multiple times
  -e ext_loc [ext_loc ...]
                        Enter locations which need to be added in sys.path for importing python modules
  --random              If this flag is given, the tests will be executed in random order
  --dark-mode           Start the gui in dark mode
  --setup-file setup_file
                        If a file is given, this setup file will be used instead of the default setup.pytest
  --check-pip-mods      Argument to check if all pip modules required to run framework are installed
  --report-dir report_dir
                        Location where reports will be generated.
  --filter filter_type [filter_values ...]
                        Filter test execution. A filter is a pair of 'filter_type', 'filter_values'.
                        See documentation for available filter types and values.
                        If multiple filter are provided, or the same filter is provided multiple
                        times, all filters must match for a testcase to be executed
  --rest-port rest_port
                        Start Contest with rest client. A Rest Client is provided with port number.
                        The port must be used equal to rest server port, which is running
                        independently on same machine.
  --timestamp time_stamp
                        Timestamp (on or off) for logging. Default is 'on'
  --reverse_selection   If this flag is given, unselected tests will be executed.
                        User selected tests will be excluded from test run
"""
CFG_SUCCESS = "Data read from configuration file"
BASE_LOC_SUCCESS = "Custom base location: " + os.path.join(SCRIPT_DIR, "sample_test")
AUTO_RUN_SUCCESS = [
    "Hello there!",
    "Finished Tests Execution",
    f"Exiting {global_vars.FW_NAME} {platform.system()} Platform",
]
NO_OF_LOOPS_SUCCESS = ["SWT_SAMPLE_REPORT_GEN_TEST_PASSv1__each", "SWT_SAMPLE_REPORT_GEN_TEST_FAILv1__each"]

CFG_ERROR = [
    "main.py: error: argument -c: expected one argument",
    "RuntimeError Occurred:\nWrong -c option detected: \n"
    "Location (path_to_error) doesn't exist. Please check if config (.ini) file exists",
]
RUN_ERROR = [
    "main.py: error: argument -r: expected one argument",
    "RuntimeError Occurred:\nWrong -r option detected: \n"
    "Please mention run mode name from this list ['auto', 'manual', 'auto_gui']",
]
NO_OF_LOOPS_ERROR = [
    "main.py: error: argument -n: expected one argument",
    "main.py: error: argument -n: invalid int value: 'abc'",
]
BASE_LOC_ERROR = [
    "main.py: error: argument -l: expected one argument",
    "RuntimeError Occurred:\nWrong -l option detected: \n"
    "Location (path_to_error) doesn't exist. Please enter correct base location",
]
SETUP_FILE_SUCCESS = ["Hello setup!", "Good Bye setup!"]
SETUP_FILE_ERROR = [
    "main.py: error: argument --setup-file: expected one argument",
    "Given setup script '" + SCRIPT_DIR + ".pytest' not found, fallback to default " "setup.pytest script",
]
FILTER_ERROR = ["main.py: error: argument --filter: expected at least one argument"]
WRONG_FILTER = ["RuntimeError Occurred:\nNo tests filtered for given tag list"]
