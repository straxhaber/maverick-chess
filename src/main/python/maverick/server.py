#!/usr/bin/python

"""server.py: A rudimentary chess server that hosts games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

import copy
import json
import logging
import pickle
import random

from twisted.internet import endpoints
from twisted.internet import protocol
from twisted.internet import reactor

from twisted.protocols import basic as basicProtocols

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

## TODO (James): Figure out a better way to get classnames for logger
#                Instantiation. I looked around and couldn't find an
#                alternative to doing it this way if we want to be
#                able to log from static methods without module-level
#                logging. I had found a best practices guide that recommends
#                not doing module-level logging at
#                http://css.dzone.com/articles/best-practices-python-logging


class ChessBoard:
    """Represents a chess game in Maverick"""

    # Constants for the pieces
    PAWN = "P"
    ROOK = "R"
    KNGT = "N"
    BISH = "B"
    QUEN = "Q"
    KING = "K"

    BOARD_SIZE = 8
    """The width and height of a standard chess board."""

    BLACK = "X"
    """Constant for the black player"""

    WHITE = "O"
    """Constant for the white player"""

    PAWN_STARTING_RANKS = {WHITE: 2, BLACK: 7}
    """Map of correct starting ranks for pawns

    Pawns have the special property that they only move up/down"""

    # A constant board, created once, that represents the board's start state
    STARTING_BOARD = [[(WHITE, ROOK), (WHITE, KNGT), (WHITE, BISH),
                       (WHITE, QUEN), (WHITE, KING), (WHITE, BISH),
                       (WHITE, KNGT), (WHITE, ROOK)],
                      [(WHITE, PAWN), (WHITE, PAWN), (WHITE, PAWN),
                       (WHITE, PAWN), (WHITE, PAWN), (WHITE, PAWN),
                       (WHITE, PAWN), (WHITE, PAWN)],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [(BLACK, PAWN), (BLACK, PAWN), (BLACK, PAWN),
                       (BLACK, PAWN), (BLACK, PAWN), (BLACK, PAWN),
                       (BLACK, PAWN), (BLACK, PAWN)],
                      [(BLACK, ROOK), (BLACK, KNGT), (BLACK, BISH),
                       (BLACK, QUEN), (BLACK, KING), (BLACK, BISH),
                       (BLACK, KNGT), (BLACK, ROOK)]]

    # Create a logger for this class
    ## TODO (James): find a better way to do this - see TODO at top of file
    logger = logging.getLogger("ChessBoard")
    logger.setLevel("INFO")

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

        # Log initialization
        ChessBoard.logger.debug("Initialized")

        # Perform deep copy of board start state into self.board
        self.board = copy.deepcopy(ChessBoard.STARTING_BOARD)

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
        - Moves the rook as well if the king is castling """

        # Check if the move is legal
        if not self.isLegalMove(color, fromRank, fromFile, toRank, toFile):
            return False
        else:
            # Remove moving piece from starting position
            movedPiece = self.board[fromRank - 1][fromFile - 1]
            self.board[fromRank - 1][fromFile - 1] = None

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
                    self.board[pawnStartRank - 2][toFile - 1] = None
                # Check if a white pawn is taken via en passant
                elif color == ChessBoard.BLACK:
                    self.board[pawnStartRank][toFile - 1] = None

            # Log the successful move
            logStrF = "Moved piece from ({0},{1}), to ({2},{3})"
            logStr = logStrF.format(fromRank, fromFile, toRank, toFile)
            ChessBoard.logger.info(logStr)

            return True

    def getSquaresInPath(self, fromRank, fromFile, toRank, toFile):
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

    def isClearLinearPath(self, fromRank, fromFile, toRank, toFile):
        """Returns true if the straight-line path from origin to destination
        is not obstructed.  To be used for horizontal, vertical, or diagonal
        moves.

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
        pathSquares = self.getSquaresInPath(fromRank, fromFile, toRank, toFile)

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
            if self.board[posnRank - 1][posnFile - 1] is not None:
                return False  # There was a piece in one of the path squares
        return True  # None of the path squares contained a piece

    def findKingAndEnemies(self, color, board):
        """Returns the location of the king of the given color, and a list
        of locations of all non-king pieces of the opposite color.

        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK
        @param board: The board to use for this check.  A two dimensional array
        of the same form as ChessBoard.board

        @return: a tuple whose two elements are as follows:
                Element 0: a tuple of form (rank, file) representing the
                location of the king of the given color
                Element 1: a list of tuples of form (rank, file) representing
                the location of all non-king enemy pieces
        """

        enemyPieceLocations = []  # List of (rank, file) non-king pieces

        # Locate given player's king, and opposing player's non-king pieces
        for r in range(len(board)):
            row = board[r]
            for f in range(len(row)):
                piece = row[f]
                if piece is not None:
                    pieceColor = piece[0]
                    pieceType = piece[1]
                    if pieceColor == color and pieceType == ChessBoard.KING:
                        kingLoc = (r + 1, f + 1)  # output as 1-indexed values
                    elif pieceColor != color and pieceType != ChessBoard.KING:
                        enemyPieceLocations.append((r + 1, f + 1))
        return (kingLoc, enemyPieceLocations)

    def getInterruptSquares(self, fromRank, fromFile, toRank, toFile):
        """ Returns a list of squares that, if moved to, would inhibit the
        piece at fromRank, fromFile from being able to move to toRank, toFile.
        This list will always  include (fromRank, fromFile)

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
        pathSquares = self.getSquaresInPath(fromRank, fromFile, toRank, toFile)

        interruptSquares += (pathSquares)

        return interruptSquares

    def isCheckMated(self, color):
        """ Returns True if the given color is in checkmate given the current
        board state.

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
        if color == ChessBoard.WHITE:
            otherColor = ChessBoard.BLACK
        else:
            otherColor = ChessBoard.WHITE
        # Get check information
        checkInfo = self.isKingInCheck(color, self.board)

        # Check that the king is in check
        if not checkInfo[0]:
            return False

        checkingPieceRank = checkInfo[1][0]  # rank of a piece checking
                                            #the king
        checkingPieceFile = checkInfo[1][0]  # file of that same checking piece

        # Find the king whose checkmate status is in question
        myKingLocation = self.findKingAndEnemies(color, self.board)[0]
        checkedKingRank = myKingLocation[0]
        checkedKingFile = myKingLocation[1]

        # Get a list of locations that, if moved to, might alleviate check
        interruptLocations = self.getInterruptSquares(checkingPieceRank,
                                                      checkingPieceFile,
                                                       checkedKingRank,
                                                       checkedKingFile)
        # Get locations of all this player's non-king pieces
        myNonKingPieceLocs = self.findKingAndEnemies(otherColor, self.board)[1]

        # Iterate through pieces, and see if any can move to potential check-
        # alleviating squares
        for pieceLoc in myNonKingPieceLocs:
            pieceRank = pieceLoc[0]
            pieceFile = pieceLoc[1]

            for interruptLoc in interruptLocations:
                interruptRank = interruptLoc[0]
                interruptFile = interruptLoc[1]

                # Check if the piece can move to this interrupt square
                if self.isLegalMove(color, pieceRank, pieceFile,
                                    interruptRank, interruptFile):

                    # Generate the board that such a move would produce
                    postMoveBoard = self.getResultBoard(pieceRank, pieceFile,
                                                        interruptRank,
                                                        interruptFile)

                    # Check if the given color is still in check in that board
                    # If not, that color is not in checkmate
                    if not self.isKingInCheck(color, postMoveBoard):
                        return False

        possibleKingMoves = []  # List of tuples of possible king moves

        # If no alleviating moves found, enumerate king's possible moves
        for r in range(checkedKingRank - 1, checkedKingRank + 1):
            for f in range(checkedKingFile - 1, checkedKingFile + 1):
                if r != checkedKingRank or f != checkedKingFile:
                    possibleKingMoves.append((r, f))

        # For each possible king move, test if it is legal.
        for move in possibleKingMoves:
            toRank = move[0]
            toFile = move[1]

            if self.isLegalMove(color, checkedKingRank, checkedKingFile,
                                toRank, toFile):
                # Generate the board that such a move would produce
                postMoveBoard = self.getResultBoard(pieceRank, pieceFile,
                                                    toRank, toFile)

                # Check if the given color is still in check in that board
                # If not, that color is not in checkmate
                if not self.isKingInCheck(color, postMoveBoard):
                    logStr = "Found that {0} is not in checkmate".format(color)
                    ChessBoard.logger.info(logStr)
                    return False

        # All tests passed - given color is in checkmate
        ChessBoard.logger.info("Found that {0} is in checkmate".format(color))
        return True

    def isKingInCheck(self, color, board):
        """Determines whether the king of the given color is in check
        in the given board.

        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK
        @param board: The board to use for this check.  A two dimensional array
        of the same form as ChessBoard.board

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
        pieceLocations = self.findKingAndEnemies(color, board)
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
            if self.isLegalMove(otherColor, pieceRank, pieceFile, kingRank,
                                kingFile):
                logStr = "Found that {0} is in check".format(color)
                ChessBoard.logger.info(logStr)
                return (True, (pieceRank, pieceFile))

        # If none of the enemy pieces could move to the king's location, the
        # king is not in check
        ChessBoard.logger.info("Found that {0} is not in check".format(color))
        return (False, None)

    def getResultBoard(self, fromRank, fromFile, toRank, toFile):
        """Returns the board that would be produced if the piece on the current
        board was moved from the given location to the given location.
        Assumes that the move is legal.
        Constructs the return value via a deep copy.
        NOTE: does not make the given move on the actual board, or modify game
        state.

        @param fromRank: the rank of the piece to be moved
        @param fromFile: the file of the piece to be moved
        @param toRank: the rank to which the piece is to be moved
        @param toFile: the file to which the piece is to be moved

        @return: a two-dimensional array representing the board that would
        result from the given move, in the form of ChessBoard.board
        """

        # Copy the board, so as not to modify anything real
        postMoveBoard = copy.deepcopy(self.board)

        # Piece to be moved
        origin_entry = postMoveBoard[fromRank - 1][fromFile - 1]

        # Move the piece
        postMoveBoard[fromRank - 1][fromFile - 1] = None
        postMoveBoard[toRank - 1][toFile - 1] = origin_entry
        return postMoveBoard

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

        # Pull out the (color, origin_type) entry at the from/to board position
        origin_entry = self.board[fromRank - 1][fromFile - 1]
        destin_entry = self.board[toRank - 1][toFile - 1]

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
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
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
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
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
            if not self.isClearLinearPath(fromRank, fromFile, toRank, toFile):
                return False

        elif origin_type == ChessBoard.KING:

            rank_delta_abs = abs(toRank - fromRank)  # num spaces moved
                                                    # vertically
            file_delta_abs = abs(toFile - fromFile)  # num spaces moved
                                                    # horizontally

            # Retrieve the kingside and queenside castle flags for this color
            castleFlagQueenside = self.flag_canCastle[color][0]
            castleFlagKingside = self.flag_canCastle[color][1]

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
        postMoveBoard = self.getResultBoard(fromRank, fromFile, toRank, toFile)

        # Check that the king would not be in check after the move
        if self.isKingInCheck(color, postMoveBoard)[0]:
            return False

        return True  # All of the error checks passed


