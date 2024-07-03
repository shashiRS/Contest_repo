"""
    This file contains information of Contest like config, report path, status, test case data
    information
    Copyright 2022 Continental Corporation

    :file: client_informer.py
    :platform: Windows, Linux
    :author:
        - M. Vanama Ravi Kumar <ravi.kumar.vanama@continental-corporation.com>
"""


class ContestFwStatus:
    """
    class for getting contest status
    """

    def __init__(self):
        self._status = "idle"
        self._version = "idle"
        self._test_name = None
        self._config_info = None
        self._loaded_config_path = None
        self._json_test_report = None
        self._txt_test_report = None
        self._html_test_report = None
        self._xml_test_report = None
        self._report_location = None
        self._setup_file_info = None
        self.allowed_contest_status = ["running", "idle"]

    def reset_variables(self):
        """
        Method triggers to reset the variables to default values
        """
        self._status = "idle"
        self._version = "idle"
        self._test_name = None
        self._config_info = None
        self._loaded_config_path = None
        self._json_test_report = None
        self._txt_test_report = None
        self._html_test_report = None
        self._xml_test_report = None
        self._report_location = None
        self._setup_file_info = None

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, status):
        if status not in self.allowed_contest_status:
            raise f"ConTest Framework Status is not in available" \
                  f" list of allowed status: {self.allowed_contest_status}."
        self._status = status

    @property
    def test_name(self):
        return self._test_name

    @test_name.setter
    def test_name(self, test_name):
        if self._status == "running":
            self._test_name = test_name
        else:
            self._test_name = None

    @property
    def loaded_config_path(self):
        return self._loaded_config_path

    @loaded_config_path.setter
    def loaded_config_path(self, loaded_config_path):
        self._loaded_config_path = loaded_config_path

    @property
    def setup_file_info(self):
        return self._setup_file_info

    @setup_file_info.setter
    def setup_file_info(self, setup_file_info):
        self._setup_file_info = setup_file_info

    @property
    def config_info(self):
        return self._config_info

    @config_info.setter
    def config_info(self, config_info):
        self._config_info = config_info

    @property
    def txt_test_report(self):
        return self._txt_test_report

    @txt_test_report.setter
    def txt_test_report(self, txt_test_report):
        self._txt_test_report = txt_test_report

    @property
    def html_test_report(self):
        return self._html_test_report

    @html_test_report.setter
    def html_test_report(self, html_test_report):
        self._html_test_report = html_test_report

    @property
    def xml_test_report(self):
        return self._xml_test_report

    @xml_test_report.setter
    def xml_test_report(self, xml_test_report):
        self._xml_test_report = xml_test_report

    @property
    def json_test_report(self):
        return self._json_test_report

    @json_test_report.setter
    def json_test_report(self, json_test_report):
        self._json_test_report = json_test_report

    @property
    def report_location(self):
        return self._report_location

    @report_location.setter
    def report_location(self, report_location):
        self._report_location = report_location


REST_CLIENT_INFORMER = ContestFwStatus()
