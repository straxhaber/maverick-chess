#!/usr/bin/python
"""data.py: common data structures for chess games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import copy
import logging
import random

# TODO (mattsh): Fix this in ALL project Python code before removing TODO
# TODO (mattsh): all position information should be of the form:
#  TODO: - Positions are ChessPosn structure
#  TODO: - Getting the value at a position can be done like so: board[posn]
#           See ChessBoard.__getitem(posn) for more info
#  TODO: - All positions 0-delimited (except for user inputs)
#  TODO: - Return move pair values as 2-tuple (fromPosn, toPosn)
#  TODO: - don't use variable name "file": it is the name of a built-in module
#  TODO: - Arguments to functions named one of:  posn, fromPosn, toPosn
#  TODO: - Structure of return values clearly documented in PyDocs
# Reason behind these changes: too much variation in posn data representation
# Example:
#  def getResultBoard(board, fromPosn, toPosn):
#    reference rank/file as fromPosn.rankN and toPosn.fileN

# TODO (mattsh): Fix this in ALL project Python code before removing TODO
# TODO (mattsh): Fix multi-line comments
# Correct:
#     code[code] = code, code.code code  # Single-line comment (simple)
#
#     # Single-line comment  # Single-line comment (more visible)
#     code[code] = code, code.code code
#
#     # Multi-line
#     # comment
#     code[code] = code, code.code code
#
#
# Not okay:
#     code[code] = code, code.code code  # Multi-line
#                                        # comment

# TODO (mattsh): Fix this in ALL project Python code before removing TODO
# TODO (mattsh): If-elif clauses properly structured
#  TODO: - if it is basically a "switch" statement, have an else with an error
#  TODO: - no if cond1 then; if cond2 then. Do if cond1 then; elif cond2 then


class ChessPosn(object):
    """Represents a position on a chess board"""

    def __init__(self, rankN, fileN):
        self.rankNum = rankN
        self.fileNum = fileN

    def __repr__(self):
        return "({0},{1})".format(self.rankN, self.fileN)


class ChessBoard(object):
    """Represents a chess game in Maverick"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.ChessBoard")
    logging.basicConfig(level=logging.INFO)

    BOARD_LAYOUT_SIZE = 8
    """The width and height of a standard chess board layout."""

    # Constants for the colors
    BLACK = "X"
    """Constant for the black player"""

    WHITE = "O"
    """Constant for the white player"""

    # Constants for the pieces
    PAWN = "P"
    """Constant for the pawn piece"""

    ROOK = "R"
    """Constant for the rook piece"""

    KNGT = "N"
    """Constant for the knight piece"""

    BISH = "B"
    """Constant for the bishop piece"""

    QUEN = "Q"
    """Constant for the queen piece"""

    KING = "K"
    """Constant for the king piece"""

    DEFAULT_STARTING_LAYOUT = [[(WHITE, ROOK),
                                (WHITE, KNGT),
                                (WHITE, BISH),
                                (WHITE, QUEN),
                                (WHITE, KING),
                                (WHITE, BISH),
                                (WHITE, KNGT),
                                (WHITE, ROOK)],
                               [(WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN),
                                (WHITE, PAWN)],
                               [None] * 8,
                               [None] * 8,
                               [None] * 8,
                               [None] * 8,
                               [(BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN),
                                (BLACK, PAWN)],
                               [(BLACK, ROOK),
                                (BLACK, KNGT),
                                (BLACK, BISH),
                                (BLACK, QUEN),
                                (BLACK, KING),
                                (BLACK, BISH),
                                (BLACK, KNGT),
                                (BLACK, ROOK)]]
    """A constant board layout that represents the board layout's initial state

        NOTE: Board layout is represented as a list of rows and 0-indexed
                be careful dereferencing!!!
            i.e., "d1" is self.layout[0][3]

        The start state corresponds roughly to this:
            [['R','N','B','Q','K','B','N','R'],
             ['P','P','P','P','P','P','P','P'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['.','.','.','.','.','.','.','.'],
             ['p','p','p','p','p','p','p','p'],
             ['r','n','b','q','k','b','n','r']]"""

    PAWN_STARTING_RANKS = {WHITE: 2, BLACK: 7}
    """Map of correct starting ranks for pawns

    Pawns have the special property that they only move up/down"""

    HUMAN_FILE_LETTERS = ["a", "b", "c", "d", "e", "f", "g", "h"]
    """Ordered listing of valid files"""

    HUMAN_RANK_NUMBERS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    """Ordered listing of valid ranks"""

    HUMAN_PIECE_TEXT = {ROOK: {WHITE: 'R', BLACK: 'r'},
                        KNGT: {WHITE: 'N', BLACK: 'n'},
                        BISH: {WHITE: 'B', BLACK: 'b'},
                        QUEN: {WHITE: 'Q', BLACK: 'q'},
                        KING: {WHITE: 'K', BLACK: 'k'},
                        PAWN: {WHITE: 'P', BLACK: 'p'}}
    """Mapping of piece constants to their visual represenataion"""

    def __init__(self,
                 startLayout=None,
                 startEnpassantFlags=None,
                 startCanCastleFlags=None):
        """Initialize a new Chess game according to normal Chess rules

        There are special states that must be kept track of:
            - En passant
            - Castling"""

        # Log initialization
        ChessBoard._logger.debug("Initialized")

        # For all instance variables, assign values if supplied in constructor

        if startLayout is None:
            # Perform deep copy of board start state into self.layout
            self.layout = copy.deepcopy(ChessBoard.DEFAULT_STARTING_LAYOUT)
        else:
            self.layout = copy.deepcopy(startLayout)

        if startEnpassantFlags is None:
            # Initialize en passant flags (True means en passant capture is
            # possible in the given column
            self.flag_enpassant = {
                ChessBoard.WHITE: [False] * ChessBoard.BOARD_SIZE,
                ChessBoard.BLACK: [False] * ChessBoard.BOARD_SIZE}
        else:
            self.flag_enpassant = copy.deepcopy(startEnpassantFlags)

        if startCanCastleFlags is None:
            # Initialize castle flags (queen-side ability, king-side ability)
            # Does not account for pieces blocking or checking the castle
            self.flag_canCastle = {
                ChessBoard.WHITE: (True, True),
                ChessBoard.BLACK: (True, True)}
        else:
            self.flag_canCastle = copy.deepcopy(startCanCastleFlags)

    def __getitem__(self, posn):
        """x.__gt__(y) <==> x>y

        Gets the (owner, pieceType) tuple for the given position"""
        return self.layout[posn.fileN][posn.rankN]

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
        - Moves the rook as well if the king is castling """

        # Check if the move is legal
        if not self.isLegalMove(color, fromRank, fromFile, toRank, toFile):
            return False
        else:
            # Remove moving piece from starting position
            movedPiece = self.layout[fromRank - 1][fromFile - 1]
            self.layout[fromRank - 1][fromFile - 1] = None

            # Reset en passant flags to false
            self.flag_enpassant[color] = [False] * ChessBoard.BOARD_SIZE

            # Update castle flags
            prevCastleFlag = self.flag_canCastle[color]
            if movedPiece == self.KING:
                self.flag_canCastle[color] = (False, False)
            if movedPiece == self.ROOK:
                if fromFile == 1:  # Queen-side rook was moved
                    self.flag_canCastle[color] = (False, prevCastleFlag[1])
                elif fromFile == 8:  # King-side rook was moved
                    self.flag_canCastle[color] = (prevCastleFlag[0], False)

            rankDeltaAbs = abs(toRank - fromRank)  # Change in rank from origin
                                                    # to destination
            pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]

            # If we've moved a pawn for the first time, set en passant flags
            if (movedPiece == self.PAWN and
                fromRank == pawnStartRank and
                rankDeltaAbs == 2):
                self.flag_enpassant[color][fromFile - 1] = True

            # Move piece to destination
            self.board[toRank - 1][toFile - 1] = movedPiece

            # Remove en passant pawns, if relevant
            if (self.flag_enpassant[color][toFile - 1] and
                toRank == pawnStartRank):
                # Check if a black pawn is taken via en passant
                if color == ChessBoard.WHITE:
                    self.layout[pawnStartRank - 2][toFile - 1] = None
                # Check if a white pawn is taken via en passant
                elif color == ChessBoard.BLACK:
                    self.layout[pawnStartRank][toFile - 1] = None

            # Log the successful move
            logStrF = "Moved piece from ({0},{1}), to ({2},{3})"
            ChessBoard._logger.info(logStrF,
                                    fromRank, fromFile, toRank, toFile)

            return True

    def __str__(self):
        """Prints out a human-readable ASCIII version of the board"""
        header = "  {0}  ".format(" ".join(self.HUMAN_FILE_LETTERS))

        s = []
        s.append(header)
        for rankNum in range(ChessBoard.BOARD_SIZE):
            rank = self.layout[rankNum]
            rankStr = " ".join([ChessBoardUtils.getPieceChar(c) for c in rank])
            s.append("{0} {1} {0}".format(rankNum + 1, rankStr))
        s.append(header)

        return "\n".join(s)


class ChessBoardUtils(object):
    """Performs various utility functions on ChessBoard objects"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.ChessBoardUtils")
    logging.basicConfig(level=logging.INFO)

    @staticmethod
    def getOtherColor(color):
        """Return the opposing color

        @param color: one of ChessBoard.WHITE or ChessBoard.BLACK

        @return: the opposing color, one of ChessBoard.WHITE or
                ChessBoard.BLACK. None if provided an invalid color."""

        if color == ChessBoard.WHITE:
            return ChessBoard.BLACK
        elif color == ChessBoard.BLACK:
            return ChessBoard.WHITE
        else:
            raise ValueError("Invalid color code")

    @staticmethod
    def isCenterSquare(rankVal, fileVal):
        """Return true if the given position is a center square

        Center squares are those that are one of D4,D5,E4,E5

        @param rankVal: rank of the position to evaluate, integer in ([0..7])
        @param fileVal: file of the position to evaluate, integer in ([0..7])

        @return: True if the given position is a center square, False
                otherwise"""

        return rankVal in [3, 4] and fileVal in [3, 4]

    @staticmethod
    def getSquaresInPath(fromRank, fromFile, toRank, toFile):
        """Returns a list of squares in the straight-line path
        from origin to destination (not including the origin or destination
        squares.)  Returns an empty list if no straight-line path exists.

        @param fromRank: the rank of the starting position  (integer in [0,7])
        @param fromFile: the file of the starting position  (integer in [0,7])
        @param toRank: the rank of the ending position  (integer in [0,7])
        @param toFile: the file of the ending position  (integer in [0,7])

        @return: A list of (rank, file) tuples representing squares in the path
        from origin to destination, not including the origin or destination
        squares.  Returns an empty list if no straight line path exists.
        """

        rank_delta_abs = abs(toRank - fromRank)  # num spaces up/down
        file_delta_abs = abs(toFile - fromFile)  # num spaces left/right
        path_rank_values = []  # Rank values of squares that must be open
        path_file_values = []  # File values of squares that must be open

        #Determine step values to use in range finding
        if fromRank < toRank:
            rankStep = 1
        else:
            rankStep = -1

        if fromFile < toFile:
            fileStep = 1
        else:
            fileStep = -1

        # Check if the path is diagonal
        if rank_delta_abs == file_delta_abs:
            # Build up lists of rank and file values to be included in path
            for r in range(fromRank, toRank, rankStep):
                if r not in [fromRank, toRank]:  # don't include origin or dest
                    path_rank_values.append(r)

            for f in range(fromFile, toFile, fileStep):
                if f not in [fromFile, toFile]:
                    path_file_values.append(f)

        #Check if the path is horizontal
        elif rank_delta_abs == 0:
            # Build up lists of rank and file values to be included in path
            for f in range(fromFile, toFile, fileStep):
                if f not in [fromFile, toFile]:  # don't include origin or dest
                    path_file_values.append(f)
            path_rank_values = [fromRank] * len(path_file_values)

        #Check if the path is vertical
        elif rank_delta_abs != 0:
            #Build up lists of rank and file values to be included in path
            for r in range(fromRank, toRank, rankStep):
                if r not in [fromRank, toRank]:  # don't include origin or dest
                    path_rank_values.append(r)
            path_file_values = [fromFile] * len(path_file_values)

        # If the path is not straight-line, return the empty list
        else:
            return []

        # Combine rank and file lists into return value
        pathSquares = zip(path_rank_values, path_file_values)
        return pathSquares

    @staticmethod
    def isClearLinearPath(board, fromRank, fromFile, toRank, toFile):
        """Returns true if the straight-line path from origin to destination
        is not obstructed.  To be used for horizontal, vertical, or diagonal
        moves.

        @param board: the board on which to perform this test
        @param fromRank: the rank of the starting position  (integer in [0,7])
        @param fromFile: the file of the starting position  (integer in [0,7])
        @param toRank: the rank of the ending position  (integer in [0,7])
        @param toFile: the file of the ending position  (integer in [0,7])

        @return: True if the path is clear, False if it is obstructed, or is
        not a straight-line path.

        Builds a list of the rank and file values of squares to check for
        clarity, then checks them all for clarity.
        """

        # Get the squares in the path, if there is one
        pathSquares = ChessBoardUtils.getSquaresInPath(fromRank, fromFile,
                                                       toRank, toFile)

        rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                # vertically
        file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                # horizontally

        # Check if squares are adjacent or, if not, if there is a path between
        # the two
        if not pathSquares and (rank_delta_abs > 1 or file_delta_abs > 1):
            return False

        # Check the squares in the path for clarity
        for square in pathSquares:
            posnRank = square[0]
            posnFile = square[1]
            if board.layout[posnRank - 1][posnFile - 1] is not None:
                return False  # There was a piece in one of the path squares
        return True  # None of the path squares contained a piece

    @staticmethod
    def findColorPieces(board, color):
        """Returns a list of of all pieces of the given color.

        @param board: The board to use for this check.
        @param color: The color of the pieces to find, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: a list of tuples of form (piecetype, (rank, file) representing
                the location of all pieces of the given color"""
        pieceLocations = []

        for r in range(ChessBoard.BOARD_LAYOUT_SIZE):
            row = board.layout[r]
            for f in range(ChessBoard.BOARD_LAYOUT_SIZE):
                piece = row[f]
                if piece is not None:
                    pieceColor = piece[0]
                    pieceType = piece[1]
                    if pieceColor == color:
                        pieceLocations.append((pieceType, (r + 1, f + 1)))
        return (pieceLocations)

    @staticmethod
    def findKingAndEnemies(board, color):
        """Returns the location of the king of the given color, and a list
        of locations of all non-king pieces of the opposite color.

        @param board: The board to use for this check.
        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: a tuple whose two elements are as follows:
                Element 0: a tuple of form (rank, file) representing the
                location of the king of the given color
                Element 1: a list of tuples of form (rank, file) representing
                the location of all non-king enemy pieces
        """

        ## TODO (James): rewrite this to use findColorPieces

        enemyPieceLocations = []  # List of (rank, file) non-king pieces

        # Locate given player's king, and opposing player's non-king pieces
        for r in range(ChessBoard.BOARD_LAYOUT_SIZE):
            row = board.layout[r]
            for f in range(ChessBoard.BOARD_LAYOUT_SIZE):
                piece = row[f]
                if piece is not None:
                    pieceColor = piece[0]
                    pieceType = piece[1]
                    if pieceColor == color and pieceType == ChessBoard.KING:
                        kingLoc = (r, f)
                    elif pieceColor != color and pieceType != ChessBoard.KING:
                        enemyPieceLocations.append((r, f))
        return (kingLoc, enemyPieceLocations)

    @staticmethod
    def getInterruptSquares(fromRank, fromFile, toRank, toFile):
        """Returns a list of squares that, if moved to, would inhibit the
        piece at fromRank, fromFile from being able to move to toRank, toFile.
        This list will always include (fromRank, fromFile)

        @param fromRank: the rank of the starting position  (integer in [0,7])
        @param fromFile: the file of the starting position  (integer in [0,7])
        @param toRank: the rank of the ending position  (integer in [0,7])
        @param toFile: the file of the ending position  (integer in [0,7])

        @return: A list of (rank, file) tuples representing squares that, if
        moved to, would inhibit the piece at fromRank, fromFile from being able
        to move to toRank, toFile
        """

        interruptSquares = []  # Squares that could interrupt path from origin
                                # to destination.  An accumulator to be built
                                # up and returned
        interruptSquares.append((fromRank, fromFile))

        # Build up list of squares in path from origin to destination
        pathSquares = ChessBoardUtils.getSquaresInPath(fromRank, fromFile,
                                                       toRank, toFile)

        interruptSquares += (pathSquares)

        return interruptSquares

    @staticmethod
    def isCheckMated(board, color):
        """ Returns True if the given color is in checkmate given the current
        board state.

        @param board: The board to use for this check
        @param color: The color of the player to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return True if the given color is in checkmate, False otherwise

        -Check if any of the given color's pieces can take the enemy piece
        checking the king

        -Check if any of the given color's pieces can move in between their
        king and the piece checking him

        -Check if the king can legally move

        If any of the above checks passes, see if that move would produce a
        board where the given color king was not in check. If one does, then
        there is no checkmate.

        """

        # Get other color
        otherColor = ChessBoardUtils.getOtherColor(color)

        # Get check information
        checkInfo = ChessBoardUtils.isKingInCheck(board, color)

        # Check that the king is in check
        if not checkInfo[0]:
            return False

        # TODO (mattsh): I don't think this is what you meant to do, James
        # I re-factored it, but this is the same function as your old code
        # It doesn't seem right, though

        # Pull out the rank and file of the piece putting the king in check
        # TODO (mattsh): James please check that the comment above is correct
        (checkPieceR, checkPieceF) = (checkInfo[1][0], checkInfo[1][0])

        # Find the king whose checkmate status is in question
        myKingLocation = ChessBoardUtils.findKingAndEnemies(board, color)[0]
        (checkedKingR, checkedKingF) = (myKingLocation[0], myKingLocation[1])

        # Get a list of locations that, if moved to, might alleviate check
        interruptLocations = ChessBoardUtils.getInterruptSquares(checkPieceR,
                                                                 checkPieceF,
                                                                 checkedKingR,
                                                                 checkedKingF)
        # Get locations of all this player's non-king pieces
        myNonKingPieceLocs = ChessBoardUtils.findKingAndEnemies(board,
                                                                otherColor)[1]

        # Iterate through pieces, and see if any can move to potential check-
        # alleviating squares
        for pieceLoc in myNonKingPieceLocs:
            pieceRank = pieceLoc[0]
            pieceFile = pieceLoc[1]

            for interruptLoc in interruptLocations:
                intruptRnk = interruptLoc[0]
                intruptFil = interruptLoc[1]

                # Check if the piece can move to this interrupt square
                if ChessBoardUtils.isLegalMove(board, color, pieceRank,
                                               pieceFile, intruptRnk,
                                               intruptFil):

                    # Generate the board that such a move would produce
                    boardAfterMove = ChessBoardUtils.getResultBoard(board,
                                                                    pieceRank,
                                                                    pieceFile,
                                                                    intruptRnk,
                                                                    intruptFil)
                    # Check if the given color is still in check in that board
                    # If not, that color is not in checkmate
                    if not ChessBoardUtils.isKingInCheck(boardAfterMove,
                                                         color):
                        return False

        possibleKingMoves = []  # List of tuples of possible king moves

        # If no alleviating moves found, enumerate king's possible moves
        for r in range(checkedKingR - 1, checkedKingR + 1):
            for f in range(checkedKingF - 1, checkedKingF + 1):
                if r != checkedKingR or f != checkedKingF:
                    possibleKingMoves.append((r, f))

        # For each possible king move, test if it is legal.
        for move in possibleKingMoves:
            toRank = move[0]
            toFile = move[1]

            if ChessBoardUtils.isLegalMove(board, color, checkedKingR,
                                           checkedKingF, toRank, toFile):
                # Generate the board that such a move would produce
                boardAfterMove = ChessBoardUtils.getResultBoard(board,
                                                                pieceRank,
                                                                pieceFile,
                                                                toRank,
                                                                toFile)

                # Check if the given color is still in check in that board
                # If not, that color is not in checkmate
                if not ChessBoardUtils.isKingInCheck(boardAfterMove, color):
                    logStrF = "Found that {0} is not in checkmate"
                    ChessBoardUtils._logger.info(logStrF, color)
                    return False

        # All tests passed - given color is in checkmate
        ChessBoardUtils._logger.info("Found that {0} is in checkmate", color)
        return True

    @staticmethod
    def isKingInCheck(board, color):
        """Determines whether the king of the given color is in check
        in the given board.

        @param board: The board to use for this check.
        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: A tuple containing two values, as follows:
                Element 0: True if the king is in check, false otherwise
                Element 1: A tuple of form (rank, file) representing the
                location of a piece which is placing the king in check.
                NOTE: this is only the first such piece detected.  There may be
                others.

        Finds the location of the king of the given color, and checks whether
        any of the other player's non-king pieces could legally move to that
        location.
        """

        # Determine enemy player's color
        if color == ChessBoard.WHITE:
            otherColor = ChessBoard.BLACK
        else:
            otherColor = ChessBoard.WHITE

        # Locate given player's king, and opposing player's non-king pieces
        pieceLocations = ChessBoardUtils.findKingAndEnemies(board, color)
        kingLocation = pieceLocations[0]
        kingRank = kingLocation[0]
        kingFile = kingLocation[1]
        enemyPieceLocations = pieceLocations[1]  # List of (rank, file)
                                                # locations of pieces that may
                                                # have the king in check

        # Check if any enemy piece can legally move to the king's location
        for piece in enemyPieceLocations:
            pieceRank = piece[0]  # Rank of the piece which may check the king
            pieceFile = piece[1]  # File of the piece which may check the king
            # If a move to the king's location is legal, the king is in check
            if ChessBoardUtils.isLegalMove(board, otherColor, pieceRank,
                                           pieceFile, kingRank, kingFile):
                ChessBoardUtils._logger.info("Found that {0} is in check",
                                             color)
                return (True, (pieceRank, pieceFile))

        # If none of the enemy pieces could move to the king's location, the
        # king is not in check
        ChessBoardUtils._logger.info("Found that {0} is not in check", color)
        return (False, None)

    @staticmethod
    def getResultBoard(board, fromRank, fromFile, toRank, toFile):
        """Returns the board object resulting from the given move

        Assumes that the move is legal.
        Constructs the return value via a deep copy.
        NOTE: does not make the given move on the actual board, or modify game
        state.

        @param fromRank: the rank of the piece to be moved
        @param fromFile: the file of the piece to be moved
        @param toRank: the rank to which the piece is to be moved
        @param toFile: the file to which the piece is to be moved

        @return: a ChessBoard object identical to that which would result from
                the given ply being made on this board
        """

        # Copy the board, so as not to modify the previous data
        postMoveBoard = copy.deepcopy(board)

        # Make the proposed ply on the hypothetical board
        postMoveBoard.makePly(fromRank, fromFile, toRank, toFile)

        return postMoveBoard

    @staticmethod
    def isLegalMove(board, color, fromRank, fromFile, toRank, toFile):
        """Returns true if the specified move is legal

        Arguments are the same as ChessBoard.makePly

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

        # Pull out the (color, origin_type) entry at the from/to board position
        origin_entry = board.layout[fromRank - 1][fromFile - 1]
        destin_entry = board.layout[toRank - 1][toFile - 1]

        # Check if:
        #  - there is no piece at the position
        #  - the player doesn't own a piece at the from position
        if origin_entry is None or origin_entry[0] != color:
            return False

        origin_type = origin_entry[1]  # the type of piece at the origin

        # Check move legality for individual piece types
        if origin_type == ChessBoard.PAWN:

            # Determine the correct starting rank and direction for each color
            pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]
            if color == ChessBoard.WHITE:
                direction = 1
            else:
                direction = -1

            rank_delta = (toRank - fromRank) * direction  # num spaces moved
                                                        #vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            if rank_delta not in [1, 2]:
                return False
            elif rank_delta == 1:
                if file_delta_abs not in [0, 1]:
                    return False  # Pawns can never move more than 1 space
                                    # horizontally
                elif file_delta_abs == 1 and destin_entry is None:
                    return False  # Cannot move diagonally unless capturing
                elif file_delta_abs == 0 and destin_entry is not None:
                    return False  # Cannot move forward and capture

            elif rank_delta == 2:
                if file_delta_abs != 0:
                    return False  # Pawns cannot move up 2 and left/right
                elif fromRank != pawnStartRank:
                    return False  # Pawns can move two spaces only on 1st move

        elif origin_type == ChessBoard.ROOK:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            #check that piece either moves up/down or left/right, but not both
            if rank_delta_abs != 0 and file_delta_abs != 0:
                return False

            #check that path between origin and destination is clear
            if not ChessBoardUtils.isClearLinearPath(board, fromRank,
                                                     fromFile, toRank, toFile):
                return False

        elif origin_type == ChessBoard.KNGT:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            # Check that destination rank is offeset by 1 and file is offset by
            # 2, or vice versa.
            if  ((rank_delta_abs == 2 and file_delta_abs != 1) or
                 (rank_delta_abs == 1 and file_delta_abs != 2) or
                 (rank_delta_abs != 1 and rank_delta_abs != 2)):
                return False

        elif origin_type == ChessBoard.BISH:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            #check that piece moves diagonally
            if rank_delta_abs != file_delta_abs:
                return False

            #check that path between origin and destination is clear
            if not ChessBoard.isClearLinearPath(board, fromRank, fromFile,
                                                toRank, toFile):
                return False

        elif origin_type == ChessBoard.QUEN:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            # check that if piece isn't moving horizontally or vertically, it's
            # moving diagonally
            if (rank_delta_abs != 0 and file_delta_abs != 0 and
                rank_delta_abs != file_delta_abs):
                return False

            #check that path between origin and destination is clear
            if not ChessBoardUtils.isClearLinearPath(board, fromRank, fromFile,
                                                     toRank, toFile):
                return False

        elif origin_type == ChessBoard.KING:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            # Retrieve the kingside and queenside castle flags for this color
            castleFlagQueenside = board.flag_canCastle[color][0]
            castleFlagKingside = board.flag_canCastle[color][1]

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
                    if not castleFlagKingside:
                        return False

                # Check for illegal queenside castle
                elif toFile == castleFileQueenside and toRank == kingStartRank:
                    if not castleFlagQueenside:
                        return False

                # Otherwise, moves of more than one square are illegal
                else:
                    return False

        # If we own a piece at the destination, we cannot move there
        if destin_entry is not None and destin_entry[0] == color:
            return False

        # Check that a move is being made
        if fromRank == toRank and fromFile == toFile:
            return False

        # Check that the proposed move is to a square on the board
        if toRank not in range(1, 9) or toFile not in range(1, 9):
            return False

        # Create the board that the proposed move would result in
        boardAfterMove = ChessBoardUtils.getResultBoard(board, fromRank,
                                                        fromFile, toRank,
                                                        toFile)

        # Check that the king would not be in check after the move
        if ChessBoardUtils.isKingInCheck(boardAfterMove, color)[0]:
            return False

        return True  # All of the error checks passed

    @staticmethod
    def getPieceChar(piece):
        """Return a character representing the given piece

        @param piece: A piece as defined in maverick.server.ChessBoard

        @return: A character representing the given piece on the chess board"""
        if piece is None:
            return '.'
        else:
            (c, p) = piece
            return ChessBoard.HUMAN_PIECE_TEXT[p][c]

    @staticmethod
    def enumerateAllMoves(board, color):
        """Enumerate all possible immediate moves for the given player

        @return: a set of tuples of the form:
            ListOf[(pieceType, (fromRank, fromFile), (toRank, toFile))]"""

        ## TODO (James): rewrite this function

        all_moves = []  # List of all possible moves. Starts empty.

        for p in ChessBoard:
            if p.color == color:
                all_moves.extend(p.getPossibleMoves(board, p.fromRank,
                                                    p.fromFile))
        return all_moves

    @staticmethod
    def getPossibleMoves(board, fromRank, fromFile):
        """Return all possible moves for the specified piece on this board

        @return ListOf[(pieceType, (fromRank, fromFile), (toRank, toFile))]"""

        ## TODO (James): Rewrite this function

        # Pull out the color and piece type from the board
        (color, piece) = board.layout[fromRank - 1][fromFile - 1]

        possible_moves = []  # List of possible moves. Starts empty

        for i in range(0, 7):
            for j in range(0, 7):
                if ChessBoardUtils.isLegalMove(board, color,
                                               fromRank - 1, fromFile - 1,
                                               i, j):
                    possible_moves.append([piece, (fromRank - 1, fromFile - 1),
                                           (i, j)])

        return possible_moves


class ChessMatch(object):
    """Represents a chess game in Maverick"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.ChessMatch")
    _logger.setLevel("INFO")

    # Constants for game status
    STATUS_PENDING = "PENDING"   # Game is waiting for players
    STATUS_ONGOING = "ONGOING"   # Game is in progress
    STATUS_BLACK_WON = "W_BLACK"   # Black won the game
    STATUS_WHITE_WON = "W_WHITE"   # White won the game
    STATUS_DRAWN = "W_DRAWN"   # White won the game
    STATUS_CANCELLED = "CANCELD"   # Game was halted early

    def __init__(self, firstPlayerID=None):
        """Initialize a new chess match with initial state

        @param firstPlayerID: if set, randomly assigned to black or white"""

        # Initialize with a new chess board
        self.board = ChessBoard()

        # Initialize match without players (whose playerIDs can be added later)
        self.players = {ChessBoard.WHITE: None, ChessBoard.BLACK: None}

        # Randomly set black or white to firstPlayerID (no-op if not specified)
        self.players[random.choice(self.players.keys())] = firstPlayerID

        # Initialize match status
        self.status = ChessMatch.STATUS_PENDING

        # Initialize ply history -- a list of (moveFrom, moveTo) plies
        self.history = []

        # Log initialization
        ChessMatch._logger.debug("Initialized")

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
                # Check for checkmates
                if ChessBoardUtils.isCheckMated(self, ChessBoard.WHITE):
                    self.status = ChessMatch.STATUS_BLACK_WON
                elif ChessBoardUtils.isCheckMated(self, ChessBoard.BLACK):
                    self.status = ChessMatch.STATUS_WHITE_WON

                self.history.append(((fromRank, fromFile), (toRank, toFile)))

                # Log this ply
                logStrF = "Added ({0},{1}) -> ({2}, {3}) to match history"
                ChessMatch._logger.debug(logStrF,
                                         fromRank, fromFile, toRank, toFile)
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
            return  # Can only join a pending game (no mid-game replacements)

        if playerID in self.players.values():
            return  # Don't allow a player to play both sides

        for color in [ChessBoard.WHITE, ChessBoard.BLACK]:
            if self.players[color] is None:
                self.players[color] = playerID
                if None not in self.players.values():
                    self.status = ChessMatch.STATUS_ONGOING
                return color
        ChessMatch._logger.info("Joined player {0} to this game", playerID)


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
