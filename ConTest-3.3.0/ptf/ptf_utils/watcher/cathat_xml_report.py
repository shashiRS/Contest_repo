"""
    Module for generating CatHat XML report
    Copyright 2022 Continental Corporation

    This module will generate CatHat XML report for overall test run according to CatHat reporting
    template.

    :platform: Linux, Windows
    :file: cathat_xml_report.py
    :author:
        - Vanama Ravi Kumar <ravi.kumar.vanama@continental-corporation.com>
"""

# standard Python imports
import os
import string
import codecs
import time
from datetime import datetime

# custom imports
from ptf.ptf_utils.test_watcher import TestWatcher
from ptf.ptf_utils.common import _get_user
from data_handling import helper
from global_vars import TEST_ENVIRONMENT, TestVerdicts


class CatHatXmlReporter(TestWatcher):
    """
    Watcher for CatHat XML report generation.
    """

    CATHAT_MAIN_TEMPLATE = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<catHat xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:noNamespaceSchemaLocation="heatSWTestFrameworkLog_v050.xsd">
    <testBases/>
    <testEnvironments>
        <testEnvironmentGroup name="">
        </testEnvironmentGroup>
    </testEnvironments>
    <testData>
    <!-- files -->
    </testData>
    <testObjects>
    <!-- files -->
    </testObjects>
    <testPlans>
    </testPlans>
    <testrun>
        <docInfo>
            <properties>
                <property name="${user_id}" value="${user_id}"/>
            </properties>
            <overview>
                <origin> </origin>
                <title> </title>
                <revisionLabel> </revisionLabel>
                <createdAt> </createdAt>
                <docStatus> </docStatus>
                <organization>"Continental ADC GmbH"</organization>
                <creationResponsible> </creationResponsible>
                <approver> </approver>
                <history> </history>
            </overview>
            <scope> ""
            </scope>
        </docInfo>
        <testsuites name="${test_environment}">
            <testsuite name="${test_environment}" tests="${total_tests}">
                <properties>
                    <property name="Tester" value="${user_id}"/>
                    <property name="InformOnMail" value="${email_id}"/>
                </properties>
                <references>
                    <testBaseRef> </testBaseRef>
                    <testObjectRef> </testObjectRef>
                    <testPlanRef> </testPlanRef>
                    <testEnvironmentRef> </testEnvironmentRef>
                    <testDataRef> </testDataRef>
                </references>
                <testsuiteResult tests="${total_tests}" failures="${failures}" errors="${errors}"
                            hostname="${user_id}" skipped="${skipped}"  duration="${ts_duration}"
                            timestampStart="${ts_start_time}">
                    <properties>
                        <property name="Tester" value="${user_id}"/>
                        <property name="InformOnMail" value="${email_id}"/>
                    </properties>
                </testsuiteResult>
                ${tcs_information}
                <history>
                <HistoryEntry date=""/>
                </history>
                <glossary>
                <term name=""/>
                </glossary>
            </testsuite>
        </testsuites>
   </testrun>
