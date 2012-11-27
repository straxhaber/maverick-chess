'''
Created on Nov 13, 2012

@author: James Magnarelli and Matthew Strax-Haber
'''

from __future__ import division

import unittest

from maverick.data.structs import ChessBoard
from maverick.players.ais.analyzers.likability import heuristicInCheck
from maverick.players.ais.analyzers.likability import heuristicPcsUnderAttack
from maverick.players.ais.analyzers.likability import heuristicPieceValue
from maverick.players.ais.analyzers.likability import heuristicPiecesCovered
from maverick.players.ais.analyzers.likability import heuristicEmptySpaceCvrg
from maverick.test.common import getBoardNew, getBoardComplex


class Test_maverick_players_ais_quiescenceSearchAI(unittest.TestCase):

    def test_newB_heuristicInCheck(self):
        # Neither player should be in check at the start
        wVal = heuristicInCheck(ChessBoard.WHITE, getBoardNew())
        bVal = heuristicInCheck(ChessBoard.BLACK, getBoardNew())

        self.assertTrue(wVal == 1)
        self.assertTrue(bVal == 1)

    def test_newB_heuristicPieceValue(self):
        wVal = heuristicPieceValue(ChessBoard.WHITE, getBoardNew())
        bVal = heuristicPieceValue(ChessBoard.BLACK, getBoardNew())

        self.assertTrue(wVal == 1)
        self.assertTrue(bVal == 1)

    def test_newB_heuristicEmptySpaceCoverage(self):
        wVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE, getBoardNew())
        bVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK, getBoardNew())

        self.assertTrue(wVal == 0)
        self.assertTrue(bVal == 0)

    def test_newB_heuristicPiecesUnderAttack(self):
        wVal = heuristicPcsUnderAttack(ChessBoard.WHITE, getBoardNew())
        bVal = heuristicPcsUnderAttack(ChessBoard.BLACK, getBoardNew())

        self.assertTrue(wVal == 1)
        self.assertTrue(bVal == 1)

    def test_newB_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        wVal = heuristicPiecesCovered(ChessBoard.WHITE, getBoardNew())
        bVal = heuristicPiecesCovered(ChessBoard.BLACK, getBoardNew())

        properRetVal = -1 + 29 / 39 * 2
        self.assertTrue(wVal == properRetVal)
        self.assertTrue(bVal == properRetVal)

    def test_bCmplx_heuristicInCheck(self):
        # Neither player should be in check at the start
        wVal = heuristicInCheck(ChessBoard.WHITE, getBoardComplex())
        bVal = heuristicInCheck(ChessBoard.BLACK, getBoardComplex())

        self.assertTrue(wVal == 1)
        self.assertTrue(bVal == 1)

    def test_bCmplx_heuristicPieceValue(self):
        wVal = heuristicPieceValue(ChessBoard.WHITE, getBoardComplex())
        bVal = heuristicPieceValue(ChessBoard.BLACK, getBoardComplex())

        properWhiteVal = (39 - 19.5) / 19.5
        properBlackVal = (35 - 19.5) / 19.5

        self.assertTrue(wVal == properWhiteVal)
        self.assertTrue(bVal == properBlackVal)

    def test_bCmplx_heuristicEmptySpaceCoverage(self):
        b = getBoardComplex()
        wVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE, b)
        bVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK, b)

        properWhiteVal = -1 + 22 / 36 * 2
        properBlackVal = -1 + 22 / 36 * 2

        self.assertTrue(wVal == properWhiteVal)
        self.assertTrue(bVal == properBlackVal)

    def test_bCmplx_heuristicPiecesUnderAttack(self):
        wVal = heuristicPcsUnderAttack(ChessBoard.WHITE, getBoardComplex())
        bVal = heuristicPcsUnderAttack(ChessBoard.BLACK, getBoardComplex())

        properWhiteVal = 1 - 2 * (10 / 39)
        properBlackVal = 1 - 2 * (12 / 39)

        self.assertTrue(wVal == properWhiteVal)
        self.assertTrue(bVal == properBlackVal)

    def test_bCmplx_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        wVal = heuristicPiecesCovered(ChessBoard.WHITE, getBoardComplex())
        bVal = heuristicPiecesCovered(ChessBoard.BLACK, getBoardComplex())

        properWhiteVal = -1 + 28 / 39 * 2
        properBlackVal = -1 + 19 / 35 * 2

        self.assertTrue(wVal == properWhiteVal)
        self.assertTrue(bVal == properBlackVal)


if __name__ == "__main__":
    unittest.main()
