import unittest

from maverick.data import ChessBoard
from maverick.server import TournamentSystem


class TestTournamentSystem(unittest.TestCase):
    # Note: this is not a proper unit test

    ts = TournamentSystem()
    p1 = ts.register("a")[1]["playerID"]
    p2 = ts.register("b")[1]["playerID"]
    gid = ts.joinGame(p1)[1]["gameID"]
    ts.joinGame(p2)
    state = ts.getState(p2, gid)

    if state[1]['youAreColor'] == ChessBoard.WHITE:
      wp = p2
      bp = p1
    else:
      wp = p1
      bp = p2

    print ts.makePly(wp, gid, 1, 4, 3, 4)
    print ts.makePly(bp, gid, 6, 4, 4, 4)
    print ts.makePly(wp, gid, 0, 3, 4, 7)
    print ts.makePly(bp, gid, 7, 2, 5, 2)
    print ts.makePly(wp, gid, 0, 5, 3, 2)
    print ts.makePly(bp, gid, 7, 6, 5, 5)
    print ts.makePly(wp, gid, 4, 7, 6, 5)

    print ts.getStatus(gid)
    print ts.getState(p2, gid)

if __name__ == '__main__':
    unittest.main()
