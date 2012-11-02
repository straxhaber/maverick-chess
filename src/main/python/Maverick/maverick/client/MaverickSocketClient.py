#!/usr/bin/python

"""NetworkClient.py: A simple network API client for Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "pre-alpha"

import json
import logging
import socket

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

## TODO (mattsh): Logging

"""Default port for server"""
DEFAULT_MAVERICK_PORT = 7782
DEfAULT_SERVER_URL = "127.0.0.1"
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickClientException(Exception):
    pass


class MaverickClient(object):
    """Protocol for connecting to the MaverickServer"""

    def __init__(self, url=DEfAULT_SERVER_URL, port=DEFAULT_MAVERICK_PORT):
        self._logger = logging.getLogger("MaverickClient")
        self.url = url
        self.port = port
        self.sock = None

    def makeRequest(self, verb, dikt):
        """Send a request to the server

        NOTE: does not validate data"""
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.url, self.port))

        welcome = sock.recv(4096)  # TODO (mattsh) cap response len in server
        # TODO parse and validate welcome message
        if welcome != welcome:
            raise MaverickClientException("invalid welcome message")

        # TODO (mattsh): remove superfluous debug statements

        print "welcome: " + welcome
        print "got here"

        requestStr = "{0} {1}\n".format(verb, json.dumps(dikt))

        print "debug 2: {0} {1}".format(verb, json.dumps(dikt))
        sock.sendall(requestStr)

        print "debug 3: sent"
        response = sock.recv(4096)  # TODO (mattsh) cap response len in server
        print "debug 4"

        print response  # TODO: do something with this

    def register(self, name):
        """TODO write a good comment"""
        args = {"name": name}
        self.makeRequest("REGISTER", args)

    def joinGame(self, playerID):
        """TODO write a good comment"""
        args = {"playerID": playerID}
        self.makeRequest("JOIN_GAME", args)

    def getStatus(self, gameID):
        """TODO write a good comment"""
        args = {"gameID": gameID}
        self.makeRequest("GET_STATUS", args)

    def getState(self, gameID):
        """TODO write a good comment"""
        args = {"gameID": gameID}
        self.makeRequest("GET_STATE", args)

    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """TODO write a good comment"""
        args = {"playerID": playerID,
                "gameID": gameID,
                "fromRank": fromRank,
                "fromFile": fromFile,
                "toRank": fromRank,
                "toFile": toFile}
        self.makeRequest("MAKE_PLY", args)


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
