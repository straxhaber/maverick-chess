#!/usr/bin/python

import os, sys, string, socket, time, datetime

from twisted.internet.protocol import Protocol
from twisted.internet.protocol import ServerFactory
from twisted.internet.endpoints import TCP4ServerEndpoint
from twisted.protocols.basic import LineOnlyReceiver
from twisted.internet import reactor

from core import TournamentSystem

################################################################################
# Code written by Matthew Strax-Haber and James Magnarelli. All Rights Reserved.
################################################################################

## Port 7782 is not registered for use with the IANA as of December 17th, 2002
defaultPort = 7782

class MaverickProt(LineOnlyReceiver):
    """
    Protocol for an asynchronous server that administers chess games to clients
    """
    _name = "MaverickChessServer"
    _version = "1.0a1"

    ## put a TournamentSystem instance here
    __tournSys = None

    def __init__(self, tournamentSystem):
        super.__init__(self)
        MaverickProt.__tournSys = tournamentSystem

    def connectionMade(self):
        """
        When a client connects, provide a welcome message
        """

        ## TODO: log client connections

        ## Print out the server name and version
        ##  (e.g., "MaverickChessServer/1.0a1")
        fStr = "{0}/{1} WaitingForRequest\n" ## Template for welcome message
        welcomeMsg = fStr.format(MaverickProt._name, MaverickProt._version)
        self.transport.write(welcomeMsg)


    def connectionLost(self):
        """
        When a client disconnects, log it
        """

        ### TODO: log client disconnections
        
    def lineReceived(self, line):
        """
        Take input line-by-line and redirect it to the core
        """

        ### TODO: log client requests

        ### FIXME: finish writing this method

        ### TODO: get request name and arguments
        requestName = "REGISTER"
        reqArgs = ["Matthew Strax-Haber"]

        errorMsg = None

        if requestName == "REGISTER":
            expectedArguments={"name"}
            if expectedArguments != set(arguments):
                fStr = "Invalid arguments, expected: {0}"
                errorMsg = fStr.format(str(list(expectedArguments)))
            else:
                (errCode, result) = self.__tournSys.register(reqArgs["name"])
                if errCode == 0:
                    fStr = "SUCCESS \"{0}\""
                    response = fStr.format(str(result["playerID"))
                elif errCode == -1:
                    errorMsg = "Unknown error"
                elif errCode == -2:
                    errorMsg = "Name already in use"

        elif requestName == "PLAY_GAME":
            expectedArguments={"playerID"}
            if expectedArguments != set(arguments):
                fStr = "Invalid arguments, expected: {0}"
                errorMsg = fStr.format(str(list(expectedArguments)))
            else:
                playerID = reqArgs["playerID"]
                (errCode, result) = self.__tournSys.playGame(playerID) ## FIXME
                if errCode == 0:
                    fStr = "SUCCESS \"{0}\""
                    response = fStr.format(str(result["gameID"]))
                elif errCode == -1:
                    errorMsg = "Unknown error"

        elif requestName == "GET_STATUS":
            expectedArguments={"playerID", "gameID"}
            if expectedArguments != set(arguments):
                fStr = "Invalid arguments, expected: {0}"
                errorMsg = fStr.format(str(list(expectedArguments)))
            else:
                playerID = reqArgs["playerID"]
                gameID = reqArgs["gameID"]
                (errCode, result) = self.__tournSys.getStatus(
                    playerID, gameID) ## FIXME
                if errCode == 0:
                    fStr = "SUCCESS \"{0}\""
                    response = fStr.format() ## FIXME
                elif errCode == -1:
                    errorMsg = "Unknown error"

        elif requestName == "GET_STATE":
            expectedArguments={"playerID", "gameID"}
            if expectedArguments != set(arguments):
                fStr = "Invalid arguments, expected: {0}"
                errorMsg = fStr.format(str(list(expectedArguments)))
            else:
                playerID = reqArgs["playerID"]
                gameID = reqArgs["gameID"]
                (errCode, result) = self.__tournSys.getState(playerID, gameID)
                if errCode == 0:
                    fStr = "SUCCESS \"{0}\""
                    response = fStr.format() ## FIXME
                elif errCode == -1:
                    errorMsg = "Unknown error"

        elif requestName == "MAKE_PLY":
            expectedArguments={"playerID", "gameID",
                               "fromRank", "fromFile",
                               "toRank", "toFile"}
            if expectedArguments != set(arguments):
                fStr = "Invalid arguments, expected: {0}"
                errorMsg = fStr.format(str(list(expectedArguments)))
            else:
                playerID = reqArgs["playerID"]
                gameID = reqArgs["gameID"]
                fromRank = reqArgs["fromRank"]
                fromFile = reqArgs["fromFile"]
                toRank = reqArgs["toRank"]
                toFile = reqArgs["toFile"]
                (errCode, result) = self.__tournSys.makePly(
                    playerID, gameID, fromRank, fromFile, toRank, toFile)
                if errCode == 0:
                    fStr = "SUCCESS \"{0}\""
                    response = fStr.format() ## FIXME
                elif errCode == -1:
                    errorMsg = "Unknown error"

        #elif requestName == "FIXME": ## FIXME
        #    expectedArguments={"fixme"} ## FIXME
        #    if expectedArguments != set(arguments):
        #        fStr = "Invalid arguments, expected: {0}"
        #        errorMsg = fStr.format(str(list(expectedArguments)))
        #    else:
        #        (errCode, result) = self.__tournSys.fixme() ## FIXME
        #        if errCode == 0:
        #            fStr = "SUCCESS \"{0}\""
        #            response = fStr.format(str(playerID))
        #        elif errCode == -1:
        #            errorMsg = "Unknown error"

        if errorMsg == None:
            self.transport.write(response)
        else:
            self._invalidRequest(line, errorMsg)
            


    def _invalidRequest(self, request, reason):
        """
        Notify the user if they make an invalid request
        """
        
        ## TODO: log invalid request

        fStr = "INVALID_REQUEST {0}: \"{1}\""
        errorMsg = fStr.format(reason, request)
        self.transport.write(errorMsg)
            

    #Deprecated code; kept for convenience
    #def dataReceived(self, data):
    #    """Run when data is received"""
    #    
    #    ### FIXME: Stub code: echos back any received strings
    #    self.transport.write(data)
    #    self.transport.loseConnection()


class ChessServerFactory(ServerFactory):
    """
    This is a simple factory that provides a ChessServerProtocol backed by a
    TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance
    """

    def __init__(self, tournamentSystem):
        """
        Store a reference to the TournamentSystem backing up this server
        """
        super.__init__()
        self._tournamentSystem = tournamentSystem
        
    def buildProtocol(self, addr):
        return ChessServerProtocol(self._tournamentSystem)

def _main(port):
    """
    Main method
    """
    ## Initialize a new instance of MaverickCore
    core = TournamentSystem()

    ## Run a server on the specified port
    endpoint = TCP4ServerEndpoint(reactor, port)
    endpoint.listen(ChessServerFactory(core))
    reactor.run()


if __name__ == '__main__':
    _main(defaultPort)
