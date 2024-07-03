"""
    Reports to html output.
    Copyright 2019 Continental Corporation

    This module contains a watcher to write the test status to html.

    :file: html_report.py
    :author:
        - Felix Wohlfrom <felix.2.wohlfrom@continental-corporation.com>
"""
# disabling too-many-lines as they are required
# disabling import-error as the missing modules will be installed separately
# pylint: disable=C0302, import-error

# standard Python imports
import os
import string
import time
import socket
from shutil import copyfile
from datetime import datetime
import pandas
import jinja2
import global_vars

# custom imports
from ptf.ptf_utils.test_watcher import TestWatcher
from ptf.ptf_utils.common import _get_user
from ptf.ptf_utils.global_params import get_reporting_parameter, _get_files_for_report
from ptf.ptf_utils import common
from data_handling import helper
from global_vars import (
    TEST_ENVIRONMENT,
    LOGO,
    LOGO_ICON,
    HTML_COPY_LINK,
    PASS_ICON,
    FAIL_ICON,
    INCONCLUSIVE_ICON,
    TestVerdicts,
    SKIP_ICON,
    HTML_TEMPLATE_PATH,
)


# pylint: disable=too-many-statements
class HtmlReporter(TestWatcher):
    """
    This watcher will create a html report per executed testcase.
    """

    # The template to be used for the html report
    TEMPLATE_LOADER = jinja2.FileSystemLoader(searchpath=HTML_TEMPLATE_PATH)
    TEMPLATE_ENV = jinja2.Environment(loader=TEMPLATE_LOADER)

    # The template to be used for the summary report
    TEMPLATE_FILE = "summary_template.html"
    SUMMARY_TEMPLATE = TEMPLATE_ENV.get_template(TEMPLATE_FILE)
    # store's all individual report data to be present in test report
    test_report_obj = []
    # store all testcase name for report sidebar display
    all_testcase_name = []

    TEMPLATE = """
<!DOCTYPE html>
<html lang="en-us">
<head>
    <link rel="icon" href=${icon}>
    <style>
        .header {
          text-align: center;
          display: inline-block;
          width: 100%;
        }
        .header img {
          width: 160px;
          height: 80px;
          align: middle;
          float: left;
          padding-left: 5em;
        }
        .reqs_body {
            float: right;
            margin: 10px;
            padding: 10px;
            min-width: 18%;
            max-width: auto;
            background-color: #f1f1c1;
            margin-right: 2.5cm;
            height: auto;
            border: 1px solid #dddddd;
        }
        .detail_body {
            float: left;
            margin: 10px;
            padding: 10px;
            width: 60%;
            margin-left: 2.5cm;
            height: auto;
            background-color: #f1f1c1;
            border: 1px solid #dddddd;
        }
        .disclaimer_style {
            float: left;
            margin: 10px;
            padding: 10px;
            width: 60%;
            margin-left: 2.5cm;
            height: auto;
        }
        h2 {
            font-weight: bold;
            margin-left: 10px;
        }
        h4 {
            font-weight: normal;
            margin-left: 30px;
        }
        #custom_style {
            font-family: georgia;
            font-size: 15px;
            margin-left: 40px;
        }
        table {
            font-family: arial, sans-serif;
            border-collapse: collapse;
            width: 90%;
            margin-left: auto;
            margin-right: auto;
            background-color: #f1f1c1;
        }
        td, th {
            border: 1px solid #dddddd;
            text-align: left;
            padding: 8px;
        }
        tr:nth-child(even) {
            background-color: white;
        }
    </style>
</head>
<body>
    <div class="header">
    <img src="${logo}" alt="logo">
    <h1 style="padding-right:7em">Test Report ${test_environment}</h1>
    <p style="padding:2em">Machine: ${machine_name}<br>User: ${user_name}</p>
    <h3>${test_case_name}</h3>
    </div>
    <div class="reqs_body">
        <table>
            <tr>
                <th>Execution Time</th>
            </tr>
            <tr>
                <td>${execution_time}</td>
            </tr>
            <tr>
                <th>Execution Date</th>
            </tr>
            <tr>
                <td>${execution_date}</td>
            </tr>
            <tr>
                <th>Status</th>
            </tr>
            <tr>
                <td bgcolor="${color}">${status}</td>
            </tr>
            <tr>
                <th>Verification IDs</th>
            </tr>
            <tr>
                <td>${verified_ids}</td>
            </tr>
            <tr>
                <th>Automates</th>
            </tr>
            <tr>
                <td>${automates_ids}</td>
            </tr>
            <tr>
                <th>Test Tags</th>
            </tr>
            <tr>
                <td>${tags}</td>
            </tr>
            <tr>
                <th>Debug output</th>
            </tr>
            <tr>
                <td><a href="${txt_report}.txt">Console Output</a></td>
            </tr>
            <tr>
                <th>Metadata Files Links</th>
            </tr>
            <tr>
                <td>${files}</td>
            </tr>
        </table>
    </div>
    <h2 id="test_disclaimer" class="disclaimer_style"></h2>
    <script>
    var view_test_disclaimer = ${show_test_disclaimer};
    if (view_test_disclaimer == 1) {
        show_test_disclaimer();
    }
    function show_test_disclaimer() {
        document.getElementById("test_disclaimer").innerHTML = "DISCLAIMER: This test case contains user-induced \
        deviations from its parameter specification and is therefore invalid.";
    }
    </script>
    <div class="detail_body">
        <h2>Test Details : </h2>
        <p id="custom_style">${details}</p>
        <h2>Precondition : </h2>
        <p id="custom_style">${precondition}</p>
        <h2>Test Case Execution Sequence : </h2>
        ${test_case_execution}
        <h2>Test Case Warning(s) : </h2>
        ${test_case_warnings}
        <h2>Verdict/Status : </h2>
        ${test_case_verdict}
    </div>
</body>
</html>
    """

    def __init__(self, paths):
        """
        Creates a new html reporter

        :param dictionary paths: Dictionary containing all paths
        """
        # extracting txt, html and base report locations from paths dictionary
        txt_report_dir = paths["paths"][helper.TXT_REPORT]
        base_report_dir = paths["paths"][helper.BASE_REPORT_DIR]
        html_report_dir = paths["paths"][helper.HTML_REPORT]
        external_report_dir = paths["paths"][helper.EXTERNAL_REPORT]
        # create a list with initial value as html report directory mentioned in cfg file
        self.html_report_dir = [html_report_dir]
        # if report directory was given via cli then add it to above list
        if external_report_dir:
            # updated the external report path by replacing the BASE_REPORT_DIR with user provided
            # EXTERNAL_REPORT in html report path and assign as updated external report path
            external_report_dir = html_report_dir.replace(base_report_dir, external_report_dir)
            self.html_report_dir.append(external_report_dir)
        self.summary_report_disclaimer_view = False
        self.summary_data = {
            "passed_tests": {
                "test_name": [],
                "log_print": [],
                "exec_time": [],
                "txt_report": [],
                "files": [],
                "html_report": [],
                "req_id": [],
                "automates_id": [],
                "s_a_tag": [],
                "inconclusive_tests": [],
            },
            "inconclusive_tests": {
                "test_name": [],
                "log_print": [],
                "exec_time": [],
                "txt_report": [],
                "files": [],
                "html_report": [],
                "req_id": [],
                "automates_id": [],
                "s_a_tag": [],
                "inconclusive_tests": [],
            },
            "skipped_tests": {
                "test_name": [],
                "log_print": [],
                "exec_time": [],
                "txt_report": [],
                "files": [],
                "html_report": [],
                "req_id": [],
                "automates_id": [],
                "s_a_tag": [],
                "inconclusive_tests": [],
            },
            "failed_tests": {
                "test_name": [],
                "log_print": [],
                "exec_time": [],
                "txt_report": [],
                "files": [],
                "html_report": [],
                "req_id": [],
                "automates_id": [],
                "s_a_tag": [],
                "inconclusive_tests": [],
            },
            "all_tests": {
                "test_name": [],
                "log_print": [],
                "exec_time": [],
                "txt_report": [],
                "files": [],
                "html_report": [],
                "req_id": [],
                "s_a_tag": [],
            },
        }
        self.test_tags = {}
        self.log_txt = (
            "For more detailed report, please go through HTML Report or Text Report"
            "<br>\u24D8 links to the reports are given next to their respective test "
            "case name"
        )
        # create relative paths which will be used later while dumping data to html files
        self.txt_report_dir_rel_path = os.path.relpath(txt_report_dir, self.html_report_dir[0])
        self.html_report_dir_rel_path = os.path.relpath(html_report_dir, self.html_report_dir[0])

        # fetching reporting parameters
        self.reporting_params = get_reporting_parameter()

        # create report directory if not exists
        for directory in self.html_report_dir:
            if not os.path.exists(directory):
                os.makedirs(directory)
            os.makedirs(os.path.join(directory, "metadata_files"))

    # disabling too-many-locals, too-many-branches as they are required
    # pylint: disable=R0914, R0912
    def test_finished(self, testcase):
        """
        Write the html report once the testcase is finished.
        :param TestCaseInfo testcase: The finished testcase.
        """
        # if the parameterized test was modified (set value changed or new set added) update value of flag which
        # will show disclaimer in summary report
        if not self.summary_report_disclaimer_view:
            self.summary_report_disclaimer_view = testcase.user_modified_param_test
        semi_auto_tag_id = "automated"
        # Ignore parameterized tests, instead only store the report for each parameter
        if testcase.test_function.__name__ == "parameterized_runner":
            return
        html_data = string.Template(HtmlReporter.TEMPLATE)
        for i, _ in enumerate(testcase.tags):
            if (testcase.tags[i]).lower() == "semi-automated".lower():
                semi_auto_tag_id = testcase.tags[i]
        # get the test case files and copy to report path while test case html creation
        # and linking the files.
        tc_files = []
        list_of_files = _get_files_for_report()
        for file in list_of_files:
            metadata_rel_file_path, base_file_name = common.get_updated_file_path(file, testcase)
            tc_files.append(f"<a href={metadata_rel_file_path} title='Original Path: {file}'>{base_file_name}</a>")

        if testcase.verdict == TestVerdicts.PASS:
            test_status = "PASSED"
            status_color = "green"
            status_text = "<b>[PASSED]</b>"
            self.summary_data["passed_tests"]["log_print"].append("No Failure(s)<br>" + self.log_txt)
            self.summary_data["all_tests"]["log_print"].append("No Failure(s)<br>" + self.log_txt)
            self.summary_data["passed_tests"]["test_name"].append(testcase.name)
            self.summary_data["passed_tests"]["exec_time"].append(
                "\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms"
            )
            self.summary_data["passed_tests"]["txt_report"].append(
                os.path.join(self.txt_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["passed_tests"]["html_report"].append(
                os.path.join(self.html_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["all_tests"]["files"].append(str.join(os.linesep, tc_files))
            self.summary_data["passed_tests"]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
            self.summary_data["passed_tests"]["s_a_tag"].append(semi_auto_tag_id)
        elif testcase.verdict == TestVerdicts.FAIL:
            test_status = "FAILED"
            status_color = "red"
            status_text = (
                "<b>[FAILED]</b> <br /><br /> --> Failure : "
                + str(testcase.failure_info)
                + "<br />See Console Output ... "
            )
            self.summary_data["failed_tests"]["test_name"].append(testcase.name)
            self.summary_data["failed_tests"]["log_print"].append(
                str(testcase.failure_info) + "<br><br>" + self.log_txt
            )
            self.summary_data["all_tests"]["log_print"].append(str(testcase.failure_info) + "<br><br>" + self.log_txt)
            self.summary_data["failed_tests"]["exec_time"].append(
                "\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms"
            )
            self.summary_data["failed_tests"]["txt_report"].append(
                os.path.join(self.txt_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["failed_tests"]["html_report"].append(
                os.path.join(self.html_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["all_tests"]["files"].append(str.join(os.linesep, tc_files))
            self.summary_data["failed_tests"]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
            self.summary_data["failed_tests"]["s_a_tag"].append(semi_auto_tag_id)
        elif testcase.verdict == TestVerdicts.INCONCLUSIVE:
            test_status = "INCONCLUSIVE"
            status_color = "#b59d04"
            status_text = "<b>[INCONCLUSIVE]</b>"
            self.summary_data["inconclusive_tests"]["inconclusive_tests"].append(testcase.name)
            self.summary_data["inconclusive_tests"]["test_name"].append(testcase.name)
            self.summary_data["inconclusive_tests"]["log_print"].append(
                "Warning(s):" + "<br><br>" + str(testcase.inconclusive_info) + "<br><br>" + self.log_txt
            )
            self.summary_data["all_tests"]["log_print"].append(
                "Warning(s):" + "<br><br>" + str(testcase.inconclusive_info) + "<br><br>" + self.log_txt
            )
            self.summary_data["inconclusive_tests"]["exec_time"].append(
                "\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms"
            )
            self.summary_data["inconclusive_tests"]["txt_report"].append(
                os.path.join(self.txt_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["inconclusive_tests"]["html_report"].append(
                os.path.join(self.html_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["all_tests"]["files"].append(str.join(os.linesep, tc_files))
            self.summary_data["inconclusive_tests"]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
            self.summary_data["inconclusive_tests"]["s_a_tag"].append(semi_auto_tag_id)
        elif testcase.verdict == TestVerdicts.SKIP:
            test_status = "SKIPPED"
            status_color = "grey"
            status_text = "<b>[SKIP]</b> <br /><br />    Skip Reason : " + str(testcase.skip_info)
            self.summary_data["skipped_tests"]["inconclusive_tests"].append(testcase.name)
            self.summary_data["skipped_tests"]["test_name"].append(testcase.name)
            self.summary_data["skipped_tests"]["log_print"].append(
                "Skip Reason:" + "<br><br>" + str(testcase.skip_info) + "<br><br>" + self.log_txt
            )
            self.summary_data["all_tests"]["log_print"].append(
                "Skip Reason:" + "<br><br>" + str(testcase.skip_info) + "<br><br>" + self.log_txt
            )
            self.summary_data["skipped_tests"]["exec_time"].append(
                "\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms"
            )
            self.summary_data["skipped_tests"]["txt_report"].append(
                os.path.join(self.txt_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["skipped_tests"]["html_report"].append(
                os.path.join(self.html_report_dir_rel_path, testcase.name.replace(":", ""))
            )
            self.summary_data["all_tests"]["files"].append(str.join(os.linesep, tc_files))
            self.summary_data["skipped_tests"]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
            self.summary_data["skipped_tests"]["s_a_tag"].append(semi_auto_tag_id)
        # Reformat the test steps
        steps = []
        for step in testcase.steps:
            if step.startswith(" Test Step"):
                step = step.replace(" Test Step", '<p id="custom_style"> <b>Test Step</b>')
                step = step + "</p>"
                steps.append(step)
            elif step.startswith(" Expected"):
                step = step.replace(" Expected", '<p id="custom_style"> <b>Expected</b>')
                step = step + "</font></p>"
                steps.append(step)
            elif step.startswith(" CANoe-Report-"):
                step = step.replace(" CANoe-Report", '<p id="custom_style"> <b>CANoe-Report</b>')
                step = step + "</p>"
                steps.append(step)
            elif step.startswith(" Link-"):
                step = step.replace(" Link", '<p id="custom_style"> <b>Link</b>')
                step = step + "</p>"
                steps.append(step)
            elif step.startswith(" Image-"):
                step = step.split(": ")[1]
                step = step + "</p>"
                steps.append(step)
        inconclusive_infos = []
        for info in testcase.inconclusive_info:
            inconclusive_infos.append(f'<p id="custom_style"> &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {info}</p>')
        test_verdict = f'<p id="custom_style"><font color="{status_color}">{status_text}</font></p>'
        # Remove double point from testcase name to allow storing on windows
        testcase_name = testcase.name.replace(":", "")
        self.summary_data["all_tests"]["test_name"].append(testcase.name)
        self.summary_data["all_tests"]["exec_time"].append("\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms")
        self.summary_data["all_tests"]["txt_report"].append(os.path.join(self.txt_report_dir_rel_path, testcase_name))
        self.summary_data["all_tests"]["html_report"].append(os.path.join(self.html_report_dir_rel_path, testcase_name))
        self.summary_data["all_tests"]["files"].append(str.join(os.linesep, tc_files))
        self.summary_data["all_tests"]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
        self.summary_data["all_tests"]["s_a_tag"].append(semi_auto_tag_id)
        # creating another dictionary with test tags
        if testcase.tags:
            for tag in testcase.tags:
                if tag not in self.test_tags:
                    self.test_tags[tag] = {}
                    self.test_tags[tag]["test_name"] = []
                    self.test_tags[tag]["log_print"] = []
                    self.test_tags[tag]["exec_time"] = []
                    self.test_tags[tag]["txt_report"] = []
                    self.test_tags[tag]["html_report"] = []
                    self.test_tags[tag]["files"] = []
                    self.test_tags[tag]["req_id"] = []
                    self.test_tags[tag]["automates_id"] = []
                    self.test_tags[tag]["s_a_tag"] = []
                self.test_tags[tag]["s_a_tag"].append(semi_auto_tag_id)
                self.test_tags[tag]["test_name"].append(testcase.name)
                self.test_tags[tag]["exec_time"].append("\u2248 " + str(round(testcase.run_time * 1000, 2)) + " ms")
                self.test_tags[tag]["txt_report"].append(os.path.join(self.txt_report_dir_rel_path, testcase_name))
                self.test_tags[tag]["html_report"].append(os.path.join(self.html_report_dir_rel_path, testcase_name))
                self.test_tags[tag]["files"].append(str.join(os.linesep, tc_files))
                self.test_tags[tag]["req_id"].append(str.join(os.linesep, testcase.verified_ids))
                self.test_tags[tag]["automates_id"].append(str.join(os.linesep, testcase.automates))
                if testcase.verdict == TestVerdicts.PASS:
                    self.test_tags[tag]["log_print"].append("No Failure(s)<br>" + self.log_txt)
                elif testcase.verdict == TestVerdicts.SKIP:
                    self.test_tags[tag]["log_print"].append(
                        "Skip Reason:" + "<br><br>" + str(testcase.skip_info) + "<br><br>" + self.log_txt
                    )
                elif testcase.verdict == TestVerdicts.INCONCLUSIVE:
                    self.test_tags[tag]["log_print"].append(
                        "Warning(s):" + "<br><br>" + str(testcase.inconclusive_info) + "<br><br>" + self.log_txt
                    )
                else:
                    self.test_tags[tag]["log_print"].append(str(testcase.failure_info) + "<br><br>" + self.log_txt)

        html_out = html_data.substitute(
            icon=os.path.join(self.html_report_dir_rel_path, "logo_icon.png"),
            logo=os.path.join(self.html_report_dir_rel_path, "logo.png"),
            test_environment=TEST_ENVIRONMENT,
            machine_name=socket.gethostname(),
            user_name=_get_user(),
            show_test_disclaimer="1" if testcase.user_modified_param_test else "0",
            test_case_name=testcase.name,
            execution_time=str(testcase.run_time * 1000) + " msec",
            execution_date=datetime.fromtimestamp(testcase.start_time).strftime("%c"),
            color=status_color,
            status=test_status,
            files=str.join("<br />", tc_files),
            verified_ids=str.join("<br />", testcase.verified_ids),
            automates_ids=str.join("<br />", testcase.automates),
            tags=str.join("<br />", testcase.tags),
            details=str.join("<br />", testcase.details),
            precondition=str.join("<br />", testcase.precondition),
            txt_report=os.path.join(self.txt_report_dir_rel_path, testcase_name),
            test_case_execution=str.join("", steps),
            test_case_warnings=str.join("", inconclusive_infos),
            test_case_verdict=str.join("", test_verdict),
        )

        all_test_case = {
            "test_environment": TEST_ENVIRONMENT,
            "show_test_disclaimer": "1" if testcase.user_modified_param_test else "0",
            "test_case_name": testcase.name,
            "execution_time": round((testcase.run_time * 1000), 2),
            "color": status_color,
            "status": test_status,
            "files": tc_files,
            "verified_ids": testcase.verified_ids,
            "automates_ids": testcase.automates,
            "tags": testcase.tags,
            "details": testcase.details,
            "precondition": testcase.precondition,
            "test_case_execution": testcase.steps,
            "test_case_warnings": inconclusive_infos,
            "test_case_verdict": test_verdict,
        }

        # dumping test case data to html report file(s)
        for directory in self.html_report_dir:
            with open(os.path.join(directory, testcase_name + ".html"), "w", encoding="utf-8") as html_file:
                html_file.write(html_out)
                html_file.close()
        HtmlReporter.all_testcase_name.append(testcase_name)
        HtmlReporter.test_report_obj.append(all_test_case)

    def test_run_finished(self, missing_tests):
        """
        Write summary report of test-cases on complete of test run

        :param list missing_tests: A list of testcases that where configured to be executed, but where not found
            during execution
        """
        # datetime object containing current date and time
        exe_time = datetime.now()
        exe_time_format = exe_time.strftime("%m/%d/%Y, %H:%M:%S")

        # Time zone object
        local_tz = time.localtime()
        timezone_format = local_tz.tm_zone

        # when no reporting parameter given update the default value to the dictionary(or table)
        if not self.reporting_params:
            self.reporting_params["-"] = "no entries found"
        # Data frame for creating table of given reporting parameters
        data_frame = pandas.DataFrame(
            list(self.reporting_params.values()), index=self.reporting_params.keys(), columns=["VALUE"]
        ).fillna("")
        data_frame.columns.name = "PARAMETER"
        # copying image files in html report directories in order to avoid logo files missing
        for directory in self.html_report_dir:
            copyfile(LOGO_ICON, os.path.join(directory, "logo_icon.png"))
            copyfile(LOGO, os.path.join(directory, "logo.png"))
            copyfile(HTML_COPY_LINK, os.path.join(directory, "html_report_copy_link_icon.png"))
            copyfile(PASS_ICON, os.path.join(directory, "pass_icon.png"))
            copyfile(INCONCLUSIVE_ICON, os.path.join(directory, "inconclusive_icon.png"))
            copyfile(SKIP_ICON, os.path.join(directory, "skip_icon.png"))
            copyfile(FAIL_ICON, os.path.join(directory, "fail_icon.png"))

        html_out_summary = {
            "icon": os.path.join(self.html_report_dir_rel_path, "logo_icon.png"),
            "logo": os.path.join(self.html_report_dir_rel_path, "logo.png"),
            "copy": os.path.join(self.html_report_dir_rel_path, "html_report_copy_link_icon.png"),
            "pass_icon_path": os.path.join(self.html_report_dir_rel_path, "pass_icon.png"),
            "inconclusive_icon_path": os.path.join(self.html_report_dir_rel_path, "inconclusive_icon.png"),
            "skip_icon_path": os.path.join(self.html_report_dir_rel_path, "skip_icon.png"),
            "fail_icon_path": os.path.join(self.html_report_dir_rel_path, "fail_icon.png"),
            "test_environment": TEST_ENVIRONMENT,
            "show_disclaimer": "true" if self.summary_report_disclaimer_view else "false",
            "machine_name": socket.gethostname(),
            "user_name": _get_user(),
            "param_table": data_frame.to_html(),
            "passed_tests": self.summary_data["passed_tests"]["test_name"],
            "inconclusive_tests": self.summary_data["inconclusive_tests"]["test_name"],
            "skip_tests": self.summary_data["skipped_tests"]["test_name"],
            "failed_tests": self.summary_data["failed_tests"]["test_name"],
            "test_names": self.summary_data["all_tests"]["test_name"],
            "pass_log": self.summary_data["passed_tests"]["log_print"],
            "fail_log": self.summary_data["failed_tests"]["log_print"],
            "inconclusive_log": self.summary_data["inconclusive_tests"]["log_print"],
            "test_log": self.summary_data["all_tests"]["log_print"],
            "pass_exec_time": self.summary_data["passed_tests"]["exec_time"],
            "fail_exec_time": self.summary_data["failed_tests"]["exec_time"],
            "inconclusive_exec_time": self.summary_data["inconclusive_tests"]["exec_time"],
            "exec_time": self.summary_data["all_tests"]["exec_time"],
            "pass_txt_report": self.summary_data["passed_tests"]["txt_report"],
            "fail_txt_report": self.summary_data["failed_tests"]["txt_report"],
            "inconclusive_txt_report": self.summary_data["inconclusive_tests"]["txt_report"],
            "txt_report": self.summary_data["all_tests"]["txt_report"],
            "files": self.summary_data["all_tests"]["files"],
            "pass_html_report": self.summary_data["passed_tests"]["html_report"],
            "fail_html_report": self.summary_data["failed_tests"]["html_report"],
            "inconclusive_html_report": self.summary_data["inconclusive_tests"]["html_report"],
            "html_report": self.summary_data["all_tests"]["html_report"],
            "pass_req_ids": self.summary_data["passed_tests"]["req_id"],
            "fail_req_ids": self.summary_data["failed_tests"]["req_id"],
            "inconclusive_req_ids": self.summary_data["inconclusive_tests"]["req_id"],
            "req_ids": self.summary_data["all_tests"]["req_id"],
            "tags": self.test_tags,
            "pass_semi_auto_tags": self.summary_data["passed_tests"]["s_a_tag"],
            "fail_semi_auto_tags": self.summary_data["failed_tests"]["s_a_tag"],
            "inconclusive_semi_auto_tags": self.summary_data["inconclusive_tests"]["s_a_tag"],
            "semi_auto_tags": self.summary_data["all_tests"]["s_a_tag"],
            "execution_date_time": exe_time_format,
            "execution_timezone": timezone_format,
            "latest_version": global_vars.LATEST_VERSION,
            "base_python_version": global_vars.BASE_PYTHON_VERSION,
            "python_path": global_vars.PYTHON_PATH,
            "python_bit_arch": global_vars.PYTHON_BIT_ARCH,
            "test_report_obj": HtmlReporter.test_report_obj,
            "all_testcase_name": HtmlReporter.all_testcase_name,
        }

        # clear test data for report
        HtmlReporter.all_testcase_name = []
        HtmlReporter.test_report_obj = []

        for directory in self.html_report_dir:
            rendered_jinja_report = HtmlReporter.SUMMARY_TEMPLATE.render(html_out_summary)
            with open(os.path.join(directory, "TESTS_SUMMARY.html"), mode="w", encoding="utf-8") as summary_report:
                summary_report.write(rendered_jinja_report)
