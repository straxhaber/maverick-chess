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
    def __canMoveTo_isOnBoard(posn):
        return (posn.rankN in range(ChessBoard.BOARD_LAYOUT_SIZE) and
                posn.fileN in range(ChessBoard.BOARD_LAYOUT_SIZE))

    @staticmethod
    def __canMoveTo_moveLoop(moves, board, color,
                                    fromPosn, translations):
        """Add moves based on translations, stopping when blocked

        WARNING: mutates moves to add relevant moves (returns None)"""
        for translation in translations:
            toPosn = fromPosn.getTranslatedBy(*translation)
            # TODO: we should worry about self-capture all at the end

            # Add moves to empty and enemy-occupied squares
            if (board[toPosn] is None or
                board[toPosn].color == ChessBoard.getOtherColor(color)):
                moves.append(toPosn)

            # Stop if blocked by a piece
            if board[toPosn] is not None:
                break

    @staticmethod
    def __canMoveTo_pawn(board, color, fromPosn):
        moves = []
        moves.append(fromPosn.getTranslatedBy(1, 0))

        # TODO only if on first row
        # TODO only if no piece one above
        moves.append(fromPosn.getTranslatedBy(2, 0))

#        for rankDelta, fileDelta in [(1, -1), (1, 1)]:
#            toPosn = fromPosn.getTranslatedBy(rankDelta, fileDelta)
#            if MaverickAI.__canMoveTo_enemyAt(board, color, toPosn):
#                moves.append(toPosn)
        return moves

    @staticmethod
    def __canMoveTo_rook(board, color, fromPosn):
        # TODO (mattsh): rewrite to use __canMoveTo_moveLoop
        moves = []

        (rN, fN) = (fromPosn.rankN, fromPosn.fileN)
        bS = ChessBoard.BOARD_LAYOUT_SIZE

        # Move up (rN+1..7, fN)
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(range(rN + 1, bS, 1),
                                            [fN] * (bS - 1 - rN)))
        # Move down (0..rN-1, fN)
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(range(rN - 1, -1, -1),
                                            [fN] * rN))
        # Move right (rN, fN+1..7)
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip([rN] * (bS - 1 - fN),
                                            range(fN + 1, bS, 1)))
        # Move left (rN, 0..fN-1)
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                           zip([rN] * fN,
                                               range(fN - 1, -1, -1)))

        return moves

    @staticmethod
    def __canMoveTo_knight(board, color, fromPosn):
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
    def __canMoveTo_bishop(board, color, fromPosn):
        moves = []

        rMin = 1
        rMax = ChessBoard.BOARD_LAYOUT_SIZE + 1
        countUp = range(rMin, rMax, 1)
        countDown = range(-rMin, -rMax, -1)

        # Move top-right
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(countUp, countUp))
        # Move top-left
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(countUp, countDown))
        # Move down-right
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(countDown, countUp))
        # Move down-left
        MaverickAI.__canMoveTo_moveLoop(moves, board, color, fromPosn,
                                        zip(countDown, countDown))
        return moves

    @staticmethod
    def __canMoveTo_queen(board, color, fromPosn):
        moves = []
        moves.extend(MaverickAI.__canMoveTo_bishop(board, color, fromPosn))
        moves.extend(MaverickAI.__canMoveTo_rook(board, color, fromPosn))
        return moves

    @staticmethod
    def __canMoveTo_king(board, color, fromPosn):
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
    def canMoveTo(board, fromPosn):
        """Return all possible toPosns for the specified piece on given board

        @return ListOf[toPosn]"""

        # Pull out the color and fromPiece type from the board
        fromPiece = board[fromPosn]

        # TODO: Assert piece exists
        # TODO: Assert piece color is owned by player

        if fromPiece.pieceType == ChessBoard.PAWN:
            moveGenerator = MaverickAI.__canMoveTo_pawn
        elif fromPiece.pieceType == ChessBoard.ROOK:
            moveGenerator = MaverickAI.__canMoveTo_rook
        elif fromPiece.pieceType == ChessBoard.KNGT:
            moveGenerator = MaverickAI.__canMoveTo_knight
        elif fromPiece.pieceType == ChessBoard.BISH:
            moveGenerator = MaverickAI.__canMoveTo_bishop
        elif fromPiece.pieceType == ChessBoard.QUEN:
            moveGenerator = MaverickAI.__canMoveTo_queen
        elif fromPiece.pieceType == ChessBoard.KING:
            moveGenerator = MaverickAI.__canMoveTo_king
        else:
            raise MaverickAIException("Invalid fromPiece type")

        # Get list of possible toPosns. Starts empty
        toPosns = moveGenerator(board, fromPiece.color, fromPosn)

        # Filter out toPosns that would put a fromPiece off the board
        toPosns = filter(MaverickAI.__canMoveTo_isOnBoard, toPosns)

        # Filter out self-capturing toPosns
        toPosns = filter(lambda p: (board[p] is None or
                                    board[p].color != fromPiece.color),
                         toPosns)

        # Filter out Filter out toPosns that would put player in check
        def selfKingNotInCheck(toPosn):
            resultBoard = board.getResultOfPly(fromPosn, toPosn)
            return not resultBoard.isKingInCheck(fromPiece.color)[0]
        toPosns = filter(selfKingNotInCheck, toPosns)

        return toPosns

    @staticmethod
    def enumBoardMoves(board, color):
        """Enumerate all possible immediate moves for the given player

        @return: a set of tuples of the form:
            ListOf[(ChessPiece, fromPosn, toPosn)]"""

        # TODO (mattsh): Once working and complete, use generator pattern

        # List of all possible moves from the given board. Must be filled.
        moves = []

        for rankN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            for fileN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
                fromPosn = ChessPosn(rankN, fileN)
                fromPiece = board[fromPosn]

                if fromPiece is not None and fromPiece.color == color:
                    moves.extend(map(lambda toPosn: (fromPiece,
                                                     fromPosn,
                                                     toPosn),
                                     MaverickAI.canMoveTo(board, fromPosn)))

        return moves


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
