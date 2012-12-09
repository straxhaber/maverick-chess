#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""
__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
import logging

from maverick.data import ChessPosn
from maverick.players.common import MaverickPlayer

__all__ = ["HumanGamer",
           "runHumanClient"]


class HumanGamer(MaverickPlayer):
    """Represents a human player connecting to the Maverick chess system."""

    ## TODO (mattsh): print "Waiting for player" once

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.human.HumanGamer")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    VALID_INPUT_FILE = ["a", "b", "c", "d", "e", "f", "g", "h"]
    """Valid input characters for the file (row) of a position"""

    VALID_INPUT_RANK = ["1", "2", "3", "4", "5", "6", "7", "8"]
    """Valid input characters for the rank (column) of a position"""

    def __init__(self, host=None, port=None):
        """Initialize a human player

        If host or port specified and not None, use them instead of defaults"""
        MaverickPlayer.__init__(self, host=host, port=port)

    def getNextMove(self, board):
        """Ask the player for a move and return it

        @return: a tuple whose first element is the origin ChessPosn and whose
                second element is the destination ChessPosn"""

        # Show the user the board
        self.printBoard()

        haveValidMove = False
        while not haveValidMove:
            qStr = "Please enter move (e.g., \"e2 e4\" to move e2 to e4):  "
            playerMove = raw_input(qStr)

            # Validate move
            if len(playerMove) != 5:
                HumanGamer._logger.debug("Invalid input formatting")
                self.displayMessage("Invalid: too many or too few characters")
            elif playerMove[2] != " ":
                HumanGamer._logger.debug("Invalid input formatting")
                self.displayMessage("Invalid: put a space between coordinates")
            elif (playerMove[0] not in HumanGamer.VALID_INPUT_FILE or
                  playerMove[3] not in HumanGamer.VALID_INPUT_FILE):
                logStr = "Invalid: file not in a to h"
                HumanGamer._logger.debug(logStr)
                self.displayMessage(logStr)
            elif (playerMove[1] not in HumanGamer.VALID_INPUT_RANK or
                  playerMove[4] not in HumanGamer.VALID_INPUT_RANK):
                logStr = "Invalid: rank not in 1 to 8"
                HumanGamer._logger.debug(logStr)
                self.displayMessage(logStr)
            else:
                haveValidMove = True

        fromFile = HumanGamer.VALID_INPUT_FILE.index(playerMove[0])
        fromRank = HumanGamer.VALID_INPUT_RANK.index(playerMove[1])
        toFile = HumanGamer.VALID_INPUT_FILE.index(playerMove[3])
        toRank = HumanGamer.VALID_INPUT_RANK.index(playerMove[4])

        # Build ChessPosns to return
        fromPosn = ChessPosn(fromRank, fromFile)
        toPosn = ChessPosn(toRank, toFile)

        return (fromPosn, toPosn)

    def getPlayerName(self):
        """Figure out the name of the player"""
        return raw_input("Please enter your name:  ")

    def _showPlayerWelcome(self):
        """Display welcome messages if appropriate"""
        welStrFArray = ("", "",
                        "Welcome to Maverick Chess. You are playing as {0}.",
                        "Pieces are represented by letters on the board ",
                        "as follows:\n",
                        "PieceType    White    Black",
                        "pawn         W~       B~",
                        "rook         WR       BR",
                        "bishop       WB       BB",
                        "queen        WQ       BQ",
                        "king         WK       BK",
                        "", "")
        welcomeStrF = "\n".join(welStrFArray)

        if self.isWhite:
            colorStr = "white"
        else:
            colorStr = "black"

        welcomeStr = welcomeStrF.format(colorStr)
        self.displayMessage(welcomeStr)

    def _showPlayerGoodbye(self):
        """Display goodbye message if appropriate"""
        self.printBoard()
        self.displayMessage("Now exiting. Run again to enter a new game.")

    def _showPlayerMove(self, board, fromPosn, toPosn):
        pass  # User doesn't need a repeat of the move they just entered

    def _handleBadMove(self, errMsg, board, fromPosn, toPosn):
        """Handle a bad move in some smart way"""
        self.displayMessage("Server didn't accept move; please retry.")
        logStrF = "Error message from server: {0}".format(errMsg)
        self.displayMessage(logStrF)
        HumanGamer._logger.debug(logStrF)


def runHumanClient(host=None, port=None):
    """Run human client that connects to host:port (None means use default)"""
    p = HumanGamer(host=host, port=port)
    p.run(startFreshP=True)


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host", default=None, type=str,
                        help="specify hostname of Maverick server")
    parser.add_argument("--port", default=None, type=int,
                        help="specify port of Maverick server")
    args = parser.parse_args()
    runHumanClient(host=args.host, port=args.port)

if __name__ == '__main__':
    main()
