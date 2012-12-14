#!/usr/bin/python
"""maverick.data.structs: common data structures for chess games"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

# # TODO (James): For ALL MAVERICK CODE - license as BeerWare

import copy
import logging
import random

__all__ = ["ChessBoard",
           "ChessMatch",
           "ChessPiece",
           "ChessPosn"]


class MaverickDataException(Exception):
    """Base class for maverick data representation exceptions"""
    pass


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
        if isinstance(other, ChessPosn):
            return (self.rankN == other.rankN and
                    self.fileN == other.fileN)
        elif isinstance(other, tuple):
            return (len(other) == 2 and
                    self.__eq__(ChessPosn(other[0], other[1])))
        else:
            return False

    def getTranslatedBy(self, deltaRank, deltaFile):
        """Return new ChessPosn translated by the coordinates provided"""
        return ChessPosn(self.rankN + deltaRank, self.fileN + deltaFile)


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

    # TODO (mattsh): Represent threefold repetition draw rule

    # TODO (mattsh): getPlyResult, unGetPlyResult should use with syntax
    #                http://www.python.org/dev/peps/pep-0343/

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.structs.ChessBoard")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    BOARD_LAYOUT_SIZE = 8
    """The width and height of a standard chess board layout."""

    # Constants for the colors
    BLACK = "B"
    """Constant for the black player"""

    WHITE = "W"
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
                 startCanCastleFlags=None,
                 drawCounter=0):
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

        # Assign draw counter
        self.drawCounter = drawCounter

    def __getitem__(self, posn):
        """x.__getitem__(y) <==> x[y]

        Gets the piece object for the given position,
        None if given a position off the board"""
        if (posn.rankN in xrange(ChessBoard.BOARD_LAYOUT_SIZE) and
            posn.fileN in xrange(ChessBoard.BOARD_LAYOUT_SIZE)):
            return self.layout[posn.rankN][posn.fileN]
        else:
            return None

    def __setitem__(self, posn, piece):
        """x.__setitem__(i, y) <==> x[i]=y

        Sets the piece object at the given position"""
        self.layout[posn.rankN][posn.fileN] = piece

    def _executePly(self, color, fromPosn, toPosn):
        """Make a ply on this board, assuming that it is legal

        Arguments  are the same as makePly for a legal move

        @return: A list of (ChessPiece, ChessPosn) tuples mapping
                pieces moved by this function to their original locations"""

        # Remove moving piece from starting position
        movedPiece = self[fromPosn]
        self[fromPosn] = None

        otherColor = ChessBoard.getOtherColor(color)

        # Accumulator for return value
        movedList = [(movedPiece, fromPosn)]

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

        # Update 50-move counter
        if movedPiece == ChessBoard.PAWN or self[toPosn] is not None:
            self.drawCounter = 0
        self.drawCounter += 1

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

        # Move piece to destination, noting what was originally there
        movedList.append((self[toPosn], toPosn))

        # Preemptively reset en passant flags, if necessary
        if (self[toPosn] is not None and
            self[toPosn].pieceType == ChessBoard.PAWN):
            self.flag_enpassant[otherColor][toPosn.fileN] = False

        # Actually move the piece
        self[toPosn] = movedPiece

        # Handle rook movement if castling

        # Check whether this ply is a castle
        if movedPiece.pieceType == ChessBoard.KING and abs(fileDelta) == 2:
            # Find posn of the rook to be moved

            # Check if this was a kingside castle
            if fileDelta > 0:
                movedRookPosn = ChessPosn(toPosn.rankN, 7)
                rookDestPosn = ChessPosn(toPosn.rankN, 5)

            # Else, this was a queenside castle
            else:
                movedRookPosn = ChessPosn(toPosn.rankN, 0)
                rookDestPosn = ChessPosn(toPosn.rankN, 3)

            # Move the rook, noting what was originally at its position

            movedList.append((self[rookDestPosn], rookDestPosn))
            movedRook = self[movedRookPosn]
            self[movedRookPosn] = None
            self[rookDestPosn] = movedRook

            # Note this movement
            movedList.append((movedRook, movedRookPosn))

        # Remove en passant pawns, if relevant

        if movedPiece.pieceType == ChessBoard.PAWN:
            # Build up information for en passant capture check

            # The normal direction for pawns of the color
            pawnMoveDir = 1 if otherColor == ChessBoard.WHITE else -1

            # The rank at which a pawn could capture via en passant
            epCapRnk = ChessBoard.PAWN_STARTING_RANKS[otherColor] + pawnMoveDir

            # Location of the pawn being captured
            pawnPosn = ChessPosn(epCapRnk + pawnMoveDir, toPosn.fileN)

            # Check whether a pawn was captured by en passant
            if (self.flag_enpassant[otherColor][toPosn.fileN] and
                toPosn.rankN == epCapRnk):

                    # If a pawn was captured, note this and remove it
                    movedList.append((self[pawnPosn], pawnPosn))

                    self[pawnPosn] = None

                    # Reset the en passant flag, pre-emptively
                    self.flag_enpassant[otherColor][toPosn.fileN] = False

        # Log the successful move
        logStrF = "Moved piece from %s, to %s"
        ChessBoard._logger.debug(logStrF, fromPosn, toPosn)

        return movedList

    def makePly(self, color, fromPosn, toPosn):
        """Make a ply on this board if legal

        @param color: the color making the move (BLACK or WHITE constant)
        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: A tuple of the following form:
                (True if the move was successful, False otherwise,
                True if progress toward Draw was made, False otherwise)

        - Checks if the move is legal
        - Removes the moving piece from the starting position
        - Updates flags if necessary
        - Adds the moving piece to the ending position (possibly overwriting)
        - Deletes pawns in en passant state if relevant
        - Moves the rook as well if the king is castling"""

        # Check if the move is legal
        isLegal = self.isLegalMove(color, fromPosn, toPosn)

        # Move iff the move is legal
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
            fStr = "ChessBoard({}={},{}={},{}={})"
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

            letters = [""] + list(ChessBoard.HUMAN_FILE_LETTERS)
        else:
            iterStart = 0
            iterStop = ChessBoard.BOARD_LAYOUT_SIZE
            iterStep = 1

            letters = list(ChessBoard.HUMAN_FILE_LETTERS) + [""]
            letters.reverse()

        boardSep = " | "
        header = "    ".join(letters)
        barrier = "  -----------------------------------------"

        boardStrA = []
        boardStrA.append(header)
        boardStrA.append(barrier)
        for rankN in xrange(iterStart, iterStop, iterStep):
            fStr = "{1}{0}{2}{0}{1}"
            pieceLetters = [ChessBoard.__str_getPieceChar(c)
                            for c in self.layout[rankN]]
            if not whitePerspective:
                pieceLetters.reverse()
            rS = fStr.format(boardSep, rankN + 1, boardSep.join(pieceLetters))
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

    def __isLegal_isClearLinearPath(self, fromPosn, toPosn):
        """True if there is a clear straight path from origin to destination

        To be used for horizontal, vertical, or diagonal moves.

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: True if the path is clear, False if it is obstructed, or is
        not a straight-line path.

        Builds a list of the rank and file values of squares to check for
        clarity, then checks them all for clarity."""

        # Get the squares in the path, if there is one
        pathPosns = ChessBoard.__isLegal_getSquaresInPath(fromPosn, toPosn)

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
    def __isLegal_getInterruptSquares(fromPosn, toPosn):
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
        pathSquares = ChessBoard.__isLegal_getSquaresInPath(fromPosn, toPosn)

        interruptSquares += (pathSquares)

        return interruptSquares

    def __isLegalMove_findKings(self, color):
        """Return the locations of the given color king, as a ChessPosn

        @param color: The color of the king to find
        @return: the location of the king of the given color, as a ChessPosn"""

        # Locate given player's king
        for r in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            for f in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
                piecePosn = ChessPosn(r, f)
                piece = self[piecePosn]
                if (piece is not None and
                    piece.pieceType == ChessBoard.KING and
                    piece.color == color):
                        return piecePosn

        # Raise exception - we have a deficit of kings
        raise MaverickDataException("No King of given color found")

    def __isLegal_IsPieceMovementInPattern(self, color, fromPosn, toPosn):
        """Check whether the given move is possible for the piece at the origin

        NOTE: Does not apply all move legality checks - the checks for moves
        resulting in a check state are done in isLegalMove

        Returns true if the given move is possible considering the movement
        pattern of the piece at fromPosn, false otherwise.

        @param color: The color of the player making the move
        @param fromPosn: The location of the piece being moved
        @param toPosn: The location to which the piece is being moved

        @return: True if the move is possible for the given piece, False
                otherwise"""

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

        if origin_entry.pieceType == ChessBoard.PAWN:
            ChessBoard._logger.debug("Found moved piecetype to be PAWN")

            # Determine the correct starting rank and direction for each color
            pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]

            # The vertical distance being moved by this pawn
            vertDist = toPosn.rankN - fromPosn.rankN

            # Check that pawns only move forward
            if ((color == ChessBoard.WHITE and vertDist < 0) or
                (color == ChessBoard.BLACK and vertDist > 0)):
                ChessBoard._logger.debug("Illegal backward movement")
                return False

            if rank_delta_abs not in [1, 2]:
                ChessBoard._logger.debug("Illegal forward move distance")
                return False
            elif file_delta_abs == 0 and destin_entry is not None:
                ChessBoard._logger.debug("Illegal forward capture")
                return False  # Cannot move forward and capture
            elif rank_delta_abs == 1:

                # Check if pawn is moving more than 1 space horizontally
                if file_delta_abs not in [0, 1]:
                    ChessBoard._logger.debug("Illegal horiz. move distance")
                    return False

                # Check if pawn is moving diagonally without capturing
                elif file_delta_abs == 1:

                    # Get the opposing player's color and en passant capture
                    # rank
                    oppClr = ChessBoard.getOtherColor(color)

                    # Find the rank at which a pawn could capture by en passant
                    if oppClr == ChessBoard.WHITE:
                        epCapRnk = ChessBoard.PAWN_STARTING_RANKS[oppClr] + 1
                    else:
                        epCapRnk = ChessBoard.PAWN_STARTING_RANKS[oppClr] - 1

                    # Get en passant flag for destination file
                    epFlag = self.flag_enpassant[oppClr][toPosn.fileN]

                    # Calculate whether an en passant capture would occur
                    # in this ply
                    epCaptureP = epFlag and (toPosn.rankN == epCapRnk)
                    if destin_entry is None and not epCaptureP:
                        ChessBoard._logger.debug("Illegal horiz. move")
                        return False

            elif rank_delta_abs == 2:
                ChessBoard._logger.debug("Pawn moving forward two spaces")
                if file_delta_abs != 0:
                    ChessBoard._logger.debug("Illegal horiz. move")
                    return False  # Pawns cannot move up 2 and left/right
                elif fromPosn.rankN != pawnStartRank:
                    ChessBoard._logger.debug("Illegal forward move")
                    return False  # Pawns can move two spaces only on 1st move
                elif not ChessBoard.__isLegal_isClearLinearPath(self,
                                                                fromPosn,
                                                                toPosn):
                    ChessBoard._logger.debug("Illegal move over piece")
                    return False  # Pawns can't fly over other pieces

        elif origin_entry.pieceType == ChessBoard.ROOK:
            ChessBoard._logger.debug("Found moved piecetype to be ROOK")

            # check that piece either moves up/down or left/right, but not both
            if rank_delta_abs != 0 and file_delta_abs != 0:
                ChessBoard._logger.debug("Illegal diagonal move")
                return False

            # check that path between origin and destination is clear
            if not ChessBoard.__isLegal_isClearLinearPath(self,
                                                          fromPosn, toPosn):
                ChessBoard._logger.debug("Illegal move over piece")
                return False

        elif origin_entry.pieceType == ChessBoard.KNGT:
            ChessBoard._logger.debug("Found moved piecetype to be KNGT")

            # Check that destination rank is offset by 1 and file is offset by
            # 2, or vice versa.
            if  ((rank_delta_abs == 2 and file_delta_abs != 1) or
                 (rank_delta_abs == 1 and file_delta_abs != 2) or
                 (rank_delta_abs != 1 and rank_delta_abs != 2)):
                ChessBoard._logger.debug("Non L-shaped move")
                return False

        elif origin_entry.pieceType == ChessBoard.BISH:
            ChessBoard._logger.debug("Found moved piecetype to be BISH")

            # Check that piece moves diagonally
            if rank_delta_abs != file_delta_abs:
                ChessBoard._logger.debug("Illegal non-diagonal move")
                return False

            # Check that path between origin and destination is clear
            elif not ChessBoard.__isLegal_isClearLinearPath(self,
                                                            fromPosn, toPosn):
                ChessBoard._logger.debug("Illegal move over piece")
                return False

        elif origin_entry.pieceType == ChessBoard.QUEN:
            ChessBoard._logger.debug("Found moved piecetype to be QUEN")

            # Check that if piece isn't moving horizontally or vertically, it's
            # moving diagonally
            if (rank_delta_abs != 0 and
                file_delta_abs != 0 and
                rank_delta_abs != file_delta_abs):

                ChessBoard._logger.debug("Illegal move path shape")
                return False

            # Check that path between origin and destination is clear
            elif not ChessBoard.__isLegal_isClearLinearPath(self,
                                                            fromPosn, toPosn):
                ChessBoard._logger.debug("Illegal move over piece")
                return False

        elif origin_entry.pieceType == ChessBoard.KING:
            ChessBoard._logger.debug("Found moved piecetype to be KING")

            # Retrieve the kingside and queenside castle flags for this color
            castleFlagQueenside = self.flag_canCastle[color][0]
            castleFlagKingside = self.flag_canCastle[color][1]

            # Determine the locations to which the king would move if castling
            castleFileQueenside = 2
            castleFileKingside = 6
            kingStartRank = 0 if color == ChessBoard.WHITE else 7

            # Check that king only moves more than one square when castling
            if file_delta_abs not in [0, 1] or rank_delta_abs not in [0, 1]:

                # Check for illegal kingside castle
                if (toPosn == ChessPosn(castleFileKingside, kingStartRank)):
                    if not castleFlagKingside:
                        ChessBoard._logger.debug("Illegal kingside castle")
                        return False

                # Check for illegal queenside castle
                elif (toPosn == ChessPosn(castleFileQueenside, kingStartRank)):
                    if not castleFlagQueenside:
                        ChessBoard._logger.debug("Illegal queenside castle")
                        return False

                # Otherwise, moves of more than one square are illegal
                else:
                    ChessBoard._logger.debug("Illegal move distance")
                    return False

        # All of the checks passed
        return True

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

        # TODO: can color be checked a level up in the makePly function,
        #       allowing isLegalMove to not take in the color?

        if not self.__isLegal_IsPieceMovementInPattern(color,
                                                           fromPosn, toPosn):
            return False

        # If we own a piece at the destination, we cannot move there
        elif self[toPosn] is not None and self[toPosn].color == color:
            ChessBoard._logger.debug("Illegal friendly piece capture")
            return False

        # If the move is to a king's position, it is illegal (this is a handler
        # for checkmates at the board level, basically)
        elif (self[toPosn] is not None and
            self[toPosn].pieceType == ChessBoard.KING):
            ChessBoard._logger.debug("Can't take king (should be impossible)")
            return False

        # Check that a move is being made
        elif fromPosn == toPosn:
            ChessBoard._logger.debug("Illegal 0-distance move")
            return False

        # Check that the proposed move is to a square on the board
        elif (toPosn.rankN not in range(0, 8) or
              toPosn.fileN not in range(0, 8)):
            ChessBoard._logger.debug("Illegal move off of board")
            return False

        # The ply could be made, but may result in a check
        else:
            # Create the board that the proposed move would result in
            boardMoveUndoDict = self.getPlyResult(fromPosn, toPosn)

            # Check that the king would not be in check after the move
            ChessBoard._logger.debug("Checking for move to in-check state")

            # Restore the old board state (prior to hypothesization)
            self.undoPlyResult(boardMoveUndoDict)

            # Perform the check
            if self.pieceCheckingKing(color) is not None:
                ChessBoard._logger.debug("Illegal move to in-check state")
                return False
            else:
                return True  # All of the error checks passed

    def getPlyResult(self, fromPosn, toPosn):
        """Returns the board object resulting from the given ply

        WARNING: Modifies the state of the board - be sure to call
                 undoPlyResult to restore board state

        NOTE: Does not check legality of move

        @param fromPosn: a ChessPosn representing the origin position
        @param toPosn: a ChessPosn representing the destination position

        @return: a dictionary of the following form:
                {"oldCastleFlags": the original castle flags of this board,
                "oldEnPassantFlags": the original enpassant flags,
                "movedPieces" A list of (ChessPiece, ChessPosn) tuples mapping
                pieces moved by this function to their original locations}

                This dictionary can be supplied as an argument to
                undoPlyResult to restore board state"""

        # Figure out the color being moved
        color = self[fromPosn].color

        # Accumulator for return value
        returnDict = {}

        returnDict['oldCastleFlags'] = self.flag_canCastle.copy()
        returnDict['oldEnPassantFlags'] = self.flag_enpassant.copy()

        # Make the proposed ply on the hypothetical board
        returnDict['movedPieces'] = self._executePly(color, fromPosn, toPosn)
        return returnDict

    # TODO (mattsh): rename this and getPlyResult to a better name
    def undoPlyResult(self, undoDict):
        """Undoes the call to getPlyResult described in the given undoDict

        NOTE: This function should only be used to undo a call to
            getPlyResult. There is no reason to ever call it if
            getPlyResult wasn't ever called first

        @param undoDict: a dictionary of the following form:
                {"oldCastleFlags": the original castle flags of this board,
                "oldEnPassantFlags": the original enpassant flags,
                "movedPieces" A list of (ChessPiece, ChessPosn) tuples mapping
                pieces moved by this function to their original locations}
                As produced by a call to getPlyResult"""

        self.flag_canCastle = undoDict['oldCastleFlags']
        self.flag_enpassant = undoDict['oldEnPassantFlags']

        for pieceRestoration in undoDict['movedPieces']:
            self[pieceRestoration[1]] = pieceRestoration[0]

    def pieceCheckingKing(self, color):
        """Return whether the color's king is in check on this board

        @param color: The color of the king to check, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: If king is in check, return a posn of a piece causing this.
                 Otherwise, return None.
                 NOTE: multiple pieces may cause check but only one is returned

        Finds the location of the king of the given color, and checks whether
        any of the other player's non-king pieces could legally move to that
        location."""

        # Locate given player's king
        kingPosn = self.__isLegalMove_findKings(color)

        # Check if any enemy piece can legally move to the king's location
        other = ChessBoard.getOtherColor(color)  # Determine enemy's color
        for loc in self.getPiecesOfColor(other):
            # If a move to the king's location is legal, the king is in check
            if self.__isLegal_IsPieceMovementInPattern(other, loc, kingPosn):
                ChessBoard._logger.debug("Found that %s is in check", color)
                return loc

        # If 0 of enemy's pieces can move to king's location, king not in check
        ChessBoard._logger.debug("Found that %s is not in check", color)
        return None

    def getPiecesOfColor(self, color):
        """Return a list of positions where the given color has pieces

        @param color: color of the pieces to find

        @return: a list of ChessPosns enumerating pieces of the given color"""

        pieceLocations = []
        for rankN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            for fileN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
                posn = ChessPosn(rankN, fileN)
                piece = self[posn]
                if piece is not None and piece.color == color:
                    pieceLocations.append(posn)
        return pieceLocations

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

        # Pull out the rank and file of piece checking king if any
        checkPiecePosn = self.pieceCheckingKing(color)

        # Check that the king is in check
        if checkPiecePosn is None:
            return False

        # TODO (James): Verify this function's functionality

        # Find the king whose checkmate status is in question
        chkdKingLoc = self.__isLegalMove_findKings(color)

        # Get a list of locations that, if moved to, might alleviate check
        interruptLocations = ChessBoard.__isLegal_getInterruptSquares(
                                                             checkPiecePosn,
                                                             chkdKingLoc)
        # Get locations of all this player's non-king pieces
        myPieceLocs = self.getPiecesOfColor(color)

        # Iterate through pieces, and see if any can move to potential check-
        # alleviating squares
        for pieceLoc in myPieceLocs:
            if pieceLoc != chkdKingLoc:
                for intrpt in interruptLocations:

                    # Check if the piece can move to this interrupt square
                    if self.isLegalMove(color, pieceLoc, intrpt):

                        # Generate the board that such a move would produce
                        boardMoveUndoDict = self.getPlyResult(pieceLoc, intrpt)
                        # Check if the given color is still in check
                        # If not, that color is not in checkmate

                        isNotInCheck = self.pieceCheckingKing(color) is None

                        # Undo the hypothetical move
                        self.undoPlyResult(boardMoveUndoDict)

                        # Perform the check
                        if isNotInCheck:
                            return False

        possibleKingMoves = []  # List of tuples of possible king moves

        # If no alleviating moves found, enumerate king's possible moves
        for r in range(chkdKingLoc.rankN - 1, chkdKingLoc.rankN + 2):
            for f in range(chkdKingLoc.fileN - 1, chkdKingLoc.fileN + 2):
                kingMove = ChessPosn(r, f)
                # Build ChessPosn object to append to list
                if kingMove != chkdKingLoc:
                    possibleKingMoves.append(kingMove)

        # For each possible king move, test if it is legal.
        for kingMove in possibleKingMoves:

            if self.isLegalMove(color, chkdKingLoc, kingMove):
                # Generate the board that such a move would produce
                boardMoveUndoDict = self.getPlyResult(chkdKingLoc, kingMove)

                # Restore the previous state of the board
                self.undoPlyResult(boardMoveUndoDict)

                # Check if the given color is still in check after the move
                if self.pieceCheckingKing(color) is None:
                    logStrF = "Found that %s is not in checkmate"
                    ChessBoard._logger.debug(logStrF, color)
                    return False

        # No possible moves out of check - given color is in checkmate
        ChessBoard._logger.debug("Found that %s is in checkmate", color)
        return True

    @staticmethod
    def __isLegal_getSquaresInPath(fromPosn, toPosn):
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
        rankStep = 1 if toPosn.rankN > fromPosn.rankN else -1
        fileStep = 1 if toPosn.fileN > fromPosn.fileN else -1

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

        # Check if the path is horizontal
        elif rank_delta_abs == 0:
            # Build up lists of rank and file values to be included in path
            for f in range(fromPosn.fileN, toPosn.fileN, fileStep):
                # Check that origin and destination are not included
                if f not in [fromPosn.fileN, toPosn.fileN]:
                    path_file_values.append(f)
            path_rank_values = [fromPosn.rankN] * len(path_file_values)

        # Check if the path is vertical
        elif rank_delta_abs != 0:
            # Build up lists of rank and file values to be included in path
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


class ChessBoardUtils(object):
    """Utilities for use with given ChessBoard objects"""

    @staticmethod
    def findPiecePosnsByColor(board, color):
        """Return a list of positions where the given color has pieces

        @param board: The board to use for this check.
        @param color: The color of the pieces to find, ChessMatch.WHITE or
        ChessMatch.BLACK

        @return: a list of ChessPosns representing
                the location of all pieces of the given color"""

        pieceLocations = []

        for r in range(ChessBoard.BOARD_LAYOUT_SIZE):
            row = board.layout[r]
            for f in range(ChessBoard.BOARD_LAYOUT_SIZE):
                piece = row[f]
                if piece is not None:
                    if piece.color == color:
                        # Build ChessPosn for piece location
                        pieceLocations.append(ChessPosn(r, f))
        return pieceLocations

class ChessMatch(object):
    """Represents a chess game in Maverick"""

    # Initialize class logger
    _logger = logging.getLogger("maverick.data.structs.ChessMatch")
    _logger.setLevel("INFO")

    # Constants for game status
    STATUS_PENDING = "PENDING"  # Game is waiting for players
    STATUS_ONGOING = "ONGOING"  # Game is in progress
    STATUS_BLACK_WON = "W_BLACK"  # Black won the game
    STATUS_WHITE_WON = "W_WHITE"  # White won the game
    STATUS_DRAWN = "W_DRAWN"  # White won the game
    STATUS_CANCELLED = "CANCELD"  # Game was halted early

    def __init__(self, firstPlayerID=None, p1ReqFreshStart=True):
        """Initialize a new chess match with initial state

        @param firstPlayerID: if set, randomly assigned to black or white"""
        # TODO: ## TODO p1ReqFreshStart

        # Initialize blankly (new chess board when both players have joined)
        self.board = None

        # Initialize match without players (whose playerIDs can be added later)
        self.players = {ChessBoard.WHITE: None, ChessBoard.BLACK: None}

        # Randomly set black or white to firstPlayerID (no-op if not specified)
        self.players[random.choice(self.players.keys())] = firstPlayerID

        # Initialize match status
        self.status = ChessMatch.STATUS_PENDING

        # Initialize ply history -- a list of (moveFrom, moveTo) plies
        self.history = []

        # True if game should start with a blank board
        self.freshStartP = p1ReqFreshStart

        # Number of moves remaining until 50-move draw kicks in
        self.drawCounter = 50

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

            moveLegal = self.board.makePly(color, fromPosn, toPosn)

            # Check if move was made
            if moveLegal:
                # Log this ply
                self.history.append((fromPosn, toPosn))
                logStrF = "Added %s -> %s to match history"
                ChessMatch._logger.debug(logStrF, fromPosn, toPosn)

                # Check for check-mates, draws, etc
                ChessMatch._logger.debug("Checking for end of game")
                if self.board.isKingCheckmated(ChessBoard.WHITE):
                    self.status = ChessMatch.STATUS_BLACK_WON
                elif self.board.isKingCheckmated(ChessBoard.BLACK):
                    self.status = ChessMatch.STATUS_WHITE_WON
                elif self.__makePly_forcedDrawP():
                    self.status = ChessMatch.STATUS_DRAWN

                return "SUCCESS"
            else:
                return "Illegal move"
        else:
            return "Game not in progress"

    def __makePly_forcedDrawP(self):
        # 51 rather than 50 to allow for the player to check-mate on 50th move
        # After that, a smart player would have asked for a draw if beneficial
        fiftyMovesDraw = self.board.drawCounter >= 51

        # TODO (mattsh): also check for three-fold repetition
        threeFoldRepetition = False

        return fiftyMovesDraw or threeFoldRepetition

    def join(self, playerID, p2ReqFreshStart=True):
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

                        self.freshStartP = self.freshStartP or p2ReqFreshStart
                        if self.freshStartP:
                            self.board = ChessBoard()
                        else:
                            ###################################################
                            ###################################################
                            ## This only exists because our AI is tuned solely
                            ## for mid-game situations
                            ###################################################
                            ###################################################
                            from maverick.data.utils import getMidGameBoard
                            self.board = getMidGameBoard()
                            del getMidGameBoard
                    retVal = color
            ChessMatch._logger.debug("Joined player %d to this game", playerID)
            return retVal


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
