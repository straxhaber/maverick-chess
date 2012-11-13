#!/usr/bin/python

"""common.py: Common code for gameplay interfaces"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging
import random
import time

from maverick.client import MaverickClient
from maverick.client import MaverickClientException
from maverick.data import ChessBoard
from maverick.data import ChessMatch

__all__ = ["MaverickPlayer"]

# TODO (mattsh): put more logging throughout this class


class MaverickPlayer(MaverickClient):
    """Provides basic methods for a Maverick AI"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.common.MaverickPlayer")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    SLEEP_TIME = 1
    """Amount of time to wait between requests when polling"""

    def __init__(self, host=None, port=None):
        """Initialize a MaverickPlayer

        If host or port specified and not None, use them instead of defaults

        NOTE: MaverickPlayer.startPlaying must be run to set playerID, gameID,
        and isWhite before the player can make moves"""

        MaverickClient.__init__(self, host=host, port=port)

        # Default name (should be overridden for a human AI)
        # i.e., MaverickAI.1234901234.12839429834
        self.name = ".".join([self.__class__.__name__,
                              str(time.time()),
                              str(random.randrange(1, 2 ** 30))])

        # These variables must be overridden
        self.playerID = None    # ID for player's system registration
        self.gameID = None      # ID for game that the player is in
        self.isWhite = None     # Is the player white?

    def displayMessage(self, message):
        """Display a message for the user"""
        print(" -- {0}".format(message))

    def startPlaying(self):
        """Enters the player into an ongoing game (blocks until successful)

        @precondition: self.name must be set"""
        self.playerID = self._request_register(self.name)
        self.gameID = self._request_joinGame(self.playerID)

        # Block until game has started
        while self._request_getStatus() == ChessMatch.STATUS_PENDING:
            self.displayMessage("Waiting until the game starts")
            time.sleep(MaverickPlayer.SLEEP_TIME)

        # NOTE: Player is now in a game that is not pending

        self.isWhite = (self._request_getState()["youAreColor"] ==
                        ChessBoard.WHITE)

    def run(self):
        """Registers user, connects to game, and starts gameplay loop"""
        self._initName()
        self.startPlaying()
        self._welcomePlayer()

        # While the game is in progress
        while self._request_getStatus() == ChessMatch.STATUS_ONGOING:

            # Wait until it is your turn
            while not self._request_isMyTurn():
#            while self._request_getState()['isWhitesTurn'] != self.isWhite:
                self.displayMessage("Waiting until turn")

                # Break if a game is stopped while waiting
                if self._request_getStatus() != ChessMatch.STATUS_ONGOING:
                    break

                time.sleep(MaverickPlayer.SLEEP_TIME)

            curBoard = self._request_getState()["board"]

            (fromPosn, toPosn) = self._getNextMove(curBoard)

            try:
                self._request_makePly(fromPosn, toPosn)
            except MaverickClientException, e:
                self._handleBadMove(e.message, curBoard,
                                    fromPosn, toPosn)

        # When this is reached, game is over
        status = self._request_getStatus()
        if status == ChessMatch.STATUS_WHITE_WON:
            self.displayMessage("GAME OVER - WHITE WON")
        elif status == ChessMatch.STATUS_BLACK_WON:
            self.displayMessage("GAME OVER - BLACK WON")
        elif status == ChessMatch.STATUS_DRAWN:
            self.displayMessage("GAME OVER - DRAWN")
        elif status == ChessMatch.STATUS_CANCELLED:
            self.displayMessage("GAME CANCELLED")
        else:
            self.displayMessage("ERROR: UNEXPECTED GAME STATUS TRANSITION")

    def _initName(self):
        """Figure out the name of the class"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _welcomePlayer(self):
        """Display welcome messages if appropriate"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _request_isMyTurn(self):
        """Requests the player's turn status from the Maverick server

        @return: True if it is my turn, False otherwise"""
        return MaverickClient._request_isMyTurn(self,
                                                self.gameID,
                                                self.playerID)

    def _request_getStatus(self):
        """Requests the status of this game from the Maverick server

        @return: one of ChessMatch.STATUS_PENDING,
                        ChessMatch.STATUS_ONGOING,
                        ChessMatch.STATUS_BLACK_WON,
                        ChessMatch.STATUS_WHITE_WON,
                        ChessMatch.STATUS_DRAWN,
                        ChessMatch.STATUS_CANCELLED,"""

        return MaverickClient._request_getStatus(self, self.gameID)

    def _request_getState(self):
        """Retrieves the current game state from the server

        @return: A dictionary of the following form:
                {"youAreColor": ChessBoard.WHITE or ChessBoard.BLACK,
                "isWhitesTurn": True or False,
                "board": a ChessBoard object representing the current board,
                "history": list of plies}"""

        return MaverickClient._request_getState(self,
                                                   self.playerID, self.gameID)

    def _request_makePly(self, fromPosn, toPosn):
        """Sends a makePly request to the server for the given ply"""
        MaverickClient._request_makePly(self,
                                       self.playerID, self.gameID,
                                       fromPosn, toPosn)


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
