#!/usr/bin/python

"""quiescenceSearchAI.py: AI that uses a quiescence search with heuristics"""

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

from __future__ import division

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
import logging

from maverick.data import ChessBoard
from maverick.players.ais.analyzers.likability import evaluateBoardLikability
from maverick.players.ais.analyzers.stateExpansion import enumPossBoardMoves
from maverick.players.ais.common import MaverickAI

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

    def getNextMove(self, board):
        """TODO PyDoc"""

        SEARCH_DEPTH = 2

        # Figure out our color
        if self.isWhite:
            color = ChessBoard.WHITE
        else:
            color = ChessBoard.BLACK

        (nextMove, _) = self._boardSearch(board, color, SEARCH_DEPTH, -1, 1,
                                          True)

        (fromPosn, toPosn) = nextMove

        return (fromPosn, toPosn)

    def _boardSearch(self, board, color, depth, min, max, isMaxNode):
        """Performs a search of the given board using alpha-beta pruning

        @param board: The starting board state to evaluate
        @param color: The color of the player to generate a move for
        @param depth: The number of plies forward that should be explored
        @param min: Nodes with a likability below this will be ignored
        @param max: Nodes with a likability above this will be ignored

        @return: A tuple with the following elements:
                1. None, or a move of the form (fromChessPosn, toChessPosn)
                    representing the next move that should be made by the given
                    player
                2. The likability of this move's path in the tree, as followed
                    by the search and as determined by the likability of the
                    leaf node terminating the path

        Implementation based on information found here: http://bit.ly/t1dHKA"""
        ##TODO (James): Incorporate quiescent search
        ## TODO (James): Incorporate timeout
        ## TODO (James): This gets stuck on depth == 0. Why?

        self._logger.info("Searching for best move to depth {0}".format(depth))

        otherColor = ChessBoard.getOtherColor(color)

        # Check if we are at a leaf node
        if ((depth == 0) or
            board.isKingCheckmated(color) or
            board.isKingCheckmated(otherColor)):
            return (None, evaluateBoardLikability(color, board))
        else:
            moveChoices = enumPossBoardMoves(board, color)

            # Check whether seeking to find minimum or maximum value
            if isMaxNode:
                newMin = min
                for move in moveChoices:
                    nodeBoard = board.getResultOfPly(move[0], move[1])

                    # Find the next move for this node, and how likable the
                    # enemy will consider this child node
                    (_, nodeEnemyLikability) = self._boardSearch(nodeBoard,
                                                                otherColor,
                                                                depth - 1,
                                                                newMin, max,
                                                                not isMaxNode)
                    # Make note of the least likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability > newMin:
                        newMin = nodeEnemyLikability

                    # Don't search outside of the target range
                    elif nodeEnemyLikability > max:
                        return (move, max)
                return (move, newMin)
            else:
                newMax = max
                for move in moveChoices:
                    nodeBoard = board.getResultOfPly(move[0], move[1])

                    # Find how likable the enemy will consider this child node
                    (_, nodeEnemyLikability) = self._boardSearch(nodeBoard,
                                                                otherColor,
                                                                depth - 1,
                                                                min, newMax,
                                                                not isMaxNode)

                    # Make note of the most likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability < newMax:
                        newMax = nodeEnemyLikability

                    # Don't bother searching outside of our target range
                    elif nodeEnemyLikability < min:
                        return min
                return (move, newMax)


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
