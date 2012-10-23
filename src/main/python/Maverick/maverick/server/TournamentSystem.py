#!/usr/bin/python

################################################################################
# Code written by Matthew Strax-Haber and James Magnarelli. All Rights Reserved.
################################################################################

"""
A chess server that administers games
"""

class ChessGame:
    """
    Represents a chess game in Maverick
    """
    __version = "1.0a1" ## TODO: check to make sure that this matches when un-pickling

    _MOVE_SUCCESS = 34923498
    _MOVE_ILLEGAL = 78996998
    _GAME_PENDING_AWAITING_PLAYERS = 87685854 
    _GAME_ONGOING = 23456342
    _GAME_FINISHED_BLACK_WON = 78739482
    _GAME_FINISHED_WHITE_WON = 14563324
    _GAME_FINISHED_CANCELLED = 14563789
    
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
    
    """The history of the game as a list of plies.  The first element in the list
    is the first ply made. Plies are recorded as tuples of form (moveFrom, moveTo)"""
    ply_history = []
    
    """The current status of the game.  Initially, it is waiting for players."""
    status = _GAME_PENDING_AWAITING_PLAYERS
    
    """A mapping of color to playerID.  When players have registered,
    will look like: {"white": whiteplayerid, "black": blackplayerid}
    """
    color_to_playerID = {"white": None, "black": None}
        
    def getStatus(self):
        """Returns a status code representing the current game state.  Possible
        return values:  GAME_WAITING_FOR_PLAYERS, GAME_IN_PROGRESS, 
        GAME_OVER_BLACK_WON, GAME_OVER_WHITE_WON
        """
        return self.status
        
    def _setStatus(self, status):
        """Sets the status of this game object to the given integer value.
        Should be one of the constant status values defined in this class."""
        self.status=status
    
    def getBlack(self):
        """Returns the PlayerID of the black player. """
        return self.color_to_playerID["black"]
        
    def getWhite(self):
        """Returns the PlayerID of the white player. """
        return self.color_to_playerID["white"]
        
    def getBoard(self):
        """Returns the current board state - an 8x8 2D array of characters."""
        return self.board
        
    def getMoveHistory(self):
        """Returns a list of all plies made in the game."""
        return self.ply_history
        
    def isWhiteTurn(self):
        """Returns true if it is currently the white player's turn, 
        false otherwise."""
        return self.ply_history.count(value)%2 == 0
        
    def makeMove(self, moveFrom, moveTo):
        """Moves the piece at location moveFrom to location moveTo.  Returns
        MOVE_SUCCESS on success, MOVE_ILLEGAL on failure."""
        
        movedPiece = getPiece(moveFrom)
        if (not(self._isValidMove(movedPiece, moveFrom, moveTo))):
            return self.MOVE_ILLEGAL
        else: #actually make the move
            takenPiece = self._pieceTaken(moveTo)
            self._doMove(movedPiece, moveTo, takenPiece)
            self._updateFlags(movedPiece, moveFrom, moveTo, takenPiece)
            #record the move
            self.ply_history.append((moveFrom, moveTo))
            return self.MOVE_SUCCESS
                
        ## TODO: write a make move that modifies the state of the board noticeably


class TournamentSystem:
    
    #the next gameID we'll add to the id_to_game map
    _next_id = 0
    
    #Maps gameIDs to game objects.  Initially empty.
    _id_to_game = {}
    
    def _newGame(self):
        """
        TODO
        
        Creates a new game, without players, and returns its gameID.
        """
        g = ChessGame()
        self._id_to_game += {self._next_id: g}
        self._next_id += 1
        return self._next_id - 1
        
    def joinGame(self, playerID):
        """
        TODO
        
        Joins the player with the given playerID to a game with fewer than 
        2 players.  If there are no such games, this creates one and adds the
        user to it.
        """
        
        for g_id, game in self._id_to_game.iteritems():
            if game.getStatus() == ChessGame._GAME_PENDING_AWAITING_PLAYERS:
                game.addPlayer(playerID)
                return g_id
            
        #If we didn't find any open games, add them to a new one.
        g_id = self._newGame()
        self._id_to_game.get(g_id).addPlayer(playerID)
        return g_id
    
    def _cancelGame(self, gameID):
        """
        Marks the game with the given gameID as canceled.
        
        @postcondition: Future calls to getStatus() for the specified game will return
        ChessGame._GAME_FINISHED_CANCELED
        
        @param gameID: TODO
        """
        try:
            self._id_to_game.get(gameID)._setStatus(ChessGame._GAME_FINISHED_CANCELLED)
        except KeyError:
            print 'Could not find gameID'
    
    ## TODO: Rewrite code above
    ## TODO: Fill in stubs below with logic
    
    def saveGames(self, fileName):
        """
        Pickles the current games' states to a file
        
        @param fileName: The file to save state to
        """
        
    def loadGames(self, fileName):
        """
        Load state from a file
        
        @param fileName: file created using TournamentSystem.saveGames 
        """
    
    def register(self, name):
        """
        Registers a player with the system, returning their playerID.
        
        This should be called before trying to join a player to a game.
        
        @param name: TODO
        
        @return: TODO
        """
        return (-1, {"playerID" : "not yet implemented"})
    
    def playGame(self, playerID):
        """
        TODO
        
        @param playerID: TODO
        
        @return: TODO
        """
        return (-1, {"gameID" : "not yet implemented"})
    
    def getStatus(self, playerID, gameID):
        """
        TODO
        
        @param playerID: TODO
        @param gameID: TODO
        
        @return: TODO
        """
        return (-1, {"status" : "not yet implemented"})
    
    def getState(self, playerID, gameID):
        """
        TODO
        
        @param playerID: TODO
        @param gameID: TODO
        
        @return: TODO
        """
        return (-1,
                { "youAre" : "not yet implemented",
                    "turn" : "not yet implemented",
                    "board" : "not yet implemented", # make this a JSON array
                    "history" : "not yet implemented"
                    } # make this a JSON array -- see spec
                )
        
    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """
        TODO
        
        @param playerID: TODO
        @param gameID: TODO
        @param fromRank: TODO
        @param fromFile: TODO
        @param toRank: TODO
        @param toFile: TODO
        
        @return: TODO
        """
        return (-1, {"result" : "not yet implemented"})
    
    
def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
