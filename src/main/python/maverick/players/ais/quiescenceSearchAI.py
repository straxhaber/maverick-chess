#!/usr/bin/python

"""quiescenceSearchAI.py: AI that uses a quiescence search with heuristics"""

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

from __future__ import division

import logging
import random

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
from time import time

from maverick.players.ais.analyzers.likability import evaluateBoardLikability
from maverick.players.ais.common import MaverickAI
from maverick.data.structs import ChessBoard
from maverick.data.utils import enumMoves

## TODO (mattsh): Not sure, but is there a way we can cache some board enums?
## TODO (James): @mattsh, yes there is - it's called a transposition table.
#                I mentioned this in an email, but there isn't time to get it
#                implemented reliably

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"
__all__ = ["QLAI", "runAI"]


class QLAI(MaverickAI):
    """Represents a quiescence search-based AI for use with Maverick"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.quiescenceSearchAI.QLAI")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.DEBUG)

    # Default heuristic weights for likability evaluation
    defaultWeights = {'pieceValWeight': 0.8,
                         'inCheckWeight': 1,
                         'pcsUnderAttackWeight': 0.5,
                         'emptySpaceCvgWeight': 0.3,
                         'piecesCoveredWeight': 0.2}

    def __init__(self, host=None, port=None, pieceValWgt=None,
                 inCheckWgt=None, piecesUnderAttackWgt=None,
                 emptySpaceCoverageWgt=None, piecesCoveredWgt=None):
        """Initialize a QLAI

        Notes the given heuristic weights, and calls superclass constructor"""

        MaverickAI.__init__(self, host=host, port=port)

        # Construct a dictionary of heuristic weight values
        self.heuristicWgts = {}
        if pieceValWgt is None:
            self.heuristicWgts['pieceValWeight'] = \
                QLAI.defaultWeights['pieceValWeight']
        else:
            self.heuristicWgts['pieceValWeight'] = pieceValWgt

        if inCheckWgt is None:
            self.heuristicWgts['inCheckWeight'] = \
                QLAI.defaultWeights['inCheckWeight']
        else:
            self.heuristicWgts['inCheckWeight'] = inCheckWgt

        if piecesUnderAttackWgt is None:
            self.heuristicWgts['pcsUnderAttackWeight'] = \
                QLAI.defaultWeights['pcsUnderAttackWeight']
        else:
            self.heuristicWgts['pcsUnderAttackWeight'] = piecesUnderAttackWgt

        if emptySpaceCoverageWgt is None:
            self.heuristicWgts['emptySpaceCvgWeight'] = \
                QLAI.defaultWeights['emptySpaceCvgWeight']
        else:
            self.heuristicWgts['emptySpaceCvgWeight'] = emptySpaceCoverageWgt

        if piecesCoveredWgt is None:
            self.heuristicWgts['piecesCoveredWeight'] = \
                QLAI.defaultWeights['piecesCoveredWeight']
        else:
            self.heuristicWgts['piecesCoveredWeight'] = piecesCoveredWgt

    def getNextMove(self, board):
        """TODO PyDoc"""
        print board

        SEARCH_DEPTH = 2  # Search to a depth of 3

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
        (nextMv, _, nodesVisited) = self._boardSearch(board, color,
                                                      SEARCH_DEPTH, -1, 1,
                                                      True, time() +
                                                      SEARCH_TIME_SECONDS)

        # Make sure we found a move
        if nextMv is None:
            possMoves = enumMoves(board, color)
            nextMv = random.choice(possMoves)

        logStrF = "Best found move was {0} -> {1}".format(nextMv[0], nextMv[1])
        QLAI._logger.info(logStrF)
        (fromPosn, toPosn) = nextMv

        return (fromPosn, toPosn)

    def _quiescentSearch(self, board, color, alpha, beta, isMaxNode):
        """Perform a quiescent search on the given board, examining captures

        Enumerates captures, and evaluates them to see if they alter results

        @param board: The starting board state to evaluate
        @param color: The color of the player to generate a move for
        @param alpha: Nodes with a likability below this will be ignored
        @param beta: Nodes with a likability above this will be ignored
        @param isMaxNode: Is this a beta node? (Is this node seeking to
                        maximize the value of child nodes?)

        @return: A tuple with the following elements:
                1. None, or a move of the form (fromChessPosn, toChessPosn)
                    representing the next move that should be made by the given
                    player
                2. The likability of this move's path in the tree, as followed
                    by the search and as determined by the likability of the
                    leaf node terminating the path

        No timeout is allowed. This shouldn't take long, anyway. If it does,
        then we're doing good things.

        Note: this was influenced by information here: http://bit.ly/VYlJVC """

        otherColor = ChessBoard.getOtherColor(color)

        # Note the appeal of this board, with no captures
        standPatVal = evaluateBoardLikability(color, board,
                                              self.heuristicWgts)

        # Build up a list of capture moves

        moveChoices = enumMoves(board, color)
        moveFilterFunct = lambda m: ((board[m[1]] is not None) and
                                    (board[m[1]].color == otherColor))
        captureMoves = filter(moveFilterFunct, moveChoices)

        # Determine whether captures are a good or a bad thing
        if isMaxNode:

            # Check whether it is even worth proceeding with evaluation
            if (standPatVal > beta):
                return (None, beta)
            elif (alpha < standPatVal):
                alpha = standPatVal

            # Evaluate all captures
            for capMv in captureMoves:
                boardMoveUndoDict = board.getPlyResult(capMv[0], capMv[1])
                moveResultScore = evaluateBoardLikability(otherColor, board,
                                                          self.heuristicWgts)
                board.undoPlyResult(boardMoveUndoDict)

                # Don't bother searching outside of target range
                if (moveResultScore > beta):
                    return (None, beta)

                # Check whether we've found something superior to our best
                elif (moveResultScore > alpha):
                    alpha = moveResultScore

            # All captures for this node have been evaluated - return best
            return (None, alpha)
        else:
            # Check whether it is even worth proceeding with evaluation
            if (standPatVal < alpha):
                return (None, alpha)
            elif (beta > standPatVal):
                beta = standPatVal

            # Evaluate all captures
            for capMv in captureMoves:
                boardMoveUndoDict = board.getPlyResult(capMv[0], capMv[1])
                moveResultScore = evaluateBoardLikability(otherColor, board,
                                                          self.heuristicWgts)
                board.undoPlyResult(boardMoveUndoDict)

                # Don't bother searching outside of target range
                if (moveResultScore > alpha):
                    return (None, alpha)

                # Check whether we've found something superior to our best
                elif (moveResultScore < beta):
                    beta = moveResultScore

            # All captures for this node have been evaluated - return best
            return (None, beta)

    def _boardSearch(self, board, color, depth, alpha, beta,
                     isMaxNode, stopSrchTime):
        """Performs a board via alpha-beta pruning/quiescence search

        NOTE: Not guaranteed to stop promptly at stopSrchTime - may take some
        time to terminate. Leave a time buffer.

        Selectively explores past the final depth if many pieces have
        been captured recently, by calling quiescent search

        @param board: The starting board state to evaluate
        @param color: The color of the player to generate a move for
        @param depth: The number of plies forward that should be explored
        @param alpha: Nodes with a likability below this will be ignored
        @param beta: Nodes with a likability above this will be ignored
        @param isMaxNode: Is this a beta node? (Is this node seeking to
                        maximize the value of child nodes?)
        @param stopSrchTime: Time at which the search should begin to terminate
        @param nodesVisited: The number of nodes already searched

        @return: A tuple with the following elements:
                1. None, or a move of the form (fromChessPosn, toChessPosn)
                    representing the next move that should be made by the given
                    player
                2. The likability of this move's path in the tree, as followed
                    by the search and as determined by the likability of the
                    leaf node terminating the path
                3. The number of nodes visited in the search

        Implementation based on information found here: http://bit.ly/t1dHKA"""
        ## TODO (James): Check timeout less than once per iteration

        ## TODO (James): Make logging conditional - temporarily disabled

        ## TODO (James): Set this to True before handing in!
        # Whether to limit based on wall clock time or number of nodes seen
        USE_WALL_CLOCK = False

        # Number of nodes to visit (for when wall clock time is not used)
        NUM_NODES_TO_VISIT = 1200

        #logStrF = "Performing minimax search to depth {0}.".format(depth)
        #QLAI._logger.debug(logStrF)

        # Note that we've visited a node
        nodesVisited = 1

        otherColor = ChessBoard.getOtherColor(color)

        # Check if we are at a leaf node
        if (depth == 0):
            (a, b) = self._quiescentSearch(board, color, alpha, beta,
                                           isMaxNode)
            return (a, b, 1)

        # Check if we should otherwise terminate
        elif (time() > stopSrchTime or
              board.isKingCheckmated(color) or
              board.isKingCheckmated(otherColor)):
            return (None, evaluateBoardLikability(color, board,
                                                  self.heuristicWgts),
                    nodesVisited)

        else:
            moveChoices = enumMoves(board, color)
            #logStrF = "Considering {0} poss. moves".format(len(moveChoices))
            #QLAI._logger.debug(logStrF)

            # Check whether seeking to find minimum or maximum value
            if isMaxNode:
                newMin = alpha
                newMoveChoice = None
                for move in moveChoices:

                    # Rather than calling getPlyResult, use THIS board. Much
                    # faster. REMEMBER TO UNDO THIS HYPOTHETICAL MOVE

                    # Save the old flag sets so they can be restored
                    boardMoveUndoDict = board.getPlyResult(move[0], move[1])

                    # Find the next move for this node, and how likable the
                    # enemy will consider this child node
                    (_, nodeEnemyLikability, nVisit) = self._boardSearch(board,
                                                                 otherColor,
                                                                 depth - 1,
                                                                 newMin, beta,
                                                                 not isMaxNode,
                                                                 stopSrchTime)
                    # RESTORE THE OLD BOARD STATE - VERY IMPORTANT
                    board.undoPlyResult(boardMoveUndoDict)

                    # Note how many more nodes we've visited
                    nodesVisited += nVisit

                    # Make note of the least likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability > newMin:
                        newMin = nodeEnemyLikability
                        newMoveChoice = move

                    # Don't search outside of the target range
                    elif nodeEnemyLikability > beta:
                        #QLAI._logger.debug("Pruning because new value > beta")
                        return (move, beta, nodesVisited)

                    # Check to see if we've evaluated the max number of nodes
                    if ((not USE_WALL_CLOCK) and
                        (nodesVisited > NUM_NODES_TO_VISIT)):
                        return (newMoveChoice, newMin, nodesVisited)

                return (newMoveChoice, newMin, nodesVisited)
            else:
                newMax = beta
                newMoveChoice = None
                for move in moveChoices:

                    # Rather than calling getPlyResult, use THIS board. Much
                    # faster. REMEMBER TO UNDO THIS HYPOTHETICAL MOVE

                    # Save the old flag sets so they can be restored
                    boardMoveUndoDict = board.getPlyResult(move[0], move[1])

                    # Find how likable the enemy will consider this child node
                    (_, nodeEnemyLikability, nVisit) = self._boardSearch(board,
                                                                 otherColor,
                                                                 depth - 1,
                                                                 alpha, newMax,
                                                                 not isMaxNode,
                                                                 stopSrchTime)

                    # RESTORE THE OLD BOARD STATE - VERY IMPORTANT:
                    board.undoPlyResult(boardMoveUndoDict)

                    # Note how many more nodes we've visited
                    nodesVisited += nVisit

                    # Make note of the most likable branches that it still
                    # makes sense to pursue, given how likable this one is
                    if nodeEnemyLikability < newMax:
                        newMax = nodeEnemyLikability
                        newMoveChoice = move

                    # Don't bother searching outside of our target range
                    elif nodeEnemyLikability < alpha:
                        #QLAI._logger.debug("pruning because new val < alpha")
                        return (move, alpha, nodesVisited)

                    # Check to see if we've evaluated the max number of nodes
                    if ((not USE_WALL_CLOCK) and
                        (nodesVisited > NUM_NODES_TO_VISIT)):
                        return (newMoveChoice, newMin, nodesVisited)
                return (newMoveChoice, newMax, nodesVisited)

    def _showPlayerMove(self, board, fromPosn, toPosn):
        pass  # No printouts needed for AI


