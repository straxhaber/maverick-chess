#!/usr/bin/python

__author__ = "Matthew Strax-Haber and James Magnarelli"
__version__ = "pre-alpha"

###############################################################################
# Code written by Matthew Strax-Haber, James Magnarelli, and Brad Fournier.
# All Rights Reserved. Not licensed for use without express permission.
###############################################################################

import unittest

from maverick.data.structs import ChessBoard
from maverick.data.structs import ChessMatch
from maverick.server import TournamentSystem


class TestTournamentSystem(unittest.TestCase):
    def test_4moveCM(self):
        # Note: this is not a proper unit test

        ts = TournamentSystem()
        p1 = ts.register("a")[1]["playerID"]
        p2 = ts.register("b")[1]["playerID"]
        gid = ts.joinGame(p1, True)[1]["gameID"]
        ts.joinGame(p2, True)
        state = ts.getState(p2, gid)

        if state[1]['youAreColor'] == ChessBoard.WHITE:
            wp = p2
            bp = p1
        else:
            wp = p1
            bp = p2

        succMove1 = ts.makePly(wp, gid, 1, 4, 3, 4)
        self.assertTrue(succMove1[0])
        self.assertEqual(succMove1[1], {})

        self.assertTrue(ts.makePly(bp, gid, 6, 4, 4, 4)[0])
        self.assertTrue(ts.makePly(wp, gid, 0, 3, 4, 7)[0])

        failedMove1 = ts.makePly(bp, gid, 7, 2, 5, 2)
        self.assertFalse(failedMove1[0])
        self.assertEqual(failedMove1[1], {"error": "Illegal move"})

        self.assertFalse(ts.makePly(wp, gid, 0, 5, 3, 2)[0])
        self.assertTrue(ts.makePly(bp, gid, 7, 6, 5, 5)[0])
        self.assertTrue(ts.makePly(wp, gid, 4, 7, 6, 5)[0])

        finalStatus = ts.getStatus(gid)
        self.assertTrue(finalStatus[0])
        self.assertEqual(finalStatus[1],
                         {"status": ChessMatch.STATUS_WHITE_WON})

        finalState = ts.getState(p2, gid)
        self.assertTrue(finalState[0])
        self.assertIsNotNone(finalState[1].get("board"))
        self.assertIsNotNone(finalState[1].get("history"))
        self.assertIsNotNone(finalState[1].get("youAreColor"))
        self.assertIsNotNone(finalState[1].get("isWhitesTurn"))

if __name__ == '__main__':
    unittest.main()
