#!/usr/bin/python

import os, sys, string, socket, time, datetime

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import Factory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.internet import reactor

def startServer(port):
    """Start a server running on the specified port"""

def stopServer():
    """Shut down the running server"""

class ChessServerProtocol(Protocol):
    """Provides a server that listens on a given socket for input and runs a chess game"""
    _name = "MaverickChessServer/1.0a1"

    """
    def connectionMade(self):
        welcomeMsg = "{0}/{1}\n".format(ChessServerProtocol._name, ChessServerProtocol._version)
        self.transport.write(welcomeMsg)
    """

    def dataReceived(self, data):
        self.transport.write(data)
        self.transport.loseConnection()


class ChessServerFactory(Factory):
    def buildProtocol(self, addr):
        return ChessServerProtocol()    

def _main():
    """Main method"""
    ## Run a server on port 7782
    endpoint = TCP4ServerEndpoint(reactor, 7782)
    endpoint.listen(ChessServerFactory())
    reactor.run()


if __name__ == '__main__':
    _main()
