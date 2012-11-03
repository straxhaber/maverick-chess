#!/usr/bin/python

"""TODO.py: TODO write a description"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

import random
import time

from ...client import MaverickClient
from ...server import ChessMatch

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################


class FooAI(MaverickClient):
    """TODO"""

    def __init__(self):
        MaverickClient.__init__(self)
        self.name = ".".join(self.__class__.__name__,
                             str(time.time()),
                             str(random.randrange(1, 2 ** 30)))

    def _getPlaying(self):
        self.playerID = self.register(self.name)
        self.gameID = self.joinGame(self.playerID)
        while True:
            self.getStatus(self.gameID)
            ChessMatch.STATUS_PENDING

    def runAI(self):
        self._getPlaying()  # TODOx


def _main():
    print "This class should not be run directly"

if __name__ == '__main__':
    _main()
