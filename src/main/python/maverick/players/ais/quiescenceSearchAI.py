#!/usr/bin/python

"""quiescenceSearchAI.py: AI that uses a quiescence search with heuristics"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.players.ais.common import MaverickAI
from maverick.data import ChessBoard
from maverick.data import ChessBoardUtils


class QLAI(MaverickAI):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.quiescenceSearchAI.QLAI")
    logging.basicConfig(level=logging.INFO)

    # Standard piece values, from
    # http://en.wikipedia.org/wiki/Chess_piece_values
    ## TODO (James): decide whether to include the king with large point value
    _pieceValues = {ChessBoard.PAWN: 1,
                    ChessBoard.KNGT: 3,
                    ChessBoard.BISH: 3,
                    ChessBoard.ROOK: 5,
                    ChessBoard.QUEN: 9}

    def getNextMove(self, board):

        # Figure out our color
        if self.isWhite:
            color = ChessBoard.WHITE
        else:
            color = ChessBoard.BLACK

        moveChoices = ChessBoardUtils.enumerateAllMoves(board, color)

        # TODO (mattsh): write this
        fromRank, fromFile, toRank, toFile = None

        return ((fromRank, fromFile), (toRank, toFile))

    def _heuristicPieceValue(self, color, board):
        """Return the total value of color's pieces on the given board.

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        Note that the king's value is not included - the undesirability of the
        king's capture will be incorporated in other heuristics."""

        # Get a list of non-king pieces for this color
        friendlyPieces = ChessBoardUtils.findColorPieces(board, color)

        # Loop through this color's pieces, adding to total value
        totalValue = 0
        for piece in friendlyPieces:
            pieceType = piece[0]
            if pieceType in QLAI._pieceValues:
                totalValue += QLAI._pieceValues[pieceType]

        return totalValue

    def _heuristicInCheck(self, color, board):
        """Return 1 if the given color king is in check on the given board

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: 1 if the given color is in check on the given board, 0
                otherwise"""

        if ChessBoardUtils.isKingInCheck(board, color):
            return 1
        else:
            return 0

    def _heuristicPiecesUnderAttack(self, color, board):
        """Return a value representing the number of enemy pieces under attack

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: a value representing the number of enemy pieces that the given
                color has under attack on the given board, weighted by piece
                value"""

        otherColor = ChessBoard.getOtherColor(color)

        # Get friendly pieces
        friendlyPieces = ChessBoardUtils.findColorPieces(board, color)

        # Get enemy pieces
        enemyPieces = ChessBoardUtils.findColorPieces(board, otherColor)

        # Record which enemy pieces are under attack
        enemyPiecesUnderAttack = []

        # For each enemyPiece, check whether any friendlyPiece can capture it
        for enemyPiece in enemyPieces:

            # Determine this piece's location
            enemyRank = enemyPiece[1][0]
            enemyFile = enemyPiece[1][1]

            for friendlyPiece in friendlyPieces:

                # Determine this piece's location
                friendRank = friendlyPiece[1][0]
                friendFile = friendlyPiece[1][1]

                # Check if this piece can capture the enemy piece
                if ChessBoardUtils.isLegalMove(board, friendRank, friendFile,
                                               enemyRank, enemyFile):

                    # Note that this enemyPiece is under attack
                    enemyPiecesUnderAttack.append(enemyPiece)
                    break

        # Sum weighted values of under-attack pieces
        weightedTotal = 0
        for piece in enemyPiecesUnderAttack:
            pieceType = piece[0]

            # Check if there is a value for this piece in the mappings
            if pieceType in QLAI._pieceValues:
                weightedTotal += QLAI._pieceValues[pieceType]

        return weightedTotal

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
        #                See http://tinyurl.com/cpjqnw4
        centerSquareValue = 2
        squareValue = 1

        # Build up a list of all piece locations as tuples

        pieceLocations = []
        otherColor = ChessBoardUtils.getOtherColor(color)

        # Find friendly piece locations and add to pieceLocations
        friendlyPieces = ChessBoardUtils.findColorPieces(board, color)

        for piece in friendlyPieces:
            pieceLoc = piece[1]
            pieceLocations.append(pieceLoc)

        # Find enemy piece locations and add to pieceLocations
        enemyPieces = ChessBoardUtils.findColorPieces(board, otherColor)

        for piece in enemyPieces:
            pieceLoc = piece[1]
            pieceLocations.append(pieceLoc)

        # Build list of empty squares

        emptyLocations = []

        # Check each location to see if it is occupied
        for r in range(0, ChessBoard.BOARD_SIZE):
            for f in range(0, ChessBoard.BOARD_SIZE):
                testLoc = (r, f)

                if testLoc not in pieceLocations:
                    emptyLocations.append(testLoc)

        # Build list of possible friendly piece moves
        friendlyMoves = ChessBoardUtils.enumerateAllMoves(board, color)

        # Find possible moves to empty squares and build up return value

        # Accumulator for return value
        weightedReturn = 0

        for move in friendlyMoves:
            moveDst = move[2]

            # Check if this move is to an empty square
            if moveDst in emptyLocations:

                #Check if it is a center square
                if ChessBoardUtils.isCenterSquare(moveDst[0], moveDst[1]):
                    weightedReturn += centerSquareValue
                else:
                    weightedReturn += squareValue

        return weightedReturn

    def _heuristicPiecesCovered(self, color, board):
        """Return a number representing how many of color's pieces are covered

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a ChessBoard object

        @return: a value representing the number of color's non-pawn pieces
                whose positions could be immediately re-taken if captured,
                weighted by piece value"""

        # Construct list of friendly pieces
        friendlyPieces = ChessBoardUtils.findColorPieces(board, color)

        # Accumulator for return value
        weightedReturn = 0

        # For each piece, test whether a friendly piece could move to its
        # position if it were taken were not present
        for lostPiece in friendlyPieces:

            # Build hypothetical board with the lost piece removed

            lostPieceRank = lostPiece[1][0]
            lostPieceFile = lostPiece[1][1]
            lostPieceLoc = (lostPieceRank, lostPieceFile)
            # Eliminate the supposedly lost piece
            board.board[lostPieceRank][lostPieceFile] = None

            # Build list of possible friendly moves
            friendlyMoves = ChessBoardUtils.enumerateAllMoves(board, color)

            # Test whether any move includes a move to the square in question
            for move in friendlyMoves:
                movedPieceType = move[0]
                moveDst = move[3]
                if lostPieceLoc == moveDst:
                    # Add piece value, if it exists, to accumulator
                    if movedPieceType in QLAI._pieceValues:
                        weightedReturn += QLAI._pieceValues[movedPieceType]

        return weightedReturn

    def combineHeuristicValues(self, res1, res2):
        """Combine the given results for the same heuristic run on both colors

        @param res1: the numerical heuristic result of the first color
        @param res2: the numerical heuristic result of the second color

        @return: the combination, calculated as follows:
                    ((res1 - res2) / ((res1 + res2) / 2))"""

        return ((res1 - res2) / ((res1 + res2) / 2))

    def evaluateBoardLikability(self, color, board):
        """Return a number in [-1,1] based on likability of the position

        @param color: one of maverick.data.ChessBoard.WHITE or
                    maverick.data.ChessBoard.BLACK
        @param board: a board state as a 3-tuple of form
                    (boardState, in form maverick.data.ChessBoard.board,
                    enPassantFlags, in form ChessBoard.flag_enpassant,
                    canCastleFlags, in form ChessBoard.flag_canCastle,

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
        pieceValueWeight = 1
        inCheckWeight = 1
        piecesUnderAttackWeight = 1
        emptySpaceCoverageWeight = 1
        piecesCoveredWeight = 1

        # Instantiate ChessBoard with given state to use for non-static method
        # ChessBoard method calls
        boardObj = ChessBoard(startBoard=board[0],
                              startEnpassantFlags=board[1],
                              startCanCastleFlage=board[2])

        # Determine opposing player color
        otherColor = ChessBoard.getOtherColor(color)

        # Data structure of 'opinions' from heuristics
        # Format: ListOf[("Name", weight, value)]
        opinions = []

        # Add piece value opinion
        pieceValueFriend = self._heuristicPieceValue(color, boardObj)
        pieceValueFoe = self._heuristicPieceValue(otherColor, board)
        pieceValueRes = self.combineHeuristicValues(pieceValueFriend,
                                                    pieceValueFoe)
        opinions.append("PieceValue", pieceValueWeight, pieceValueRes)

        # Add in check opinion
        inCheckFriend = self._heuristicInCheck(color, boardObj)
        inCheckFoe = self._heuristicInCheck(otherColor, board)
        inCheckRes = self.combineHeuristicValues(inCheckFriend,
                                                    inCheckFoe)
        opinions.append("InCheck", inCheckWeight, inCheckRes)

        # Add pieces under attack opinion
        pcsUnderAtkFriend = self._heuristicPiecesUnderAttack(color, boardObj)
        pcsUnderAtkFoe = self._heuristicPiecesUnderAttack(otherColor, board)
        pcsUnderAtkRes = self.combineHeuristicValues(pcsUnderAtkFriend,
                                                     pcsUnderAtkFoe)
        opinions.append("PiecesUnderAttack", piecesUnderAttackWeight,
                        pcsUnderAtkRes)

        # Add empty space coverage opinion
        emptySpcsCvdFriend = self._heuristicEmptySpaceCoverage(color, boardObj)
        emptySpcsCvdFoe = self._heuristicEmptySpaceCoverage(otherColor, board)
        emptySpcsCvdRes = self.combineHeuristicValues(emptySpcsCvdFriend,
                                                      emptySpcsCvdFoe)
        opinions.append("EmptySpaceCoverage", emptySpaceCoverageWeight,
                        emptySpcsCvdRes)

        # Add pieces covered opinion
        pcsCoveredFriend = self._heuristicPiecesCovered(color, boardObj)
        pcsCoveredFoe = self._heuristicPiecesCovered(otherColor, board)
        pcsCoveredRes = self.combineHeuristicValues(pcsCoveredFriend,
                                                    pcsCoveredFoe)
        opinions.append("PiecesCovered", piecesCoveredWeight,
                        pcsCoveredRes)

        # Return the weighted average
        return sum([weight * value for (_, weight, value) in opinions]) / \
            sum([weight for (_, weight, _) in opinions])


def main():
    ai = QLAI()
    ai.runAI()

if __name__ == '__main__':
    main()
