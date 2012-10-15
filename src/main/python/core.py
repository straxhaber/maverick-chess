#!/usr/bin/python

import os,sys


class Game:
    """Represents a chess game in Maverick"""

    MOVE_SUCCESS = 34923498
    MOVE_ILLEGAL = 78996998
    GAME_WAITING_FOR_PLAYERS = 87685854 
    GAME_IN_PROGRESS = 23456342
    GAME_OVER_BLACK_WON = 78739482
    GAME_OVER_WHITE_WON = 14563324    
    
    def saveGames(self, fileName):
        """Pickles the current games' states to a file of the given filename."""
        
    def loadGames(self, fileName):
        """Loads state from a file of the given fileName, previously created 
        via the saveGames(fileName) method.
        """
        
    def newGame(self):
        """Creates a new game, without players, and returns its gameID."""
    
    def haltGame(self, gameID):
        """Deletes the game of the given gameID, if it exists."""
    
    def getStatus(self):
        """Returns a status code representing the current game state.  Possible
        return values:  GAME_WAITING_FOR_PLAYERS, GAME_IN_PROGRESS, 
        GAME_OVER_BLACK_WON, GAME_OVER_WHITE_WON
        """
        
    def getBlack(self):
        """Returns the PlayerID of the black player. """
        
    def getWhite(self):
        """Returns the PlayerID of the white player. """
        
    def getBoard(self):
        """Returns the current board state - an 8x8 2D array of characters."""
        
    def getMoveHistory(self):
        """Returns a list of all plies made in the game."""
        
    def isWhiteTurn(self):
        """Returns true if it is currently the white player's turn, false otherwise."""
        
    def makeMove(self, moveFrom, moveTo):
        """Moves the piece at location moveFrom to location moveTo.  Returns
        MOVE_SUCCESS on success, MOVE_ILLEGAL on failure."""


def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
