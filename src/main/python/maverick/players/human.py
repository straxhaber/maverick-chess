#!/usr/bin/python

"""human.py: A simple chess client for human users to play games"""

__author__ = "James Magnarelli, Matthew Strax-Haber, and Brad Fournier"
__version__ = "1.0"

#import os
#import sys

import time
from ..server import ChessBoard
from ..server import ChessMatch
from ..client import MaverickClient

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################


class HumanClient:
    ## TODO (James): Write comments for class and class methods

    pieceCharMappings = {ChessBoard.ROOK: 'r', ChessBoard.KNGT: 'n',
                         ChessBoard.BISH: 'b', ChessBoard.QUEN: 'q',
                         ChessBoard.KING: 'k', ChessBoard.PAWN: 'p'}

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
        self.state = self.nc.getState(self.playerID, self.gameID)
        self.status = self.nc.getStatus(self.gameID)
        self.myColor = self.state['youAreColor']
        self.amWhite = self.myColor == ChessBoard.WHITE
        if self.myColor == ChessBoard.WHITE:
            self.myWinStatus = ChessMatch.STATUS_WHITE_WON
            colorStr = "white"
        else:
            self.myWinStatus = ChessMatch.STATUS_BLACK_WON
            colorStr = "black"

        print "You are playing as {0}".format(colorStr)

    def getMoveAndMake(self):
        qStr = "It is your move.  Please enter a move of form X1,Y1,X2,Y2: "
        move = raw_input(qStr)
        moveCoords = move.sp(",")

        self.nc.makePly(self.playerID, self.gameID, moveCoords[0],
                        moveCoords[1], moveCoords[2], moveCoords[3])

    def playGame(self):
        # Wait for game to start
        while self.status == ChessMatch.STATUS_PENDING:
            # If pending, sleep and then check status again
            time.sleep(1)
            self.status = self.nc.getStatus(self.gameID)

        # Print the initial state of the board
        self.printBoard()

        # While the game is in progress
        while self.status == ChessMatch.STATUS_ONGOING:
            time.sleep(1)  # Don't poll the server too rapidly

            newState = self.nc.getState(self.playerID, self.gameID)

            # Prompt user for a move if it's their turn
            if newState['isWhitesTurn'] == self.amWhite:
                self.getMoveAndMake()

            # Print board and other info only if changes have occurred
            if newState['isWhitesTurn'] != self.state['isWhitesTurn']:
                self.printBoard()
                self.state = newState

            #Refresh status
            self.status = self.nc.getStatus(self.gameID)

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
        if piece is None:
            return '.'

        pieceColor = piece[0]
        pieceType = piece[1]
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

        for rank in range(0, ChessBoard.BOARD_SIZE):
            # Print rank number
            print "{0}: ".format(rank)
            row = self.state["board"][rank]
            fileStr = ""
            for file in range(0, ChessBoard.BOARD_SIZE):
                piece = row[file]
                fileStr += self.getPieceChar(piece)
            print fileStr + "\n"

        # Print file numbers below board
        for file in range(1, ChessBoard.BOARD_SIZE + 1):
            print file
        print "\n"

        ## TODO (James): space pieces evenly
        ## TODO (James): fix file number printing to be horizontal


def main(host='127.0.0.1', port=7782):
        humanClient = HumanClient(host, port)
        humanClient.getNameAndJoin()
        humanClient.playGame()

if __name__ == '__main__':
    main()


# Untested version of printBoard
## TODO (James): decide whether to use this
#def printBoard(self, gameID):
#    '''
    #TODO: Fix code. Preliminary write by Brad, but I'm sure it is wrong.
    #TODO: Comment.

#    '''

#    self.gameID = gameID
#    for i in range(0, 7):
#        row = '{0}'.format(i)
#        for j in range(0, 7):
#            row += " " + self.ChessBoard[i][j]
#        print row
#    print '1 2 3 4 5 6 7 8'

#    """
#    print ("1" + self.ChessBoard[0] + self.ChessBoard[1] + self.ChessBoard[2] +
#        self.ChessBoard[3] + self.ChessBoard[4] + self.ChessBoard[5] +
#        self.ChessBoard[6] + self.ChessBoard[7] + \n + "2" +
#        self.ChessBoard[8] + self.ChessBoard[9] + self.ChessBoard[10] +
#        self.ChessBoard[11] + self.ChessBoard[12] + self.ChessBoard[13] +
#        self.ChessBoard[14] + self.ChessBoard[15] + \n + "3" +
#        self.ChessBoard[16] + self.ChessBoard[17] + self.ChessBoard[18] +
#        self.ChessBoard[19] + self.ChessBoard[20] + self.ChessBoard[21] +
#        self.ChessBoard[22] + self.ChessBoard[23] + \n + "4" +
#        self.ChessBoard[24] + self.Chessboard[25] + self.ChessBoard[26] +
#        self.ChessBoard[27] + self.ChessBoard[28] + self.ChessBoard[29] +
#        self.ChessBoard[30] + self.ChessBoard[31] + \n + "5" +
#        self.ChessBoard[32] + self.ChessBoard[33] + self.ChessBoard[34] +
#        self.ChessBoard[35] + self.ChessBoard[36] + self.ChessBoard[37] +
#        self.ChessBoard[38] + self.ChessBoard[39] + \n + "6" +
#        self.ChessBoard[40] + self.ChessBoard[41] + self.ChessBoard[42] +
#        self.ChessBoard[43] + self.ChessBoard[44] + self.ChessBoard[45] +
#        self.ChessBoard[46] + self.ChessBoard[47] + \n + "7" +
#        self.ChessBoard[48] + self.ChessBoard[49] + self.ChessBoard[50] +
#        self.ChessBoard[51] + self.ChessBoard[52] + self.ChessBoard[53] +
#        self.ChessBoard[54] + self.ChessBoard[55] + \n + "8" +
#        self.ChessBoard[56] + self.ChessBoard[57] + self.ChessBoard[58] +
#        self.ChessBoard[59] + self.ChessBoard[60] + self.ChessBoard[61] +
#        self.ChessBoard[62] + self.ChessBoard[63] + \n + "1" + "2" + "3" +
#        "4" + "5" + "6" + "7" + "8")
#    """

