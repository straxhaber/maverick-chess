#!/usr/bin/python

"""common.py: Common code shared between all AIs"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.data import ChessBoard
from maverick.players.common import MaverickPlayer


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

    def _initName(self):
        """Figure out the name of the class"""
        pass  # Default name is appropriate

    def _welcomePlayer(self):
        """Display welcome messages if appropriate"""
        MaverickAI._logger.info("I, %s (%d), have entered game %d",
                                self.name,
                                self.playerID,
                                self.gameID)

    def _handleBadMove(self, errMsg, board, fromPosn, toPosn):
        """Calculate the next move based on the provided board"""
        raise MaverickAIException("Invalid move made: {}->{}".format(fromPosn,
                                                                     toPosn))

    def _getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")

    @staticmethod
    def _enumerateAllMoves(board, color):
        """Enumerate all possible immediate moves for the given player

        @return: a set of tuples of the form:
            ListOf[(ChessPiece, fromPosn, toPosn)]"""

        ## TODO (James): rewrite this function

        all_moves = []  # List of all possible moves. Starts empty.

        for p in ChessBoard:
            if p.color == color:
                all_moves.extend(p._getPossibleMoves(board, p.fromRank,
                                                    p.fromFile))
        return all_moves

    @staticmethod
    def _getPossibleMoves(board, fromRank, fromFile):
        """Return all possible moves for the specified piece on given board

        @return ListOf[(ChessPiece, fromPosn, toPosn)]"""

        ## TODO (James): Rewrite this function

        # Pull out the color and piece type from the board
        (color, piece) = board.layout[fromRank - 1][fromFile - 1]

        possible_moves = []  # List of possible moves. Starts empty

        for i in range(0, 7):
            for j in range(0, 7):
                if board.isLegalMove(color, fromRank - 1, fromFile - 1, i, j):
                    possible_moves.append([piece, (fromRank - 1, fromFile - 1),
                                           (i, j)])

        return possible_moves


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
