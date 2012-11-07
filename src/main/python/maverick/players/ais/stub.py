#!/usr/bin/python

"""stub.py: TODO (mattsh) write a description in concrete copy of this stub"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.players.common import MaverickPlayer


class MaverickAIException(Exception):
    """Base class for Exceptions from Maverick AIs"""
    pass


class MaverickAI(MaverickPlayer):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.stub.MaverickAI")
    logging.basicConfig(level=logging.INFO)

    CALCULATION_TIMEOUT = 5
    """Maximum amount of time for the AI to take to make its move"""

    def initName(self):
        """Figure out the name of the class"""
        pass  # Default name is appropriate

    def welcomePlayer(self):
        """Display welcome messages if appropriate"""
        MaverickAI._logger.info("I, {0} ({1}), have entered game {2}",
                                self.name,
                                self.playerID,
                                self.gameID)

    def getNextMove(self, board):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")
        # TODO (mattsh): write this

    def handleBadMove(self, errMsg, board, fromRank, fromFile, toRank, toFile):
        """Calculate the next move based on the provided board"""
        raise NotImplementedError("Must be overridden by the extending class")


def main():
    ai = MaverickAI()
    ai.runAI()

if __name__ == '__main__':
    main()
