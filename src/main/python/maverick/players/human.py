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
import time

from maverick.server import ChessMatch
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

    def playerMakeMove(self):
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
            elif (playerMove[0] not in HumanGamer.HUMAN_FILE_LETTERS or
                  playerMove[3] not in HumanGamer.HUMAN_FILE_LETTERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            elif (playerMove[1] not in HumanGamer.HUMAN_RANK_NUMBERS or
                  playerMove[4] not in HumanGamer.HUMAN_RANK_NUMBERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            else:
                haveValidMove = True

        fromFile = HumanGamer.HUMAN_FILE_LETTERS.index(playerMove[0])
        fromRank = HumanGamer.HUMAN_RANK_NUMBERS.index(playerMove[1])
        toFile = HumanGamer.HUMAN_FILE_LETTERS.index(playerMove[3])
        toRank = HumanGamer.HUMAN_RANK_NUMBERS.index(playerMove[4])

        try:
            self.makePly(fromFile, fromRank, toFile, toRank)
        except MaverickClientException, msg:
            self.displayMessage("Server did not accept move - please retry.")
            self.displayMessage("Message from server: {0}".format(msg))

    def run(self):
        """Interact with the player, showing them the board and prompting them
        for moves on their turn"""

        #  Get the user's name and get into a game
        self.name = raw_input("Please enter your name:  ")
        self.startPlaying()

        # Display a welcome message to the player
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

        # While the game is in progress
        while self.getStatus() == ChessMatch.STATUS_ONGOING:

            # Wait until it is your turn
            while self.getState()['isWhitesTurn'] != self.isWhite:
                self.displayMessage("Waiting until it is your turn")

                # Break if a game is stopped while waiting
                if self.getStatus() != ChessMatch.STATUS_ONGOING:
                    break

                time.sleep(MaverickPlayer.SLEEP_TIME)

            # Have the player make a move
            self.playerMakeMove()

        # When this is reached, game is over
        status = self.getStatus()
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

    def printBoard(self):
        """Print out an ASCII version of the chess board"""
        board = self.getState()["board"]  # TODO: currently just a list
        boardText = board.__str__()
        self.displayMessage(boardText)


def main(host='127.0.0.1', port=7782):
        p = HumanGamer(host, port)
        p.run()

if __name__ == '__main__':
    main()
