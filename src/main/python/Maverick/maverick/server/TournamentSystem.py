"""TournamentSystem.py: A chess server that administers games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "pre-alpha"

import pickle
import random
import copy

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and
# Brad Fournier. All Rights Reserved.
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
    
    # Constants for the players
    BLACK = "X"
    WHITE = "O"
        
    # Map of correct starting ranks for pawns (which have special properties)
    PAWN_STARTING_RANKS = {WHITE: 1, BLACK: 6}
    
    ## TODO: Create a constant for INITIAL_BOARD that is created once

    def __init__(self, startBoard=None):
        """Initialize a new Chess game according to normal Chess rules

        NOTE: Board is represented as a list of rows and 0-indexed
                be careful dereferencing!!!
            i.e., "d1" is self.board[0][3]

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
            - Castling"""
            
        ## TODO: make sure everything is properly 0-indexed for dereferences
        
        # Initialize board to the basic chess starting position
        # NOTE: the board is referenced as self.board[rank][file].
        if startBoard == None:
            ## TODO: Use INITIAL_BOARD constant and create a deep copy
            
            self.board = []
            self.board.append([
                    (ChessBoard.WHITE, ChessBoard.ROOK),
                    (ChessBoard.WHITE, ChessBoard.KNGT),
                    (ChessBoard.WHITE, ChessBoard.BISH),
                    (ChessBoard.WHITE, ChessBoard.QUEN),
                    (ChessBoard.WHITE, ChessBoard.KING),
                    (ChessBoard.WHITE, ChessBoard.BISH),
                    (ChessBoard.WHITE, ChessBoard.KNGT),
                    (ChessBoard.WHITE, ChessBoard.ROOK)])
            self.board.append([(ChessBoard.WHITE, ChessBoard.PAWN)] * 8)
            self.board += [[None] * 8] * 4
            self.board.append([(ChessBoard.BLACK, ChessBoard.PAWN)] * 8)
            self.board.append([
                    (ChessBoard.BLACK, ChessBoard.ROOK),
                    (ChessBoard.BLACK, ChessBoard.KNGT),
                    (ChessBoard.BLACK, ChessBoard.BISH),
                    (ChessBoard.BLACK, ChessBoard.QUEN),
                    (ChessBoard.BLACK, ChessBoard.KING),
                    (ChessBoard.BLACK, ChessBoard.BISH),
                    (ChessBoard.BLACK, ChessBoard.KNGT),
                    (ChessBoard.BLACK, ChessBoard.ROOK)])
        else:
            ## TODO: Create deep copy of startBoard and store to self.board
            self.board = startBoard

        # Initialize en passant flags (True means en passant capture is
        # possible in the given column
        self.flag_enpassant = {
            ChessBoard.WHITE: [False] * ChessBoard.BOARD_SIZE,
            ChessBoard.BLACK: [False] * ChessBoard.BOARD_SIZE}
        
        # Initialize castle flags (queen-side ability, king-side ability)
        # Does not account for pieces blocking or checking the castle
        self.flag_canCastle = {
            ChessBoard.WHITE: (True, True),
            ChessBoard.BLACK: (True, True)}
    
    def makePly(self, color, fromRank, fromFile, toRank, toFile):
        """Makes a ply if legal
        
        @param color: the color making the move (BLACK or WHITE constant)
        @param fromRank: the rank from which piece is moving (integer in [0,7])
        @param fromFile: the file from which piece is moving (integer in [0,7])
        @param toRank: the rank to which piece is moving (integer in [0,7])
        @param toFile: the file to which piece is moving (integer in [0,7])
        
        @return: True if the move was successful, False otherwise
        
        - Check if the move is legal
        - Remove the moving piece from the starting position
        - Update flags if necessary
        - Add the moving piece to the ending position (possibly overwriting)
        - Delete pawns in en passant state if relevant
        - Moves the rook as well if the king is castling
        """
        
        # Check if the move is legal
        if not self.isLegalMove(color, fromRank, fromFile, toRank, toFile):
            return False
        else:
            # Remove moving piece from starting position
            movedPiece = self.board[fromRank][fromFile]
            self.board[fromRank][fromFile] = None
            
            # Reset en passant flags to false
            self.flag_enpassant[color] = [False] * ChessBoard.BOARD_SIZE
            
            # Update castle flags
            prevCastleFlag = self.flag_canCastle[color]
            if movedPiece == self.KING:
                self.flag_canCastle[color] = (False, False)
            if movedPiece == self.ROOK:
                if fromFile == 0: # Queen-side rook was moved
                    self.flag_canCastle[color] = (False, prevCastleFlag[1])
                elif fromFile == 7: # King-side rook was moved
                    self.flag_canCastle[color] = (prevCastleFlag[0], False)
                    
            # If we've moved a pawn for the first time, set the en passant flags
            if (movedPiece == self.PAWN and 
                fromRank == {ChessBoard.WHITE: 1, ChessBoard.BLACK: 6}[color] and
                abs(toRank - fromRank) == 2):
                self.flag_enpassant[color][fromFile] = True             
            
            # Move piece to destination
            self.board[toRank][toFile] = movedPiece
            
            # Remove en passant pawns, if relevant
            if self.flag_enpassant[color][toFile]:
                if (color == ChessBoard.WHITE and 
                    toRank == ChessBoard.BOARD_SIZE - 2): 
                    # We should take a black pawn via en passant
                    self.board[ChessBoard.BOARD_SIZE - 2][toFile] = None
                elif (color == ChessBoard.BLACK and toRank == 1):
                    # We should take a white pawn via en passant
                    self.board[2][toFile] = None
                    
            return True
        
    def isClearLinearPath(self, fromRank, fromFile, toRank, toFile):
        """Returns true if the straight-line path from origin to destination
        is not obstructed.  To be used for horizontal, vertical, or diagonal
        moves.
        
        @param fromRank: the rank of the starting position  (integer in [0,7])
        @param fromFile: the file of the starting position  (integer in [0,7])
        @param toRank: the rank of the ending position  (integer in [0,7])
        @param toFile: the file of the ending position  (integer in [0,7])
        
        @return: True if the path is clear, False otherwise
        
        Builds a list of the rank and file values of squares to check for
        clarity, then checks them all for clarity.
        """
        
        rank_delta_abs = abs(toRank-fromRank) # num spaces up/down
        file_delta_abs = abs(toFile-fromFile) # num spaces left/right
        path_rank_values = [] # Rank values of squares that must be open
        path_file_values = [] # File values of squares that must be open
        
        # Check if the path is diagonal
        if rank_delta_abs == file_delta_abs:
            # Build up lists of rank and file values to be checked
            for r in range(fromRank, toRank):
                if r not in [fromRank, toRank]:#don't check origin or dest
                    path_rank_values += r
                
            for f in range(fromFile, toFile):
                if f not in [fromFile, toFile]:
                    path_file_values += f
                    
        #Check if the path is horizontal
        elif rank_delta_abs == 0:
            # Build up lists of rank and file values to be checked for clarity
            for f in range(fromFile, toFile):
                if f not in [fromFile, toFile]:
                    path_file_values += f
            path_rank_values = [fromRank] * len(path_file_values)
        
        #Check if the path is vertical
        elif rank_delta_abs != 0:
            #Build up lists of rank and file values to be checked for clarity
            for r in range(fromRank, toRank):
                if r not in [fromRank, toRank]:
                    path_rank_values += r
            path_file_values = [fromFile] * len(path_file_values)
            
        # Check the squares in the path for clarity
        for i in range(len(path_rank_values)):
            rank_pos = path_rank_values[i]
            file_pos = path_file_values[i]
            if self.board[rank_pos][file_pos] is not None:
                return False # There was a piece in one of the path squares
        return True # None of the path squares contained a piece
        
    def isKingInCheck(self, color, board):
        """ Returns True if the king of the given color is in check
        in the given board
        
        @param color: The color of the king to check, ChessMatch.WHITE or 
        ChessMatch.BLACK
        @param board: The board to use for this check.  A two dimensional array,
        of the same form as ChessBoard.board
        
        @return: True if the king of the given color is in check on the given
        board, False otherwise
        
        Finds the location of the king of the given color, and checks whether
        any of the other player's non-king pieces could legally move to that
        location.
        """
        
        # Determine enemy player's color
        if color == ChessBoard.WHITE:
            otherColor = ChessBoard.BLACK
        else:
            otherColor = ChessBoard.WHITE
        
        enemyPieceLocations = [] # List of (rank, file) locations of pieces
                                # that may have the king in check
        # Locate given player's king, and opposing player's non-king pieces
        for r in len(board):
            row = board[r]
            for f in len(row):
                piece = row[f]
                pieceColor = piece[0]
                pieceType = piece[1]
                if pieceColor == color and pieceType == ChessBoard.KING:
                    kingRank = r
                    kingFile = f
                elif pieceColor != color and pieceType != ChessBoard.KING:
                    enemyPieceLocations += (r,f)
        
        # Check if any enemy piece can legally move to the king's location
        for piece in enemyPieceLocations:
            pieceRank = piece[0] # Rank of the piece which may check the king
            pieceFile = piece[1] # File of the piece which may check the king
            # If a move to the king's location is legal, the king is in check
            if self.isLegalMove(otherColor, pieceRank, pieceFile, kingRank,
                                kingFile):
                return True
        
        # If none of the enemy pieces could move to the king's location, the
        # king is not in check
        return False
            
            
    def isLegalMove(self, color, fromRank, fromFile, toRank, toFile):
        """Returns true if the specified move is legal
        
        Arguments are the same as makePly
        
        Checks if:
         - there is a piece at the from position
         - the to position doesn't contain a piece owned by the color
         - flags don't preclude the move (i.e., castling)
         - the path to make the move is free (for bishops, rooks, queens, etc.)
         - this is a legal move for the piece type
         - the king would not be in check after the move
         - the move alters the board state
 
        Pawns:
         - normally move one space up away from their color's starting position
         - can move two spaces on first move
         - can capture diagonally if there is a piece to be captured
         
        Rooks:
         - move horizontally and vertically
         - require a clear path between origin and destination
        
        Knights:
         - move in the traditional "L" pattern
         - do not require a clear path between origin and destination 
        
        Bishops:
         - move diagonally
         - require a clear path between origin and destination
        
        Queens:
         - can make all moves that a rook or bishop would make from the same 
         position
        
        Kings:
         - can move one square in any direction
         - can move two squares toward a rook if the canCastle flag for that
         direction ("a" file or "h" file) is True"""
        
        # Pull out the (color, origin_type) entry at the from/to board positions
        origin_entry = self.board[fromRank][fromFile]
        destin_entry = self.board[toRank][toFile]
        
        # Check if:
        #  - there is no piece at the position
        #  - the player doesn't own a piece at the from position
        if origin_entry == None or origin_entry[0] != color:
            return False
        
        origin_type = origin_entry[1] # the type of piece at the origin 
        
        # Check move legality for individual piece types
        if origin_type == ChessBoard.PAWN:
            
            # Determine the correct starting rank and direction for each color
            pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]
            if color == ChessBoard.WHITE:
                direction = 1
            else:
                direction = -1
            
            rank_delta = (toRank - fromRank) * direction # num spaces 'forward'
            file_delta_abs = abs(toFile-fromFile) # num spaces left/right
            
            if rank_delta not in [1,2]:
                return False
            elif rank_delta == 1:
                if file_delta_abs not in [0,1]:
                    return False # Pawns can't move more than 1 space left/right
                elif file_delta_abs == 1 and destin_entry == None:
                    return False # Cannot move diagonally unless capturing
                elif file_delta_abs == 0 and destin_entry != None:
                    return False # Cannot move forward and capture
            
            elif rank_delta == 2:
                if file_delta_abs != 0:
                    return False # Pawns cannot move up 2 and left/right
                elif fromFile != pawnStartRank:
                    return False # Pawns can only move two spaces on first move
        
        elif origin_type == ChessBoard.Rook:
            
            rank_delta_abs = abs(toRank-fromRank) # num spaces moved up/down
            file_delta_abs = abs(toFile-fromFile) # num spaces moved left/right
            
            #check that piece either moves up/down or left/right, but not both
            if rank_delta_abs != 0 and file_delta_abs != 0:
                return False
            
            #check that path between origin and destination is clear
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
                return False
                
        elif origin_type == ChessBoard.Knight:
            rank_delta_abs = abs(toRank-fromRank) # num spaces moved up/down
            file_delta_abs = abs(toFile-fromFile) # num spaces moved left/right
            
            # Check that destination rank is offeset by 1 and file is offset by
            # 2, or vice versa. 
            if  ((rank_delta_abs == 2 and file_delta_abs != 1) or
                (rank_delta_abs == 1 and file_delta_abs != 2)):
                return False
            
        elif origin_type == ChessBoard.Bishop:
            
            rank_delta_abs = abs(toRank-fromRank) # num spaces moved up/down
            file_delta_abs = abs(toFile-fromFile) # num spaces moved left/right
            
            #check that piece moves diagonally
            if rank_delta_abs !=  file_delta_abs:
                return False
            
            #check that path between origin and destination is clear
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
                return False
            
        elif origin_type == ChessBoard.Queen:
            
            rank_delta_abs = abs(toRank-fromRank) # num spaces moved up/down
            file_delta_abs = abs(toFile-fromFile) # num spaces moved left/right
            
            # check that if piece isn't moving horizontally or vertically, it is
            # moving diagonally
            if rank_delta_abs != 0 and file_delta_abs != 0 and
                rank_delta_abs != file_delta_abs:
                return False
            
            #check that path between origin and destination is clear
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
                return False
            
        elif origin_type == ChessBoard.King:
            
            rank_delta_abs = abs(toRank-fromRank) # num spaces moved up/down
            file_delta_abs = abs(toFile-fromFile) # num spaces moved left/right
            
            # Retrieve the kingside and queenside castle flags for this color
            castleFlagQueenside = self.flag_CanCastle[color][0]
            castleFlagKingside = self.flag_CanCastle[color][1]
            
            # Determine the locations to which the king would move if castling
            castleFileQueenside = 3
            castleFileKingside = 6
            if color == ChessBoard.WHITE:
                kingStartRank = 1
            else:
                kingStartRank = 7
            
            # Check that king only moves more than one square when castling
            if file_delta_abs != 1 and rank_delta_abs != 1:
                
                # Check for illegal kingside castle
                if toFile == castleFileKingside and toRank == kingStartRank:
                    if not castleFlagKingside
                        return False
                    
                # Check for illegal queenside castle
                elif toFile == castleFileQueenside and toRank == kingStartRank:
                    if not castleFlagQueenside:
                        return False
                 
                # Otherwise, moves of more than one square are illegal
                else:
                    return False
            
        # If we own a piece at the destination, we cannot move there
        if destin_entry != None and destin_entry[0] == color:
            return False
        
        # Check that a move is being made
        if fromRank == toRank and fromFile == toFile:
            return False
        
        # Check that the proposed move is to a square on the board
        if toRank not in range(1,7) or toFile not in range(1,7):
            return False
        
        # Create the board that the proposed move would result in
        postMoveBoard = copy.deepcopy(self.board)
        postMoveBoard[fromRank][fromFile] = None
        postMoveBoard[toRank][toFile] = origin_entry
        
        # Check that the king would not be in check after the move
        if self.kingInCheck(postMoveBoard):
            return False
        
        return True # All of the error checks passed
    
    
class ChessMatch:
    # Constants for game status
    STATUS_PENDING   = "PENDING"   # Game is waiting for players
    STATUS_ONGOING   = "ONGOING"   # Game is in progress
    STATUS_BLACK_WON = "W_BLACK"   # Black won the game
    STATUS_WHITE_WON = "W_WHITE"   # White won the game
    STATUS_DRAWN     = "W_DRAWN"   # White won the game
    STATUS_CANCELLED = "CANCELD"   # Game was halted early
    
    ## TODO: Detect and deal with check-mates
    
    def __init__(self, firstPlayerID=None):
        """Initialize a new chess match with initial state
        
        @param firstPlayerID: if set, randomly assigned to black or white"""
        
        # Initialize with a new chess board
        self.board = ChessBoard()
        
        # Initialize match without players (whose playerIDs can be added later)
        self.players = { ChessBoard.WHITE : None, ChessBoard.BLACK : None}
        
        # Randomly set black or white to firstPlayerID (no-op if not specified)
        self.players[random.choice(self.players.keys())] = firstPlayerID
    
        # Initialize match status
        self.status = ChessMatch.STATUS_PENDING
        
        # Initialize ply history -- a list of (moveFrom, moveTo) plies
        self.history = []
        
    def whoseTurn(self):
        """Returns True if it is whites turn, False otherwise"""
        if (len(self.history) % 2 == 0):
            return ChessBoard.WHITE
        else:
            return ChessBoard.BLACK
    
    def makePly(self, player, fromRank, fromFile, toRank, toFile):
        """Makes a move if legal
        
        @return: "SUCCESS" if move was successful, error message otherwise"""
        if self.status == ChessMatch.STATUS_ONGOING:
            if (self.players[ChessBoard.WHITE] == player):
                color = ChessBoard.WHITE
            elif (self.players[ChessBoard.BLACK] == player):
                color = ChessBoard.BLACK
            else:
                return "You are not a player in this game"
            
            if color != self.whoseTurn():
                return "It is not your turn"
            
            if self.board.makePly(color, fromRank, fromFile, toRank, toFile):
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
        
        for color in [ChessBoard.WHITE, ChessBoard.BLACK]:
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

        @param fileName: file created using TournamentSystem.saveGames"""
        
        fd = open(fileName)
        tournament = pickle.load(fd)
        
        if (tournament._version != __version__):
            raise TypeError("Attempted loading of an incompatible version")
        
        return tournament
    
    def register(self, name):
        """Registers a player with the system, returning their playerID.
        
        This should be called before trying to join a player to a game.
        
        @param name: A String containing the player's name
        
        @return: On failure, returns a tuple of form (False, {"error": "some 
        error message"}).  On success, returns a tuple of form (True, 
        {"PlayerID": someInteger})
        """
        if name in self.players.values():
            return (False, {"error" : "player with this name already exists"})
        else:
            newID = _getUniqueInt(self.players.keys())
            self.players[newID] = name
            return (True, {"playerID" : newID})
    
    def joinGame(self, playerID):
        """Adds the player to a new or pending game.
        
        @param playerID: playerID of the player joining a game
        
        @return: On failure, returns a tuple of form (False, {"error": "some 
        error message"}).  On success, returns a tuple of form (True, 
        {"gameID": someInteger})
        """
        
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
        """
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
                           "isWhitesTurn": (g.whoseTurn() == ChessBoard.WHITE),
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
            result = self.games[gameID].makePly(playerID, gameID,
                                                fromRank, fromFile,
                                                toRank, toFile)
            if result == "SUCCESS":
                return (True, {})
            else:
                return (False, {"error" : result})
        else:
            return (False, {"error" : "Invalid game ID"})
    
    
def _getUniqueInt(intList):
    """Return a random integer in [1,2**32-1] that is not in intList"""
    maxVals = 2**32-1   # Maximum value of an int
    maxSize = 2**31     # Maximum number of allocated ints

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