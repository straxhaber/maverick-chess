#!/usr/bin/python

"""NetworkServer.py: A simple network API server for Maverick"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

from twisted.internet  import protocol, endpoints, reactor
from twisted.protocols import basic as basicProtocols

from TournamentSystem import TournamentSystem

import json

################################################################################
# Code written by Matthew Strax-Haber and James Magnarelli. All Rights Reserved.
################################################################################

"""Default port for server"""
DEFAULT_PORT = 7782
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002

class MaverickProtocol(basicProtocols.LineOnlyReceiver):
    """Protocol for asynchronous server that administers chess games to clients
    
    Initiates all connections with a message:
     MaverickChessServer/{version} WAITING_FOR_REQUEST
    
    Takes in queries of the form:
     VERB {JSON of arguments}
     
    Responds back in the form:
     if Successful:    SUCCESS {JSON of response}
     if Error:         ERROR {error message} [{query}]
     
    After the query is responded to, the server disconnects the client"""
    _name = "MaverickChessServer"
    _version = "1.0a1"

    # put a TournamentSystem instance here
    _ts = None

    def __init__(self, tournamentSystem):
        """Store a reference to the TournamentSystem backing up this server"""
        MaverickProtocol._ts = tournamentSystem

    def connectionMade(self):
        """When a client connects, provide a welcome message"""
        ## TODO: log connections

        # Print out the server name and version
        #  (e.g., "MaverickChessServer/1.0a1")
        fStr = "{0}/{1} WAITING_FOR_REQUEST" # Template for welcome message
        welcomeMsg = fStr.format(MaverickProtocol._name,
                                 MaverickProtocol._version)
        self.sendLine(welcomeMsg)

    def connectionLost(self, reason=None):
        """When a client disconnects, log it"""
        ## TODO: log disconnections
    
    def lineReceived(self, line):
        """Take input line-by-line and redirect it to the core"""
        
        # Map of valid request names to
        #  - corresponding TournamentSystem function
        #  - expected arguments
        #  - expected return values (currently unused)
        validRequests = {"REGISTER": (self._ts.register,
                                      {"name"},
                                      {"playerID"}),
                         "JOIN_GAME": (self._ts.joinGame,
                                       {"playerID"},
                                       {"gameID"}),
                         "GET_STATUS": (self._ts.getStatus,
                                        {"gameID"},
                                        {"status"}),
                         "GET_STATE": (self._ts.getState,
                                       {"gameID"},
                                       {"players", "isWhitesTurn",
                                        "board", "history"}),
                         "MAKE_PLY": (self._ts.makePly,
                                      {"playerID", "gameID",
                                       "fromRank", "fromFile",
                                       "toRank", "toFile"},
                                      {"status"})}
        
        requestName = line.partition(" ")[0] # Request name (e.g., "REGISTER")
        ## TODO: log requests
        requestArgsString = line.partition(" ")[2] # Arguments (unparsed)
        
        errMsg = None # If this gets set, there was an error
        if requestName in validRequests.keys():
            try:
                requestArgs = json.loads(requestArgsString)
            except ValueError:
                errMsg = "Invalid JSON for arguments"
            else:
                # Pull out the requirements for this request
                (tsCommand, expArgs, _) = validRequests[requestName]
                
                if expArgs != set(requestArgs.keys()):
                    # Give an error if not provided the correct arguments
                    fStr = "Invalid arguments, expected: {0}"
                    errMsg = fStr.format(",".join(list(expArgs)))
                else:
                    try:
                        # Dispatch command to TournamentSystem instance
                        (successP, result) = tsCommand(**requestArgs)
                    except:
                        # Give an error if caught an exception
                        errMsg = "Uncaught exception"
                    else:
                        if successP:
                            # Provide successful results to the user
                            jsonStr = json.dumps(result, ensure_ascii=True)
                            response = "SUCCESS {0}".format(jsonStr)
                        if not successP:
                            # Pull out structured error messages from func call
                            errMsg = result["error"]
        else:
            # Give an error if provided an invalid command
            errMsg = "Unrecognized verb \"{0}\" in request".format(requestName)
        
        # Respond to the client
        if errMsg == None:
            # Provide client with the response
            self.sendLine(response)
        else:
            # Provide client with the error
            response = "ERROR {1} [query=\"{0}\"]".format(line, errMsg)
            self.sendLine(response)
        
        # Close connection after each request
        self.transport.loseConnection()
        

class MaverickProtocolFactory(protocol.ServerFactory):
    """Provides a MaverickProtocol backed by a TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance"""

    def __init__(self, tournamentSystem):
        """
        Store a reference to the TournamentSystem backing up this server
        """
        self._tournamentSystem = tournamentSystem
        
    def buildProtocol(self, addr):
        """Create an instance of MaverickProtocol"""
        return MaverickProtocol(self._tournamentSystem)

def _main(port):
    """Main method: called when the server code is run"""
    # Initialize a new instance of MaverickCore
    core = TournamentSystem()

    # Run a server on the specified port
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(MaverickProtocolFactory(core))
    reactor.run() #@UndefinedVariable
    
if __name__ == '__main__':
    _main(DEFAULT_PORT)
