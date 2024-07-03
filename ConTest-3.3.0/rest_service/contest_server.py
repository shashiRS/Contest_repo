"""
    Server used to communicate with User and Client(Contest)
    Copyright 2022 Continental Corporation

    :file: contest_server.py
    :platform: Windows, Linux
    :synopsis:
        This file contains code for controlling the User requests from webpage and pass to client
        (Contest)
        User<-> Server communication is on tornado.web.RequestHandler
        Server <-> Client(Contest) communication is on tornado.web.WebsocketHandler
        The User requested information is communicated to Client(Contest) via Server which is in
        this file
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
# standard Python modules imports
import logging
import logging.config
import concurrent
import asyncio
import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.options
import json
import socket
import datetime
import sys
import argparse
from http import HTTPStatus

# Initial version of the server is v1
SERVER_VERSION = "v1"

LOG = logging.getLogger("ConTest_REST_Server_{}".format(SERVER_VERSION))
# welcome print
DESC_STRING = "======== " + " CONTEST REST SERVER  " + SERVER_VERSION + " ========"

# used for http status as key
HTTP_STATUS = "http_status"


class ReceivedClientData:
    """
    Class stores the received client data and used by server for sending back to user
    """
    # stores the contest client message for the requested user
    recv_client_msg = dict()
    # Flag used to check before proceeding with  request handler
    client_connected = False
    client_unavailable = "Contest REST Client is not connected. Please start the Contest"


def get_host_name_ip():
    """
    Function returns the current running host ip address
    :rtype: str
    :return: returns the ip address of the current host PC
    """
    try:
        host_name = socket.gethostname()
        host_ip = socket.gethostbyname(host_name)
        LOG.info("Server Hostname :  {}".format(host_name))
        LOG.info("Server Host IP Address :  {}".format(host_ip))
        return host_ip
    except Exception as error:
        LOG.info("Unable to get Hostname and IP Address.\nError: {}".format(error))


def blocking_method(value):
    """
    Method triggers and runs in a different thread from user RequestHandler get method.
    This method is used for delay purpose until server receives the data from client and
    updated in a RECEIVED_CLIENT_DATA.recv_client_msg and returned

    :param str value: contains requested value and time stamp
    """
    while True:
        # Here its in a while loop until message from client is filled in  On_message method
        # in the recv_client_msg as dictionary.
        # Here it checks the message available or not
        if value in ReceivedClientData.recv_client_msg.keys():
            recv_client_msg = ReceivedClientData.recv_client_msg[value]
            time_stamp = value.split("/")
            recv_client_msg["time_stamp"] = time_stamp[1]
            ReceivedClientData.recv_client_msg.pop(value)
            return recv_client_msg


def get_date_and_timestamp():
    """
    Method returns the timestamp with date
    :rtype: datetime
    :return: returns the date and timestamp
    """
    return datetime.datetime.now()


class ServerAPIVersion(tornado.web.RequestHandler):
    """
    Class for Server API Version which is required by user to communicate with Contest Server
    """

    async def get(self):
        """
        Method triggers when user requests with version of the Contest Server
        """
        LOG.info("Requested Server API Version")
        ReceivedClientData.recv_client_msg = {"server_api_version": SERVER_VERSION}
        # concurrent.futures.ThreadPoolExecutor is created
        # asyncio.get_event_loop() created
        # Processing the requested data with blocking method with delay in separate thread pool
        # future = loop.run_in_executor(executor, blocking_method)
        # returns the blocking_method with proper information from client in await future
        # stored in result variable
        reqinfo_timestamp = "server_version" + "/" + str(get_date_and_timestamp())
        ReceivedClientData.recv_client_msg[reqinfo_timestamp] = \
            {"server_api_version": SERVER_VERSION, HTTP_STATUS: HTTPStatus.OK}
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
        loop = asyncio.get_event_loop()
        future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
        result = await future
        # writing the response back to the requested user
        self.write(json.dumps(result))
        self.set_status(HTTPStatus.OK)
        self.finish()


class StatusHandler(tornado.web.RequestHandler):
    """
    Class for Status of the Contest which is requested by user from WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with status of the Contest

        :param str req_value: contains string value as status
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Contest Status")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            # call back is added to send the message to Client(Contest) about the status
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in separate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            # writing the response back to the requested user
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.finish()


