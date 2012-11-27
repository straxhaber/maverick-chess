#!/usr/bin/python
"""maverick.data.utils: useful operators for the chess structs"""

__author__ = "Matthew Strax-Haber, James Magnarelli, and Brad Fournier"
__version__ = "1.0"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import random

from maverick.data.structs import ChessBoard
from maverick.data.structs import ChessPiece
from maverick.data.structs import ChessPosn

__all__ = ["genRandomLegalBoard"]


def genRandomLegalBoard():
    """Returns a random ChessBoard object  with neither king in check

    @return: a ChessBoard object with a subset of the standard pieces
            where neither king is in check"""

    # # TODO (James): get this working for test board generation

    # Mapping of piece types to tuples of form (max number,
    #                    probability that one is placed at each iteration)
    boardPieces = {ChessBoard.KING: (1, 1),
                   ChessBoard.PAWN: (8, 0.5),
                   ChessBoard.ROOK: (2, 0.3),
                   ChessBoard.KNGT: (2, 0.4),
                   ChessBoard.BISH: (2, 0.3),
                   ChessBoard.QUEN: (1, 0.7)}

    emptyStartLayout = [[None] * 8] * 8
    # The board to be built up
    board = ChessBoard(startLayout=emptyStartLayout)

    # Keep track of the remaining empty posns
    emptyPosns = []
    for r in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
        for f in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            emptyPosns.append(ChessPosn(r, f))

    # Note the number of kings on the board.  Cannot check for check until
    # kings are placed
    numKingsPlaced = 0

    for color in [ChessBoard.WHITE, ChessBoard.BLACK]:
        otherColor = ChessBoard.getOtherColor(color)
        for pieceType, placementTuple in boardPieces.iteritems():
            numPcsToPlace = placementTuple[0]

            # Try to place the specified number of pieces
            while numPcsToPlace > 0:
                randNum = random.random()
                placementChance = placementTuple[1]
                if randNum <= placementChance:
                    # Choose a remaining empty posn and place this piece
                    emptyPosnIdx = random.randrange(0, len(emptyPosns))
                    placementPosn = emptyPosns[emptyPosnIdx]
                    # If this is an illegal placement, try again
                    # But don't bother checking if we haven't placed kings
                    if ((numKingsPlaced == 2) and
                        ## TODO: should this check is None or is not None?
                        board.pieceCheckingKing(otherColor) is None):
                        break
                    else:
                        if pieceType == ChessBoard.KING:
                            numKingsPlaced += 1

                        # Place the piece and note the posn is non-empty

                        board[placementPosn] = ChessPiece(color, pieceType)
                        del emptyPosns[emptyPosnIdx]
                numPcsToPlace -= 1

    return board