</catHat>
    """
    TEST_CASE_TEMPLATE = """
                <testcase classname="${class_name}" name="${tc_name}">
                    <testcaseResult verdict="${tc_verdict}" duration="${tc_duration}"
                        timestampStart="${tc_start_time}">
                        <properties>
                            <property name="Tester" value="${user_id}"/>
                            <property name="InformOnMail" value="${email_id}"/>
                        </properties>
                    </testcaseResult>
                    <attributes>
                        <isRegression>no</isRegression>
                        <isDestructive>no</isDestructive>
                        <priority>0</priority>
                        <estimatedExecutionTime>0</estimatedExecutionTime>
                    </attributes>
                    ${tc_verified_ids}
                    <description>"${tc_details}"</description>
                    <testSteps name="${tc_name}">
                        <step id="">
                            <description>"${tc_steps}"</description>
                            <expectedResults>"${tc_expected_results}"</expectedResults>
                            <observedResults verdict="${tc_verdict}"
                             timestampStart="${tc_start_time}" timestampEnd="${tc_end_time}">
                                    <system-out>"${tc_observed_results}"
                                    </system-out>
                            </observedResults>
                        </step>
                        <properties>
                            <property name="heppy-cli::etmReadOnly::DatabaseId"
                            value="${tc_automates}"/>
                        </properties>
                    </testSteps>
                </testcase>"""

    def __init__(self, paths):
        """
        Initializes the CatHat xml reporter

        :param dictionary paths: Dictionary containing all paths
        """
        # extracting txt and base report locations from paths dictionary
        txt_report_path = paths["paths"][helper.TXT_REPORT]
        base_report_dir = paths["paths"][helper.BASE_REPORT_DIR]
        # create a list with initial value as txt report file
        self.report_file = [os.path.join(txt_report_path, "CATHAT_TEST_RESULT.xml")]
        external_report_dir = paths["paths"][helper.EXTERNAL_REPORT]
        # if report directory was given via cli then add it to above list
        if external_report_dir:
            # prepare path for cli report directory and append to report file list
            external_report_dir = txt_report_path.replace(base_report_dir, external_report_dir)
            self.report_file.append(os.path.join(external_report_dir, "CATHAT_TEST_RESULT.xml"))
        # dictionary for storing data
        self.__xml_data = {
            "start_time": None,
            "start_date_time": None,
            "failed_tests": 0,
            "passed_tests": 0,
            "ignored_tests": 0,
        }
        # for storing prints during a test case execution
        self.__system_output = ""
        # for storing all the test cases information of CatHat XML format.
        self.__test_cases_cathat_xml = ""

    def write(self, *args, **kwargs):
        """
        Overwrite method for capturing prints during test case execution

        :param tuple args: Tuple containing print information
        :param dictionary kwargs: Keyword args dictionary
        """
        # updating system output variable with prints
        self.__system_output = self.__system_output + args[0]

    # pylint: disable=too-many-branches, too-many-locals
    def __update_test_element_data(self, test_case, failure=False, skipped=False):
        """
        Method for updating test case elements with data in ''TEST_CASE_TEMPLATE''

        :param TestCaseInfo test_case: The test_case whose element need to be created
        :param bool failure: True if test passed else False
        :param bool skipped: True if test is ignored or skipped else False
        """
        steps = ""
        expected_results = ""
        # if test is not skipped or ignored then add respective attributes
        if not skipped:
            # get test steps and expected results
            steps, expected_results = self.get_test_steps_and_expected_results(test_case)
            # in-case test case failed then add failure element as child to test_element
            if failure:
                test_verdict = "failed"
            else:
                test_verdict = "passed"
        # else if test is skipped then add test name attribute and skipped element
        else:
            test_verdict = "skipped"
        cathat_xml_tc_data = string.Template(CatHatXmlReporter.TEST_CASE_TEMPLATE)

        # test case verified ids used to add in the CatHat XML report
        tc_verifyids = []
        cnt = 0
        if test_case.verified_ids:
            for ids in test_case.verified_ids:
                # tabs added for the alignment of multiple verified ids on CatHat XML report opened in pycharm or
                # notepad++
                # pylint: disable=C0209
                if cnt == 0:
                    tc_verifyids.append("<traceability id = '" "{}" "' />".format(str(ids)))
                else:
                    tc_verifyids.append("\t\t\t\t\t<traceability id = '" "{}" "' />".format(str(ids)))
                cnt += 1
        # test case automate ids used to add in the CatHat XML report
        if test_case.automates:
            if len(test_case.automates) > 1:
                tc_automate_msg = "Multiple automates ids encountered"
            else:
                tc_automate_msg = test_case.automates[0]
        else:
            tc_automate_msg = ""

        if not skipped:
            # Test case data is filled and created the test case CatHat XMl output as string
            cathat_xml_tc_output = cathat_xml_tc_data.substitute(
                class_name=TEST_ENVIRONMENT,
                tc_name=test_case.name,
                tc_verdict=test_verdict,
                tc_duration=str(test_case.run_time),
                tc_start_time=str(test_case.start_date_time),
                user_id=_get_user(),
                email_id=_get_user() + "@continental.com",
                tc_verified_ids="\n".join(tc_verifyids),
                tc_automates=tc_automate_msg,
                tc_details="".join(test_case.details),
                tc_end_time=str(test_case.stop_date_time),
                tc_expected_results="".join(expected_results),
                tc_observed_results=self.__system_output,
                tc_steps="".join(steps),
            )
        else:
            date_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
            cathat_xml_tc_output = cathat_xml_tc_data.substitute(
                class_name=TEST_ENVIRONMENT,
                tc_name=test_case,
                tc_verdict=test_verdict,
                tc_duration="0.000000000",
                tc_start_time=str(date_time),
                user_id=_get_user(),
                email_id=_get_user() + "@continental.com",
                tc_verified_ids="\n".join(tc_verifyids),
                tc_automates=tc_automate_msg,
                tc_details="",
                tc_end_time=str(date_time),
                tc_expected_results="",
                tc_observed_results=self.__system_output,
                tc_steps="".join(steps),
            )
        self.__test_cases_cathat_xml += cathat_xml_tc_output
        # if test is not skipped and if canoe test module contains test cases then add it
        # in-case of skipped = True the test_case will be the name of skipped test
        # pylint: disable=too-many-nested-blocks
        if not skipped:
            if test_case.canoe_tm_tc_verdicts:
                for test_module in test_case.canoe_tm_tc_verdicts:
                    if test_case.name in test_module:
                        test_cases_list = test_module[test_case.name]
                        # adding the test module of test cases into test cases list of CAtHat XML
                        for test_data in test_cases_list:
                            date_time = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")
                            duration = "0.000000000"
                            if test_data["test_case_duration"]:
                                duration = test_data["test_case_duration"]
                            cathat_xml_tc_output = cathat_xml_tc_data.substitute(
                                class_name=TEST_ENVIRONMENT,
                                tc_name=test_data["test_case_name"],
                                tc_verdict=test_data["test_status"].lower(),
                                tc_duration=duration,
                                tc_start_time=str(date_time),
                                user_id=_get_user(),
                                email_id=_get_user() + "@continental.com",
                                tc_verified_ids="",
                                tc_automates="",
                                tc_details="",
                                tc_end_time=str(date_time),
                                tc_expected_results="",
                                tc_observed_results="",
                                tc_steps="",
                            )
                            self.__test_cases_cathat_xml += cathat_xml_tc_output

    @staticmethod
    def get_test_steps_and_expected_results(test_case):
        """
        Method to get the test steps and expected results from the test_case info

        :param TestCaseInfo test_case: The test_case whose execution is finished
        """
        # Reformat the test steps
        steps = []
        expected_results = []
        for step in test_case.steps:
            if step.startswith(" Test Step"):
                steps.append(step)
            elif step.startswith(" Expected"):
                expected_results.append(step)
        return steps, expected_results

    def test_finished(self, testcase):
        """
        Method for creating a 'testcase' element (Pass/Fail) and appending it to main test suite

        :param TestCaseInfo testcase: The testcase whose execution is finished
        """

        if testcase.name not in ["global_setup", "global_teardown"]:
            # Ignore parameterized tests, instead only store the report for each parameter
            if testcase.test_function.__name__ == "parameterized_runner":
                return
            # disable report generation of a test case which is parameterized and its been modified by user (value
            # changed or new set added)
            if not testcase.user_modified_param_test:
                if testcase.verdict == TestVerdicts.PASS:
                    # incrementing the pass tests counter
                    self.__xml_data["passed_tests"] = self.__xml_data["passed_tests"] + 1
                    self.__update_test_element_data(testcase)
                else:
                    # incrementing the fail tests counter if test is not passing i.e. failed or inconclusive
                    # please note that inconclusive verdict of a test case (only warning occurred in test) is treated as
                    # failure in cathat xml report generated here as cathat xml does not have separate section for
                    # inconclusive reporting and it was agreed with CatHat tool owner
                    self.__xml_data["failed_tests"] = self.__xml_data["failed_tests"] + 1
                    self.__update_test_element_data(testcase, failure=True)
        # clearing system output variable after each test run finished
        self.__system_output = ""

    def test_run_started(self, _):
        """
        Triggered if test run is started.
        """
        self.__xml_data["start_time"] = time.time()
        self.__xml_data["start_date_time"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S")

    def test_run_finished(self, _):
        """
        Method for adding final information for creating CatHat XML report
        """
        total_run_time = str((time.time() - self.__xml_data["start_time"]))
        total_tests = (
            self.__xml_data["passed_tests"] + self.__xml_data["failed_tests"] + self.__xml_data["ignored_tests"]
        )
        # CatHat XML is filling the with test suite, test case data etc..
        cathat_final_xml = string.Template(CatHatXmlReporter.CATHAT_MAIN_TEMPLATE)
        cathat_final_xml_out = cathat_final_xml.substitute(
            user_id=_get_user(),
            test_environment=TEST_ENVIRONMENT,
            email_id=_get_user() + "@continental.com",
            total_tests=str(total_tests),
            failures=str(self.__xml_data["failed_tests"]),
            errors="0",
            skipped=str(self.__xml_data["ignored_tests"]),
            tests=str(self.__xml_data["passed_tests"]),
            ts_duration=total_run_time,
            ts_start_time=str(self.__xml_data["start_date_time"]),
            tcs_information=self.__test_cases_cathat_xml,
        )

        self.__test_cases_cathat_xml = ""
        # writing the CatHat XML file as output.
        for report in self.report_file:
            with codecs.open(report, "w", "utf-8") as cathat_xml_file:
                cathat_xml_file.write(cathat_final_xml_out)
