#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""
from maverick.client import MaverickClientException

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.server import ChessBoard
from maverick.players.common import MaverickPlayer


class HumanGamer(MaverickPlayer):
    """Represents a human player connecting to the Maverick chess system."""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.human.HumanGamer")
    logging.basicConfig(level=logging.INFO)

    # TODO (mattsh): put some logging throughout this class

    def __init__(self, host, port):
        """Initialize a human player"""
        MaverickPlayer.__init__(self)

    def getNextMove(self, board):
        """Ask the player for a move and make it"""

        # Show the user the board
        self.printBoard()

        haveValidMove = False
        while not haveValidMove:
            qStr = "Please enter move (e.g., \"a1 b3\" to move a1 to b3):  "
            playerMove = raw_input(qStr)

            # TODO (mattsh): get the actual move stuff to work - 0-delimited?

            # Validate move
            if len(playerMove) == 6:
                self.displayMessage("Invalid: too many or too few characters")
            elif playerMove[2] != " ":
                self.displayMessage("Invalid: put a space between coordinates")
            elif (playerMove[0] not in ChessBoard.HUMAN_FILE_LETTERS or
                  playerMove[3] not in ChessBoard.HUMAN_FILE_LETTERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            elif (playerMove[1] not in ChessBoard.HUMAN_RANK_NUMBERS or
                  playerMove[4] not in ChessBoard.HUMAN_RANK_NUMBERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            else:
                haveValidMove = True

        fromFile = ChessBoard.HUMAN_FILE_LETTERS.index(playerMove[0])
        fromRank = ChessBoard.HUMAN_RANK_NUMBERS.index(playerMove[1])
        toFile = ChessBoard.HUMAN_FILE_LETTERS.index(playerMove[3])
        toRank = ChessBoard.HUMAN_RANK_NUMBERS.index(playerMove[4])

        return (fromRank, fromFile, toRank, toFile)

    def initName(self):
        """Figure out the name of the class"""
        # Get the user's name
        self.name = raw_input("Please enter your name:  ")

    def welcomePlayer(self):
        """Display welcome messages if appropriate"""
        welcomeStrF = ("Welcome to Maverick Chess. You are playing as {0}. "
                       "Pieces are represented by letters on the board "
                        "as follows:\n"
                        "P = pawn\n"
                        "R = rook\n"
                        "N = knight\n"
                        "B = bishop\n"
                        "Q = queen\n"
                        "K = king\n"
                        ". = no piece\n\n"

                        "Upper-case letters are white pieces, and lower-case "
                        "letters are black pieces.  Have fun. \n\n")

        if self.isWhite:
            colorStr = "white"
        else:
            colorStr = "black"

        welcomeStr = welcomeStrF.format(colorStr)
        self.displayMessage(welcomeStr)

    def handleBadMove(self, errMsg, board, fromRank, fromFile, toRank, toFile):
        """Calculate the next move based on the provided board"""
        self.displayMessage("Server didn't accept move; please retry.")
        self.displayMessage("Message from server: {0}".format(errMsg))

    def printBoard(self):
        """Print out an ASCII version of the chess board"""
        board = self.request_getState()["board"]  # TODO: currently just a list
        boardText = board.__str__()
        print(boardText)


def main(host='127.0.0.1', port=7782):
        p = HumanGamer(host, port)
        p.run()

if __name__ == '__main__':
    main()