class ChessMatch:
    """Represents a chess game in Maverick"""

    # Constants for game status
    STATUS_PENDING = "PENDING"   # Game is waiting for players
    STATUS_ONGOING = "ONGOING"   # Game is in progress
    STATUS_BLACK_WON = "W_BLACK"   # Black won the game
    STATUS_WHITE_WON = "W_WHITE"   # White won the game
    STATUS_DRAWN = "W_DRAWN"   # White won the game
    STATUS_CANCELLED = "CANCELD"   # Game was halted early

    # Create a logger for this class
    ## TODO (James): find a better way to do this - see TODO at top of file
    logger = logging.getLogger("ChessMatch")
    logger.setLevel("INFO")

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
        ChessMatch.logger.debug("Initialized")

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
                if self.board.isCheckMated(ChessBoard.WHITE):
                    self.status = ChessMatch.STATUS_BLACK_WON
                elif self.board.isCheckMated(ChessBoard.BLACK):
                    self.status = ChessMatch.STATUS_WHITE_WON

                self.history.append(((fromRank, fromFile), (toRank, toFile)))

                # Log this ply
                logStrF = "Added ({0},{1}) -> ({2}, {3}) to match history"
                logStr = logStrF.format(fromRank, fromFile, toRank,
                                              toFile)
                ChessMatch.logger.debug(logStr)
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
        logStr = "Joined player {0} to this game".format(playerID)
        ChessMatch.logger.info(logStr)


