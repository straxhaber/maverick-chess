#!/usr/bin/python
"""data.py: common data structures for chess games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

## TODO (James): For ALL MAVERICK CODE - license as BeerWare

import copy
import logging
import random

__all__ = ["ChessBoard",
           "ChessMatch",
           "ChessPiece",
           "ChessPosn"]


class ChessPosn(object):
    """Represents a position on a chess board"""

    def __init__(self, rankN, fileN):
        """ChessPosn wraps a rank (row) and a file (column)"""
        self.rankN = rankN
        self.fileN = fileN

    def __str__(self):
        """Represent a ChessPosn as a 2-tuple (rank, file)"""
        return "({0},{1})".format(self.rankN, self.fileN)

    def __repr__(self):
        return "ChessPosn({0},{1})".format(self.rankN, self.fileN)

    def __eq__(self, other):
        """x.__eq__(y) <==> x==y

        Compares two ChessPosns for deep equality"""
        return (isinstance(other, ChessPosn) and
                self.rankN == other.rankN and
                self.fileN == other.fileN)

    def getTranslatedBy(self, deltaRank, deltaFile):
        """Return new ChessPosn translated by the coordinates provided"""
        return ChessPosn(self.rankN + deltaRank,
                         self.fileN + deltaFile)


class ChessPiece(object):
    """Represents chess piece in Maverick"""

    def __init__(self, color, pieceType):
        """ChessPosn wraps a color and a piece type"""
        self.color = color
        self.pieceType = pieceType

    def __str__(self):
        return "{}{}".format(["B", "W"][self.color == ChessBoard.WHITE],
                             ChessBoard.HUMAN_PIECE_TEXT[self.pieceType])

    def __repr__(self):
        return "ChessPiece(\"{}\",\"{}\")".format(self.color, self.pieceType)

    def __eq__(self, other):
        """"x.__eq__(y) <==> x==y

        Compares two ChessPosns for deep equality"""
        return (isinstance(other, ChessPiece) and
                self.color == other.color and
                self.pieceType == other.pieceType)


class ChessBoard(object):
    """Represents a chess game in Maverick"""

    # TODO (mattsh): Represent 50-move draw rule
    # TODO (mattsh): Represent threefold repetition draw rule

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.ChessBoard")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    BOARD_LAYOUT_SIZE = 8
    """The width and height of a standard chess board layout."""

    # Constants for the colors
    BLACK = "X"
    """Constant for the black player"""

    WHITE = "O"
    """Constant for the white player"""

    # Constants for the piece types
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

    DEFAULT_INITIAL_LAYOUT = [[ChessPiece(WHITE, ROOK),
                               ChessPiece(WHITE, KNGT),
                               ChessPiece(WHITE, BISH),
                               ChessPiece(WHITE, QUEN),
                               ChessPiece(WHITE, KING),
                               ChessPiece(WHITE, BISH),
                               ChessPiece(WHITE, KNGT),
                               ChessPiece(WHITE, ROOK)],
                              [ChessPiece(WHITE, PAWN)] * 8,
                              [None] * 8,
                              [None] * 8,
                              [None] * 8,
                              [None] * 8,
                              [ChessPiece(BLACK, PAWN)] * 8,
                              [ChessPiece(BLACK, ROOK),
                               ChessPiece(BLACK, KNGT),
                               ChessPiece(BLACK, BISH),
                               ChessPiece(BLACK, QUEN),
                               ChessPiece(BLACK, KING),
                               ChessPiece(BLACK, BISH),
                               ChessPiece(BLACK, KNGT),
                               ChessPiece(BLACK, ROOK)]]
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

    PAWN_STARTING_RANKS = {WHITE: 1, BLACK: 6}
    """Map of correct starting ranks for pawns

    Pawns have the special property that they only move up/down"""

    HUMAN_FILE_LETTERS = ["A", "B", "C", "D", "E", "F", "G", "H"]
    """Ordered listing of valid files"""

    HUMAN_RANK_NUMBERS = ["1", "2", "3", "4", "5", "6", "7", "8"]
    """Ordered listing of valid ranks"""

    HUMAN_PIECE_TEXT = {PAWN: "~",
                        ROOK: "R",
                        KNGT: "N",
                        BISH: "B",
                        QUEN: "Q",
                        KING: "K"}
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
            self.layout = copy.deepcopy(ChessBoard.DEFAULT_INITIAL_LAYOUT)
        else:
            self.layout = copy.deepcopy(startLayout)

        if startEnpassantFlags is None:
            # Initialize en passant flags (True means en passant capture is
            # possible in the given column
            self.flag_enpassant = {
                ChessBoard.WHITE: [False] * ChessBoard.BOARD_LAYOUT_SIZE,
                ChessBoard.BLACK: [False] * ChessBoard.BOARD_LAYOUT_SIZE}
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
        """x.__getitem__(y) <==> x[y]

        Gets the piece object for the given position,
        None if given a position off the board"""
        if (posn.rankN in xrange(ChessBoard.BOARD_LAYOUT_SIZE) and
            posn.fileN in xrange(ChessBoard.BOARD_LAYOUT_SIZE)):
            return self.layout[posn.rankN][posn.fileN]
        else:
            return None

    def __setitem__(self, posnLayoutLoc, piece):
        """x.__setitem__(i, y) <==> x[i]=y

        Sets the piece object at the given position"""
        self.layout[posnLayoutLoc.rankN][posnLayoutLoc.fileN] = piece

    def getPiecesOfColor(self, color):
        """TODO"""
        for row in self.layout:
            for col in row:
                p = self.layout[row][col]
                if p is not None and p.color == color:
                    yield p

    def _executePly(self, color, fromPosn, toPosn):
        """Make a ply on this board, assuming that it is legal

        Arguments and are the same as makePly for a legal move"""

        # Remove moving piece from starting position
        movedPiece = self[fromPosn]
        self[fromPosn] = None

        # Reset en passant flags to false
        self.flag_enpassant[color] = [False] * ChessBoard.BOARD_LAYOUT_SIZE

        # Update castle flags
        prevCastleFlag = self.flag_canCastle[color]
        if movedPiece.pieceType == ChessBoard.KING:
            self.flag_canCastle[color] = (False, False)
        elif movedPiece.pieceType == ChessBoard.ROOK:
            if fromPosn.fileN == 0:  # Queen-side rook was moved
                self.flag_canCastle[color] = (False, prevCastleFlag[1])
            elif fromPosn.fileN == 7:  # King-side rook was moved
                self.flag_canCastle[color] = (prevCastleFlag[0], False)

        # Change in rank from origin to destination
        rankDeltaAbs = abs(toPosn.rankN - fromPosn.rankN)

        # Increase
        fileDelta = toPosn.fileN - fromPosn.fileN

        pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]

        # If we've moved a pawn for the first time, set en passant flags
        if (movedPiece.pieceType == ChessBoard.PAWN and
            fromPosn.rankN == pawnStartRank and
            rankDeltaAbs == 2):
            self.flag_enpassant[color][fromPosn.fileN] = True

        # Move piece to destination
        self[toPosn] = movedPiece

        otherColor = ChessBoard.getOtherColor(color)
        otherPawnStartRank = ChessBoard.PAWN_STARTING_RANKS[otherColor]

        # Handle rook movement if castling

        # Check whether this ply is a castle
        if movedPiece.pieceType == ChessBoard.KING and abs(fileDelta) == 2:
            # Find posn of the rook to be moved

            #Check if this was a kingside castle
            if fileDelta > 0:
                movedRookPosn = ChessPosn(toPosn.rankN, 7)
                rookDestPosn = ChessPosn(toPosn.rankN, 5)

            # Else, this was a queenside castle
            else:
                movedRookPosn = ChessPosn(toPosn.rankN, 0)
                rookDestPosn = ChessPosn(toPosn.rankN, 3)

            # Move the rook
            movedRook = self[movedRookPosn]
            self[movedRookPosn] = None
            self[rookDestPosn] = movedRook

        # Remove en passant pawns, if relevant

        if movedPiece.pieceType == ChessBoard.PAWN:

            # Build up information for en passant capture check
            if otherColor == ChessBoard.WHITE:
                # The rank at which a pawn could capture via en passant
                epCapRnk = ChessBoard.PAWN_STARTING_RANKS[otherColor] + 1
                # Location of the pawn being captured
                pawnPosn = ChessPosn(epCapRnk + 1, toPosn.fileN)
            else:
                epCapRnk = ChessBoard.PAWN_STARTING_RANKS[otherColor] - 1
                # Location of the pawn being captured
                pawnPosn = ChessPosn(epCapRnk - 1, toPosn.fileN)

            # Check whether a pawn was captured by en passant
            if (self.flag_enpassant[otherColor][toPosn.fileN] and
                toPosn.rankN == epCapRnk):

                    # If a pawn was captured, remove it
                    self[pawnPosn] = None

        # Log the successful move
        logStrF = "Moved piece from %s, to %s"
        ChessBoard._logger.debug(logStrF, fromPosn, toPosn)

    def makePly(self, color, fromPosn, toPosn):
        """Make a ply on this board if legal

        @param color: the color making the move (BLACK or WHITE constant)
        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: True if the move was successful, False otherwise

        - Checks if the move is legal
        - Removes the moving piece from the starting position
        - Updates flags if necessary
        - Adds the moving piece to the ending position (possibly overwriting)
        - Deletes pawns in en passant state if relevant
        - Moves the rook as well if the king is castling"""

        # Check if the move is legal
        isLegal = self.isLegalMove(color, fromPosn, toPosn)
        if isLegal:
            self._executePly(color, fromPosn, toPosn)

        return isLegal

    @staticmethod
    def __str_getPieceChar(piece):
        """Return a character representing the given piece

        @param piece: A piece as defined in maverick.data.ChessBoard

        @return: ASCII character representing the given piece"""
        return "  " if piece is None else piece.__str__()

    def __repr__(self, fullRepr=False):
        if fullRepr:
            fStr = "ChessBoard({}={},{}={},{}={}"
            return fStr.format("startLayout", self.layout,
                               "startEnpassantFlags", self.flag_enpassant,
                               "startCanCastleFlags", self.flag_canCastle)
        else:
            return object.__repr__(self)

    def __str__(self, whitePerspective=True):
        """Prints out a human-readable ASCII version of the board

        if whitePerspective is True (default), print the board with the 1-row
        on bottom and the 8-row on top

        if whitePerspective if False, print the board with the 8-row
        on bottom and the 1-row on top"""

        if whitePerspective:
            iterStart = ChessBoard.BOARD_LAYOUT_SIZE - 1
            iterStop = -1
            iterStep = -1
        else:
            iterStart = 0
            iterStop = ChessBoard.BOARD_LAYOUT_SIZE
            iterStep = 1

        boardSep = " | "
        header = "    A    B    C    D    E    F    G    H"
        barrier = "  -----------------------------------------"

        boardStrA = []
        boardStrA.append(header)
        boardStrA.append(barrier)
        for rankN in xrange(iterStart, iterStop, iterStep):
            fStr = "{1}{0}{2}{0}{1}"
            rS = fStr.format(boardSep,
                             rankN + 1,
                             boardSep.join([ChessBoard.__str_getPieceChar(c)
                                            for c in self.layout[rankN]]))
            boardStrA.append(rS)
            boardStrA.append(barrier)
        boardStrA.append(header)

        boardStr = "\n".join(boardStrA)
        return boardStr

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

    def __isLegalMove_isClearLinearPath(self, fromPosn, toPosn):
        """True if there is a clear straight path from origin to destination

        To be used for horizontal, vertical, or diagonal moves.

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: True if the path is clear, False if it is obstructed, or is
        not a straight-line path.

        Builds a list of the rank and file values of squares to check for
        clarity, then checks them all for clarity."""

        # Get the squares in the path, if there is one
        pathPosns = ChessBoard.__isLegalMove_getSquaresInPath(fromPosn, toPosn)

        # Number spaces moved vertically
        rank_delta_abs = abs(toPosn.rankN - fromPosn.rankN)

        # Number of spaces moved horizontally
        file_delta_abs = abs(toPosn.fileN - fromPosn.fileN)

        # Check if squares are adjacent or, if not, if there is a path between
        # the two
        if not pathPosns and (rank_delta_abs > 1 or file_delta_abs > 1):
            return False

        # Check the squares in the path for clarity
        for pathPosn in pathPosns:
            if self[pathPosn] is not None:
                return False  # There was a piece in one of the path squares
        return True  # None of the path squares contained a piece

    @staticmethod
    def __isLegalMove_getInterruptSquares(fromPosn, toPosn):
        """Return a list of squares that block the given path if moved to

        NOTE: This list will always include fromPosn

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: A list of ChessPosn objects representing squares that, if
        moved to, would inhibit the piece at fromPosn from being able
        to move to toPosn"""

        # Squares that could interrupt path from origin to destination. An
        # Accumulator to built up and returned
        interruptSquares = []
        interruptSquares.append(fromPosn)

        # Build up list of squares in path from origin to destination
        pathSquares = ChessBoard.__isLegalMove_getSquaresInPath(fromPosn,
                                                                toPosn)

        interruptSquares += (pathSquares)

        return interruptSquares

    def __isLegalMove_findKngAndEnems(self, color):
        """Return the location color's king and all opposing non-king pieces

        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: a tuple whose two elements are as follows:
                Element 0: A ChessPosn representing the
                location of the king of the given color
                Element 1: A list of ChessTuples representing
                the location of all non-king enemy pieces"""

        # TODO (mattsh): Why is a function this hack-ish here?
        #                Might be a good reason, but should discuss with James

        enemyPiecePosns = []  # List of ChessPosns of non-king pieces

        # Locate given player's king, and opposing player's non-king pieces
        for r in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            row = self.layout[r]
            for f in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
                piece = row[f]
                if piece is not None:
                    if (piece.color == color and
                        piece.pieceType == ChessBoard.KING):
                        myKingLoc = ChessPosn(r, f)
                    elif (piece.color != color and
                          piece.pieceType != ChessBoard.KING):

                        # Create a ChessPosn to append to the return list
                        piecePosn = ChessPosn(r, f)
                        enemyPiecePosns.append(piecePosn)
                    else:
                        pass  # This is not one of the requested pieces
        return (myKingLoc, enemyPiecePosns)

    def isLegalMove(self, color, fromPosn, toPosn):
        """Returns true if the specified move is legal

        Arguments are the same as ChessBoard.makePly

        Checks if:
         - there is a piece at the from position
         - the to position doesn't contain a piece owned by the color
         - flags don't preclude the move (i.e., castling)
         - the path to make the move is free (for bishops, rooks, queens, etc.)
         - this is a legal move for the piece pieceType
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

        # TODO (mattsh): double-check that pawns can't skip over another piece
        #                on first move

        # Pull out the (color, origin_type) entry at the from/to board position
        origin_entry = self[fromPosn]
        destin_entry = self[toPosn]

        # Check if:
        #  - there is no piece at the position
        #  - the player doesn't own a piece at the from position
        if origin_entry is None or origin_entry.color != color:
            return False

        # Number of spaces moved vertically
        rank_delta_abs = abs(toPosn.rankN - fromPosn.rankN)

        # Number of spaces moved horizontally
        file_delta_abs = abs(toPosn.fileN - fromPosn.fileN)

        # Check move legality for individual piece types
        if origin_entry.pieceType == ChessBoard.PAWN:

            # TODO (mattsh): Do you check that pawns only move forward?

            # Determine the correct starting rank and direction for each color
            pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]

            if rank_delta_abs not in [1, 2]:
                return False
            elif rank_delta_abs == 1:

                # Check if pawn is moving more than 1 space horizontally
                if file_delta_abs not in [0, 1]:
                    return False

                # Check if pawn is moving diagonally without capturing
                elif file_delta_abs == 1:

                    # Get the opposing player's color and en passant capture
                    # rank
                    oppClr = ChessBoard.getOtherColor(color)

                    if oppClr == ChessBoard.WHITE:
                        # The rank at which a pawn could capture via en passant
                        epCapRnk = ChessBoard.PAWN_STARTING_RANKS[oppClr] + 1
                    else:
                        epCapRnk = ChessBoard.PAWN_STARTING_RANKS[oppClr] - 1

                    # Get en passant flag for this file
                    epFlag = self.flag_enpassant[oppClr][toPosn.fileN]

                    # Calculate whether an en passant capture would occur
                    # in this ply
                    # TODO (mattsh): I think you may have overlooked something
                    epCaptureP = epFlag and (toPosn.rankN == epCapRnk)
                    if destin_entry is None and not epFlag:
                        return False

                elif file_delta_abs == 0 and destin_entry is not None:
                    return False  # Cannot move forward and capture

            elif rank_delta_abs == 2:
                if file_delta_abs != 0:
                    return False  # Pawns cannot move up 2 and left/right
                elif fromPosn.rankN != pawnStartRank:
                    return False  # Pawns can move two spaces only on 1st move

        elif origin_entry.pieceType == ChessBoard.ROOK:

            #check that piece either moves up/down or left/right, but not both
            if rank_delta_abs != 0 and file_delta_abs != 0:
                return False

            #check that path between origin and destination is clear
            if not ChessBoard.__isLegalMove_isClearLinearPath(self,
                                                              fromPosn,
                                                              toPosn):
                return False

        elif origin_entry.pieceType == ChessBoard.KNGT:

            # Check that destination rank is offset by 1 and file is offset by
            # 2, or vice versa.
            if  ((rank_delta_abs == 2 and file_delta_abs != 1) or
                 (rank_delta_abs == 1 and file_delta_abs != 2) or
                 (rank_delta_abs != 1 and rank_delta_abs != 2)):
                return False

        elif origin_entry.pieceType == ChessBoard.BISH:

            # Check that piece moves diagonally
            if rank_delta_abs != file_delta_abs:
                return False

            # Check that path between origin and destination is clear
            if not ChessBoard.__isLegalMove_isClearLinearPath(self,
                                                              fromPosn,
                                                              toPosn):
                return False

        elif origin_entry.pieceType == ChessBoard.QUEN:

            # Check that if piece isn't moving horizontally or vertically, it's
            # moving diagonally
            if (rank_delta_abs != 0 and file_delta_abs != 0 and
                rank_delta_abs != file_delta_abs):
                return False

            # Check that path between origin and destination is clear
            if not ChessBoard.__isLegalMove_isClearLinearPath(self,
                                                              fromPosn,
                                                              toPosn):
                return False

        elif origin_entry.pieceType == ChessBoard.KING:

            # Retrieve the kingside and queenside castle flags for this color
            castleFlagQueenside = self.flag_canCastle[color][0]
            castleFlagKingside = self.flag_canCastle[color][1]

            # Determine the locations to which the king would move if castling
            castleFileQueenside = 2
            castleFileKingside = 6
            if color == ChessBoard.WHITE:
                kingStartRank = 0
            else:
                kingStartRank = 7

            # Check that king only moves more than one square when castling
            if file_delta_abs != 1 or rank_delta_abs != 1:

                # Check for illegal kingside castle
                if (toPosn.fileN == castleFileKingside and
                    toPosn.rankN == kingStartRank):
                    if not castleFlagKingside:
                        return False

                # Check for illegal queenside castle
                elif (toPosn.fileN == castleFileQueenside and
                      toPosn.rankN == kingStartRank):
                    if not castleFlagQueenside:
                        return False

                # Otherwise, moves of more than one square are illegal
                else:
                    return False

        # If we own a piece at the destination, we cannot move there
        if destin_entry is not None and destin_entry.color == color:
            return False

        # Check that a move is being made
        elif fromPosn == toPosn:
            return False

        # Check that the proposed move is to a square on the board
        elif (toPosn.rankN not in range(0, 8) or
              toPosn.fileN not in range(0, 8)):
            return False

        # The ply could be made, but may result in a check
        else:

            # Create the board that the proposed move would result in
            boardAfterMove = self.getResultOfPly(fromPosn, toPosn)

            # Check that the king would not be in check after the move
            if boardAfterMove.isKingInCheck(color)[0]:
                return False
            else:
                return True  # All of the error checks passed

    def getResultOfPly(self, fromPosn, toPosn):
        """Returns the board object resulting from the given ply

        NOTE: Does not check legality of move, and creates a copy for operation

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: a ChessBoard object identical to that which would result from
                the given ply being made on this board"""

        # Figure out the color being moved
        color = self[fromPosn].color

        # Copy the board, so as not to modify anything real
        postMoveBoard = copy.deepcopy(self)

        # Make the proposed ply on the hypothetical board
        postMoveBoard._executePly(color, fromPosn, toPosn)
        return postMoveBoard

    def isKingInCheck(self, color):
        """Return true if color's king is in check on the given self

        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: A tuple containing two values, as follows:
                Element 0: True if the king is in check, false otherwise
                Element 1: A ChessPosn representing the
                location of a piece which is placing the king in check.
                NOTE: this is only the first such piece detected.  There may be
                others.

        Finds the location of the king of the given color, and checks whether
        any of the other player's non-king pieces could legally move to that
        location."""

        # Determine enemy player's color
        otherColor = ChessBoard.getOtherColor(color)

        # Locate given player's king, and opposing player's non-king pieces
        pieceLocations = self.__isLegalMove_findKngAndEnems(color)
        kingLoc = pieceLocations[0]
        # List of ChessPosns of pieces that may have the king
        # in check
        enemyPieceLocations = pieceLocations[1]

        # Check if any enemy piece can legally move to the king's location
        for pieceLoc in enemyPieceLocations:

            # If a move to the king's location is legal, the king is in check
            if self.isLegalMove(otherColor, pieceLoc, kingLoc):
                ChessBoard._logger.debug("Not in check")
                return (True, pieceLoc)

        # If none of the enemy pieces could move to the king's location, the
        # king is not in check
        ChessBoard._logger.debug("Found that %s is not in check", color)
        return (False, None)

    def isKingCheckmated(self, color):
        """Returns True if the given color is in checkmate on this board

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
        there is no checkmate."""

        # Get other color
        otherColor = ChessBoard.getOtherColor(color)

        # Get check information
        checkInfo = self.isKingInCheck(color)

        # Check that the king is in check
        if not checkInfo[0]:
            return False

        # TODO (James): Verify this function's functionality

        # Pull out the rank and file of the piece putting the king in check
        checkPiecePosn = checkInfo[1]

        # Find the king whose checkmate status is in question
        chkdKingLoc = self.__isLegalMove_findKngAndEnems(color)[0]

        # Get a list of locations that, if moved to, might alleviate check
        interruptLocations = ChessBoard.__isLegalMove_getInterruptSquares(
                                                             checkPiecePosn,
                                                             chkdKingLoc)
        # Get locations of all this player's non-king pieces
        myNonKingPieceLocs = self.__isLegalMove_findKngAndEnems(otherColor)[1]

        # Iterate through pieces, and see if any can move to potential check-
        # alleviating squares
        for pieceLoc in myNonKingPieceLocs:
            for intruptLoc in interruptLocations:

                # Check if the piece can move to this interrupt square
                if self.isLegalMove(color, pieceLoc,
                                    intruptLoc):

                    # Generate the board that such a move would produce
                    boardAfterMove = self.getResultOfPly(pieceLoc,
                                                          intruptLoc)
                    # Check if the given color is still in check in that board
                    # If not, that color is not in checkmate
                    if not boardAfterMove.isKingInCheck(color):
                        return False

        possibleKingMoves = []  # List of tuples of possible king moves

        # If no alleviating moves found, enumerate king's possible moves
        for r in range(chkdKingLoc.rankN - 1, chkdKingLoc.rankN + 1):
            for f in range(chkdKingLoc.fileN - 1, chkdKingLoc.fileN + 1):
                if r != chkdKingLoc.rankN or f != chkdKingLoc.fileN:

                    # Build ChessPosn object to append to list
                    kingMove = ChessPosn(r, f)
                    possibleKingMoves.append(kingMove)

        # For each possible king move, test if it is legal.
        for kingMove in possibleKingMoves:

            if self.isLegalMove(color, chkdKingLoc, kingMove):
                # Generate the board that such a move would produce
                boardAfterMove = self.getResultOfPly(chkdKingLoc, kingMove)

                # Check if the given color is still in check in that board
                # If not, that color is not in checkmate
                if not boardAfterMove.isKingInCheck(color):
                    logStrF = "Found that %s is not in checkmate"
                    ChessBoard._logger.debug(logStrF, color)
                    return False

        # All tests passed - given color is in checkmate
        ChessBoard._logger.debug("Found that %s is in checkmate", color)
        return True

    @staticmethod
    def __isLegalMove_getSquaresInPath(fromPosn, toPosn):
        """Returns a list of squares in the straight path from origin to dest

        NOTE: Return path does not include the origin or destination

        Returns an empty list if no straight-line path exists.

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: A list of ChessPosn objects representing squares in the path
        from origin to destination, not including the origin or destination"""

        # Number of spaces moved vertically
        rank_delta_abs = abs(toPosn.rankN - fromPosn.rankN)

        # Number of spaces moved horizontally
        file_delta_abs = abs(toPosn.fileN - fromPosn.fileN)
        path_rank_values = []  # Rank values of squares that must be open
        path_file_values = []  # File values of squares that must be open

        # Determine step values to use in range finding

        if toPosn.rankN > fromPosn.rankN:
            rankStep = 1
        else:
            rankStep = -1

        if toPosn.fileN > fromPosn.fileN:
            fileStep = 1
        else:
            fileStep = -1

        # Check if the path is diagonal
        if rank_delta_abs == file_delta_abs:
            # Build up lists of rank and file values to be included in path
            for r in range(fromPosn.rankN, toPosn.rankN, rankStep):
                # Check that include origin or dest is not included
                if r not in [fromPosn.rankN, toPosn.rankN]:
                    path_rank_values.append(r)

            for f in range(fromPosn.fileN, toPosn.fileN, fileStep):
                if f not in [fromPosn.fileN, toPosn.fileN]:
                    path_file_values.append(f)

        #Check if the path is horizontal
        elif rank_delta_abs == 0:
            # Build up lists of rank and file values to be included in path
            for f in range(fromPosn.fileN, toPosn.fileN, fileStep):
                # Check that origin and destination are not included
                if f not in [fromPosn.fileN, toPosn.fileN]:
                    path_file_values.append(f)
            path_rank_values = [fromPosn.rankN] * len(path_file_values)

        #Check if the path is vertical
        elif rank_delta_abs != 0:
            #Build up lists of rank and file values to be included in path
            for r in range(fromPosn.rankN, toPosn.rankN, rankStep):
                # Check that origin and destination aren't included
                if r not in [fromPosn.rankN, toPosn.rankN]:
                    path_rank_values.append(r)
            path_file_values = [fromPosn.fileN] * len(path_rank_values)

        # If the path is not straight-line, return the empty list
        else:
            return []

        # Combine rank and file lists into list of tuples (rank, file)
        pathSquares = zip(path_rank_values, path_file_values)

        # Build list of posns out of zipped tuples
        pathPosns = []

        for square in pathSquares:
            # Create a new posn and append it to the accumulator
            posn = ChessPosn(square[0], square[1])
            pathPosns.append(posn)

        return pathPosns


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

    def getColorOfPlayer(self, playerID):
        """Returns the color of the player (None if player is not in game)"""
        if playerID == self.players[ChessBoard.WHITE]:
            return ChessBoard.WHITE
        elif playerID == self.players[ChessBoard.BLACK]:
            return ChessBoard.BLACK
        else:
            return None

    def makePly(self, player, fromPosn, toPosn):
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

            if self.board.makePly(color, fromPosn, toPosn):
                # Check for checkmates
                if self.board.isKingCheckmated(ChessBoard.WHITE):
                    self.status = ChessMatch.STATUS_BLACK_WON
                elif self.board.isKingCheckmated(ChessBoard.BLACK):
                    self.status = ChessMatch.STATUS_WHITE_WON
                else:
                    self.history.append((fromPosn, toPosn))

                    # Log this ply
                    logStrF = "Added %s -> %s to match history"
                    ChessMatch._logger.debug(logStrF,
                                             fromPosn, toPosn)
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

        elif playerID in self.players.itervalues():
            return  # Don't allow a player to play both sides
        else:
            for color in [ChessBoard.WHITE, ChessBoard.BLACK]:
                if self.players[color] is None:
                    self.players[color] = playerID
                    if None not in self.players.itervalues():
                        self.status = ChessMatch.STATUS_ONGOING
                    return color
            ChessMatch._logger.debug("Joined player %d to this game", playerID)


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
