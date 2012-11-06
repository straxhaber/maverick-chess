#!/usr/bin/python

"""common.py: Common code for gameplay interfaces"""

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import logging
import random
import time

from maverick.client import MaverickClient
from maverick.server import ChessBoard
from maverick.server import ChessMatch


class MaverickPlayer(MaverickClient):
    """Provides basic methods for a Maverick AI"""

    # Initialize class _logger
    _logger = logging.getLogger("maverick.players.common.MaverickPlayer")
    logging.basicConfig(level=logging.INFO)

    SLEEP_TIME = 1
    """Amount of time to wait between requests when polling"""

    def __init__(self):
        """Initialize a MaverickPlayer

        NOTE: MaverickPlayer.startPlaying must be run to set playerID, gameID,
        and isWhite before the player can make moves"""

        MaverickClient.__init__(self)

        # Default name (should be overridden for a human AI)
        # i.e., MaverickAI.1234901234.12839429834
        self.name = ".".join([self.__class__.__name__,
                              str(time.time()),
                              str(random.randrange(1, 2 ** 30))])

        # These variables must be overridden
        self.playerID = None    # ID for player's system registration
        self.gameID = None      # ID for game that the player is in
        self.isWhite = None     # Is the player white?

    def displayMessage(self, message):
        """Display a message for the user"""
        print(" -- {0}".format(message))

    def startPlaying(self):
        """Enters the player into an ongoing game (blocks until successful)

        @precondition: self.name must be set"""
        self.playerID = self.register(self.name)
        self.gameID = self.joinGame(self.playerID)

        # Block until game has started
        while self.getStatus() == ChessMatch.STATUS_PENDING:
            self.displayMessage("Waiting until the game starts")
            time.sleep(MaverickPlayer.SLEEP_TIME)

        # NOTE: Player is now in a game that is not pending

        if self.getState()["youAreColor"] == ChessBoard.WHITE:
            self.isWhite = True
        else:
            self.isWhite = False

    def run(self):
        """TODO method comment"""
        raise NotImplementedError("Must be overridden by the extending class")

    def getStatus(self):
        return MaverickClient.getStatus(self, self.gameID)
    #MaverickPlayer.getStatus.__doc__ = MaverickClient.getStatus.__doc__

    def getState(self):
        return MaverickClient.getState(self, self.playerID, self.gameID)
    #MaverickPlayer.getState.__doc__ = MaverickClient.getState.__doc__

    def makePly(self, fromRank, fromFile, toRank, toFile):
        MaverickClient.makePly(self,
                               self.playerID, self.gameID,
                               fromRank, fromFile,
                               toRank, toFile)
    ## TODO
    #MaverickPlayer.makePly.__doc__ = MaverickClient.makePly.__doc__


def main():
    print "This class should not be run directly"

if __name__ == '__main__':
    main()
