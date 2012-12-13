#!/usr/bin/python

"""randomAI.py: Provides an AI that makes random moves"""

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

from __future__ import division

from argparse import ArgumentDefaultsHelpFormatter
from argparse import ArgumentParser
import logging
import random

from maverick.data.structs import ChessBoard
from maverick.players.ais.common import MaverickAI, MaverickAIException
from maverick.data.utils import enumMoves


__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"
__all__ = ["RandomAI", "runAI"]


class RandomAI(MaverickAI):
    """Represents a random mover AI for use with Maverick"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.randomAI.RandomAI")
    # Initialize if not already initialized
    logging.basicConfig(level=logging.INFO)

    def getNextMove(self, board):
        """Pick a random move from an enumeration of legal moves"""
        color = ChessBoard.WHITE if self.isWhite else ChessBoard.BLACK
        moveChoices = enumMoves(board, color)
        if moveChoices:
            move = random.choice(moveChoices)
            return move
        else:
            # NOTE: This code should be unreachable. If it gets here,
            #       either stale-mate detection is broken or a race condition
            #       is leading to the AI being asked for a move guess before
            #       stale-mate is properly updated
            raise MaverickAIException("No possible moves... SEE CODE COMMENT")


def runAI(host=None, port=None):
    ai = RandomAI(host=host, port=port)
    ai.run(startFreshP=True)


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