class TournamentSystem:
    """A class for managing player interaction with chess matches"""

    # Initialize logging configuration to avoid handler errors
    logging.basicConfig()
    ## TODO (James): find a better way to do this - see TODO at top of file
    logger = logging.getLogger("TournamentSystem")
    logger.setLevel("INFO")

    def __init__(self):
        """Initializes a new tournament system with no games"""
        self.games = {}  # Dict from gameIDs to game objects. Initially empty.
        self.players = {}  # Dict from playerID to player name
        self._version = __version__  # Used in version check during un-pickling

        # Log initialization
        TournamentSystem.logger.debug("Initialized")

    @staticmethod
    def saveTS(tournament, fileName):
        """Pickles the current games' states to a file

        @param fileName: The file to save state to"""
        fd = open(fileName)
        pickle.dump(tournament, fd)
        logStr = "Dumped game state to {0}".format(fileName)
        TournamentSystem.logger.debug(logStr)

    @staticmethod
    def loadTS(tournament, fileName):
        """Load state from a file

        @param fileName: file created using TournamentSystem.saveGames"""

        fd = open(fileName)
        tournament = pickle.load(fd)

        if (tournament._version != __version__):
            raise TypeError("Attempted loading of an incompatible version")

        logStr = "Loaded game state from pickle file at {0}".format(fileName)
        TournamentSystem.logger.debug(logStr)

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
            return (False, {"error": "player with this name already exists"})
        else:
            newID = _getUniqueInt(self.players.keys())
            self.players[newID] = name
            logStr = "Registered {0} with playerID {1}".format(name, newID)
            TournamentSystem.logger.info(logStr)
            return (True, {"playerID": newID})

    def joinGame(self, playerID):
        """Adds the player to a new or pending game.

        @param playerID: playerID of the player joining a game

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"gameID": someInteger})
        """

        # Log the join attempt
        logStr = "joinGame called with pid {0}".format(playerID)
        TournamentSystem.logger.debug(logStr)

        # Add the player to a pending game if one exists
        for gameID, game in self.games.iteritems():
            if game.status == ChessMatch.STATUS_PENDING:
                color = game.join(playerID)
                if color:
                    # Build up a string to enter in the log
                    logStrF = "Added player {0} to existing game {1}"
                    logStr = logStrF.format(playerID, gameID)
                    TournamentSystem.logger.debug(logStr)
                    return (True, {"gameID": gameID})

        # Add a player to a new game otherwise
        newGame = ChessMatch(playerID)
        newID = _getUniqueInt(self.games.keys())
        self.games[newID] = newGame
        logStr = "Added player{0} to new game {1}".format(playerID, newID)
        TournamentSystem.logger.info(logStr)
        return (True, {"gameID": newID})

    def cancelGame(self, gameID):
        """Marks the given match as cancelled

        @return: True if successful, false otherwise
        @precondition: game is ongoing or bending
        @postcondition: game.getStatus() = ChessBoard.STATUS_CANCELED
        """
        if gameID in self.games:
            if (self.games[gameID].status in [ChessMatch.STATUS_ONGOING,
                                              ChessMatch.STATUS_PENDING]):
                TournamentSystem.logger("Canceled game {0}".format(gameID))
                self.games[gameID].status = ChessMatch.STATUS_CANCELLED
            else:
                return (False, {"error": "Game not active"})
        else:
            return (False, {"error": "Invalid game ID"})

    def getStatus(self, gameID):
        """Returns the status of the game with the given gameID, if it exists.

        @param gameID: the integer gameID of an in-progress game

        @return:  On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"status": someStatus})"""

        if gameID in self.games:
            status = self.games[gameID].status
            logStrF = "Found status of game {0} to be {1}"
            logStr = logStrF.format(gameID, status)
            TournamentSystem.logger.info(logStr)
            return (True, {"status": status})
        else:
            return (False, {"error": "Invalid game ID"})

    def getState(self, playerID, gameID):
        """
        Returns the current state of the game, containing information about
        the playerIDs of the black and white players, whose turn it is,
        the current board state, and the game history.

        @param gameID:  the integer gameID of an in-progress game

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True,
        {"youAreColor": ChessBoard.WHITE or ChessBoard.BLACK,
         "isWhitesTurn": someBoolean,
         "board": someBoard,
         "history": listOfPlies})"""

        if gameID in self.games:
            g = self.games[gameID]

            # Determine which player the client is
            if g.players[ChessBoard.WHITE] == playerID:
                youAreColor = ChessBoard.WHITE
            elif g.players[ChessBoard.BLACK] == playerID:
                youAreColor = ChessBoard.BLACK
            else:
                return (False, {"error": "You are not a player in this game"})

            return (True, {"youAreColor": youAreColor,
                           "isWhitesTurn": (g.whoseTurn() == ChessBoard.WHITE),
                           "board": g.board.board,
                           "history": g.history})
        else:
            return (False, {"error": "Invalid game ID"})

    def makePly(self, playerID, gameID, fromRank, fromFile, toRank, toFile):
        """Makes the given ply in the given game on behalf of the given
        player, if it is legal to do so.

        @param playerID: The integer playerID of a registered player.
        @param gameID: The integer gameID of an in-progress game which
        has been joined by the given player
        @param fromRank: The rank of the piece to be moved
        @param fromFile: The file of the piece to be moved
        @param toRank: The file to which the piece should be moved
        @param toFile: The rank to which the piece should be moved

        @return: On failure, returns a tuple of form (False, {"error": "some
        error message"}).  On success, returns a tuple of form (True, {})
        """

        if gameID in self.games:
            result = self.games[gameID].makePly(playerID, fromRank, fromFile,
                                                toRank, toFile)
            if result == "SUCCESS":
                return (True, {})
            else:
                return (False, {"error": result})
        else:
            return (False, {"error": "Invalid game ID"})


