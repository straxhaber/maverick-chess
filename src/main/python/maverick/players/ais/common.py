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
                                self.name, self.playerID, self.gameID)
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
        fStr = "Invalid move made: {}->{}"
        raise MaverickAIException(fStr.format(fromPosn, toPosn))

    @staticmethod
    def __getPossPlies_colorAt(board, color, posn):
        p = board[posn]
        return p is not None and p.color == color

    @staticmethod
    def __getPossPlies_enemyAt(board, color, posn):
        """Return True iff there is a piece of the opposite color at posn"""
        enemyColor = ChessBoard.getOtherColor(color)
        return MaverickAI.__getPossPlies_colorAt(board, enemyColor, posn)

    @staticmethod
    def __getPossPlies_isOnBoard(posn):
        return (posn.rankN in range(0, 8) and
                posn.fileN in range(0, 8))

    @staticmethod
    def __getPossPlies_moveLoop(moves, board, color,
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
    def __getPossPlies_pawn(board, color, fromPosn):
        moves = []
        moves.append(fromPosn.getTranslatedBy(1, 0))

        # TODO only if on first row
        # TODO only if no piece one above
        moves.append(fromPosn.getTranslatedBy(2, 0))

        for rankDelta, fileDelta in [(1, -1), (1, 1)]:
            toPosn = fromPosn.getTranslatedBy(rankDelta, fileDelta)
            if MaverickAI.__getPossPlies_enemyAt(board, color, toPosn):
                moves.append(toPosn)
        return moves

    @staticmethod
    def __getPossPlies_rook(board, color, fromPosn):
        # TODO (mattsh): rewrite to use __getPossPlies_moveLoop
        moves = []
        # Move up
        for toRank in xrange(fromPosn.rankN + 1, 8):
            toPosn = ChessPosn(toRank, fromPosn.fileN)
            if (board[toPosn] is None or
                MaverickAI.__getPossPlies_enemyAt(board, color, toPosn)):
                moves.append(toPosn)
            if board[toPosn] is not None:
                break
        # Move down
        for toRank in xrange(fromPosn.rankN - 1, -1, -1):
            toPosn = ChessPosn(toRank, fromPosn.fileN)
            if (board[toPosn] is None or
                MaverickAI.__getPossPlies_enemyAt(board, color, toPosn)):
                moves.append(toPosn)
            if board[toPosn] is not None:
                break
        # Move right
        for toFile in xrange(fromPosn.fileN + 1, 8):
            toPosn = ChessPosn(fromPosn.rankN, toFile)
            if (board[toPosn] is None or
                MaverickAI.__getPossPlies_enemyAt(board, color, toPosn)):
                moves.append(toPosn)
            if board[toPosn] is not None:
                break
        # Move left
        for toFile in xrange(fromPosn.fileN - 1, -1, -1):
            toPosn = ChessPosn(fromPosn.rankN, toFile)
            if (board[toPosn] is None or
                MaverickAI.__getPossPlies_enemyAt(board, color, toPosn)):
                moves.append(toPosn)
            if board[toPosn] is not None:
                break
        return moves

    @staticmethod
    def __getPossPlies_knight(board, color, fromPosn):
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
    def __getPossPlies_bishop(board, color, fromPosn):
        moves = []
        # Move top-right
        MaverickAI.__getPossPlies_moveLoop(moves, board, color, fromPosn,
                                           zip(range(1, 8),
                                               range(1, 8)))
        # Move top-left
        MaverickAI.__getPossPlies_moveLoop(moves, board, color, fromPosn,
                                           zip(range(1, 8),
                                               range(-1, -8, -1)))
        # Move down-right
        MaverickAI.__getPossPlies_moveLoop(moves, board, color, fromPosn,
                                           zip(range(-1, -8, -1),
                                               range(1, 8)))
        # Move down-left
        MaverickAI.__getPossPlies_moveLoop(moves, board, color, fromPosn,
                                           zip(range(-1, -8, -1),
                                               range(-1, -8, -1)))
        return moves

    @staticmethod
    def __getPossPlies_queen(board, color, fromPosn):
        moves = []
        moves.extend(MaverickAI.__getPossPlies_bishop(board, color, fromPosn))
        moves.extend(MaverickAI.__getPossPlies_rook(board, color, fromPosn))
        return moves

    @staticmethod
    def __getPossPlies_king(board, color, fromPosn):
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
    def getPossPlies(board, fromPosn):
        """Return all possible moves for the specified piece on given board

        @return ListOf[toPosn]"""

        ## TODO (James): Rewrite this function

        # Pull out the color and piece type from the board
        piece = board[fromPosn]

        if piece.pieceType == ChessBoard.PAWN:
            moveGenerator = MaverickAI.__getPossPlies_pawn
        elif piece.pieceType == ChessBoard.ROOK:
            moveGenerator = MaverickAI.__getPossPlies_rook
        elif piece.pieceType == ChessBoard.KNGT:
            moveGenerator = MaverickAI.__getPossPlies_knight
        elif piece.pieceType == ChessBoard.BISH:
            moveGenerator = MaverickAI.__getPossPlies_bishop
        elif piece.pieceType == ChessBoard.QUEN:
            moveGenerator = MaverickAI.__getPossPlies_queen
        elif piece.pieceType == ChessBoard.KING:
            moveGenerator = MaverickAI.__getPossPlies_king
        else:
            raise MaverickAIException("Invalid piece type")

        # Get list of possible moves. Starts empty
        moves = moveGenerator(board, piece.color, fromPosn)

        # Filter out moves that would put a piece off the board
        moves = filter(MaverickAI.__getPossPlies_isOnBoard, moves)

        # Filter out self-capturing moves
        moves = filter(lambda p: MaverickAI.__getPossPlies_colorAt(board,
                                                                   piece.color,
                                                                   p),
                       moves)

        # Filter out Filter out moves that would put player in check
        def kingNotInCheck(toPosn):
            resultBoard = board.getResultOfPly(fromPosn, toPosn)
            return not resultBoard.isKingInCheck(piece.color)[0]
        moves = filter(kingNotInCheck, moves)

        return moves

    @staticmethod
    def enumBoardMoves(board, color):
        """Enumerate all possible immediate moves for the given player

        @return: a set of tuples of the form:
            ListOf[(ChessPiece, fromPosn, toPosn)]"""

        # TODO (mattsh): Once working and complete, use generator pattern

        # List of all possible moves from the given board. Must be filled.
        moves = []

        for rankN in xrange(0, 8):
            for fileN in xrange(0, 7):
                fromPosn = ChessPosn(rankN, fileN)
                fromPiece = board[fromPosn]

                if fromPiece is not None and fromPiece.color == color:
                    moves.extend(map(lambda toPosn: (fromPiece,
                                                     fromPosn,
                                                     toPosn),
                                     MaverickAI.getPossPlies(board, fromPosn)))

        return moves


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
