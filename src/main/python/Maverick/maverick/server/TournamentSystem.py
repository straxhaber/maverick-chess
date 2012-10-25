#!/usr/bin/python

"""TournamentSystem.py: A chess server that administers games"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"
__status__ = "Development"
__maintainer__ = "Matthew Strax-Haber and James Magnarelli"

import pickle, random

###############################################################################
# Code written by Matthew Strax-Haber & James Magnarelli. All Rights Reserved.
###############################################################################


class ChessBoard:
    """Represents a chess game in Maverick"""

    # Constants for the pieces
    PAWN = "P"
    ROOK = "R"
    KNGT = "N"
    BISH = "B"
    QUEN = "Q"
    KING = "K"

    # The width and height of a standard chess board.  Probably won't change.
    BOARD_SIZE = 8

    def __init__(self):
        """Initialize a new Chess game according to normal Chess rules

        NOTE: Board is represented as a list of rows; be careful dereferencing
            i.e., "d1" is self.board[1][4]

        The start state corresponds roughly to this:
            [['R','N','B','Q','K','B','N','R'],
             ['P','P','P','P','P','P','P','P'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['p','p','p','p','p','p','p','p'],
             ['r','n','b','q','k','b','n','r']]
             
        There are special states that must be kept track of:
            - En passant
            - Castling
        """
        
        # Initialize board to the basic chess starting position
        # NOTE: the board is referenced as self.board[row][column].
        self.board = []
        self.board.append([
                (ChessMatch.WHITE, ChessBoard.ROOK),
                (ChessMatch.WHITE, ChessBoard.KNGT),
                (ChessMatch.WHITE, ChessBoard.BISH),
                (ChessMatch.WHITE, ChessBoard.QUEN),
                (ChessMatch.WHITE, ChessBoard.KING),
                (ChessMatch.WHITE, ChessBoard.BISH),
                (ChessMatch.WHITE, ChessBoard.KNGT),
                (ChessMatch.WHITE, ChessBoard.ROOK)])
        self.board += [(ChessMatch.WHITE, ChessBoard.PAWN)] * 8
        self.board += [[None] * 8] * 4
        self.board += [(ChessMatch.BLACK, ChessBoard.PAWN)] * 8
        self.board.append([
                (ChessMatch.BLACK, ChessBoard.ROOK),
                (ChessMatch.BLACK, ChessBoard.KNGT),
                (ChessMatch.BLACK, ChessBoard.BISH),
                (ChessMatch.BLACK, ChessBoard.QUEN),
                (ChessMatch.BLACK, ChessBoard.KING),
                (ChessMatch.BLACK, ChessBoard.BISH),
                (ChessMatch.BLACK, ChessBoard.KNGT),
                (ChessMatch.BLACK, ChessBoard.ROOK)])

        # Initialize en passant flags (True means en passant capture is
        # possible in the given column
        self.flag_enpassant = {
            ChessMatch.WHITE: [False] * ChessBoard.BOARD_SIZE,
            ChessMatch.BLACK: [False] * ChessBoard.BOARD_SIZE}
        
        # Initialize castle flags (queen-side ability, king-side ability)
        # Does not account for pieces blocking or checking the castle
        self.flag_canCastle = {
            ChessMatch.WHITE: (True, True),
            ChessMatch.BLACK: (True, True)}
    
    def makePly(self, color, fromRank, fromFile, toRank, toFile):
        """Makes a move if legal
        
        @param color: the color making the move (BLACK or WHITE constant)
        @param fromRank: the rank from which piece is moving (integer in [0,7])
        @param fromFile: the file from which piece is moving (integer in [0,7])
        @param toRank: the rank to which piece is moving (integer in [0,7])
        @param toFile: the file to which piece is moving (integer in [0,7])
        
        @return: True if the move was successful, false otherwise
        
        - Check if the move is legal
        - Remove the moving piece from the starting position
        - Update flags if necessary
        - Add the moving piece to the ending position (possibly overwriting)
        - Delete pawns in en passant state if relevant
        
        @todo: write the code for this method"""
        
        # Remove moving piece from starting position
        movedPiece = self.board[fromRank][fromFile]
        self.board[fromRank][fromFile] = None
        
        ## TODO: update flags
        # Reset en passant flags to false
        self.flag_enpassant[color] = False * ChessBoard.BOARD_SIZE
        
        # Update castle flags
        prevCastleFlag = self.canCastle[color]
        if movedPiece == self.KING:
            self.flag_canCastle[color] = (False, False)
        if movedPiece == self.ROOK:
            if fromFile == 0: # Queen-side rook was moved
                self.flag_canCastle[color] = (False, prevCastleFlag[1])
            elif fromFile == 7: # King-side rook was moved
                self.flag_canCastle[color] = (prevCastleFlag[0], False)
                
        # If we've moved a pawn for the first time, set the en passant flags
        if (movedPiece == self.PAWN and 
            fromRank == {ChessMatch.White: 1, ChessMatch.Black: 6}[color] and
            abs(toRank - fromRank) == 2):
            self.flag_enpassant[color][fromFile] = True             
        
        # Move piece to destination
        self.board[toRank][toFile] = movedPiece
        
        # Remove en passant pawns, if relevant
        if self.flag_enpassant[color][toFile] == True:
            if (color == ChessMatch.White and 
                toRank == ChessBoard.BOARD_SIZE - 2): 
                # We should take a black pawn via en passant
                self.board[ChessBoard.BOARD_SIZE - 2][toFile] = None
            elif (color == ChessMatch.Black and toRank == 1):
                # We should take a white pawn via en passant
                self.board[2][toFile] = None
                
        return True
        
    def legalMoveP(self, color, fromRank, fromFile, toRank, toFile):
        """Returns true if the specified move is legal
        
        Arguments are the same as makePly
        
        Checks if:
         - There is a piece at the from position
         - The to position doesn't contain a piece owned by the color
         - The path to make the move is free (for bishops, rooks, queens, etc.)
         - Flags don't preclude the move (i.e., castling)
        
        @todo: write the code for this class"""
        
        return False ## FIXME
    
class ChessMatch:
    # Constants for game status
    STATUS_PENDING   = "PENDING"   # Game is waiting for players
    STATUS_ONGOING   = "ONGOING"   # Game is in progress
    STATUS_BLACK_WON = "W_BLACK"   # Black won the game
    STATUS_WHITE_WON = "W_WHITE"   # White won the game
    STATUS_DRAWN     = "W_DRAWN"   # White won the game
    STATUS_CANCELLED = "CANCELD"   # Game was halted early
    
    # Constants for the players
    BLACK = "X"
    WHITE = "O"
    
    def __init__(self, firstPlayerID=None):
        """Initialize a new chess match with initial state
        
        @param firstPlayerID: if set, randomly assigned to black or white"""
        
        # Initialize with a new chess board
        self.board = ChessBoard()
        
        # Initialize match without players (whose playerIDs can be added later)
        self.players = { ChessMatch.WHITE : None, ChessMatch.BLACK : None}
        
        # Randomly set black or white to firstPlayerID (no-op if not specified)
        self.players[random.choice(self.players.keys())] = firstPlayerID
    
        # Initialize match status
        self.status = ChessMatch.STATUS_PENDING
        
        # Initialize ply history -- a list of (moveFrom, moveTo) plies
        self.history = []
        
    def whoseTurn(self):
        """Returns True if it is whites turn, False otherwise"""
        return len(self.ply_history) % 2 == 0
    
    def makePly(self, player, fromRank, fromFile, toRank, toFile):
        """Makes a move if legal
        
        @return: "SUCCESS" if move was successful, error message otherwise"""
        if self.status == ChessMatch.STATUS_ONGOING:
            # TODO: Check if a player
            # TODO: Translate playerID to color
            
            color = None
            
            if self.legalMoveP(color, fromRank, fromFile, toRank, toFile):
                self.board.makePly(color, fromRank, fromFile, toRank, toFile)
                self.history.append(((fromRank, fromFile),(toRank, toFile)))
                return "SUCCESS"
            else:
                return "Illegal move"
        else:
            return "Game not in progress"
    
    def join(self, playerID):
        """Joins the match in an empty slot. If ready, game starts.
        
        @param playerID: ID of the player being added
        @return: color constant if successful, None otherwise"""
        
        if self.status != ChessMatch.STATUS_PENDING:
            return # Can only join a pending game (no mid-game replacements)
        
        if playerID in self.players.values():
            return # Don't allow a player to play both sides
        
        for color in [ChessMatch.WHITE, ChessMatch.BLACK]:
            if self.players[color] == None:
                self.players[color] = playerID
                if None not in self.players.values():
                    self.status = ChessMatch.STATUS_ONGOING
                return color

class TournamentSystem:
    
    def __init__(self):
        """Initializes a new tournament system with no games"""
        self.games = {} # Dict from gameIDs to game objects. Initially empty.
        self.players = {} # Dict from playerID to player name
        self._version = __version__ # Used in version check during un-pickling

    @staticmethod
    def saveTS(tournament, fileName):
        """Pickles the current games' states to a file

        @param fileName: The file to save state to"""
        fd = open(fileName)
        pickle.dump(tournament, fd)
        
    @staticmethod
    def loadTS(tournament, fileName):
        """Load state from a file

        @param fileName: file created using TournamentSystem.saveGames
        @todo: check to make sure that the pickled data is the same version"""
        fd = open(fileName)
        tournament = pickle.load(fd)
        
        if (tournament._version != __version__):
            raise TypeError("Attempted loading of an incompatible version")
        
        return tournament
    
    def register(self, name):
        """Registers a player with the system, returning their playerID.
        
        This should be called before trying to join a player to a game.
        
        @param name: TODO
        
        @return: TODO"""
        if name in self.players.values():
            return (False, {"error" : "player with this name already exists"})
        else:
            newID = _getUniqueInt(self.players.keys())
            self.players[newID] = name
            return (True, {"playerID" : newID})
    
    def joinGame(self, playerID):
        """Adds the player to a new or pending game.
        
        @param playerID: playerID of the player joining a game
        @return: TODO"""
        
        # Add the player to a pending game if one exists 
        for (gameID, game) in self.games:
            if game.getStatus() == ChessMatch.STATUS_PENDING:
                color = game.join(playerID)
                if color:
                    return (True, {"gameID" : gameID})

        # Add a player to a new game otherwise
        newGame = ChessMatch(playerID)
        newID = _getUniqueInt(self.games.keys())
        self.games[newID] = newGame
        return (True, {"gameID" : newID})
    
    def cancelGame(self, gameID):
        """Marks the given match as cancelled
        
        @return: True if successful, false otherwise
        @precondition: game is ongoing or bending
        @postcondition: game.getStatus() = ChessBoard.STATUS_CANCELED
        
        @todo: Check if the game ID exists and is ongoing or pending"""
        if self.games.has_key(gameID):
            if (self.games[gameID].status in [ChessMatch.STATUS_ONGOING,
                                              ChessMatch.STATUS_PENDING]):
                self.games[gameID].status = ChessMatch.STATUS_CANCELLED
            else:
                return (False, {"error" : "Game not active"})
        else:
            return (False, {"error" : "Invalid game ID"})
    
    def getStatus(self, gameID):
        """TODO
        
        @param gameID: TODO
        
        @return: TODO"""
        
        if self.games.has_key(gameID):
            status = self.games[gameID].status
            return (True, {"status": status})
        else:
            return (False, {"error" : "Invalid game ID"})
    
    def getState(self, gameID):
        """TODO
        
        @param playerID: TODO
        @param gameID: TODO
        
        @return: TODO"""

        if self.games.has_key(gameID):
            g = self.games[gameID]
            return (True, {"players": g.players,
                           "isWhitesTurn": g.isWhitesTurn(),
                           "board": g.board.board,
                           "history" : g.board.history})
        else:
            return (False, {"error" : "Invalid game ID"})
        
    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """TODO
        
        @param playerID: TODO
        @param gameID: TODO
        @param fromRank: TODO
        @param fromFile: TODO
        @param toRank: TODO
        @param toFile: TODO
        
        @return: TODO"""
        
        if self.games.has_key(gameID):
            g = self.games[gameID]
            
        
        if (not self.games.has_key(gameID)):
            return (TournamentSystem.ERR_GAMENOTFOUND, {})
#        elif (not self.players.)
        
#        retCode = self.games
        return (False, {"error" : "not yet implemented"})
    
    
def _getUniqueInt(intList):
    maxVals = 2**32-1   # Maximum value of an int
    maxSize = maxVals/2 # Maximum number of allocated ints

    # Fail fast if the list is more than half filled in
    if (len(intList) >= maxSize):
        raise RuntimeError("Cannot play more than 2**31-1 games concurrently")
    
    # Get a unique value
    n = random.randint(1,maxVals)
    while n in intList:
        n = random.randint(1,maxVals)
    return n
    
def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
    
    
# Orphaned code (kept for re-use)
if False:
    @staticmethod
    def standardChessReferenceToArrayDereference(loc):
        """Converts a position given in standard chess notation to a tuple
        containing the y and x coordinates of the position in our board
        representation. Example: "d1" -> (1,4)"""
        (columnLetter, rowNum) = loc
        columnNum = {
               'a':1,
               'b':2,
               'c':3,
               'd':4,
               'e':5,
               'f':6,
               'g':7,
               'h':8 }[columnLetter]
        return (rowNum, columnNum)
    
    def _pieceTaken(self, loc):
        """Returns true if a move to the given location (given in (y,x) form)
        would capture a piece.
        
        @param loc: The location to be evaluated for piece capture, given in x-y 
        form for our board representation
        
        @return: A tuple containing the piece that would be taken (possibly None),
        and the loc from which it would be taken (in (y,x) form) (possibly None)
        """
        # Check for en passant
        if (self.isWhiteTurn()):
            passantRow = 2
            pawnRow = 3
            pawn = self._P_WHITE_PAWN
            flags = self.passant_flags['white'] 
        else:
            passantRow = 7
            pawnRow = 6
            pawn = self._P_BLACK_PAWN
            flags = self.passant_flags['black']
        
        if ((loc[1] == passantRow) and flags[loc[0]]):
            tLoc = loc[0], pawnRow
            return pawn, tLoc
        
        #no en-passant.  test for normal capture
        piece = self._getPiece(loc)
        if (piece != None):
            return piece, loc
        else:
            return None, None
        
    def _doMove(self, movedPiece, moveFromLoc, moveToLoc, takenLoc):
        """Makes the given move, in which movedPiece moves to moveTo, taking 
        the piece at takenLoc in the process.  Updates the board.
         
        @param movedPiece the piece being moved
        @param moveTo the location that movedPiece is moving to.  Assumed to be
        legal and in Y-X format as output by self._stdLocToXY
        @param takenLoc the location of the taken piece in Y-X format as output
        by self._stdLocToXY.  Will be null if no pieces are taken"""
        
        piece = self._getPiece(moveFromLoc)
        self.board[takenLoc[0]][takenLoc[1]] = self._P_EMPTY_SPACE
        self.board[moveFromLoc[0]][moveFromLoc[1]] = self._P_EMPTY_SPACE
        self.board[moveToLoc[0]][moveToLoc[1]] = piece
        
    def makePly(self, moveFrom, moveTo):
        """Moves the piece at location moveFrom to location moveTo.  Returns
        MOVE_SUCCESS on success, MOVE_ILLEGAL on failure."""
        
        #convert both locations to Y-X format for use with our board array
        moveFromYX = self._stdLocToXY(moveFrom)
        moveToYX = self._stdLocToXY(moveTo)
        
        if (not(self._isValidMove(moveFromYX, moveToYX))): # TODO: implement this method
            return self.MOVE_ILLEGAL
        else: #actually make the move
            takenPieceInfo = self._pieceTaken(moveToYX)
            self._doMove(moveFromYX, moveToYX, takenPieceInfo[1])
            self._updateFlags(moveFromYX, moveToYX, takenPieceInfo[1]) # TODO: implement this method
            #record the move
            self.ply_history.append((moveFromYX, moveToYX))
            return self.MOVE_SUCCESS
