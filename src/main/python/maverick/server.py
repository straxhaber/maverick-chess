#!/usr/bin/python

"""server.py: A rudimentary chess server that hosts games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import json
import logging
import pickle
import random

from maverick.data import ChessBoard
from maverick.data import ChessMatch
from maverick.data import ChessPosn

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor

from twisted.protocols import basic as basicProtocols


class TournamentSystem(object):
    """A class for managing player interaction with chess matches"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.server.TournamentSystem")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    def __init__(self):
        """Initializes a new tournament system with no games"""
        self.games = {}  # Dict from gameIDs to game objects. Initially empty.
        self.players = {}  # Dict from playerID to player name
        self._version = __version__  # Used in version check during un-pickling

        # Log initialization
        TournamentSystem._logger.debug("Initialized")

    @staticmethod
    def saveTS(tournament, fileName):
        """Pickles the current games' states to a file

        @param fileName: The file to save state to"""
        fd = open(fileName)
        pickle.dump(tournament, fd)
        TournamentSystem._logger.debug("Dumped game state to %s", fileName)

    @staticmethod
    def loadTS(tournament, fileName):
        """Load state from a file

        @param fileName: file created using TournamentSystem.saveGames"""

        fd = open(fileName)
        tournament = pickle.load(fd)

        if (tournament._version != __version__):
            raise TypeError("Attempted loading of an incompatible version")

        logStrF = "Loaded game state from pickle file at "
        TournamentSystem._logger.debug(logStrF, fileName)

        return tournament

    def register(self, name):
        """Registers a player with the system, returning their playerID.

        This should be called before trying to join a player to a game.

        @param name: A String containing the player's name

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"PlayerID": someInteger})"""

        if name in self.players.itervalues():
            userPID = dict((self.players[k], k) for k in self.players)[name]
            self._logger.debug("Player already exists, giving ID")
            return (True, {"playerID": userPID})
        else:
            newID = _getUniqueInt(self.players.keys())
            self.players[newID] = name
            TournamentSystem._logger.info("Registered %s with playerID %d",
                                          name, newID)
            return (True, {"playerID": newID})

    def joinGame(self, playerID):
        """Adds the player to a new or pending game.

        @param playerID: playerID of the player joining a game

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"gameID": someInteger})"""

        # Log the join attempt
        TournamentSystem._logger.debug("joinGame called with playerID %d",
                                       playerID)

        # Add the player to a pending game if one exists
        for gameID, game in self.games.iteritems():
            if game.status == ChessMatch.STATUS_PENDING:
                color = game.join(playerID)
                if color:
                    logStrF = "Added player %d to existing game %d"
                    TournamentSystem._logger.debug(logStrF, playerID, gameID)
                    return (True, {"gameID": gameID})

        # Add a player to a new game otherwise
        newGame = ChessMatch(playerID)
        newID = _getUniqueInt(self.games.keys())
        self.games[newID] = newGame
        TournamentSystem._logger.info("Added player %d to new game %d",
                                      playerID, newID)
        return (True, {"gameID": newID})

    def cancelGame(self, gameID):
        """Marks the given match as cancelled

        @return: True if successful, false otherwise
        @precondition: game is ongoing or bending
        @postcondition: game.getStatus() = ChessBoard.STATUS_CANCELED"""

        if gameID in self.games:
            if (self.games[gameID].status in [ChessMatch.STATUS_ONGOING,
                                              ChessMatch.STATUS_PENDING]):
                TournamentSystem._logger("Canceled game %d", gameID)
                self.games[gameID].status = ChessMatch.STATUS_CANCELLED
            else:
                return (False, {"error": "Game not active"})
        else:
            return (False, {"error": "Invalid game ID"})

    def getStatus(self, gameID):
        """Returns the status of the game with the given gameID, if it exists.

        @param gameID: the integer gameID of an in-progress game

        @return:  On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"status": someStatus})"""

        if gameID in self.games:
            status = self.games[gameID].status
            TournamentSystem._logger.debug("Found status of game %d to be %s",
                                          gameID, status)
            return (True, {"status": status})
        else:
            return (False, {"error": "Invalid game ID"})

    @staticmethod
    def __getState_serializeLayout(board):
        """Serialize the layout of the given ChessBoard object

        @param board: The ChessBoard object to serialize

        @return: A list of rows of piece information, each either None or a
                tuple of form (pieceColor, pieceType)"""

        # Accumulator for return value
        rowsList = []
        # Iterate through each row constructing piece tuples
        for row in board.layout:
            rowPieceTupleList = []
            for piece in row:
                if piece is None:
                    rowPieceTupleList.append(None)
                else:
                    pieceTuple = (piece.color, piece.pieceType)
                    rowPieceTupleList.append(pieceTuple)
            rowsList.append(rowPieceTupleList)

        return rowsList

    @staticmethod
    def __getState_serializeHistory(history):
        """Serialize the given list of ChessPosn objects

        @param history: A list of (fromPosn, toPosn) tuples

        @return: A list of dictionaries of the form:
                {"fromPosn": (fromRank, fromFile),
                "toPosn": (toRank, toFile)}"""

        # Accumulator for serialized posns
        plyDictList = []

        for ply in history:
            # Create dictionary of this ply and append it to accumulator

            plyDict = {}
            plyDict['fromRank'] = ply[0].rankN
            plyDict['fromFile'] = ply[0].fileN
            plyDict['toRank'] = ply[1].rankN
            plyDict['toFile'] = ply[1].fileN

            plyDictList.append(plyDict)

        return plyDictList

    def isMyTurn(self, gameID, playerID):
        """Returns whether it is the given player's turn in the game specified

        @param gameID: the integer gameID of an in-progress game
        @param playerID: the integer gameID of a player in that game

        @return:    On failure: tuple of form (False, {"error": "some err"}),
            On success: tuble of form (True, {"isMyTurn": True/False/None})"""
        if gameID in self.games:
            match = self.games[gameID]
            myColor = match.getColorOfPlayer(playerID)
            if myColor is None:
                return (False, {"error": "Not a player in the game"})
            else:
                return (True, {"isMyTurn": match.whoseTurn() == myColor})
        else:
            return (False, {"error": "Invalid game ID"})

    def getState(self, playerID, gameID):
        """Returns the current state of the game

        The state contains information about
        the playerIDs of the black and white players, whose turn it is,
        the current board state, and the game history.

        @param gameID:  the integer gameID of an in-progress game

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"youAreColor": ChessBoard.WHITE or ChessBoard.BLACK,
         "isWhitesTurn": someBoolean,
         "board": {"layout": 2d board array as returned by
                        __getState_serializeLayout,
                   "enPassantFlags": flags of form
                        ChessBoard.flag_enpassant,
                    "canCastleFlags": flags of form
                        ChessBoard.flag_canCastle"},
         "history": list of ply dictionaries of form:
                     {'fromRank': fromRank,
                      'fromFile': fromFile,
                      'toRank': toRank,
                      'toFile': toFile}"""

        if gameID in self.games:
            g = self.games[gameID]

            # Determine which player the client is
            youAreColor = g.getColorOfPlayer(playerID)
            if youAreColor is None:
                return (False, {"error": "You are not a player in this game"})

            # Serialize layout and history
            serialLayout = TournamentSystem.__getState_serializeLayout(g.board)
            serialHst = TournamentSystem.__getState_serializeHistory(g.history)

            board = {"layout": serialLayout,
                     "enPassantFlags": g.board.flag_enpassant,
                     "canCastleFlags": g.board.flag_canCastle}

            return (True, {"youAreColor": youAreColor,
                           "isWhitesTurn": (g.whoseTurn() ==
                                            ChessBoard.WHITE),
                           "board": board,
                           "history": serialHst})
        else:
            return (False, {"error": "Invalid game ID"})

    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """Makes the given ply in the given game for given player if legal

        @param playerID: The integer playerID of a registered player.
        @param gameID: The integer gameID of an in-progress game which
                       has been joined by the given player
        @param fromRank: The rank of the piece to be moved
        @param fromFile: The file of the piece to be moved
        @param toRank: The file to which the piece should be moved
        @param toFile: The rank to which the piece should be moved

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True, {})"""

        # Build ChessPosn objects from received client data

        fromPosn = ChessPosn(fromRank, fromFile)
        toPosn = ChessPosn(toRank, toFile)

        if gameID in self.games:
            result = self.games[gameID].makePly(playerID, fromPosn, toPosn)
            if result == "SUCCESS":
                return (True, {})
            else:
                return (False, {"error": result})
        else:
            return (False, {"error": "Invalid game ID"})