class VersionHandler(tornado.web.RequestHandler):
    """
    Class for version of the Contest(Client) which is requested by user from WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with version of the Contest

        :param str req_value: contains string value as version
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested contest version")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class CurrentloadedConfigHandler(tornado.web.RequestHandler):
    """
    Class for current loaded config of the Contest(Client) which is requested by user from WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with loaded config of the Contest

        :param str req_value: contains string value as loaded_config
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested loaded config")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ConfigInfoHandler(tornado.web.RequestHandler):
    """
    Class for config information of the Contest(Client) which is requested by user from WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests config information of the Contest

        :param str req_value: contains string value as config_info
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:

            LOG.info("Requested for config information")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class SetupfileHandler(tornado.web.RequestHandler):
    """
    Class for loaded setup file information of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests loaded setup file information of the Contest

        :param str req_value: contains string value as setup_file
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested for loaded setup file")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
            ReceivedClientData.already_requested = False
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ReportFolderLocationHandler(tornado.web.RequestHandler):
    """
    Class for report folder location path of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with report location folder of the Contest

        :param str req_value: contains string as report_folder
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Report folder location")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
            ReceivedClientData.already_requested = False
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ReportTextLocationHandler(tornado.web.RequestHandler):
    """
    Class for report text location path of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with report text location of the Contest

        :param str req_value: contains string as report_txt
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Text Report location")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
            ReceivedClientData.already_requested = False
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ReportJsonLocationHandler(tornado.web.RequestHandler):
    """
    Class for report json location path of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with report json location of the Contest

        :param str req_value: contains string as report_json
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Json Report location")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ReportHtmlLocationHandler(tornado.web.RequestHandler):
    """
    Class for report html location path of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with report html location of the Contest

        :param str req_value: contains string as report_html
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Html Report location")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class ReportXmlLocationHandler(tornado.web.RequestHandler):
    """
    Class for report xml location path of the Contest(Client) which is requested by user from
    WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with report xml location of the Contest

        :param str req_value: contains string as report_xml
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Xml Report location")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class TestCaseDataInfoHandler(tornado.web.RequestHandler):
    """
    Class for TestCase data information which is executed in the Contest and which is requested by
    user from WebPage
    """

    async def get(self, req_value):
        """
        Method triggers when user requests with status of the Contest
        """
        # Checking if client is connected, otherwise goes to else and send back message
        # immediately
        if ReceivedClientData.client_connected:
            LOG.info("Requested Test Case Data ")
            reqinfo_timestamp = str(req_value) + "/" + str(get_date_and_timestamp())
            tornado.ioloop.IOLoop.current().add_callback(ServerHandler.send_message,
                                                         reqinfo_timestamp)
            # concurrent.futures.ThreadPoolExecutor is created
            # asyncio.get_event_loop() created
            # Processing the requested data with blocking method with delay in seperate thread pool
            # future = loop.run_in_executor(executor, blocking_method)
            # returns the blocking_method with proper information from client in await future
            # stored in result variable
            executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
            loop = asyncio.get_event_loop()
            future = loop.run_in_executor(executor, blocking_method, reqinfo_timestamp)
            result = await future
            result[HTTP_STATUS] = HTTPStatus.OK
            self.write(json.dumps(result))
            # 'OK', 'Request fulfilled, document follows'
            self.set_status(HTTPStatus.OK)
            self.finish()
        else:
            self.write(json.dumps({req_value: ReceivedClientData.client_unavailable,
                                   HTTP_STATUS: HTTPStatus.SERVICE_UNAVAILABLE}))
            self.set_status(HTTPStatus.SERVICE_UNAVAILABLE)
            self.finish()


class Application(tornado.web.Application):
    """
    Class for tornado.web.Application with WebSocketHandler  and tornado.web.RequestHandler between
    User<->Server<->Client(Contest) in Bi-directional communication.
    """

    def __init__(self):
        # Here Initializing the SeverHandler Class with WebSocketHandler to communicate between
        # Server and  Client ( Server <-> Client)
        # Different RequestHandler like Status, Version, Config etc... to communicate with
        # User and Server (User <-> Server)
        self.handlers = [(r"/", ServerHandler),
                         (r"/api/version", ServerAPIVersion),
                         (r"/api/{}/contest/(status)".format(SERVER_VERSION), StatusHandler),
                         (r"/api/{}/contest/(version)".format(SERVER_VERSION), VersionHandler),
                         (r"/api/{}/contest/(loaded_config)".format(SERVER_VERSION),
                          CurrentloadedConfigHandler),
                         (r"/api/{}/contest/(config_info)".format(SERVER_VERSION),
                          ConfigInfoHandler),
                         (r"/api/{}/contest/(setup_file)".format(SERVER_VERSION),
                          SetupfileHandler),
                         (r"/api/{}/contest/(report_folder)".format(SERVER_VERSION),
                          ReportFolderLocationHandler),
                         (r"/api/{}/contest/(report_txt)".format(SERVER_VERSION),
                          ReportTextLocationHandler),
                         (r"/api/{}/contest/(report_json)".format(SERVER_VERSION),
                          ReportJsonLocationHandler),
                         (r"/api/{}/contest/(report_html)".format(SERVER_VERSION),
                          ReportHtmlLocationHandler),
                         (r"/api/{}/contest/(report_xml)".format(SERVER_VERSION),
                          ReportXmlLocationHandler),
                         (r"/api/{}/contest/test_info/(SWT_.*)".format(SERVER_VERSION),
                          TestCaseDataInfoHandler)]
        settings = dict(debug=True)
        tornado.web.Application.__init__(self, self.handlers, **settings)


class ServerHandler(tornado.websocket.WebSocketHandler):
    """
    Class for ServerHandler with WebSocketHandler creation and communicates with Client in
    Bi-directional communication.
    Server<->Client(Contest)
    """
    live_web_sockets = set()

    def open(self):
        """
        Method triggers when the client is connected to server the socket connection opens
        for communication
        This is override function from tornado.websocket.WebSocketHandler
        """
        LOG.debug("WebSocket opened")
        # once the websocket connection is established. set_nodelay is set to True
        # For more info : site-packages\tornado\websocket.py
        self.set_nodelay(True)
        # storing the created sockets, Here self is the websockethandler object
        self.live_web_sockets.add(self)
        # writing to client with client connected to server
        self.write_message("you've been connected. Congratz.")
        LOG.info("Contest REST Service Client Connected.")
        ReceivedClientData.client_connected = True

    def on_close(self):
        """
        Method triggers when the client is disconnected from the server the socket connection closed
        This is override function from tornado.websocket.WebSocketHandler
        """
        ReceivedClientData.client_connected = False
        LOG.info("ConTest REST Service Client Disconnected")

    async def on_message(self, message):
        """
        Method triggers when the client send messages to server
        This is override function from tornado.websocket.WebSocketHandler
        """
        if message != 'ConTest REST Client Running ...':
            result_dict = json.loads(message)
            for key, value in result_dict.items():
                ReceivedClientData.recv_client_msg[key] = value

    @classmethod
    def send_message(cls, message):
        """
        Method triggers based on the RequestHandler information by user with callback
        :param str message: contains string with requested information by user
        """
        removable = set()
        # Here live_web_sockets set used to store the connected clients sockets in open method
        # we are getting each connected client websocket object and writing the message to
        # connected clients
        for ws in cls.live_web_sockets:
            # if connection is not there then store the websocket object into other removable set.
            # else write the message
            if not ws.ws_connection or not ws.ws_connection.stream.socket:
                removable.add(ws)
            else:
                ws.write_message(message)
        # it removes the disconnected client object from the live_web_sockets set
        for ws in removable:
            cls.live_web_sockets.remove(ws)


def __check_port(port_no):
    """
    Checks the given port is valid to use or not
    Should be called as first function within the main function.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    res = sock.connect_ex(('localhost', port_no))
    sock.close()
    if res == 0:
        return False
    else:
        return True


