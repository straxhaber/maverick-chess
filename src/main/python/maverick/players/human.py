#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""
__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.server import ChessBoard
from maverick.server import ChessPosn
from maverick.players.common import MaverickPlayer


class HumanGamer(MaverickPlayer):
    """Represents a human player connecting to the Maverick chess system."""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.human.HumanGamer")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    # TODO (mattsh): put some logging throughout this class

    def __init__(self, host, port):
        """Initialize a human player"""
        MaverickPlayer.__init__(self)

    def _getNextMove(self, board):
        """Ask the player for a move and return it

        @return: a tuple whose first element is the origin ChessPosn and whose
                second element is the destination ChessPosn"""

        # Show the user the board
        self.printBoard()

        haveValidMove = False
        while not haveValidMove:
            qStr = "Please enter move (e.g., \"a1 b3\" to move a1 to b3):  "
            playerMove = raw_input(qStr)

            # TODO (mattsh): get the actual move stuff to work - 0-delimited?

            # Validate move
            if len(playerMove) == 6:
                HumanGamer._logger.debug("Invalid input formatting")
                self.displayMessage("Invalid: too many or too few characters")
            elif playerMove[2] != " ":
                HumanGamer._logger.debug("Invalid input formatting")
                self.displayMessage("Invalid: put a space between coordinates")
            elif (playerMove[0] not in ChessBoard.HUMAN_FILE_LETTERS or
                  playerMove[3] not in ChessBoard.HUMAN_FILE_LETTERS):
                logStr = "Invalid: file not in a to h"
                HumanGamer._logger.debug(logStr)
                self.displayMessage(logStr)
            elif (playerMove[1] not in ChessBoard.HUMAN_RANK_NUMBERS or
                  playerMove[4] not in ChessBoard.HUMAN_RANK_NUMBERS):
                logStr = "Invalid: rank not in 1 to 8"
                HumanGamer._logger.debug(logStr)
                self.displayMessage(logStr)
            else:
                haveValidMove = True

        fromFile = ChessBoard.HUMAN_FILE_LETTERS.index(playerMove[0])
        fromRank = ChessBoard.HUMAN_RANK_NUMBERS.index(playerMove[1])
        toFile = ChessBoard.HUMAN_FILE_LETTERS.index(playerMove[3])
        toRank = ChessBoard.HUMAN_RANK_NUMBERS.index(playerMove[4])

        # Build ChessPosns to return
        fromPosn = ChessPosn(fromRank, fromFile)
        toPosn = ChessPosn(toRank, toFile)

        return (fromPosn, toPosn)

    def _initName(self):
        """Figure out the name of the player"""
        # Get the user's name
        self.name = raw_input("Please enter your name:  ")

    def _welcomePlayer(self):
        """Display welcome messages if appropriate"""
        welStrFArray = ("", "",
                        "Welcome to Maverick Chess. You are playing as {0}.",
                        "Pieces are represented by letters on the board ",
                        "as follows:\n",
                        "PieceType    White    Black",
                        "pawn         X        O",
                        "rook         R        r",
                        "bishop       B        b",
                        "queen        Q        q",
                        "king         K        k",
                        "no piece         .",
                        "", "")
        welcomeStrF = "\n".join(welStrFArray)

        if self.isWhite:
            colorStr = "white"
        else:
            colorStr = "black"

        welcomeStr = welcomeStrF.format(colorStr)
        self.displayMessage(welcomeStr)

    def _handleBadMove(self, errMsg, board, fromPosn, toPosn):
        """Handle a bad move in some smart way"""
        self.displayMessage("Server didn't accept move; please retry.")
        self.displayMessage("Message from server: {0}".format(errMsg))

    def printBoard(self):
        """Print out an ASCII version of the chess board"""
        board = self._request_getState()["board"]
        print
        print(board.__str__(whitePerspective=self.isWhite))
        print


def main(host='127.0.0.1', port=7782):
        p = HumanGamer(host, port)
        p.run()

if __name__ == '__main__':
    main()
