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

    def __init__(self, host, port):
        self.nc = MaverickClient(host, port)

    def getNameAndJoin(self):
        #  Get the user's name and register them
        self.name = raw_input("Please enter your name: ")
        self.playerID = self.nc.register(self.name)

        # Actually join a game
        self.gameID = self.nc.joinGame(playerID)
        print("You have joined game {0}".format(self.gameID))

        # Figure out what color player we are
        self.state = self.nc.getState(gameID)
        self.status = self.nc.getStatus(playerID, gameID)
        self.myColor = status['youAreColor']
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
        
    def printBoard(self, gameID):
        '''
        #TODO: Fix code. Preliminary write by Brad, but I'm sure it is wrong.
        #TODO: Comment.
    
        '''
    
        self.gameID = gameID
        print "1" + self.ChessBoard[0] + self.ChessBoard[1] + self.ChessBoard[2] +
            self.ChessBoard[3] + self.ChessBoard[4] + self.ChessBoard[5] +
            self.ChessBoard[6] + self.ChessBoard[7] + \n + "2" +
            self.ChessBoard[8] + self.ChessBoard[9] + self.ChessBoard[10] +
            self.ChessBoard[11] + self.ChessBoard[12] + self.ChessBoard[13] +
            self.ChessBoard[14] + self.ChessBoard[15] + \n + "3" +
            self.ChessBoard[16] + self.ChessBoard[17] + self.ChessBoard[18] +
            self.ChessBoard[19] + self.ChessBoard[20] + self.ChessBoard[21] +
            self.ChessBoard[22] + self.ChessBoard[23] + \n + "4" +
            self.ChessBoard[24] + self.Chessboard[25] + self.ChessBoard[26] +
            self.ChessBoard[27] + self.ChessBoard[28] + self.ChessBoard[29] +
            self.ChessBoard[30] + self.ChessBoard[31] + \n + "5" +
            self.ChessBoard[32] + self.ChessBoard[33] + self.ChessBoard[34] +
            self.ChessBoard[35] + self.ChessBoard[36] + self.ChessBoard[37] +
            self.ChessBoard[38] + self.ChessBoard[39] + \n + "6" +
            self.ChessBoard[40] + self.ChessBoard[41] + self.ChessBoard[42] +
            self.ChessBoard[43] + self.ChessBoard[44] + self.ChessBoard[45] +
            self.ChessBoard[46] + self.ChessBoard[47] + \n + "7" +
            self.ChessBoard[48] + self.ChessBoard[49] + self.ChessBoard[50] +
            self.ChessBoard[51] + self.ChessBoard[52] + self.ChessBoard[53] +
            self.ChessBoard[54] + self.ChessBoard[55] + \n + "8" +
            self.ChessBoard[56] + self.ChessBoard[57] + self.ChessBoard[58] +
            self.ChessBoard[59] + self.ChessBoard[60] + self.ChessBoard[61] +
            self.ChessBoard[62] + self.ChessBoard[63] + \n + "1" + "2" + "3" +
            "4" + "5" + "6" + "7" + "8"


def main(self, host='127.0.0.1', port=server.DEFAULT_MAVERICK_PORT):
        humanClient = HumanClient(host, port)
        humanClient.getNameAndJoin()
        humanClient.playGame()

if __name__ == '__main__':
    main()

    
