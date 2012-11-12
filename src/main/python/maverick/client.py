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


class MaverickClientException(Exception):
    """Base class for Exceptions from the Maverick Network Client"""
    pass


class MaverickClient(object):
    """Protocol for connecting to the MaverickServer"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.client.MaverickClient")
    logging.basicConfig(level=logging.INFO)

    TIMEOUT = 2
    """Timeout (in seconds) for the telnet connections"""

    def __init__(self, host="127.0.0.1", port=7782):
        """Initializes a MaverickClient, for use in Maverick Chess

        NOTE: Port 7782 is not registered with the IANA as of 2012-12-17"""

        self.host = host
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
            MaverickClient._logger.warn("Invalid server welcome ({0}): {1}",
                                        err,
                                        welcome)
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
            MaverickClient._logger.warn("Received error response: {0}", errMsg)
            raise MaverickClientException(errMsg)
        else:
            msg = "Invalid status string received"
            MaverickClient._logger.warn(msg)
            raise MaverickClientException(msg)

    def request_register(self, name):
        """Registers a player with the system, returning their playerID.

        This should be called before trying to join a player to a game.

        @param name: A String containing the player's name"""

        response = self._makeRequest("REGISTER", name=name)
        return response["playerID"]

    def request_joinGame(self, playerID):
        """Adds the player to a new or pending game.

        @param playerID: playerID of the player joining a game"""
        response = self._makeRequest("JOIN_GAME", playerID=playerID)
        return response["gameID"]

    def request_getStatus(self, gameID):
        """Returns the status of the game with the given gameID, if it exists.

        @param gameID: the integer gameID of an in-progress game"""
        response = self._makeRequest("GET_STATUS", gameID=gameID)
        return response["status"]

    def request_getState(self, playerID, gameID):
        """
        Returns the current state of the game, containing information about
        the playerIDs of the black and white players, whose turn it is,
        the current board state, and the game history.

        @param playerID: the integer of the playerID of the player on which
                         request_getState is being called
        @param gameID: the integer gameID of an in-progress game"""

        response = self._makeRequest("GET_STATE",
                                     playerID=playerID,
                                     gameID=gameID)
        return {"youAreColor": response["youAreColor"],
                "isWhitesTurn": response["isWhitesTurn"],
                "board": response["board"],
                "enPassantFlags": response["enPassantFlags"],
                "canCastleFlags": response["canCastleFlags"],
                "history": response["history"]}

    def request_makePly(self, playerID, gameID,
                        fromRank, fromFile,
                        toRank, toFile):
        """Makes the given ply in the given game on behalf of the given
        player, if it is legal to do so.

        @param playerID: The integer playerID of a registered player.
        @param gameID: The integer gameID of an in-progress game which
        has been joined by the given player
        @param fromRank: The rank of the piece to be moved (0-delimited)
        @param fromFile: The file of the piece to be moved (0-delimited)
        @param toRank: File to which the piece should be moved (0-delimited)
        @param toFile: Rank to which the piece should be moved (0-delimited)"""

        self._makeRequest("MAKE_PLY",
                          playerID=playerID,
                          gameID=gameID,
                          fromRank=fromRank,
                          fromFile=fromFile,
                          toRank=toRank,
                          toFile=toFile)


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
            item = _asciify_json_list(item)
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
