#!/usr/bin/python

"""NetworkClient.py: A simple network API client for Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "pre-alpha"

import json
import logging

from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols import basic as basicProtocols

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

"""Default port for server"""
DEFAULT_MAVERICK_PORT = 7782
DEfAULT_SERVER_URL = "127.0.0.1"
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickClientProtocol(basicProtocols.LineOnlyReceiver):
    """Protocol for connecting to the MaverickServer"""

    def register(self, **args):
        """Expected args: name

        TODO write a good comment"""
        MaverickClientProtocol.checkArguments({"name"}, args)
        self._sendRequest("REGISTER", args)

    def joinGame(self, **args):
        """Expected args: playerID

        TODO write a good comment"""
        MaverickClientProtocol.checkArguments({"playerID"}, args)
        self._sendRequest("JOIN_GAME", args)

    def getStatus(self, **args):
        """Expected args: gameID

        TODO write a good comment"""
        MaverickClientProtocol.checkArguments({"gameID"}, args)
        self._sendRequest("GET_STATUS", args)

    def getState(self, **args):
        """Expected args: gameID

        TODO write a good comment"""
        MaverickClientProtocol.checkArguments({"gameID"}, args)
        self._sendRequest("GET_STATE", args)

    def makePly(self, **args):
        """Expected args: playerID, gameID, fromRank, fromFile, toRank, toFile

        TODO write a good comment"""
        expectedArguments = {"playerID", "gameID",
                             "fromRank", "fromFile",
                             "toRank", "toFile"}
        MaverickClientProtocol.checkArguments(expectedArguments, args)
        self._sendRequest("MAKE_PLY", args)

    def _sendRequest(self, verb, dikt):
        """Send a request to the server

        NOTE: does not validate data"""
        requestStr = "%s %s".format(verb, json.dumps(dikt))
        self.sendLine(requestStr)

    @staticmethod
    def checkArguments(expArgs, givenArgs):
        """Asserts that the set expArgs and the keys of givenArgs match

        If they don't, raise a TypeError with a sensible error message"""
        if (expArgs == set(givenArgs)):
            return
        elif (expArgs.issuperset(givenArgs)):
            raise TypeError("unexpected keyword arg(s): %s".
                            format(str(givenArgs.difference(expArgs))))
        else:
            raise TypeError("missing expected keyword arg(s): %s".
                            format(str(expArgs.difference(givenArgs))))


class MaverickClientFactory(protocol.ClientFactory):
    """Provides a MaverickClientProtocol for communication with a maverick
    server.
    """

    def __init__(self):
        """
        Instantiate a logger.
        """
        self.logger = logging.getLogger("MaverickClient")

    def clientConnectionFailed(self, connector, reason):
        self.logger.info("Connection failed - goodbye!")
        reactor.stop()  # @UndefinedVariable

    def clientConnectionLost(self, connector, reason):
        self.logger.info("Connection lost.")
        reactor.stop()  # @UndefinedVariable

    def buildProtocol(self, addr):
        """Create an instance of MaverickClientProtocol"""
        return MaverickClientProtocol()


##  TODO: completely re-think this. There needs to be a way for client code
##        to call into this code as if it were a library
def _main(url=DEfAULT_SERVER_URL, port=DEFAULT_MAVERICK_PORT):
    """Main method: called when the client code is run"""

    # Run a client to connect to a server on the specified port
    f = MaverickClientFactory()
    reactor.connectTCP("localhost", port, f)  # @UndefinedVariable
    reactor.run()  # @UndefinedVariable

if __name__ == '__main__':
    _main()
