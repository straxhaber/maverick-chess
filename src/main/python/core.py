#!/usr/bin/python

import os,sys


class Game:
    """Represents a chess game in Maverick"""
    __version = "1.0a1" ## TODO: check to make sure that this matches when un-pickling

    _MOVE_SUCCESS = 34923498
    _LMOVE_ILLEGAL = 78996998
    _GAME_WAITING_FOR_PLAYERS = 87685854 
    _GAME_IN_PROGRESS = 23456342
    _GAME_OVER_BLACK_WON = 78739482
    _GAME_OVER_WHITE_WON = 14563324
    _GAME_CANCELLED = 14563789
    
    _P_EMPTY_SPACE ="."
    _P_BLACK_PAWN ="p"
    _P_BLACK_ROOK ="r"
    _P_BLACK_KNIGHT ="n"
    _P_BLACK_BISHOP ="b"
    _P_BLACK_QUEEN ="q"
    _P_BLACK_KING ="k"
    _P_WHITE_PAWN ="P"
    _P_WHITE_ROOK ="R"
    _P_WHITE_KNIGHT ="N"
    _P_WHITE_BISHOP ="B"
    _P_WHITE_QUEEN ="Q"
    _P_WHITE_KING ="K"
    #The width and height of a standard chess board.  Probably won't change.
    _BOARD_WIDTH = 8
    
    
    """The initial state of the board.
    NOTE:  THIS IS INCONSISTENT WITH THE ORDERING IN ALGEBRAIC CHESS NOTATION.
    Explanation:  Traditionally, the starting position of the white king
    might be represented with a string like "d1", meaning column d row 1.
    One might think of representing this in a 2-D array at location [4][1]  
    HOWEVER, our representation is indexed as follows: [row][column],
    SO THE POSITION "d1" IS REPRESENTED IN THE board ARRAY AT [1][4].
     
    The start state corresponds roughly to this:
        [    ['R','N','B','Q','K','B','N','R'],
             ['P','P','P','P','P','P','P','P'],       
             ['.','.','.','.','.','.','.','.'],       
             ['.','.','.','.','.','.','.','.'],       
             ['.','.','.','.','.','.','.','.'],       
             ['.','.','.','.','.','.','.','.'],       
             ['p','p','p','p','p','p','p','p'],
             ['r','n','b','q','k','b','n','r']]
    """
    _initial_board = []
    #Remember, the board is [row][column].  
    #tack on the first row of pieces (white bishop at c1 should be at [0][2]
    _initial_board.append([_P_WHITE_ROOK, _P_WHITE_KNIGHT, _P_WHITE_BISHOP,
                       _P_WHITE_QUEEN, _P_WHITE_KING, _P_WHITE_BISHOP, 
                       _P_WHITE_KNIGHT, _P_WHITE_ROOK])
    _initial_board.append([_P_WHITE_PAWN for x in range(_BOARD_WIDTH)])
    _initial_board += [[_P_EMPTY_SPACE] * 8] * 4
    _initial_board.append([_P_BLACK_PAWN for x in range(_BOARD_WIDTH)])
    _initial_board.append([_P_BLACK_ROOK, _P_BLACK_KNIGHT, _P_BLACK_BISHOP,
                       _P_BLACK_QUEEN, _P_BLACK_KING, _P_BLACK_BISHOP, 
                       _P_BLACK_KNIGHT, _P_BLACK_ROOK])
    
    """The current state of the board.  Initialized to _initial_board.
    Remember, the board is [row][column]."""
    board = _initial_board
    
    """The current status of the game.  Initially, it is waiting for players."""
    status = _GAME_WAITING_FOR_PLAYERS
    
    """A mapping of color to playerID.  When players have registered,
    will look like: {"white": whiteplayerid, "black": blackplayerid}
    """
    color_to_playerID = {"white": None, "black": None}
        
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
        """Returns true if it is currently the white player's turn, 
        false otherwise."""
        
    def makeMove(self, moveFrom, moveTo):
        """Moves the piece at location moveFrom to location moveTo.  Returns
        MOVE_SUCCESS on success, MOVE_ILLEGAL on failure."""
        
        ## TODO: write a make move that modifies the state of the board noticeably


class TournamentSystem:
    
    #the next gameID we'll add to the id_to_game map
    _next_id = 0
    
    #Maps gameIDs to game objects.  Initially empty
    _id_to_game = {}
    
    
    def saveGames(self, fileName):
        """Pickles the current games' states to a file of the given filename."""
        
    def loadGames(self, fileName):
        """Loads state from a file of the given fileName, previously created 
        via the saveGames(fileName) method.
        """
        
    def newGame(self):
        """Creates a new game, without players, and returns its gameID."""
        g = Game()
        _id_to_game += {_next_id: g}
        _next_id += 1
    
    def haltGame(self, gameID):
        """Deletes the game of the given gameID, if it exists."""
        try:
            _id_to_game.pop(gameID)
        except KeyError:
            print 'Could not find gameID'
        
    
def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
