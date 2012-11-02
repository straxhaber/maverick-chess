#!/usr/bin/python

"""NetworkServer.py: A simple network API server for Maverick"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

import json
import logging

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor

from twisted.protocols import basic as basicProtocols

from TournamentSystem import TournamentSystem

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

# TODO (mattsh): Logging


"""Default port for server"""
DEFAULT_MAVERICK_PORT = 7782
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickServerProtocol(basicProtocols.LineOnlyReceiver):
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
    _version = __version__

    _ts = None
    """put a TournamentSystem instance here"""

    def __init__(self, tournamentSystem):
        """Store a reference to the TournamentSystem backing up this server"""
        MaverickServerProtocol._ts = tournamentSystem

        # Instantiate a logger
        self._logger = logging.getLogger(self.__class__.__name__)

        # Log initialization
        self._logger.debug("Initialized")

    def connectionMade(self):
        """When a client connects, provide a welcome message"""

        # Log the connection
        self._logger.debug("Connection made with client.")

        # Print out the server name, version, and prompt
        #  (e.g., "MaverickChessServer/1.0a1 WAITING_FOR_REQUEST")
        fStr = "{0}/{1} WAITING_FOR_REQUEST"  # Template for welcome message
        welcomeMsg = fStr.format(MaverickServerProtocol._name,
                                 MaverickServerProtocol._version)
        self._logger.debug("Sending welcome message")
        self.sendLine(welcomeMsg)

    def connectionLost(self, reason=None):
        """When a client disconnects, log it"""

        # Log the disconnection
        self._logger.debug("Client disconnected.")

    def lineReceived(self, line):
        """Take input line-by-line and redirect it to the core"""

        # Log the request
        self._logger.debug("Request received: {0}".format(line))

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
                                       {"playerID", "gameID"},
                                       {"youAreColor", "isWhitesTurn",
                                        "board", "history"}),
                         "MAKE_PLY": (self._ts.makePly,
                                      {"playerID", "gameID",
                                       "fromRank", "fromFile",
                                       "toRank", "toFile"},
                                      {})}

        requestName = line.partition(" ")[0]  # Request name (e.g., "REGISTER")

        requestArgsString = line.partition(" ")[2]  # Arguments (unparsed)

        errMsg = None  # If this gets set, there was an error
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
        if errMsg is None:
            # Provide client with the response
            logStr = "RESPONSE [query=\"{0}\"]: {1}".format(line, response)
            self._logger.info(logStr)  # Log successful response
            self.sendLine(response)  # Send successful response
        else:
            # Provide client with the error
            response = "ERROR {1} [query=\"{0}\"]".format(line, errMsg)
            self._logger.info(response)  # Log error response
            self.sendLine(response)  # Send error response

        # Close connection after each request
        self._logger.debug("Dropping connection to user after completion")
        self.transport.loseConnection()


class MaverickServerProtocolFactory(protocol.ServerFactory):
    """Provides a MaverickServerProtocol backed by a TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance"""

    def __init__(self, tournamentSystem):
        """Initialize server state

        Makes a link to the TournamentSystem instance provided"""

        # Store a reference to the TournamentSystem backing up this server
        self._tournamentSystem = tournamentSystem

        # Instantiate a logger
        self._logger = logging.getLogger(self.__class__.__name__)

        # Log initialization
        self._logger.debug("Initialized")

    def buildProtocol(self, addr):
        """Create an instance of MaverickServerProtocol"""
        return MaverickServerProtocol(self._tournamentSystem)


def _main(port=DEFAULT_MAVERICK_PORT, logLevelStr='INFO'):
    """Main method: called when the server code is run

    @param port: The port to use for communication with a Maverick server
    @param logLevelStr: The desired log level.  One of 'INFO', 'DEBUG',
    'WARNING', 'ERROR', or 'CRITICAL'. Defaults to 'INFO' """

    # Set logging level to whatever was specified
    logLevel = getattr(logging, logLevelStr.upper(), None)
    if not isinstance(logLevel, int):
        raise ValueError('Invalid log level: {0}'.format(logLevelStr))
    logging.basicConfig(level=logLevel)

    # Initialize a new instance of MaverickCore
    core = TournamentSystem()

    # Run a server on the specified port
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(MaverickServerProtocolFactory(core))
    reactor.run()  # @UndefinedVariable

if __name__ == '__main__':
    _main()