def runAI(host=None, port=None, pieceValWeight=None, inCheckWeight=None,
          piecesUnderAttackWeight=None, emptySpaceCoverageWeight=None,
          piecesCoveredWeight=None):
    ai = QLAI(host=host, port=port, pieceValWgt=pieceValWeight,
              inCheckWgt=inCheckWeight,
              piecesUnderAttackWgt=piecesUnderAttackWeight,
              emptySpaceCoverageWgt=emptySpaceCoverageWeight,
              piecesCoveredWgt=piecesCoveredWeight)
    ai.run(startFreshP=False)


def main():
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("--host", default=None, type=str,
                        help="specify hostname of Maverick server")
    parser.add_argument("--port", default=None, type=int,
                        help="specify port of Maverick server")
    parser.add_argument("--piecevalweight", default=None, type=int,
                        help="specify weight of pieceValue heuristic")
    parser.add_argument("--incheckweight", default=None, type=int,
                        help="specify weight of inCheck heuristic")
    parser.add_argument("--piecesunderattackweight", default=None, type=int,
                        help="specify weight of piecesUnderAttack heuristic")
    parser.add_argument("--emptyspacecoverageweight", default=None, type=int,
                        help="specify weight of emptySpaceCoverage heuristic")
    parser.add_argument("--piecescoveredweight", default=None, type=int,
                        help="specify weight of piecesCovered heuristic")
    args = parser.parse_args()
    runAI(host=args.host, port=args.port, pieceValWeight=args.piecevalweight,
          inCheckWeight=args.incheckweight,
          piecesUnderAttackWeight=args.piecesunderattackweight,
          emptySpaceCoverageWeight=args.emptyspacecoverageweight,
          piecesCoveredWeight=args.piecescoveredweight)

if __name__ == '__main__':
    main()
