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


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
