#!/usr/bin/python

"""NetworkClient.py: A simple network API client for Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "pre-alpha"

import json
import logging

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor
from twisted.protocols import basic as basicProtocols

#############################################################
# Code written by Matthew Strax-Haber, James Magnarelli,    #
# and Brad Fournier. All Rights Reserved.                   #
#############################################################

"""Default port for server"""
DEFAULT_SERVER_PORT = 7782
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickClientProtocol(basicProtocols.LineOnlyReceiver):
    """
    """
    pass
    ## TODO (James): Write the code for this class.


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
        reactor.stop()

    def clientConnectionLost(self, connector, reason):
        self.logger.info("Connection lost.")
        reactor.stop()

    def buildProtocol(self, addr):
        """Create an instance of MaverickClientProtocol"""
        return MaverickClientProtocol()


def _main(port):
    """Main method: called when the client code is run"""

    # Run a client to connect to a server on the specified port
    f = MaverickClientFactory()
    reactor.connectTCP("localhost", port, f)
    reactor.run()  # @UndefinedVariable

if __name__ == '__main__':
    _main(DEFAULT_SERVER_PORT)
