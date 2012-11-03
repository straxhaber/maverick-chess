#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

#import os
#import sys

from ..client import MaverickClient

from ..server import ChessBoard
from ..server import ChessMatch

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################


class HumanClient:
    ## TODO (James): Write comments for class and class methods

    pieceCharMappings = {ChessBoard.ROOK: 'r', ChessBoard.KNGT: 'n',
                         ChessBoard.BISH: 'b', ChessBoard.QUEN: 'q',
                         ChessBoard.KING: 'k'}

    def __init__(self, host, port):
        self.nc = MaverickClient(host, port)

    def getNameAndJoin(self):
        #  Get the user's name and register them
        self.name = raw_input("Please enter your name: ")
        self.playerID = self.nc.register(self.name)

        # Actually join a game
        self.gameID = self.nc.joinGame(self.playerID)
        print("You have joined game {0}".format(self.gameID))

        # Figure out what color player we are
        self.state = self.nc.getState(self.gameID)
        self.status = self.nc.getStatus(self.playerID, self.gameID)
        self.myColor = self.status['youAreColor']
        self.amWhite = self.myColor == ChessBoard.WHITE
        if self.myColor == ChessBoard.WHITE:
            self.myWinStatus = ChessMatch.STATUS_WHITE_WON
        else:
            self.myWinStatus = ChessMatch.STATUS_BLACK_WON

    def playGame(self):
        # Wait for game to start
        while self.status == ChessMatch.STATUS_PENDING:
            # If pending, sleep and then check status again
            sleep(1)
            self.status = self.nc.getStatus(self.playerID, self.gameID)

        # While the game is in progress
        while self.status == ChessMatch.STATUS_ONGOING:
            sleep(1)  # Don't poll the server too rapidly

            newState = self.nc.getState(self.playerID, self.gameID)

            # Prompt user for a move if it's their turn
            if newState['isWhitesTurn'] == self.amWhite:
                self.getMoveAndMake()

            # Print board and other info only if changes have occurred
            if newState['isWhitesTurn'] != self.state['isWhitesTurn']:
                self.printBoard()
                self.state = newState

            #Refresh status
            self.status = self.nc.getStatus(self.playerID, self.gameID)

        # When this is reached, game is over
        endGameStr = "GAME OVER - {0}"
        if self.status == ChessMatch.STATUS_WHITE_WON:
            endGameStr.format("WHITE WON")
        elif self.status == ChessMatch.STATUS_BLACK_WON:
            endGameStr.format("BLACK WON")
        elif self.status == ChessMatch.STATUS_DRAWN:
            endGameStr.format("DRAWN")
        else:
            endGameStr.format("GAME CANCELLED")

        print endGameStr

    def getPieceChar(self, piece):
        pieceType = piece[0]
        pieceColor = piece[1]
        pieceChar = HumanClient.pieceCharMappings[pieceType]

        # Capitalize character if piece is white
        if pieceColor == ChessBoard.WHITE:
            pieceChar = pieceChar.upper()
        else:
            pieceChar = pieceChar.lower()

        return pieceChar

    def printBoard(self):
        """
        #TODO: Fix code. Preliminary write by Brad, but I'm sure it is wrong.
        #TODO: Comment.

        """
        fileOrdinal = ord('A')

        for rank in range(1, ChessBoard.BOARD_SIZE + 1):
            # Print rank number
            print "{0}: ".format(rank)
            row = self.board[rank]
            for file in range(1, ChessBoard.BOARD_SIZE + 1):
                piece = row[file]
                print self.getPieceChar(piece)
            print "\n"

        # Print file numbers below board
        for file in range(1, ChessBoard.BOARD_SIZE + 1):
            print file
        print "\n"


def main(self, host='127.0.0.1', port=7782):
        humanClient = HumanClient(host, port)
        humanClient.getNameAndJoin()
        humanClient.playGame()

if __name__ == '__main__':
    main()

    
