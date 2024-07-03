"""
    Client used to communicate with Server which runs independently
    Copyright 2022 Continental Corporation

    :file: contest_client.py
    :platform: Windows, Linux
    :synopsis:
        This file contains code for controlling received requests from server and reply back with
        proper information
        Client(Contest) <-> Server communication is on tornado.web.WebsocketHandler
        # The below are the reference links useful for understanding the communication between
        # User <-> Server <-> Client(Contest)
        # https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/server.py
        # https://github.com/ilkerkesen/tornado-websocket-client-example/blob/master/client.py
        # https://www.tornadoweb.org/en/stable/web.html
        # https://stackoverflow.com/questions/40263284/why-asyncios-run-in-executor-blocks-tornados-get-handler
        # https://www.tornadoweb.org/en/latest/faq.html#why-isn-t-this-example-with-time-sleep-running-in-parallel
        # https://github.com/tornadoweb/tornado/issues/2308

    :author:
        - M. Vanama Ravi Kumar <ravi.kumar.vanama@continental-corporation.com>
"""
import tornado
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen
from tornado.websocket import websocket_connect
import json
import asyncio
import logging
from global_vars import CONTEST_VERSION
from rest_service import client_informer
from ptf.ptf_utils.global_params import get_testcase_data

# polling every 5 secs if client is connected or not.
TIMEOUT = 5000
LOG = logging.getLogger("REST Client")


class Client(object):
    """
    Class for Client which communicates with Server based on the requests from server.
    """

    def __init__(self, url, timeout):
        self.url = url
        self.timeout = timeout
        self.ws = None
        self.log_flag = True

    def start_client(self):
        """
        Method triggers in a thread which runs and communicates with Server based on the requests
        """
        # starting the client
        LOG.info("Starting ConTest REST Service Client")
        # import asyncio is eventloop which is to be handle in a Thread when handling other
        # Blocking application
        # in our case ConTest is single GUI thread based application, to avoid that currently used
        # asyncio module
        asyncio.set_event_loop(asyncio.new_event_loop())
        self.connect()
        PeriodicCallback(self.keep_alive, TIMEOUT).start()
        tornado.ioloop.IOLoop.instance().start()

    @staticmethod
    def stop_client():
        """
        Method triggers when the client(Contest) application exits
        """
        # import asyncio is eventloop which is to be handle in a Thread when handling other
        # Blocking application
        # in our case ConTest is single GUI thread based application, to avoid that currently used
        # asyncio module
        LOG.info("ConTest REST Service Client Stopped")
        tornado.ioloop.IOLoop.instance().stop()

    # this gen.coroutine is used to yield the websocket connections
    @gen.coroutine
    def connect(self):
        """
        Method triggers when the Client(Contest Start's) and try to establish a connection with
        server if server is running already.
        """
        if self.log_flag:
            LOG.info("Trying To Connect with ConTest REST Server")
        try:
            self.ws = yield websocket_connect(self.url)
        except Exception as error:
            if self.log_flag:
                LOG.error("ConnectionRefusedError: {}\nPlease check Contest REST Server started"
                          "".format(error))
                self.log_flag = False
        else:
            LOG.info("Connected To ConTest REST Server")
            self.run()

    @gen.coroutine
    def run(self):
        """
        Method triggers when the Client(Contest Start's) and establish a connection with
        server, then it enters in run loop and stays there and checks for incoming messages from
        server. When Message received then proper reply is returned back to server
        """
        while True:
            # reading the messages which sent by server
            msg = yield self.ws.read_message()
            LOG.info(f"Message from server {msg}")
            if msg is None:
                self.log_flag = True
                LOG.info("Connection Closed")
                self.ws = None
                break
            else:
                req_info = msg.split("/")
                requested_items = self.update_test_status_dict()
                list_requested_items = requested_items.keys()
                if req_info[0] in list_requested_items:
                    out_msg = requested_items[req_info[0]]
                    # writing back to server with proper information to server
                    self.ws.write_message(json.dumps({msg: out_msg}))
                elif req_info[0].startswith("SWT_"):
                    out_msg = get_testcase_data(req_info[0])
                    # writing back to server with proper information to server
                    self.ws.write_message(json.dumps({msg: {req_info[0]: out_msg}}))

    def keep_alive(self):
        """
        Method triggers based on polling to check the Contest Client connection is alive.
        """
        # if websocket is none trying to connect to server
        if self.ws is None:
            self.connect()
        else:
            self.ws.write_message("ConTest REST Client Running ...")

    @staticmethod
    def update_test_status_dict():
        """
        Methods triggers for the requested message from server to client and returns with updated
        data
        """
        get_requested_information = {"loaded_config": {
            "loaded_config": client_informer.REST_CLIENT_INFORMER.loaded_config_path},
            "status": {"status": client_informer.REST_CLIENT_INFORMER.status,
                       "running_test_name": client_informer.REST_CLIENT_INFORMER.test_name},
            "report_json": {"report_json": client_informer.REST_CLIENT_INFORMER.json_test_report},
            "report_xml": {"report_xml": client_informer.REST_CLIENT_INFORMER.xml_test_report},
            "report_txt": {
                "report_txt": client_informer.REST_CLIENT_INFORMER.txt_test_report},
            "report_html": {
                "report_html": client_informer.REST_CLIENT_INFORMER.html_test_report},
            "report_folder": {
                "report_folder": client_informer.REST_CLIENT_INFORMER.report_location},
            "version": {"version": CONTEST_VERSION},
            "setup_file": {"setup_file": client_informer.REST_CLIENT_INFORMER.setup_file_info},
            "config_info": {"config_info": client_informer.REST_CLIENT_INFORMER.config_info}}
        return get_requested_information