def _getUniqueInt(intList):
    """Return a random integer in [1,2**32-1] that is not in intList"""
    maxVals = 2 ** 32 - 1   # Maximum value of an int
    maxSize = 2 ** 31     # Maximum number of allocated ints

    # Fail fast if the list is more than half filled in
    if (len(intList) >= maxSize):
        raise RuntimeError("Cannot play more than 2**31-1 games concurrently")

    # Get a unique value
    n = random.randint(1, maxVals)
    while n in intList:
        n = random.randint(1, maxVals)
    return n

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

    # Initialize class logger
    _logger = logging.getLogger("maverick.server.MaverickServerProtocol")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    name = "MaverickChessServer"
    """The name of this server, as reported in its response headers"""

    version = __version__
    """The version of this server, as reported in its response headers"""

    VALID_REQUESTS = {"REGISTER": (TournamentSystem.register,
                                   {"name"},
                                   {"playerID"}),
                      "JOIN_GAME": (TournamentSystem.joinGame,
                                    {"playerID"},
                                    {"gameID"}),
                      "GET_STATUS": (TournamentSystem.getStatus,
                                     {"gameID"},
                                     {"status"}),
                      "IS_MY_TURN": (TournamentSystem.isMyTurn,
                                     {"gameID", "playerID"},
                                     {"isMyTurn"}),
                      "GET_STATE": (TournamentSystem.getState,
                                    {"playerID", "gameID"},
                                    {"youAreColor", "isWhitesTurn",
                                     "board", "history"}),
                      "MAKE_PLY": (TournamentSystem.makePly,
                                   {"playerID", "gameID",
                                    "fromRank", "fromFile",
                                    "toRank", "toFile"},
                                   {})}
    """Map of valid request names to:
        - corresponding TournamentSystem function
        - expected arguments
        - expected return values (currently unused)"""

    def __init__(self, tournamentSystem):
        """Initialize with a reference to a TournamentSystem backing"""

        # put a TournamentSystem instance here
        self._ts = tournamentSystem

        # Log initialization fact
        MaverickServerProtocol._logger.debug("Initialized")

    def connectionMade(self):
        """When a client connects, provide a welcome message"""

        # Log the connection
        MaverickServerProtocol._logger.debug("Connection made with client.")

        # Print out the server name, version, and prompt
        #  (e.g., "MaverickChessServer/1.0a1 WAITING_FOR_REQUEST")
        fStr = "{0}/{1} WAITING_FOR_REQUEST"  # Template for welcome message
        welcomeMsg = fStr.format(MaverickServerProtocol.name,
                                 MaverickServerProtocol.version)
        MaverickServerProtocol._logger.debug("Sending welcome message: %s",
                                             welcomeMsg)
        self.sendLine(welcomeMsg)

    def connectionLost(self, reason=None):
        """When a client disconnects, log it"""

        # Log the disconnection
        MaverickServerProtocol._logger.debug("Client disconnected.")

    def lineReceived(self, line):
        """Take input line-by-line and redirect it to the core"""

        # Log request
        MaverickServerProtocol._logger.debug("Request received: %s", line)

        # Pull out request name (e.g., "REGISTER") and arguments (unparsed)
        (requestName, _, requestArgsString) = line.partition(" ")

        errMsg = None  # If this gets set, there was an error
        if requestName in MaverickServerProtocol.VALID_REQUESTS:
            try:
                requestArgs = json.loads(requestArgsString,
                                         encoding="utf-8")
            except ValueError:
                errMsg = "Invalid JSON for arguments"
            else:
                # Pull out the requirements for this request
                (tsCommand, expArgs, _) = \
                    MaverickServerProtocol.VALID_REQUESTS[requestName]

                if expArgs != set(requestArgs.keys()):
                    # Give an error if not provided the correct arguments
                    fStr = "Invalid arguments, expected: {0}"
                    errMsg = fStr.format(",".join(list(expArgs)))
                else:
                    try:
                        # Dispatch command to TournamentSystem instance
                        (successP, result) = tsCommand(self._ts, **requestArgs)

                    except:
                        # Give an error if caught an exception
                        errMsg = "Uncaught exception"
                    else:
                        if successP:
                            # TODO (mattsh): check keys of response

                            # Provide successful results to the user
                            jsonStr = json.dumps(result,
                                                 ensure_ascii=True,
                                                 encoding="utf-8")
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

            # Log successful response
            logStrF = "RESPONSE [query=\"%s\"]: %s"
            MaverickServerProtocol._logger.info(logStrF, line, response)

            # Send successful response
            self.sendLine(response)
        else:
            # Provide client with the error

            # Compute error response
            response = "ERROR {0}".format(errMsg, line)

            # Log error response
            logStrF = "RESPONSE [query=\"%s\"]: %s"
            MaverickServerProtocol._logger.info(logStrF, line, response)

            # Send error response
            self.sendLine(response)

        # Log the fact that the connection is being closed
        logStrF = "Dropping connection to user after completion"
        MaverickServerProtocol._logger.debug(logStrF)

        # Close connection after each request
        self.transport.loseConnection()


class MaverickServerProtFactory(protocol.ServerFactory):
    """Provides a MaverickServerProtocol backed by a TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.server.MaverickServerProtFactory")
    _logger.setLevel("INFO")

    def __init__(self, tournamentSystem):
        """Initialize server state

        Makes a link to the TournamentSystem instance provided"""

        # Store a reference to the TournamentSystem backing up this server
        self._tournamentSystem = tournamentSystem

        # Log initialization
        MaverickServerProtFactory._logger.info("Server initialized")

    def buildProtocol(self, addr):
        """Create an instance of MaverickServerProtocol"""
        return MaverickServerProtocol(self._tournamentSystem)


def main(port=DEFAULT_MAVERICK_PORT):
    """Main method: called when the server code is run

    @param port: The port to use for communication with a Maverick server"""

    # Initialize a new instance of MaverickCore
    core = TournamentSystem()

    # Run a server on the specified port
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(MaverickServerProtFactory(core))
    reactor.run()  # @UndefinedVariable

if __name__ == '__main__':
    main()
