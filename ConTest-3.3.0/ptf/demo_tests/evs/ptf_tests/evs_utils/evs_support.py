"""
 Copyright 2018 Continental Corporation

 Author:
    M. Shan Ur Rehman <Muhammad.Shan.ur.Rehman@continental-corporation.com>
    M. F. Ali Khan <Muhammad.fakhar.ali.khan@continental-corporation.com>

 File:
    evs_support.py

 Details:
    This file contains custom helper/support class to be used for EVS tests
"""

# Python imports
from collections import deque


class ResponseHandler:
    """
    Class for handling the response of ECU through Goepel CAN Box.
    """
    def __init__(self):
        """
        constructor
        """
        # defining a que for response storage
        self.response_queue = deque()

    def callback_func(self, response_struct):
        """
        Callback function to handle response from ECU

        :param ctype structure response_struct: Structure filled wih target response data
        """
        resp_lst = []
        for i in range(len(response_struct.Data)):
            resp_lst.append(response_struct.Data[i])

        # appending the response queue in FIFO style.
        self.response_queue.appendleft(resp_lst)

    def fetch(self):
        """
        Method to pop the response queue.
        """
        if self.response_queue:
            return bytes(self.response_queue.pop())
        else:
            print("No response to be fetched!")
