#!/usr/bin/python

"""NetworkClient.py: A simple network API client for Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "pre-alpha"

import logging

from twisted.internet import protocol
#from twisted.internet import reactor
from twisted.protocols import basic as basicProtocols

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

## TODO (mattsh): Logging

"""Default port for server"""
DEFAULT_MAVERICK_PORT = 7782
DEfAULT_SERVER_URL = "127.0.0.1"
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickClientProtocol(basicProtocols.LineOnlyReceiver):
    """Protocol for connecting to the MaverickServer"""

    def __init__(self):
        self._responseWelcome = None    # Intial welcome message
        self._responseRequest = None    # Response to request
        self._requestMadeP = False      # Has a request been made?

        # TODO (mattsh): welcome cannot come before connection
        # TODO (mattsh): response cannot come before request sent

    def lineReceived(self, line):
        """Handle responses from the server"""
        if self._responseWelcome is None:
            self._responseWelcome = line
        elif self._responseRequest is None:
            if not self._requestMadeP:
                raise RuntimeError("Response received before request made !?")
            else:
                self._responseRequest = line
        else:
            raise RuntimeError("Unexpected data from server")

    def sendLine(self, line):
        """Send a request to the server"""
        if self._responseWelcome is None:
            raise RuntimeError("Cannot send request before receiving welcome")
        elif self._requestMadeP:
            raise RuntimeError("Cannot run multiple requests per connection")
        else:
            self._requestMadeP = True
            return basicProtocols.LineOnlyReceiver.sendLine(self, line)

#    def _makeRequest(self, verb, dikt):
#        """Send a request to the server
#
#        NOTE: does not validate data"""
#        requestStr = "%s %s".format(verb, json.dumps(dikt))
#        self.sendLine(requestStr)
#        ## TODO Write this


class MaverickClientFactory(protocol.ClientFactory):
    """Provides a MaverickClientProtocol for communication with server."""

    def __init__(self, url=DEfAULT_SERVER_URL, port=DEFAULT_MAVERICK_PORT):
        """Instantiate a logger."""
        self._logger = logging.getLogger("MaverickClient")
        self.protocol = MaverickClientProtocol


def MaverickClient(Object):
    """TODO this is stub code

    need to figure out how to build an asynchronous client that can dispatch
    methods"""

    def register(self, name):
        """TODO write a good comment"""
        args = {"name": name}
        self._makeRequest("REGISTER", args)

    def joinGame(self, playerID):
        """TODO write a good comment"""
        args = {"playerID": playerID}
        self._makeRequest("JOIN_GAME", args)

    def getStatus(self, gameID):
        """TODO write a good comment"""
        args = {"gameID": gameID}
        self._makeRequest("GET_STATUS", args)

    def getState(self, gameID):
        """TODO write a good comment"""
        args = {"gameID": gameID}
        self._makeRequest("GET_STATE", args)

    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """TODO write a good comment"""
        args = {"playerID": playerID,
                "gameID": gameID,
                "fromRank": fromRank,
                "fromFile": fromFile,
                "toRank": fromRank,
                "toFile": toFile}
        self._makeRequest("MAKE_PLY", args)

    def _makeRequest(self, verb, dikt):
        """Sends a Maverick request to the server"""
        pass  # TODO write this


        # Run a client to connect to a server on the specified port
        #reactor.connectTCP(url, port, self)  # @UndefinedVariable

def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
