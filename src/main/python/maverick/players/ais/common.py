#!/usr/bin/python

"""common.py: TODO write a description"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import random
import time

from maverick.client import MaverickClient
from maverick.server import ChessMatch


class MaverickAI(MaverickClient):
    """Provides basic methods for a Maverick AI"""

    SLEEP_TIME = 0.5
    """Amount of time to wait between requests when polling"""

    def __init__(self):
        """TODO method comment"""
        MaverickClient.__init__(self)

        ## i.e., MaverickAI.1234901234.12839429834
        self.name = ".".join([self.__class__.__name__,
                              str(time.time()),
                              str(random.randrange(1, 2 ** 30))])

    def startPlaying(self):
        """Enters the AI into an ongoing game (blocks until successful)"""
        self.playerID = self.register(self.name)
        self.gameID = self.joinGame(self.playerID)
        while self.getStatus(self.gameID) == ChessMatch.STATUS_PENDING:
            time.sleep(MaverickAI.SLEEP_TIME)
        # Player is now in a game that is not pending

    def runAI(self):
        """TODO method comment"""
        raise NotImplementedError("Must be overridden by the extending class")


def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
