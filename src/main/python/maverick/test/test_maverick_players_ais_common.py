'''
Created on Nov 13, 2012

@author: mattsh
'''
import unittest

from maverick.data import ChessBoard
from maverick.data import ChessPosn
from maverick.players.ais.common import MaverickAI


class Test(unittest.TestCase):

    def test_Name(self):
        cb = ChessBoard()

        allM = MaverickAI.enumBoardMoves(cb, ChessBoard.WHITE)

        # "Should be 20 possible moves at start")
        self.assertItemsEqual([(ChessPosn(1, 0), ChessPosn(2, 0)),
                               (ChessPosn(1, 0), ChessPosn(3, 0)),
                               (ChessPosn(1, 1), ChessPosn(2, 1)),
                               (ChessPosn(1, 1), ChessPosn(3, 1)),
                               (ChessPosn(1, 2), ChessPosn(2, 2)),
                               (ChessPosn(1, 2), ChessPosn(3, 2)),
                               (ChessPosn(1, 3), ChessPosn(2, 3)),
                               (ChessPosn(1, 3), ChessPosn(3, 3)),
                               (ChessPosn(1, 4), ChessPosn(2, 4)),
                               (ChessPosn(1, 4), ChessPosn(3, 4)),
                               (ChessPosn(1, 5), ChessPosn(2, 5)),
                               (ChessPosn(1, 5), ChessPosn(3, 5)),
                               (ChessPosn(1, 6), ChessPosn(2, 6)),
                               (ChessPosn(1, 6), ChessPosn(3, 6)),
                               (ChessPosn(1, 7), ChessPosn(2, 7)),
                               (ChessPosn(1, 7), ChessPosn(3, 7)),
                               (ChessPosn(0, 1), ChessPosn(2, 0)),
                               (ChessPosn(0, 1), ChessPosn(2, 2)),
                               (ChessPosn(0, 6), ChessPosn(2, 5)),
                               (ChessPosn(0, 6), ChessPosn(2, 7))],
                              allM)
        self.assertEqual(20, len(allM))


if __name__ == "__main__":
    unittest.main()