def main():
    """
    This method is the start point of the Contest Server
    """
    logging.basicConfig(level=logging.INFO, format='[%(name)s %(levelname)s '
                                                   '%(asctime)s] %(message)s')

    # create argument parser which is used then to parse
    parser = argparse.ArgumentParser(
        description=DESC_STRING,
        formatter_class=argparse.RawTextHelpFormatter)

    # adding rest_server argument
    parser.add_argument(
        '--port',
        help="Port number for REST server on which connection shall be made",
        type=int,
        required=False,
        default=5001,
        metavar='port_number'
    )

    # grabbing the configuration file in arguments
    args = parser.parse_args()
    # if sure not provided default port number is provided
    port_no = args.port
    app = Application()
    exit_code = 0
    try:
        if __check_port(port_no):
            LOG.info("Port number available to use: {}".format(port_no))
            app.listen(port_no)
            LOG.info("Waiting for client connection ...")
            tornado.ioloop.IOLoop.instance().start()
        else:
            raise Exception(
                "Port number '{}' already in use. Please provide port number which is not "
                "used.".format(port_no))
    # raise basic exception
    except Exception as error:  # pylint: disable=broad-except
        LOG.error('-' * 100)
        LOG.exception(error)
        LOG.error("Contest Server port number not available to use, so exiting the system.")
        LOG.error('-' * 100)
        exit_code = 1
    finally:
        sys.exit(exit_code)


if __name__ == "__main__":
    main()
