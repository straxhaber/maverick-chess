#!/usr/bin/python

"""TODO.py: TODO write a description"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging

from maverick.players.common import MaverickPlayer


class MaverickAI(MaverickPlayer):

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.ais.stub.MaverickAI")
    logging.basicConfig(level=logging.INFO)

    def runAI(self):
        self.startPlaying()
        MaverickAI._logger("I ({0}) have entered game {1}",
                           self.playerID,
                           self.gameID)

        # TODO: play a game (probably some sort of loop)


def main():
    ai = MaverickAI()
    ai.runAI()

if __name__ == '__main__':
    main()
