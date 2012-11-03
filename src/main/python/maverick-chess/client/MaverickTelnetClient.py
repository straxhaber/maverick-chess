#!/usr/bin/python

"""NetworkClient.py: A simple network API client for Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "pre-alpha"

import json
import logging

from telnetlib import Telnet

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

# TODO (mattsh): Logging

DEFAULT_MAVERICK_HOST = "127.0.0.1"
"""Default host for server"""

DEFAULT_MAVERICK_PORT = 7782
"""Default port for server

NOTE: Port 7782 isn't registered with the IANA as of December 17th, 2002"""


class MaverickClientException(Exception):
    pass


class MaverickClient(object):
    """Protocol for connecting to the MaverickServer"""

    TIMEOUT = 2
    """Timeout (in seconds) for the telnet connections"""

    def __init__(self, host=DEFAULT_MAVERICK_HOST, port=DEFAULT_MAVERICK_PORT):
        self._logger = logging.getLogger("MaverickClient")
        self.host = host
        self.port = port

    def _makeRequest(self, verb, **dikt):
        """Send a request to the server

        NOTE: does not validate the content of responses"""

        # Connect via telnet to the server
        connection = Telnet(self.host, self.port)

        # Receive the welcome message and validate it
        # Example: MaverickChessServer/1.0a1 WAITING_FOR_REQUEST
        welcome = connection.read_until("\r\n", MaverickClient.TIMEOUT)
        try:
            assert welcome[:19] == "MaverickChessServer", "bad_name"
            assert welcome[19] == "/", "bad_header_separator"
            (version, sep, status) = welcome[20:].partition(" ")
            assert version == __version__, "incompatible_version"
            assert sep == " ", "bad_separator"
            assert status == "WAITING_FOR_REQUEST\r\n", "bad_status"
        except AssertionError, msg:
            raise MaverickClientException(
                "Invalid welcome from server ({0}): {1}".format(msg,
                                                                welcome))

        # Send the request
        requestStr = "{0} {1}\r\n".format(verb, json.dumps(dikt))
        connection.write(requestStr)

        # Receive the response
        response = connection.read_until("\n", MaverickClient.TIMEOUT)

        # Parse the response and deal with it accordingly
        statusString, _, value = response.partition(" ")
        if statusString == "SUCCESS":
            result = json.loads(value)
            return result
        elif statusString == "ERROR":
            errMsg = value[:]
            raise MaverickClientException(errMsg)
        else:
            raise MaverickClientException("Unknown status string received")

    def register(self, name):
        """TODO write a good comment"""
        response = self._makeRequest("REGISTER", name=name)
        return response["playerID"]

    def joinGame(self, playerID):
        """TODO write a good comment"""
        response = self._makeRequest("JOIN_GAME", playerID=playerID)
        return response["gameID"]

    def getStatus(self, gameID):
        """TODO write a good comment"""
        response = self._makeRequest("GET_STATUS", gameID=gameID)
        return response["status"]

    def getState(self, playerID, gameID):
        """TODO write a good comment"""
        response = self._makeRequest("GET_STATE",
                                     playerID=playerID,
                                     gameID=gameID)
        return response

    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """TODO write a good comment"""
        self._makeRequest("MAKE_PLY",
                          playerID=playerID,
                          gameID=gameID,
                          fromRank=fromRank,
                          fromFile=fromFile,
                          toRank=toRank,
                          toFile=toFile)


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
