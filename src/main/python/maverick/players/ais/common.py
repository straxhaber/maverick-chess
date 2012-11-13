#!/usr/bin/python

"""common.py: Common code shared between all AIs"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging
import time
import random

from maverick.data import ChessBoard
from maverick.data import ChessMatch
from maverick.data import ChessPosn
from maverick.players.common import MaverickPlayer

__all__ = ["MaverickAI",
           "MaverickAIException"]


class MaverickAIException(Exception):
    """Base class for Exceptions from Maverick AIs"""
    pass


class MaverickAI(MaverickPlayer):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.common.MaverickAI")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    CALCULATION_TIMEOUT = 5
    """Maximum amount of time for the AI to take to make its move"""

    def getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    def getPlayerName(self):
        """Figure out the name of the class"""
        # TODO (mattsh): Why isn't random.randint being run??
        return "%s %d %d" % (self.__class__.__name__,
                             time.time(),
                             random.randint(1, 10 ** 9))

    def _showPlayerWelcome(self):
        """Display welcome messages if appropriate"""
        MaverickAI._logger.info("I, %s (%d), have entered game %d",
                                self.name,
                                self.playerID,
                                self.gameID)

    def _showPlayerGoodbye(self):
        """Display goodbye messages if appropriate"""
        MaverickAI._logger.info("I, %s (%d), have finished game %d",
                                self.name,
                                self.playerID,
                                self.gameID)
        status = self._request_getStatus()
        if status == ChessMatch.STATUS_WHITE_WON:
            result = "white won"
        elif status == ChessMatch.STATUS_BLACK_WON:
            result = "black won"
        elif status == ChessMatch.STATUS_DRAWN:
            result = "ended in a draw"
        elif status == ChessMatch.STATUS_CANCELLED:
            result = "game was cancelled"
        else:
            MaverickAI._logger.error("Unexpected status code: %d", status)
            result = "UNEXPECTED FINISH STATUS"
        MaverickAI._logger.info("The result was: %s", result)

    def _handleBadMove(self, errMsg, board, fromPosn, toPosn):
        """Calculate the next move based on the provided board"""
        raise MaverickAIException("Invalid move made: {}->{}".format(fromPosn,
                                                                     toPosn))

    @staticmethod
    def _enumerateAllMoves(board, color):
        """Enumerate all possible immediate moves for the given player

        @return: a set of tuples of the form:
            ListOf[(ChessPiece, fromPosn, toPosn)]"""

        # List of all possible moves from the given board. Must be filled.
        all_moves = []

        for rankN in xrange(0, 8):
            for fileN in xrange(0, 7):
                fromPosn = ChessPosn(rankN, fileN)
                fromPiece = board[fromPosn]

                if fromPiece is not None and fromPiece.color == color:
                    all_moves.extend(map(lambda toPosn: (fromPiece,
                                                         fromPosn,
                                                         toPosn),
                                         MaverickAI.getPossiblePlies(board,
                                                              fromPosn)))

        return all_moves

    @staticmethod
    def __getPossiblePlies_colorPieceAtPosn(board, color, posn):
        p = board[posn]
        return p is not None and p.color == color

    @staticmethod
    def __getPossiblePlies_enemyAtPosn(board, color, posn):
        """Return True iff there is a piece of the opposite color at posn"""
        enemyColor = ChessBoard.getOtherColor(color)
        return MaverickAI.__getPossiblePlies_colorPieceAtPosn(board,
                                                              enemyColor,
                                                              posn)

    @staticmethod
    def __getPossiblePlies_isOnBoard(posn):
        return (posn.rankN in range(0, 8) and
                posn.fileN in range(0, 8))

    @staticmethod
    def __getPossiblePlies_moveLoop(moves, board, color,
                                    fromPosn, translations):
        """Add moves based on translations, stopping at an enemy piece

        WARNING: mutates moves to add relevant moves (returns None)"""
        for translation in translations:
            toPosn = fromPosn.getTranslatedBy(*translation)
            moves.append(toPosn)  # NOTE: self-capture is prevented later

            # Stop if at a piece
            if board[toPosn] is not None:
                break

    @staticmethod
    def __getPossiblePlies_pawn(board, color, fromPosn):
        moves = []
        moves.append(fromPosn.getTranslatedBy(1, 0))

        # TODO only if on first row
        # TODO only if no piece one above
        moves.append(fromPosn.getTranslatedBy(2, 0))

        for rankDelta, fileDelta in [(1, -1), (1, 1)]:
            toPosn = fromPosn.getTranslatedBy(rankDelta, fileDelta)
            if MaverickAI.__getPossiblePlies_enemyAtPosn(board, color, toPosn):
                moves.append(toPosn)
        return moves

    @staticmethod
    def __getPossiblePlies_rook(board, color, fromPosn):
        # TODO (mattsh): rewrite to use __getPossiblePlies_moveLoop
        moves = []
        # Move up
        for toRank in xrange(fromPosn.rankN + 1, 8):
            toPosn = ChessPosn(toRank, fromPosn.fileN)
            moves.append(toPosn)
            if MaverickAI.__getPossiblePlies_enemyAtPosn(board, color, toPosn):
                break
        # Move down
        for toRank in xrange(fromPosn.rankN - 1, -1, -1):
            toPosn = ChessPosn(toRank, fromPosn.fileN)
            moves.append(toPosn)
            if MaverickAI.__getPossiblePlies_enemyAtPosn(board, color, toPosn):
                break
        # Move right
        for toFile in xrange(fromPosn.fileN + 1, 8):
            toPosn = ChessPosn(fromPosn.rankN, toFile)
            moves.append(toPosn)
            if MaverickAI.__getPossiblePlies_enemyAtPosn(board, color, toPosn):
                break
        # Move left
        for toFile in xrange(fromPosn.fileN - 1, -1, -1):
            toPosn = ChessPosn(fromPosn.rankN, toFile)
            moves.append(toPosn)
            if MaverickAI.__getPossiblePlies_enemyAtPosn(board, color, toPosn):
                break
        return moves

    @staticmethod
    def __getPossiblePlies_knight(board, color, fromPosn):
        moves = []
        moves.append(fromPosn.getTranslatedBy(2, -1))
        moves.append(fromPosn.getTranslatedBy(2, 1))
        moves.append(fromPosn.getTranslatedBy(1, -2))
        moves.append(fromPosn.getTranslatedBy(1, 2))
        moves.append(fromPosn.getTranslatedBy(-1, -2))
        moves.append(fromPosn.getTranslatedBy(-1, 2))
        moves.append(fromPosn.getTranslatedBy(-2, -1))
        moves.append(fromPosn.getTranslatedBy(-2, 1))
        return moves

    @staticmethod
    def __getPossiblePlies_bishop(board, color, fromPosn):
        moves = []
        # Move top-right
        MaverickAI.__getPossiblePlies_moveLoop(moves, board, color, fromPosn,
                                       zip(range(1, 8), range(1, 8)))
        # Move top-left
        MaverickAI.__getPossiblePlies_moveLoop(moves, board, color, fromPosn,
                                       zip(range(1, 8), range(-1, -8, -1)))
        # Move down-right
        MaverickAI.__getPossiblePlies_moveLoop(moves, board, color, fromPosn,
                                       zip(range(-1, -8, -1), range(1, 8)))
        # Move down-left
        MaverickAI.__getPossiblePlies_moveLoop(moves, board, color, fromPosn,
                                       zip(range(-1, -8, -1),
                                           range(-1, -8, -1)))
        return moves

    @staticmethod
    def __getPossiblePlies_queen(board, color, fromPosn):
        moves = []
        moves.extend(MaverickAI.__getPossiblePlies_bishop(board, color,
                                                          fromPosn))
        moves.extend(MaverickAI.__getPossiblePlies_rook(board, color,
                                                        fromPosn))
        return moves

    @staticmethod
    def __getPossiblePlies_king(board, color, fromPosn):
        moves = []
        moves.append(fromPosn.getTranslatedBy(1, 1))
        moves.append(fromPosn.getTranslatedBy(1, 0))
        moves.append(fromPosn.getTranslatedBy(1, -1))
        moves.append(fromPosn.getTranslatedBy(0, 1))
        moves.append(fromPosn.getTranslatedBy(0, -1))
        moves.append(fromPosn.getTranslatedBy(-1, 1))
        moves.append(fromPosn.getTranslatedBy(-1, 0))
        moves.append(fromPosn.getTranslatedBy(-1, -1))

        (canCastleQueenSide, canCastleKingSide) = board.flag_canCastle[color]
        if canCastleQueenSide:
            pass  # TODO (mattsh)
        if canCastleKingSide:
            pass  # TODO (mattsh)

        # TODO add castling
        return moves

    @staticmethod
    def getPossiblePlies(board, fromPosn):
        """Return all possible moves for the specified piece on given board

        @return ListOf[toPosn]"""

        ## TODO (James): Rewrite this function

        # Pull out the color and piece type from the board
        piece = board[fromPosn]

        if piece.pieceType == ChessBoard.PAWN:
            moveGenerator = MaverickAI.__getPossiblePlies_pawn
        elif piece.pieceType == ChessBoard.ROOK:
            moveGenerator = MaverickAI.__getPossiblePlies_rook
        elif piece.pieceType == ChessBoard.KNGT:
            moveGenerator = MaverickAI.__getPossiblePlies_knight
        elif piece.pieceType == ChessBoard.BISH:
            moveGenerator = MaverickAI.__getPossiblePlies_bishop
        elif piece.pieceType == ChessBoard.QUEN:
            moveGenerator = MaverickAI.__getPossiblePlies_queen
        elif piece.pieceType == ChessBoard.KING:
            moveGenerator = MaverickAI.__getPossiblePlies_king
        else:
            raise MaverickAIException("Invalid piece type")

        # Get list of possible moves. Starts empty
        moves = moveGenerator(board, piece.color, fromPosn)

        # Filter out moves off board
        moves = filter(MaverickAI.__getPossiblePlies_isOnBoard, moves)

        # Filter out self-capturing moves
        def notCapturingOwnPiece(toPosn):
            return not MaverickAI.__getPossiblePlies_colorPieceAtPosn(board,
                                                              piece.color,
                                                              toPosn)
        moves = filter(notCapturingOwnPiece, moves)

        # Filter out Filter out moves that would put player in check
        def kingNotInCheck(toPosn):
            resultBoard = board.getResultOfPly(fromPosn, toPosn)
            return not resultBoard.isKingInCheck(piece.color)[0]
        moves = filter(kingNotInCheck, moves)

        return moves


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
