'''
Created on Nov 13, 2012

@author: James Magnarelli and Matthew Strax-Haber
'''

from __future__ import division

import unittest

from maverick.data import ChessBoard, ChessBoardUtils, ChessPiece
from maverick.data import ChessPosn
from maverick.players.ais.common import MaverickAI
from maverick.players.ais.quiescenceSearchAI import QLAI


class Test_maverick_players_ais_quiescenceSearchAI(unittest.TestCase):

    def setUp(self):
        self.q = QLAI()
        self.bNew = ChessBoard()
        self.bNewEnum = MaverickAI.enumBoardMoves(self.bNew, ChessBoard.WHITE)

        self.bWD4 = self.bNew.getResultOfPly(ChessPosn(1, 3), ChessPosn(3, 3))
        self.bWD4Enum = MaverickAI.enumBoardMoves(self.bWD4, ChessBoard.BLACK)

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
        whiteInCheckVal = self.q._heuristicInCheck(ChessBoard.WHITE, self.bNew)
        blackInCheckVal = self.q._heuristicInCheck(ChessBoard.BLACK, self.bNew)
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_newB_heuristicPieceValue(self):
        whitePieceVal = self.q._heuristicPieceValue(ChessBoard.WHITE,
                                                    self.bNew)
        blackPieceVal = self.q._heuristicPieceValue(ChessBoard.BLACK,
                                                    self.bNew)
        self.assertTrue((whitePieceVal == 1) and (blackPieceVal == 1))

    def test_newB_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = self.q._heuristicEmptySpaceCoverage(ChessBoard.WHITE,
                                                            self.bNew)
        blackBoardVal = self.q._heuristicEmptySpaceCoverage(ChessBoard.BLACK,
                                                            self.bNew)
        self.assertTrue((whiteBoardVal == 0) and (blackBoardVal == 0))

    def test_newB_heuristicPiecesUnderAttack(self):
        whiteBoardVal = self.q._heuristicPiecesUnderAttack(ChessBoard.WHITE,
                                                           self.bNew)
        blackBoardVal = self.q._heuristicPiecesUnderAttack(ChessBoard.BLACK,
                                                           self.bNew)
        self.assertTrue((whiteBoardVal == 1) and (blackBoardVal == 1))

    @unittest.expectedFailure  # TODO: moves not being enumerated correctly?
    def test_newB_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = self.q._heuristicPiecesCovered(ChessBoard.WHITE,
                                                       self.bNew)
        blackBoardVal = self.q._heuristicPiecesCovered(ChessBoard.BLACK,
                                                       self.bNew)
        properRetVal = -1 + 21 / 39 * 2
        self.assertTrue((whiteBoardVal == properRetVal)
                        and (blackBoardVal == properRetVal))

    def test_bCmplx_heuristicInCheck(self):
        # Neither player should be in check at the start
        whiteInCheckVal = self.q._heuristicInCheck(ChessBoard.WHITE,
                                                   self.bCmplx)
        blackInCheckVal = self.q._heuristicInCheck(ChessBoard.BLACK,
                                                   self.bCmplx)
        self.assertTrue((whiteInCheckVal == 1) and
                        (blackInCheckVal == 1))

    def test_bCmplx_heuristicPieceValue(self):
        whitePieceVal = self.q._heuristicPieceValue(ChessBoard.WHITE,
                                                    self.bCmplx)
        blackPieceVal = self.q._heuristicPieceValue(ChessBoard.BLACK,
                                                    self.bCmplx)
        properWhiteVal = (39 - 19.5) / 19.5
        properBlackVal = (35 - 19.5) / 19.5
        self.assertTrue((whitePieceVal == properWhiteVal) and
                        (blackPieceVal == properBlackVal))

    @unittest.expectedFailure  # TODO: this heuristic is broken
    def test_bCmplx_heuristicEmptySpaceCoverage(self):
        whiteBoardVal = self.q._heuristicEmptySpaceCoverage(ChessBoard.WHITE,
                                                            self.bCmplx)
        blackBoardVal = self.q._heuristicEmptySpaceCoverage(ChessBoard.BLACK,
                                                            self.bCmplx)
        properWhiteVal = 1 - 23 / 36 * 2
        properBlackVal = 1 - 17 / 36 * 2
        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    def test_bCmplx_heuristicPiecesUnderAttack(self):
        whiteBoardVal = self.q._heuristicPiecesUnderAttack(ChessBoard.WHITE,
                                                           self.bCmplx)
        blackBoardVal = self.q._heuristicPiecesUnderAttack(ChessBoard.BLACK,
                                                           self.bCmplx)
        properWhiteVal = 1 - 2 * (10 / 39)
        properBlackVal = 1 - 2 * (12 / 39)
        self.assertTrue((whiteBoardVal == properWhiteVal) and
                        (blackBoardVal == properBlackVal))

    @unittest.expectedFailure  # TODO: moves not being enumerated correctly?
    def test_bCmplx_heuristicPiecesCovered(self):
        # Maximum covered value for new board is 39
        whiteBoardVal = self.q._heuristicPiecesCovered(ChessBoard.WHITE,
                                                       self.bCmplx)
        blackBoardVal = self.q._heuristicPiecesCovered(ChessBoard.BLACK,
                                                       self.bCmplx)
        properWhiteVal = -1 + 31 / 39 * 2
        properBlackVal = -1 + 19 / 35 * 2
        self.assertTrue((whiteBoardVal == properWhiteVal)
                        and (blackBoardVal == properBlackVal))


if __name__ == "__main__":
    unittest.main()
