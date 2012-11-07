import unittest

from maverick.server import TournamentSystem


class TestTournamentSystem(unittest.TestCase):
    # Note: this is not a proper unit test

    ts = TournamentSystem()
    p1 = ts.request_register("a")[1]["playerID"]
    p2 = ts.request_register("b")[1]["playerID"]
    gid = ts.request_joinGame(p1)[1]["gameID"]
    ts.request_joinGame(p2)
    state = ts.request_getState(gid)

    wp = state[1]['players']['O']
    bp = state[1]['players']['X']

    print ts.request_makePly(wp, gid, 2, 5, 4, 5)
    print ts.request_makePly(bp, gid, 7, 5, 5, 5)
    print ts.request_makePly(wp, gid, 1, 4, 5, 8)
    print ts.request_makePly(bp, gid, 8, 2, 6, 3)
    print ts.request_makePly(wp, gid, 1, 6, 4, 3)
    print ts.request_makePly(bp, gid, 8, 7, 6, 6)
    print ts.request_makePly(wp, gid, 5, 8, 7, 6)

    print ts.request_getStatus(gid)
    print ts.request_getState(gid)

if __name__ == '__main__':
    unittest.main()
