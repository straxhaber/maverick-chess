#!/usr/bin/python

"""quiescenceSearchAI.py: AI that uses a quiescence search with heuristics"""

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

from __future__ import division

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
import copy
import logging

from maverick.players.ais.common import MaverickAI
from maverick.data import ChessBoard
from maverick.data import ChessBoardUtils
from maverick.data import ChessPosn

## TODO (James): Make sure that heuristic functions to return an int in [-1..1]

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"
__all__ = ["QLAI", "runAI"]


class QLAI(MaverickAI):
    """Represents a quiescence search-based AI for use with Maverick"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.quiescenceSearchAI.QLAI")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    # Standard piece values, from
    # http://en.wikipedia.org/wiki/Chess_piece_values
    _pieceValues = {ChessBoard.PAWN: 1,
                    ChessBoard.KNGT: 3,
                    ChessBoard.BISH: 3,
                    ChessBoard.ROOK: 5,
                    ChessBoard.QUEN: 9,
                    ChessBoard.KING: 0}
    """Point values for all pieces. King's value is reflected in checkmate"""

    _maxTotalPieceVal = 39
    """The sum of piece values for a full set of one player's chess pieces"""

    def getNextMove(self, board):
        """TODO PyDoc"""

        # Figure out our color
        if self.isWhite:
            color = ChessBoard.WHITE
        else:
            color = ChessBoard.BLACK

        moveChoices = self.enumBoardMoves(board, color)

        # TODO (mattsh): write this
        (fromPosn, toPosn) = (None, None)

        return (fromPosn, toPosn)

    @staticmethod
    def __heuristicEmptySpaceCoverage_isCenterSquare(square):
        """Return true if the given position is a center square

        Center squares are those that are one of D4,D5,E4,E5

        @param square: A ChessPosn representing the square to be evaluated

        @return: True if the given position is a center square, False
                otherwise"""

        return square.rankN in [3, 4] and square.fileN in [3, 4]

    def _heuristicPieceValue(self, color, board):
        """Return the total value of color's pieces on the given board.

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        Note that the king's value is not included - the undesirability of the
        king's capture is handled elsewhere by checkmate checks."""

        # Locate all of this color's pieces
        piecePosns = ChessBoardUtils.findPiecePosnsByColor(board, color)

        # Loop through this color's pieces, adding to total value
        totalValue = sum([QLAI._pieceValues[board[posn].pieceType]
                          for posn in piecePosns])

        # Compress return value into range [-1..1]
        halfMaxVal = QLAI._maxTotalPieceVal / 2
        return (totalValue - halfMaxVal) / halfMaxVal

    def _heuristicInCheck(self, color, board):
        """Return -1 if the given color king is in check on the given board

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: -1 if the given color is in check on the given board, 1
                otherwise"""

        if board.isKingInCheck(color)[0]:
            return -1
        else:
            return 1

    def _heuristicPiecesUnderAttack(self, color, board):
        """Return the value of the given color's pieces that are under attack

        @param color: The color of the pieces to test -
                    one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: A number representing the value of the given color's
                pieces that are under attack, weighted by piece value"""

        otherColor = ChessBoard.getOtherColor(color)

        # Get friendly pieces
        attackingPiecePosns = ChessBoardUtils.findPiecePosnsByColor(board,
                                                                    otherColor)

        # Get enemy pieces
        attackedPiecePosns = ChessBoardUtils.findPiecePosnsByColor(board,
                                                                   color)

        # Record which enemy pieces are under attack
        piecesUnderAttack = []

        # For each enemyPiece, check whether any friendlyPiece can capture it
        for attackedPiecePosn in attackedPiecePosns:

            for attackingPiecePosn in attackingPiecePosns:

                # Check if this piece can capture the enemy piece
                if board.isLegalMove(otherColor,
                                     attackingPiecePosn,
                                     attackedPiecePosn):

                    # Note that this enemyPiece is under attack
                    piecesUnderAttack.append(attackedPiecePosn)
                    # Each piece can only be attacked once, so break here
                    break

        # Sum weighted values of under-attack pieces
        weightedTotal = 0
        for piecePosn in piecesUnderAttack:

            piece = board[piecePosn]
            # Check if there is a value for this piece in the mappings
            if piece.pieceType in QLAI._pieceValues:
                weightedTotal += QLAI._pieceValues[piece.pieceType]

        # Compress return value into range [-1..1]
        return 1 - 2 * (weightedTotal / QLAI._maxTotalPieceVal)

    def _heuristicEmptySpaceCoverage(self, color, board):
        """Return a value representing the number of empty squares controlled

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: a value representing the number of empty squares that the
                given color can attack on the given board, with weight for
                center squares"""

        # The value of regular and center squares
        ## TODO (James): research and tweak these.
        #                See http://tinyurl.com/cpjqnw4l
        centerSquareValue = 2
        squareValue = 1

        # Build up a list of all piece locations as tuples

        pieceLocations = []
        otherColor = ChessBoard.getOtherColor(color)

        # Find friendly piece locations and add to pieceLocations
        friendPiecePosns = ChessBoardUtils.findPiecePosnsByColor(board, color)

        for piecePosn in friendPiecePosns:
            pieceLocations.append(piecePosn)

        # Find enemy piece locations and add to pieceLocations
        enemyPiecePosns = ChessBoardUtils.findPiecePosnsByColor(board,
                                                                otherColor)

        for enemyPiecePosn in enemyPiecePosns:
            pieceLocations.append(enemyPiecePosn)

        # Build list of empty squares

        emptyLocations = []

        # Check each location to see if it is occupied
        for r in range(0, ChessBoard.BOARD_LAYOUT_SIZE):
            for f in range(0, ChessBoard.BOARD_LAYOUT_SIZE):
                testPosn = ChessPosn(r, f)

                if testPosn not in pieceLocations:
                    emptyLocations.append(testPosn)

        # Build list of possible friendly piece moves
        friendlyMoves = self.enumBoardMoves(board, color)
        friendlyMoveDestPosns = map(lambda x: x[2], friendlyMoves)

        # Find possible moves to empty squares and build up return value

        # Accumulator for return value
        weightedReturn = 0

        for dest in emptyLocations:

            # Check if a move can be made to that Posn
            if dest in friendlyMoveDestPosns:

                #Check if it is a center square
                if QLAI.__heuristicEmptySpaceCoverage_isCenterSquare(dest):
                    weightedReturn += centerSquareValue
                else:
                    weightedReturn += squareValue

        # Calculate total weight of empty squares on board
        totalEmptyPosnWeight = 0
        for posn in emptyLocations:
            if QLAI.__heuristicEmptySpaceCoverage_isCenterSquare(posn):
                totalEmptyPosnWeight += centerSquareValue
            else:
                totalEmptyPosnWeight += squareValue

        # Compress return value into range [-1..1]
        return -1 + weightedReturn / totalEmptyPosnWeight * 2

    def _heuristicPiecesCovered(self, color, board):
        """Return a number representing how many of color's pieces are covered

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: a value representing the number of color's non-pawn pieces
                whose positions could be immediately re-taken if captured,
                weighted by piece value"""

        ## TODO (James): make this find all covered pieces for WHITE - not
        #                currently considering non-pawn white pieces

        # Construct list of friendly pieces
        friendPiecePosns = ChessBoardUtils.findPiecePosnsByColor(board, color)

        # Accumulator for return value
        weightedReturn = 0

        # For each piece, test whether a friendly piece could move to its
        # position if it were not present
        for lostPiecePosn in friendPiecePosns:

            # Don't test this for kings - it's meaningless
            if board[lostPiecePosn].pieceType != ChessBoard.KING:
                # Build hypothetical board with the lost piece removed

                ## TODO (James): consider a more efficient way of doing this,
                #                rather than a deep copy
                hypoBoard = copy.deepcopy(board)
                # Eliminate the supposedly lost piece
                hypoBoard[lostPiecePosn] = None

                # Build list of possible friendly moves
                friendlyMoves = self.enumBoardMoves(hypoBoard, color)

                lostPieceType = board[lostPiecePosn].pieceType
                lostPieceValue = QLAI._pieceValues[lostPieceType]

                # Test whether any move includes a move to the destination
                for move in friendlyMoves:
                    moveDstPosn = move[2]
                    if lostPiecePosn == moveDstPosn:
                        # Add piece value, to accumulator
                        weightedReturn += lostPieceValue
                        # Only add once per piece being covered
                        break

        # Sum the total possible piece value for all pieces of this color

        pcPosnValSumF = lambda a, b: a + QLAI._pieceValues[board[b].pieceType]
        maxCoveredValue = reduce(pcPosnValSumF, friendPiecePosns, 0)

        # Compress return value into range [-1..1]
        return -1 + weightedReturn / maxCoveredValue * 2

    def combineHeuristicValues(self, res1, res2):
        """Combine the given results for the same heuristic run on both colors

        @param res1: the numerical heuristic result of the first color
        @param res2: the numerical heuristic result of the second color

        @return: the combination, calculated as follows:
                    ((res1 - res2) / ((res1 + res2) / 2))"""

        return ((res1 - res2) / 2)

    def evaluateBoardLikability(self, color, board):
        """Return a number in [-1,1] based on board's likability to color

        @param color: One of maverick.data.ChessBoard.WHITE or
                       maverick.data.ChessBoard.BLACK
        @param board: A ChessBoard Object

        @return: a number in [-1,1] indicating the likability of the given
        board state for the given color, where -1 is least likable and 1 is
        most likable.

        The calculated value has the following properties:
         - Lower numbers indicate greater likelihood of a bad outcome (loss)
         - Higher numbers indicate greater likelihood of a good outcome (win)
         - -1 means guaranteed loss
         - 0 means neither player is favored; can mean a state of draw
         - +1 means guaranteed win"""

        # Pairing of heuristics with their weights
        ## TODO (James): research and tweak these
        pieceValueWeight = 3
        inCheckWeight = 4
        piecesUnderAttackWeight = 3
        emptySpaceCoverageWeight = 1
        piecesCoveredWeight = 1

        # Determine opposing player color
        otherColor = ChessBoard.getOtherColor(color)

        # Check to see if either player is checkmated and return appropriately
        if board.isKingCheckmated(otherColor):
            return 1
        elif board.isKingCheckmated(color):
            return -1
        else:

            # Data structure of 'opinions' from heuristics
            # Format: ListOf[("Name", weight, value)]
            opinions = []

            ## TODO (James): Clean up the code below a bit - there has to be
            #                a cleaner way to do this

            # Add piece value opinion
            pieceValueFriend = self._heuristicPieceValue(color, board)
            pieceValueFoe = self._heuristicPieceValue(otherColor, board)
            pieceValueRes = self.combineHeuristicValues(pieceValueFriend,
                                                        pieceValueFoe)
            opinions.append(("PieceValue", pieceValueWeight, pieceValueRes))

            # Add in check opinion
            inCheckFriend = self._heuristicInCheck(color, board)
            inCheckFoe = self._heuristicInCheck(otherColor, board)
            inCheckRes = self.combineHeuristicValues(inCheckFriend,
                                                        inCheckFoe)
            opinions.append(("InCheck", inCheckWeight, inCheckRes))

            # Add pieces under attack opinion
            pcsUnderAtkFriend = self._heuristicPiecesUnderAttack(color, board)
            pcsUnderAtkFoe = self._heuristicPiecesUnderAttack(otherColor,
                                                              board)
            pcsUnderAtkRes = self.combineHeuristicValues(pcsUnderAtkFriend,
                                                         pcsUnderAtkFoe)
            opinions.append(("PiecesUnderAttack", piecesUnderAttackWeight,
                            pcsUnderAtkRes))

            # Add empty space coverage opinion
            emptySpcsCvdFriend = self._heuristicEmptySpaceCoverage(color,
                                                                   board)
            emptySpcsCvdFoe = self._heuristicEmptySpaceCoverage(otherColor,
                                                                board)
            emptySpcsCvdRes = self.combineHeuristicValues(emptySpcsCvdFriend,
                                                          emptySpcsCvdFoe)
            opinions.append(("EmptySpaceCoverage", emptySpaceCoverageWeight,
                            emptySpcsCvdRes))

            # Add pieces covered opinion
            pcsCoveredFriend = self._heuristicPiecesCovered(color, board)
            pcsCoveredFoe = self._heuristicPiecesCovered(otherColor, board)
            pcsCoveredRes = self.combineHeuristicValues(pcsCoveredFriend,
                                                        pcsCoveredFoe)
            opinions.append(("PiecesCovered", piecesCoveredWeight,
                            pcsCoveredRes))

            # Return the weighted average
            return sum([weight * value for (_, weight, value) in opinions]) / \
                sum([weight for (_, weight, _) in opinions])


def runAI(host=None, port=None):
    ai = QLAI(host=host, port=port)
    ai.run()


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host", default=None, type=str,
                        help="specify hostname of Maverick server")
    parser.add_argument("--port", default=None, type=int,
                        help="specify port of Maverick server")
    args = parser.parse_args()
    runAI(host=args.host, port=args.port)

if __name__ == '__main__':
    runAI()