def _getUniqueInt(intList):
    """Return a random integer in [1,2**32-1] that is not in intList"""
    maxVals = 2 ** 32 - 1   # Maximum value of an int
    maxSize = 2 ** 31     # Maximum number of allocated ints

    # Fail fast if the list is more than half filled in
    if (len(intList) >= maxSize):
        raise RuntimeError("Cannot play more than 2**31-1 games concurrently")

    # Get a unique value
    n = random.randint(1, maxVals)
    while n in intList:
        n = random.randint(1, maxVals)
    return n

"""Default port for server"""
DEFAULT_MAVERICK_PORT = 7782
# Port 7782 isn't registered for use with the IANA as of December 17th, 2002


class MaverickServerProtocol(basicProtocols.LineOnlyReceiver):
    """Protocol for asynchronous server that administers chess games to clients

    Initiates all connections with a message:
     MaverickChessServer/{version} WAITING_FOR_REQUEST

    Takes in queries of the form:
     VERB {JSON of arguments}

    Responds back in the form:
     if Successful:    SUCCESS {JSON of response}
     if Error:         ERROR {error message} [{query}]

    After the query is responded to, the server disconnects the client"""

    _name = "MaverickChessServer"
    """The name of this server, as reported in its response headers"""

    _version = __version__

    _ts = None
    """put a TournamentSystem instance here"""

    ## TODO (James): find a better way to do this - see TODO at top of file
    logger = logging.getLogger("MaverickServerProtocol")
    logger.setLevel("INFO")

    def __init__(self, tournamentSystem):
        """Initialize with a reference to a TournamentSystem backing"""

        MaverickServerProtocol._ts = tournamentSystem

        # Log initialization
        MaverickServerProtocol.logger.debug("Initialized")

    def connectionMade(self):
        """When a client connects, provide a welcome message"""

        # Log the connection
        MaverickServerProtocol.logger.debug("Connection made with client.")

        # Print out the server name, version, and prompt
        #  (e.g., "MaverickChessServer/1.0a1 WAITING_FOR_REQUEST")
        fStr = "{0}/{1} WAITING_FOR_REQUEST"  # Template for welcome message
        welcomeMsg = fStr.format(MaverickServerProtocol._name,
                                 MaverickServerProtocol._version)
        MaverickServerProtocol.logger.debug("Sending welcome message")
        self.sendLine(welcomeMsg)

    def connectionLost(self, reason=None):
        """When a client disconnects, log it"""

        # Log the disconnection
        MaverickServerProtocol.logger.debug("Client disconnected.")

    def lineReceived(self, line):
        """Take input line-by-line and redirect it to the core"""

        # Build up a log string and log this request
        logStr = "Request received: {0}".format(line)
        MaverickServerProtocol.logger.debug(logStr)

        # Map of valid request names to
        #  - corresponding TournamentSystem function
        #  - expected arguments
        #  - expected return values (currently unused)
        validRequests = {"REGISTER": (self._ts.register,
                                      {"name"},
                                      {"playerID"}),
                         "JOIN_GAME": (self._ts.joinGame,
                                       {"playerID"},
                                       {"gameID"}),
                         "GET_STATUS": (self._ts.getStatus,
                                        {"gameID"},
                                        {"status"}),
                         "GET_STATE": (self._ts.getState,
                                       {"playerID", "gameID"},
                                       {"youAreColor", "isWhitesTurn",
                                        "board", "history"}),
                         "MAKE_PLY": (self._ts.makePly,
                                      {"playerID", "gameID",
                                       "fromRank", "fromFile",
                                       "toRank", "toFile"},
                                      {})}

        requestName = line.partition(" ")[0]  # Request name (e.g., "REGISTER")

        requestArgsString = line.partition(" ")[2]  # Arguments (unparsed)

        errMsg = None  # If this gets set, there was an error
        if requestName in validRequests.keys():
            try:
                requestArgs = json.loads(requestArgsString)
            except ValueError:
                errMsg = "Invalid JSON for arguments"
            else:
                # Pull out the requirements for this request
                (tsCommand, expArgs, _) = validRequests[requestName]

                if expArgs != set(requestArgs.keys()):
                    # Give an error if not provided the correct arguments
                    fStr = "Invalid arguments, expected: {0}"
                    errMsg = fStr.format(",".join(list(expArgs)))
                else:
                    try:
                        # Dispatch command to TournamentSystem instance
                        (successP, result) = tsCommand(**requestArgs)
                    except:
                        # Give an error if caught an exception
                        errMsg = "Uncaught exception"
                    else:
                        if successP:
                            # Provide successful results to the user
                            jsonStr = json.dumps(result, ensure_ascii=True)
                            response = "SUCCESS {0}".format(jsonStr)
                        if not successP:
                            # Pull out structured error messages from func call
                            errMsg = result["error"]
        else:
            # Give an error if provided an invalid command
            errMsg = "Unrecognized verb \"{0}\" in request".format(requestName)

        # Respond to the client
        if errMsg is None:
            # Provide client with the response
            logStr = "RESPONSE [query=\"{0}\"]: {1}".format(line, response)

            # Log successful response
            MaverickServerProtocol.logger.info(logStr)
            self.sendLine(response)  # Send successful response

        else:
            # Provide client with the error
            response = "ERROR {1} [query=\"{0}\"]".format(line, errMsg)
            MaverickServerProtocol.logger.info(response)  # Log error response
            self.sendLine(response)  # Send error response

        # Log the fact that the connection is being closed
        logStr = "Dropping connection to user after completion"
        MaverickServerProtocol.logger.debug(logStr)

        # Close connection after each request
        self.transport.loseConnection()


