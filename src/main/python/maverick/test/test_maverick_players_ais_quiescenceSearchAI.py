'''
Created on Nov 13, 2012

@author: James Magnarelli and Matthew Strax-Haber
'''

from __future__ import division

import unittest

from maverick.data import ChessBoard
from maverick.players.ais.analyzers.likability import heuristicInCheck
from maverick.players.ais.analyzers.likability import heuristicPcsUnderAttack
from maverick.players.ais.analyzers.likability import heuristicPieceValue
from maverick.players.ais.analyzers.likability import heuristicPiecesCovered
from maverick.players.ais.analyzers.likability import heuristicEmptySpaceCvrg
from maverick.test import common as commonTest


class Test_maverick_players_ais_quiescenceSearchAI(unittest.TestCase):

    def setUp(self):
        pass

    def test_newB_heuristicInCheck(self):
        # Neither player should be in check at the start
        whiteInCheckVal = heuristicInCheck(ChessBoard.WHITE,
                                           commonTest.getBoardNew())
        blackInCheckVal = heuristicInCheck(ChessBoard.BLACK,
                                           commonTest.getBoardNew())
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_newB_heuristicPieceValue(self):
        whitePieceVal = heuristicPieceValue(ChessBoard.WHITE,
                                            commonTest.getBoardNew())
        blackPieceVal = heuristicPieceValue(ChessBoard.BLACK,
                                            commonTest.getBoardNew())
        self.assertTrue((whitePieceVal == 1) and (blackPieceVal == 1))

    def test_newB_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE,
                                                commonTest.getBoardNew())
        blackBoardVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK,
                                                commonTest.getBoardNew())
        self.assertTrue((whiteBoardVal == 0) and (blackBoardVal == 0))

    def test_newB_heuristicPiecesUnderAttack(self):
        whiteBoardVal = heuristicPcsUnderAttack(ChessBoard.WHITE,
                                                commonTest.getBoardNew())
        blackBoardVal = heuristicPcsUnderAttack(ChessBoard.BLACK,
                                                commonTest.getBoardNew())
        self.assertTrue((whiteBoardVal == 1) and (blackBoardVal == 1))

    def test_newB_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = heuristicPiecesCovered(ChessBoard.WHITE,
                                               commonTest.getBoardNew())
        blackBoardVal = heuristicPiecesCovered(ChessBoard.BLACK,
                                               commonTest.getBoardNew())
        properRetVal = -1 + 29 / 39 * 2
        self.assertTrue((whiteBoardVal == properRetVal)
                        and (blackBoardVal == properRetVal))

    def test_bCmplx_heuristicInCheck(self):
        # Neither player should be in check at the start
        whiteInCheckVal = heuristicInCheck(ChessBoard.WHITE,
                                           commonTest.getBoardComplex())
        blackInCheckVal = heuristicInCheck(ChessBoard.BLACK,
                                           commonTest.getBoardComplex())
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_bCmplx_heuristicPieceValue(self):
        whitePieceVal = heuristicPieceValue(ChessBoard.WHITE,
                                            commonTest.getBoardComplex())
        blackPieceVal = heuristicPieceValue(ChessBoard.BLACK,
                                            commonTest.getBoardComplex())
        properWhiteVal = (39 - 19.5) / 19.5
        properBlackVal = (35 - 19.5) / 19.5
        self.assertTrue((whitePieceVal == properWhiteVal) and
                        (blackPieceVal == properBlackVal))

    def test_bCmplx_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE,
                                                commonTest.getBoardComplex())
        blackBoardVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK,
                                                commonTest.getBoardComplex())
        properWhiteVal = -1 + 22 / 36 * 2
        properBlackVal = -1 + 22 / 36 * 2

        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    def test_bCmplx_heuristicPiecesUnderAttack(self):
        whiteBoardVal = heuristicPcsUnderAttack(ChessBoard.WHITE,
                                                commonTest.getBoardComplex())
        blackBoardVal = heuristicPcsUnderAttack(ChessBoard.BLACK,
                                                commonTest.getBoardComplex())
        properWhiteVal = 1 - 2 * (10 / 39)
        properBlackVal = 1 - 2 * (12 / 39)
        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    def test_bCmplx_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = heuristicPiecesCovered(ChessBoard.WHITE,
                                               commonTest.getBoardComplex())
        blackBoardVal = heuristicPiecesCovered(ChessBoard.BLACK,
                                               commonTest.getBoardComplex())
        properWhiteVal = -1 + 28 / 39 * 2
        properBlackVal = -1 + 19 / 35 * 2
        self.assertTrue((whiteBoardVal == properWhiteVal)
                        and (blackBoardVal == properBlackVal))


if __name__ == "__main__":
    unittest.main()
