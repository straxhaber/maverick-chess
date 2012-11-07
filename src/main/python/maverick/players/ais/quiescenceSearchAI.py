#!/usr/bin/python

"""QLAI.py: AI that uses a quiescence search with a likability heuristic"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.players.ais.common import MaverickAI


class QLAI(MaverickAI):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.quiescenceSearchAI.QLAI")
    logging.basicConfig(level=logging.INFO)

    def getNextMove(self, board):
        pass  # TODO (mattsh): write this

    def evaluateBoardLikability(self):
        """Returns a number in [-1,1] based on likability of the position

        The calculated value has the following properties:
         - Lower numbers indicate greater likelihood of a bad outcome (loss)
         - Higher numbers indicate greater likelihood of a good outcome (win)
         - -1 means guaranteed loss
         - 0 means neither player is favored; can mean a state of draw
         - +1 means guaranteed win"""

        # Data structure of 'opinions' from heuristics
        # Format: ListOf[("Name", weight, value)]
        opinions = [("PeanutGallery", 1, 0)]

        # TODO (mattsh): write heuristics

        # Return the weighted average
        return sum([weight * value for (_, weight, value) in opinions]) / \
            sum([weight for (_, weight, _) in opinions])


def main():
    ai = QLAI()
    ai.runAI()

if __name__ == '__main__':
    main()
