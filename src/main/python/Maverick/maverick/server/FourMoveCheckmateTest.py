import unittest

from TournamentSystem import TournamentSystem


class TestTournamentSystem(unittest.TestCase):
    ts = TournamentSystem()
    p1 = ts.register("a")[1]["playerID"]
    p2 = ts.register("b")[1]["playerID"]
    gid = ts.joinGame(p1)[1]["gameID"]
    ts.joinGame(p2)
    state = ts.getState(gid)

    wp = state[1]['players']['O']
    bp = state[1]['players']['X']

    print ts.makePly(wp, gid, 2, 5, 4, 5)
    print ts.makePly(bp, gid, 7, 5, 5, 5)
    print ts.makePly(wp, gid, 1, 4, 5, 8)
    print ts.makePly(bp, gid, 8, 2, 6, 3)
    print ts.makePly(wp, gid, 1, 6, 4, 3)
    print ts.makePly(bp, gid, 8, 7, 6, 6)
    print ts.makePly(wp, gid, 5, 8, 7, 6)

    print ts.getStatus(gid)
    print ts.getState(gid)

if __name__ == '__main__':
    unittest.main()
