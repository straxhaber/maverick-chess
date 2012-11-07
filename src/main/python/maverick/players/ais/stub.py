#!/usr/bin/python

"""stub.py: TODO (mattsh) write a description in concrete copy of this stub"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.data import ChessMatch
from maverick.players.common import MaverickPlayer


class MaverickAI(MaverickPlayer):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.stub.MaverickAI")
    logging.basicConfig(level=logging.INFO)

    def runAI(self):
        self.startPlaying()
        MaverickAI._logger.info("I, {0} ({1}), have entered game {2}",
                                self.name,
                                self.playerID,
                                self.gameID)

        while self.getStatus() == ChessMatch.STATUS_ONGOING:
            pass

        # TODO (mattsh): in concrete copy of this stub, play a game
        # (probably some sort of loop)


def main():
    ai = MaverickAI()
    ai.runAI()

if __name__ == '__main__':
    main()
