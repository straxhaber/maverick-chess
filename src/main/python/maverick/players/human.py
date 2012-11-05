#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

#import os
#import sys

import logging
import time

from maverick.server import ChessBoard
from maverick.server import ChessMatch
from maverick.players.common import MaverickPlayer

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

# TODO (mattsh): Properly catch and deal with exceptions


class HumanGamer(MaverickPlayer):
    """TODO write a comment"""
    ## TODO (James): Write comments for class and class methods

    FILE_LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h"]
    """Ordered listing of valid files"""

    RANK_NUMBERS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    """Ordered listing of valid ranks"""

    PIECE_TEXTUAL_REPR = {ChessBoard.ROOK: {ChessBoard.WHITE: 'R',
                                            ChessBoard.BLACK: 'r'},
                          ChessBoard.KNGT: {ChessBoard.WHITE: 'N',
                                            ChessBoard.BLACK: 'n'},
                          ChessBoard.BISH: {ChessBoard.WHITE: 'B',
                                            ChessBoard.BLACK: 'b'},
                          ChessBoard.QUEN: {ChessBoard.WHITE: 'Q',
                                            ChessBoard.BLACK: 'q'},
                          ChessBoard.KING: {ChessBoard.WHITE: 'K',
                                            ChessBoard.BLACK: 'k'},
                          ChessBoard.PAWN: {ChessBoard.WHITE: 'P',
                                            ChessBoard.BLACK: 'p'}}
    """Mapping of piece constants to their visual represenataion"""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    def __init__(self, host, port):
        """Initialize a human player"""
        MaverickPlayer.__init__(self)

    def playerMakeMove(self):
        """Ask the player for a move and make it"""

        # Show the user the board
        self.printBoard()

        haveValidMove = False
        while not haveValidMove:
            qStr = "Please enter move (e.g., \"a1 b3\" to move a1 to b3):"
            playerMove = raw_input(qStr)

            # TODO (mattsh): get the actual move stuff to work Ñ 0-delimited?

            # Validate move
            if len(playerMove) == 6:
                self.displayMessage("Invalid: too many or too few characters")
            elif playerMove[2] != " ":
                self.displayMessage("Invalid: put a space between coordinates")
            elif (playerMove[0] not in HumanGamer.FILE_LETTERS or
                  playerMove[3] not in HumanGamer.FILE_LETTERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            elif (playerMove[1] not in HumanGamer.RANK_NUMBERS or
                  playerMove[4] not in HumanGamer.RANK_NUMBERS):
                self.displayMessage("Invalid: rank not in 1 to 8")
            else:
                haveValidMove = True

        fromFile = HumanGamer.FILE_LETTERS.index(playerMove[0])
        fromRank = HumanGamer.RANK_NUMBERS.index(playerMove[1])
        toFile = HumanGamer.FILE_LETTERS.index(playerMove[3])
        toRank = HumanGamer.RANK_NUMBERS.index(playerMove[4])

        self.makePly(fromFile, fromRank, toFile, toRank)

    def run(self):
        """TODO write a comment"""

        #  Get the user's name and get into a game
        self.name = raw_input("Please enter your name: ")
        self.startPlaying()

        # TODO: welcome text

        # Print the initial state of the board
#        self.printBoard()  #TODO remove this

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

    def getPieceChar(self, piece):
        """TODO write a comment"""
        if piece is None:
            return '.'
        else:
            (c, p) = piece
            return HumanGamer.PIECE_TEXTUAL_REPR[p][c]

    def printBoard(self):
        """Print out an ASCII version of the chess board"""

        board = self.getState()["board"]

        self.displayMessage("  {0}  ".format(" ".join(self.FILE_LETTERS)))
        for rankNum in range(ChessBoard.BOARD_SIZE):
            rank = board[rankNum]
            rankStr = " ".join([self.getPieceChar(c) for c in rank])
            self.displayMessage("{0} {1} {0}".format(rankNum + 1, rankStr))
        self.displayMessage("  {0}  ".format(" ".join(self.FILE_LETTERS)))


def main(host='127.0.0.1', port=7782):
        p = HumanGamer(host, port)
        p.run()

#def main():
#    print "This class should not be run directly"

if __name__ == '__main__':
    main()
