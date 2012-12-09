#!/usr/bin/python

"""MaverickTelnetClient.py: A simple client stub for connecting to Maverick"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import json
import logging
from telnetlib import Telnet

from maverick.data import ChessBoard
from maverick.data import ChessPiece
from maverick.data import ChessPosn

__all__ = ["MaverickClient",
           "MaverickClientException"]


class MaverickClientException(Exception):
    """Base class for Exceptions from the Maverick Network Client"""
    pass


class MaverickClient(object):
    """Protocol for connecting to the MaverickServer"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.client.MaverickClient")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    TIMEOUT = 2
    """Timeout (in seconds) for the telnet connections"""

    DEFAULT_HOST = "127.0.0.1"
    """Default host to connect to"""

    DEFAULT_PORT = 7782
    """Default port to connect to"""

    def __init__(self, host=None, port=None):
        """Initializes a MaverickClient, for use in Maverick Chess

        If host or port specified and not None, use them instead of defaults
        NOTE: Port 7782 is not registered with the IANA as of 2012-12-17"""

        if host is None:
            self.host = MaverickClient.DEFAULT_HOST
        else:
            self.host = host

        if port is None:
            self.port = MaverickClient.DEFAULT_PORT
        else:
            self.port = port

    def _makeRequest(self, verb, **dikt):
        """Send a request to the server

        NOTE: does not validate the content of responses"""

        # Connect via telnet to the server
        connection = Telnet(self.host, self.port)

        # Receive the welcome message
        # Example: MaverickChessServer/1.0a1 WAITING_FOR_REQUEST
        welcome = connection.read_until("\r\n", MaverickClient.TIMEOUT)

        # Validate the welcome message
        err = None
        if welcome[:19] != "MaverickChessServer":
            err = "bad_name"
        elif welcome[19] != "/":
            err = "bad_header_separator"
        else:
            (version, sep, status) = welcome[20:].partition(" ")

            if version != __version__:
                err = "incompatible_version"
            elif sep != " ":
                err = "bad_separator"
            elif status != "WAITING_FOR_REQUEST\r\n":
                err = "bad_status"
        if err != None:
            MaverickClient._logger.error("Invalid server welcome (%s): %s",
                                         err, welcome)
            raise MaverickClientException("Invalid server welcome")

        # Send the request
        requestStr = "{0} {1}\r\n".format(verb,
                                          json.dumps(dikt,
                                                     encoding="utf-8"))
        connection.write(requestStr)

        # Receive the response
        response = connection.read_until("\n", MaverickClient.TIMEOUT)

        # Parse the response and deal with it accordingly
        statusString, _, value = response.partition(" ")
        if statusString == "SUCCESS":
            try:
                result = json.loads(value, object_hook=_asciify_json_dict)
            except ValueError:
                raise MaverickClientException("Invalid JSON in response")
            return result
        elif statusString == "ERROR":
            errMsg = value[:]
            MaverickClient._logger.debug("Received error response: %s", errMsg)
            raise MaverickClientException(errMsg)
        else:
            msg = "Invalid status string received"
            MaverickClient._logger.error(msg)
            raise MaverickClientException(msg)

    def _request_register(self, name):
        """Registers a player with the system, returning their playerID.

        This should be called before trying to join a player to a game.

        @param name: A String containing the player's name"""

        response = self._makeRequest("REGISTER", name=name)
        return response["playerID"]

    def _request_joinGame(self, playerID, startFreshP):
        """Adds the player to a new or pending game.

        @param playerID: playerID of the player joining a game"""
        response = self._makeRequest("JOIN_GAME",
                                     playerID=playerID,
                                     startFreshP=startFreshP)
        return response["gameID"]

    def _request_getStatus(self, gameID):
        """Returns the status of the game with the given gameID, if it exists.

        @param gameID: the integer gameID of an in-progress game"""
        response = self._makeRequest("GET_STATUS", gameID=gameID)
        return response["status"]

    @staticmethod
    def __request_getState_deserializeLayout(layoutRaw):
        """De-serialize a board layoutRaw as received over the network

        @param layoutRaw: The textual input

        @return: A list of rows of pieces, each either None or a
                ChessPiece object"""

        # Accumulator for return value
        rowsList = []

        # Iterate through each row, constructing ChessPiece objects
        for row in layoutRaw:
            rowPieceList = []
            for pieceTuple in row:
                if pieceTuple is None:
                    rowPieceList.append(None)
                else:
                    ## TODO (James): Validate form of tuples?
                    pieceObj = ChessPiece(pieceTuple[0], pieceTuple[1])
                    rowPieceList.append(pieceObj)
            # This row is complete, append it to the master list
            rowsList.append(rowPieceList)

        return rowsList

    @staticmethod
    def __request_getState_deserializeHistory(rawHistory):
        """De-serialize a ChessMatch rawHistory as received over the network

        @param rawHistory: The textual input, as produced by
                        TournamentSystem.__getState._serializeHistory()

        @return: A list of plies as tuples of ChessPosn objects of form
                (fromPosn, toPosn)"""

        # Accumulate return value
        plyList = []

        for plyDict in rawHistory:
            # Construct ply of from, to tuples and append it to the accumulator

            fromPosn = ChessPosn(plyDict['fromRank'], plyDict['fromFile'])
            toPosn = ChessPosn(plyDict['toRank'], plyDict['toFile'])
            plyList.append((fromPosn, toPosn))

        return plyList

    def _request_isMyTurn(self, gameID, playerID):
        """Return True if it is the given player's turn in the given game

        @param gameID: The integer id of an in-progress game
        @param playerID: The integer id of a registered player

        @return: True if it is the given player's turn, false otherwise"""
        response = self._makeRequest("IS_MY_TURN",
                                     gameID=gameID,
                                     playerID=playerID)
        return response["isMyTurn"]

    def _request_getState(self, playerID, gameID):
        """Return the current state of the game

        The state contains information about
        the playerIDs of the black and white players, whose turn it is,
        the current board state, and the game history.

        @param playerID: the integer of the playerID of the player on which
                         _request_getState is being called
        @param gameID: the integer gameID of an in-progress game"""

        response = self._makeRequest("GET_STATE",
                                     playerID=playerID,
                                     gameID=gameID)
        ## TODO (James): check constants to validate received data

        # Construct board object from serialized data

        # The serialized board layout
        rawLayout = response["board"]["layout"]
        # The deserialized board layout
        layout = MaverickClient.__request_getState_deserializeLayout(rawLayout)

        # The serialized history
        rawHst = response["history"]
        # Deserialize the history
        histList = MaverickClient.__request_getState_deserializeHistory(rawHst)

        curEnPassantFlags = response["board"]["enPassantFlags"]
        curCastleFlags = response["board"]["canCastleFlags"]

        curBoardObj = ChessBoard(startLayout=layout,
                                 startEnpassantFlags=curEnPassantFlags,
                                 startCanCastleFlags=curCastleFlags)

        # Build up return dictionary
        stateDict = {}
        stateDict["youAreColor"] = response["youAreColor"]
        stateDict["isWhitesTurn"] = response["isWhitesTurn"]
        stateDict["board"] = curBoardObj
        stateDict["history"] = histList

        return stateDict

    def _request_makePly(self, playerID, gameID, fromPosn, toPosn):
        """Makes the given ply for the given player if legal to do so

        @param playerID: The integer playerID of a registered player.
        @param gameID: The integer gameID of an in-progress game which
        has been joined by the given player
        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position"""

        self._makeRequest("MAKE_PLY",
                          playerID=playerID,
                          gameID=gameID,
                          fromRank=fromPosn.rankN,
                          fromFile=fromPosn.fileN,
                          toRank=toPosn.rankN,
                          toFile=toPosn.fileN)


def _asciify_json_list(data):
    """Turn strings within a JSON list to ASCII"""
    # Adapted from: bit.ly/TtJpzH
    rv = []
    for item in data:
        if isinstance(item, unicode):
            item = item.encode('ascii')
        elif isinstance(item, list):
            item = _asciify_json_list(item)
        elif isinstance(item, dict):
            item = _asciify_json_dict(item)
        rv.append(item)
    return rv


def _asciify_json_dict(data):
    """Turn strings within a JSON dictionary to ASCII"""
    # Adapted from: bit.ly/TtJpzH
    rv = {}
    for key, value in data.iteritems():
        if isinstance(key, unicode):
            key = key.encode('ascii')
        if isinstance(value, unicode):
            value = value.encode('ascii')
        elif isinstance(value, list):
            value = _asciify_json_list(value)
        elif isinstance(value, dict):
            value = _asciify_json_dict(value)
        rv[key] = value
    return rv


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
