#!/usr/bin/python

"""common.py: Common code for gameplay interfaces"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging
import time

from maverick.client import MaverickClient
from maverick.client import MaverickClientException

from maverick.data.structs import ChessBoard
from maverick.data.structs import ChessMatch

__all__ = ["MaverickPlayer"]

# TODO (mattsh): put more logging throughout this class


class MaverickPlayer(MaverickClient):
    """Provides basic methods for a Maverick AI"""
    # TODO (mattsh): Show board one last time at game's end

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.common.MaverickPlayer")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    SLEEP_TIME = 0.1
    """Amount of time to wait between requests when polling"""

    def __init__(self, host=None, port=None):
        """Initialize a MaverickPlayer

        If host or port specified and not None, use them instead of defaults

        NOTE: MaverickPlayer.startPlaying must be run to set playerID, gameID,
        and isWhite before the player can make moves"""

        MaverickClient.__init__(self, host=host, port=port)

        # These variables must be overridden
        self.playerID = None    # ID for player's system registration
        self.gameID = None      # ID for game that the player is in
        self.isWhite = None     # Is the player white?

    def getPlayerName(self):
        """Figure out the name of the class"""
        raise NotImplementedError("Must be overridden by the extending class")

    def getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _showPlayerWelcome(self):
        """Display welcome messages if appropriate"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _showPlayerGoodbye(self):
        """Display goodbye messages if appropriate"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _handleBadMove(self):
        """Handle a bad move in some smart way"""
        raise NotImplementedError("Must be overridden by the extending class")

    def _showPlayerMove(self, board, fromPosn, toPosn):
        """Override to modify display of players' moves / associated boards"""

        self.printBoard()
        print("can castle flags: {}".format(board.flag_canCastle))
        print("en passant flags: {}".format(board.flag_enpassant))
        self.displayMessage("Moving {} to {}".format(fromPosn, toPosn))

    def displayMessage(self, message):
        """Display a message for the user"""
        print(" -- {0}".format(message))

    def printBoard(self):
        """Print out an ASCII version of the chess board"""
        board = self._request_getState()["board"]
        print
        print(board.__str__(whitePerspective=self.isWhite))
        print

    def startPlaying(self, startFreshP):
        """Enters the player into an ongoing game (blocks until successful)

        @precondition: self.name must be set"""
        self.playerID = self._request_register(self.name)
        self.gameID = self._request_joinGame(self.playerID, startFreshP)

        # Block until game has started
        gameStartWaitMessageDisplayedP = False
        while self._request_getStatus() == ChessMatch.STATUS_PENDING:
            if not gameStartWaitMessageDisplayedP:
                self.displayMessage("Waiting until the game starts")
                gameStartWaitMessageDisplayedP = True
            time.sleep(MaverickPlayer.SLEEP_TIME)

        # NOTE: Player is now in a game that is not pending

        self.isWhite = (self._request_getState()["youAreColor"] ==
                        ChessBoard.WHITE)

    def run(self, startFreshP):
        """Registers user, connects to game, and starts gameplay loop"""
        self.name = self.getPlayerName()
        self.startPlaying(startFreshP)
        self._showPlayerWelcome()

        # While the game is in progress
        while self._request_getStatus() == ChessMatch.STATUS_ONGOING:

            # Don't want to print the message many times (keep track of this)
            waitMessagePrintedP = False

            # Wait until it is your turn
            while not self._request_isMyTurn():
                if not waitMessagePrintedP:
                    self.displayMessage("Waiting until turn")
                    waitMessagePrintedP = True
                time.sleep(MaverickPlayer.SLEEP_TIME)

                # Break if the game was stopped while sleeping
                if self._request_getStatus() != ChessMatch.STATUS_ONGOING:
                    break

            else:  # It is now our turn (wrapped in else in case of break)
                board = self._request_getState()["board"]
                (fromPosn, toPosn) = self.getNextMove(board)

                self._showPlayerMove(board, fromPosn, toPosn)

                try:
                    self._request_makePly(fromPosn, toPosn)
                except MaverickClientException, e:
                    self._handleBadMove(e.message, board, fromPosn, toPosn)

        # When this is reached, game is over
        status = self._request_getStatus()
        if status == ChessMatch.STATUS_WHITE_WON:
            stat = "won" if self.isWhite else "lost"
            self.displayMessage("GAME OVER - WHITE WON (you {0})".format(stat))
        elif status == ChessMatch.STATUS_BLACK_WON:
            stat = "lost" if self.isWhite else "won"
            self.displayMessage("GAME OVER - BLACK WON (you {0})".format(stat))
        elif status == ChessMatch.STATUS_DRAWN:
            self.displayMessage("GAME OVER - DRAWN")
        elif status == ChessMatch.STATUS_CANCELLED:
            self.displayMessage("GAME OVER CANCELLED")
        else:
            self.displayMessage("ERROR: UNEXPECTED GAME STATUS TRANSITION")

        self._showPlayerGoodbye()

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
