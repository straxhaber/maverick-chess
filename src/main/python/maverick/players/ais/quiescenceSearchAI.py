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
import random
from time import clock, time

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
    logging.basicConfig(level=logging.DEBUG)

    numNodesCovered = 0
    nodesCoveredByDepth = {0: [0, 0],
                           1: [0, 0],
                           2: [0, 0],
                           #3: [0, 0],
                           3: [0, 1]}

    def getNextMove(self, board):
        """TODO PyDoc"""

        # TODO (James): Remove this - show us the board, just for development
        self.printBoard()

        SEARCH_DEPTH = 3

        # How long we want to allow the search to run before it starts
        # terminating - most tournaments allow 3 minutes per turn.
        # Experience shows that 0.5 seconds is more than enough buffer time
        SEARCH_TIME_SECONDS = (MaverickAI.CALCULATION_TIMEOUT * 60) - 0.5

        # Figure out our color
        if self.isWhite:
            color = ChessBoard.WHITE
        else:
            color = ChessBoard.BLACK

        QLAI._logger.info("Calculating next move")
        QLAI.numNodesCovered = 0
        (nextMove, _) = self._boardSearch(board, color, SEARCH_DEPTH, -1, 1,
                                          True, time() + SEARCH_TIME_SECONDS)
        logStrF = "Best found move was {0} -> {1}".format(nextMove[0],
                                                          nextMove[1])
        QLAI._logger.info(logStrF)

        print "Evaluated {0} nodes".format(QLAI.numNodesCovered)

        nc = QLAI.nodesCoveredByDepth
        print "Evaluated {0} of {1} level 0 nodes, \
                {2} of {3} level 1 nodes,\
                {4} of {5} level 2 nodes,\
                {6} of {7} level 3 nodes".format(nc[0][0], nc[0][1],
                                                  nc[1][0], nc[1][1],
                                                  nc[2][0], nc[2][1],
                                                  nc[3][0], nc[3][1])
        for i in range(0, 4):
            for j in range(0, 2):
                QLAI.nodesCoveredByDepth[i][j] = 0
        QLAI.nodesCoveredByDepth[3][1] = 1

        # Make sure we found a move
        if nextMove is None:
            possMoves = enumPossBoardMoves(board, color)
            nextMove = random.choice(possMoves)

        (fromPosn, toPosn) = nextMove

        return (fromPosn, toPosn)

    def _boardSearch(self, board, color, depth, alpha, beta,
                     isMaxNode, stopSrchTime):
        """Performs a search of the given board using alpha-beta pruning

        NOTE: Not guaranteed to stop promptly at stopSrchTime - may take some
        time to terminate. Leave a time buffer.

        @param board: The starting board state to evaluate
        @param color: The color of the player to generate a move for
        @param depth: The number of plies forward that should be explored
        @param alpha: Nodes with a likability below this will be ignored
        @param beta: Nodes with a likability above this will be ignored
        @param isMaxNode: Is this a beta node? (Is this node seeking to
                        maximize the value of child nodes?)
        @param stopSrchTime: Time at which the search should begin to terminate

        @return: A tuple with the following elements:
                1. None, or a move of the form (fromChessPosn, toChessPosn)
                    representing the next move that should be made by the given
                    player
                2. The likability of this move's path in the tree, as followed
                    by the search and as determined by the likability of the
                    leaf node terminating the path

        Implementation based on information found here: http://bit.ly/t1dHKA"""
        ## TODO (James): Incorporate quiescence search
        ## TODO (James): Check timeout less than once per iteration
        ## TODO (James): remove references to QLAI.numNodesCovered - it is only
        #                here for testing purposes
        ## TODO (James): Make logging conditional - temporarily disabled
        QLAI.numNodesCovered += 1

        #logStrF = "Performing minimax search to depth {0}.".format(depth)
        #QLAI._logger.debug(logStrF)

        otherColor = ChessBoard.getOtherColor(color)

        QLAI.nodesCoveredByDepth[depth][0] += 1
        # Check if we are at a leaf node, or should otherwise terminate
        if ((depth == 0) or
            time() > stopSrchTime or
            board.isKingCheckmated(color) or
            board.isKingCheckmated(otherColor)):
            return (None, evaluateBoardLikability(color, board))

        else:
            moveChoices = enumPossBoardMoves(board, color)
            QLAI.nodesCoveredByDepth[depth - 1][1] += len(moveChoices)
            #logStrF = "Considering {0} possible moves".format(len(moveChoices))
            #QLAI._logger.debug(logStrF)

            # Check whether seeking to find minimum or maximum value
            if isMaxNode:
                newMin = alpha
                newMoveChoice = None
                for move in moveChoices:

                    # Rather than calling getResultOfPly, use THIS board. Much
                    # faster. REMEMBER TO UNDO THIS HYPOTHETICAL MOVE

                    # Save the old flag sets so they can be restored
                    boardMoveUndoDict = board.getResultOfPly(move[0], move[1])

                    # Find the next move for this node, and how likable the
                    # enemy will consider this child node
                    (_, nodeEnemyLikability) = self._boardSearch(board,
                                                                 otherColor,
                                                                 depth - 1,
                                                                 newMin, beta,
                                                                 not isMaxNode,
                                                                 stopSrchTime)
##################### RESTORE THE OLD BOARD STATE - VERY IMPORTANT:############

                    board.unGetResultOfPly(boardMoveUndoDict)

###############################################################################

                    # Make note of the least likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability > newMin:
                        newMin = nodeEnemyLikability
                        newMoveChoice = move

                    # Don't search outside of the target range
                    elif nodeEnemyLikability > beta:
                        #QLAI._logger.debug("Pruning because new value > beta")
                        return (move, beta)
                return (newMoveChoice, newMin)
            else:
                newMax = beta
                newMoveChoice = None
                for move in moveChoices:

                    # Rather than calling getResultOfPly, use THIS board. Much
                    # faster. REMEMBER TO UNDO THIS HYPOTHETICAL MOVE

                    # Save the old flag sets so they can be restored
                    boardMoveUndoDict = board.getResultOfPly(move[0], move[1])

                    # Find how likable the enemy will consider this child node
                    (_, nodeEnemyLikability) = self._boardSearch(board,
                                                                 otherColor,
                                                                 depth - 1,
                                                                 alpha, newMax,
                                                                 not isMaxNode,
                                                                 stopSrchTime)

##################### RESTORE THE OLD BOARD STATE - VERY IMPORTANT:############

                    board.unGetResultOfPly(boardMoveUndoDict)

###############################################################################

                    # Make note of the most likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability < newMax:
                        newMax = nodeEnemyLikability
                        newMoveChoice = move

                    # Don't bother searching outside of our target range
                    elif nodeEnemyLikability < alpha:
                        #QLAI._logger.debug("pruning because new value < alpha")
                        return (move, alpha)
                return (newMoveChoice, newMax)

    def _showPlayerMove(self, board, fromPosn, toPosn):
        pass  # No printouts needed for AI


def runAI(host=None, port=None):
    ai = QLAI(host=host, port=port)
    ai.run(startFreshP=False)


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host", default=None, type=str,
                        help="specify hostname of Maverick server")
    parser.add_argument("--port", default=None, type=int,
                        help="specify port of Maverick server")
    args = parser.parse_args()
    runAI(host=args.host, port=args.port)

if __name__ == '__main__':
    import cProfile
    cProfile.run('runAI()', '/home/jimbo/aiprofilefile')
