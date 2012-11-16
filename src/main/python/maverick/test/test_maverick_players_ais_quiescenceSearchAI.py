'''
Created on Nov 13, 2012

@author: James Magnarelli and Matthew Strax-Haber
'''

from __future__ import division

import unittest

from maverick.data import ChessBoard
from maverick.data import ChessPiece
from maverick.data import ChessPosn
from maverick.players.ais.analyzers.likability import heuristicInCheck
from maverick.players.ais.analyzers.likability import heuristicPcsUnderAttack
from maverick.players.ais.analyzers.likability import heuristicPieceValue
from maverick.players.ais.analyzers.likability import heuristicPiecesCovered
from maverick.players.ais.analyzers.likability import heuristicEmptySpaceCvrg
from maverick.players.ais.analyzers.stateExpansion import enumPossBoardMoves
from maverick.players.ais.quiescenceSearchAI import QLAI


class Test_maverick_players_ais_quiescenceSearchAI(unittest.TestCase):

    def setUp(self):
        self.q = QLAI()
        self.bNew = ChessBoard()
        self.bNewEnum = enumPossBoardMoves(self.bNew, ChessBoard.WHITE)

        self.bWD4 = self.bNew.getResultOfPly(ChessPosn(1, 3), ChessPosn(3, 3))
        self.bWD4Enum = enumPossBoardMoves(self.bWD4, ChessBoard.BLACK)

        w = ChessBoard.WHITE
        b = ChessBoard.BLACK

        self.bCmplx = ChessBoard(startLayout=[[ChessPiece(w, ChessBoard.ROOK),
                                               ChessPiece(w, "N"),
                                               ChessPiece(w, "B"),
                                               ChessPiece(b, "R"),
                                               None,
                                               ChessPiece(w, "B"),
                                               None,
                                               None],
                                              [ChessPiece(w, "P"),
                                               ChessPiece(w, "P"),
                                               None,
                                               None,
                                               ChessPiece(w, "K"),
                                               None,
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "P")],
                                              [None,
                                               None,
                                               None,
                                               ChessPiece(w, "P"),
                                               None,
                                               None,
                                               None,
                                               None],
                                              [None,
                                               None,
                                               ChessPiece(w, "Q"),
                                               ChessPiece(w, "R"),
                                               None,
                                               None,
                                               ChessPiece(b, "N"),
                                               None],
                                              [None,
                                               ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(w, "N"),
                                               None,
                                               None,
                                               None,
                                               None],
                                              [None,
                                               None,
                                               None,
                                               None,
                                               ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(w, "P"),
                                               None],
                                              [ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               None,
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P")],
                                              [ChessPiece(b, "R"),
                                               ChessPiece(b, "N"),
                                               None,
                                               ChessPiece(b, "Q"),
                                               ChessPiece(b, "K"),
                                               ChessPiece(b, "B"),
                                               None,
                                               None]],
                                 startEnpassantFlags={b: [False] * 8,
                                                      w: [False] * 8},
                                 startCanCastleFlags={b: (False, False),
                                                      w: (True, False)})

    def test_newB_heuristicInCheck(self):
        # Neither player should be in check at the start
        whiteInCheckVal = heuristicInCheck(ChessBoard.WHITE, self.bNew)
        blackInCheckVal = heuristicInCheck(ChessBoard.BLACK, self.bNew)
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_newB_heuristicPieceValue(self):
        whitePieceVal = heuristicPieceValue(ChessBoard.WHITE,
                                                    self.bNew)
        blackPieceVal = heuristicPieceValue(ChessBoard.BLACK,
                                                    self.bNew)
        self.assertTrue((whitePieceVal == 1) and (blackPieceVal == 1))

    def test_newB_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE,
                                                            self.bNew)
        blackBoardVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK,
                                                            self.bNew)
        self.assertTrue((whiteBoardVal == 0) and (blackBoardVal == 0))

    def test_newB_heuristicPiecesUnderAttack(self):
        whiteBoardVal = heuristicPcsUnderAttack(ChessBoard.WHITE,
                                                           self.bNew)
        blackBoardVal = heuristicPcsUnderAttack(ChessBoard.BLACK,
                                                           self.bNew)
        self.assertTrue((whiteBoardVal == 1) and (blackBoardVal == 1))

    def test_newB_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = heuristicPiecesCovered(ChessBoard.WHITE,
                                                       self.bNew)
        blackBoardVal = heuristicPiecesCovered(ChessBoard.BLACK,
                                                       self.bNew)
        properRetVal = -1 + 29 / 39 * 2
        self.assertTrue((whiteBoardVal == properRetVal)
                        and (blackBoardVal == properRetVal))

    def test_bCmplx_heuristicInCheck(self):
        # Neither player should be in check at the start
        whiteInCheckVal = heuristicInCheck(ChessBoard.WHITE,
                                                   self.bCmplx)
        blackInCheckVal = heuristicInCheck(ChessBoard.BLACK,
                                                   self.bCmplx)
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_bCmplx_heuristicPieceValue(self):
        whitePieceVal = heuristicPieceValue(ChessBoard.WHITE,
                                                    self.bCmplx)
        blackPieceVal = heuristicPieceValue(ChessBoard.BLACK,
                                                    self.bCmplx)
        properWhiteVal = (39 - 19.5) / 19.5
        properBlackVal = (35 - 19.5) / 19.5
        self.assertTrue((whitePieceVal == properWhiteVal) and
                        (blackPieceVal == properBlackVal))

    def test_bCmplx_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = heuristicEmptySpaceCvrg(ChessBoard.WHITE,
                                                            self.bCmplx)
        blackBoardVal = heuristicEmptySpaceCvrg(ChessBoard.BLACK,
                                                            self.bCmplx)
        properWhiteVal = -1 + 22 / 36 * 2
        properBlackVal = -1 + 22 / 36 * 2

        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    def test_bCmplx_heuristicPiecesUnderAttack(self):
        whiteBoardVal = heuristicPcsUnderAttack(ChessBoard.WHITE,
                                                           self.bCmplx)
        blackBoardVal = heuristicPcsUnderAttack(ChessBoard.BLACK,
                                                           self.bCmplx)
        properWhiteVal = 1 - 2 * (10 / 39)
        properBlackVal = 1 - 2 * (12 / 39)
        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    def test_bCmplx_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = heuristicPiecesCovered(ChessBoard.WHITE,
                                                       self.bCmplx)
        blackBoardVal = heuristicPiecesCovered(ChessBoard.BLACK,
                                                       self.bCmplx)
        properWhiteVal = -1 + 28 / 39 * 2
        properBlackVal = -1 + 19 / 35 * 2
        self.assertTrue((whiteBoardVal == properWhiteVal)
                        and (blackBoardVal == properBlackVal))


if __name__ == "__main__":
    unittest.main()