class MaverickServerProtocolFactory(protocol.ServerFactory):
    """Provides a MaverickServerProtocol backed by a TournamentSystem instance

    It does little more than build a protocol with a reference to the
    provided TournamentSystem instance"""

    # Create a logger for this class
    ## TODO (James): find a better way to do this - see TODO at top of file
    logger = logging.getLogger("MaverickServerProtocolFactory")
    logger.setLevel("INFO")

    def __init__(self, tournamentSystem):
        """Initialize server state

        Makes a link to the TournamentSystem instance provided"""

        # Store a reference to the TournamentSystem backing up this server
        self._tournamentSystem = tournamentSystem

        # Log initialization
        MaverickServerProtocolFactory.logger.info("Server initialized")

    def buildProtocol(self, addr):
        """Create an instance of MaverickServerProtocol"""
        return MaverickServerProtocol(self._tournamentSystem)


def main(port=DEFAULT_MAVERICK_PORT):
    """Main method: called when the server code is run

    @param port: The port to use for communication with a Maverick server"""

    # Initialize a new instance of MaverickCore
    core = TournamentSystem()

    # Run a server on the specified port
    endpoint = endpoints.TCP4ServerEndpoint(reactor, port)
    endpoint.listen(MaverickServerProtocolFactory(core))
    reactor.run()  # @UndefinedVariable

if __name__ == '__main__':
    main()
