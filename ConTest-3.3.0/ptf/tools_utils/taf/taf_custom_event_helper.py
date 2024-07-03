"""
    Copyright 2024 Continental Corporation

    :file: taf_custom_event_helper.py
    :platform: Windows
    :synopsis:
        File provides utility functions for handling custom events in the TAF

    :author:
        - Calin-Radu Maghiari (uif26903)
"""

import logging
import os
import re
from datetime import datetime, timezone
from enum import Enum
from contest_verify.verify import contest_asserts

LOGGER = logging.getLogger(__name__)


class CustomEvent:
    """
    CustomEvent class provides methods for handling custom events.
    """

    class TestType(Enum):
        """
        Available test types
        """

        NOTEST = 0
        TRACE32 = 1
        CANOE = 2
        FLASHING_T32 = 3
        FLASHING_XCP = 4
        FLASHING_FLASHTOOL = 5
        FLASHING_PCAT = 6
        FLASHING_SCP = 7

    def __init__(self):
        self.test_type = self.TestType.NOTEST

    def set_test_type(self, test_type):
        """
        Set the test type for the custom event.
        """
        self.test_type = test_type

    def log_event(self, is_start, event_id, subname, name="bat", message=""):
        """
        Logs a custom event.
        """
        if subname in ["TSFlash", "TSXmlParser"]:
            # we use utc in case we want to print out date - timestamps is always utc anyway
            dt = datetime.now(tz=timezone.utc)
            # timestamp in ms
            timestamp = round(dt.timestamp() * 1e3)
            time = str(timestamp)
            if is_start:
                template = f"customevent.duration.v2|{time}|start|{event_id}|{name}|{subname}|{message}|"
            else:
                template = f"customevent.duration.v2|{time}|end|{event_id}|"
            LOGGER.info(template)
        else:
            if is_start:
                template = f"customevent.duration.v1|start|{event_id}|{name}|{subname}|{message}|"
            else:
                template = f"customevent.duration.v1|end|{event_id}|"
            LOGGER.info(template)

    def log_custom_event(self, is_start, variant, event_id_prefix, subname, name="bat", message=""):
        """
        Logs a custom event for starting/ending an operation identified by subname.
        """
        if not os.environ.get("JENKINS_URL"):
            return
        try:
            event_id = re.sub(r"taf_\d{1,3}", event_id_prefix, os.environ["CUSTOM_EVENT_ID_SETUP"])
            type_of_run = os.environ["CUSTOM_EVENT_TYPE_OF_RUN"]
            tas_name = os.environ["NODE_NAME"]
            if not variant:
                variant = os.environ["CUSTOM_EVENT_VARIANT"]
        except Exception as exc:  # pylint: disable=broad-except
            print(f"Error occurred: {exc}")
            print("Custom Event not implemented (missing environment variables: CUSTOM_EVENT_*)?")
            contest_asserts.fail(exc)
        retry_count = event_id[-1]
        start_message = f"variant: {variant}, retry: {retry_count}, type_of_run: {type_of_run}, TAS: {tas_name}"
        if message:
            full_message = f"{start_message}, {message}"
        else:
            full_message = f"{start_message}"
        if is_start:
            self.log_event(is_start=is_start, event_id=event_id, subname=subname, name=name, message=full_message)
        else:
            self.log_event(is_start=is_start, event_id=event_id, subname=subname, name=name)

    def custom_events_start_flash(self, variant, flashtool):
        """
        Logs a custom event for starting flash operation.
        """
        self.log_custom_event(True, variant, "taf_200", "TSFlash", "bat", f"flashing tool: {flashtool}")

    def custom_events_end_flash(self, variant=""):
        """
        Logs a custom event for ending flash operation.
        """
        self.log_custom_event(False, variant, "taf_100", "TSSetup")
        self.log_custom_event(False, variant, "taf_200", "TSFlash")
        self.log_custom_event(True, variant, "taf_300", "TSExec")

    def start_xmlparser_custom_event(self, variant):
        """
        Logs a custom event for starting XML parsing operation.
        """
        self.log_custom_event(True, variant, "taf_350", "TSXmlParser")

    def stop_xmlparser_custom_event(self, variant):
        """
        Logs a custom event for ending XML parsing operation.
        """
        self.log_custom_event(False, variant, "taf_350", "TSXmlParser")
