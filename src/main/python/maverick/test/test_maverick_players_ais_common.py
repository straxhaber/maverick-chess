'''
Created on Nov 13, 2012

@author: mattsh
'''
import unittest

from maverick.data import ChessBoard, ChessPiece
from maverick.data import ChessPosn
from maverick.players.ais.common import MaverickAI


class Test_maverick_players_ais_common(unittest.TestCase):

    @staticmethod
    def _getComplxChessBoard():
        w = ChessBoard.WHITE
        b = ChessBoard.BLACK

        return ChessBoard(startLayout=[[ChessPiece(w, ChessBoard.ROOK),
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

    def _assertEqLists(self, l1, l2):
#        print "l1"
#        for item in l1:
#            print "\t{}".format(item)
#        print "l2"
#        for item in l2:
#            print "\t{}".format(item)

        for item in l1:
            self.assertTrue(item in l2, "item not in l2: {}".format(item))
        for item in l2:
            self.assertTrue(item in l1, "item not in l1: {}".format(item))

    def _onlyLegalMoves(self, board, color, enums):
        self.assertNotIn(False,
                         map(lambda m: board.isLegalMove(color, m[0], m[1]),
                             enums),
                         "all moves should be valid")

    def _allLegalMoves(self, board, color, enums):
        mvs = []
        for rNF in range(ChessBoard.BOARD_LAYOUT_SIZE):
            for fNF in range(ChessBoard.BOARD_LAYOUT_SIZE):
                fromPosn = ChessPosn(rNF, fNF)
                piece = board[fromPosn]
                if (piece is not None and
                    piece.color == color):
                    for rNT in range(ChessBoard.BOARD_LAYOUT_SIZE):
                        for fNT in range(ChessBoard.BOARD_LAYOUT_SIZE):
                            toPosn = ChessPosn(rNT, fNT)
                            if board.isLegalMove(color, fromPosn, toPosn):
                                mvs.append((fromPosn, toPosn))
        self._assertEqLists(mvs, enums)

    def setUp(self):
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

        self.bRand1 = ChessBoard(startLayout=[[ChessPiece(w, ChessBoard.ROOK),
                                               ChessPiece(w, "N"),
                                               ChessPiece(w, "B"),
                                               ChessPiece(w, "Q"),
                                               None,
                                               ChessPiece(w, "B"),
                                               ChessPiece(w, "N"),
                                               ChessPiece(w, "R")],
                                              [None,
                                               ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(w, "K"),
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "P")],
                                              [ChessPiece(w, "P"),
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None],
                                              [None,
                                               None,
                                               ChessPiece(w, "P"),
                                               None,
                                               None,
                                               None,
                                               None,
                                               None],
                                              [None,
                                               None,
                                               ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(b, "P"),
                                               None,
                                               None,
                                               ChessPiece(b, "P")],
                                              [None,
                                               ChessPiece(b, "P"),
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               ChessPiece(b, "R")],
                                              [ChessPiece(b, "P"),
                                               None,
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               None,
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               None],
                                              [ChessPiece(b, "R"),
                                               ChessPiece(b, "N"),
                                               ChessPiece(b, "B"),
                                               ChessPiece(b, "Q"),
                                               ChessPiece(b, "K"),
                                               None,
                                               ChessPiece(b, "N"),
                                               None]],
                                 startEnpassantFlags={b: [False] * 8,
                                                      w: [False] * 8},
                                 startCanCastleFlags={b: (True, False),
                                                      w: (False, False)})

        self.bRand2 = ChessBoard(startLayout=[[None,
                                               None,
                                               None,
                                               ChessPiece(w, "N"),
                                               ChessPiece(w, "R"),
                                               None,
                                               ChessPiece(w, "N"),
                                               None],
                                              [ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "K"),
                                               ChessPiece(w, "Q"),
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "B"),
                                               ChessPiece(w, "R")],
                                              [None,
                                               None,
                                               None,
                                               None,
                                               ChessPiece(w, "P"),
                                               None,
                                               ChessPiece(w, "P"),
                                               ChessPiece(w, "P")],
                                              [None,
                                               ChessPiece(w, "P"),
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None],
                                              [None,
                                               None,
                                               ChessPiece(b, "Q"),
                                               ChessPiece(b, "P"),
                                               None,
                                               None,
                                               ChessPiece(b, "P"),
                                               None],
                                              [None,
                                               ChessPiece(b, "P"),
                                               None,
                                               None,
                                               None,
                                               None,
                                               None,
                                               None],
                                              [ChessPiece(b, "P"),
                                               ChessPiece(b, "B"),
                                               ChessPiece(w, "B"),
                                               None,
                                               ChessPiece(b, "P"),
                                               ChessPiece(b, "P"),
                                               None,
                                               ChessPiece(b, "P")],
                                              [ChessPiece(b, "R"),
                                               None,
                                               None,
                                               None,
                                               ChessPiece(b, "K"),
                                               ChessPiece(b, "B"),
                                               ChessPiece(b, "N"),
                                               ChessPiece(b, "R")]],
                                 startEnpassantFlags={b: [False] * 8,
                                                      w: [False] * 8},
                                 startCanCastleFlags={b: (True, True),
                                                      w: (False, False)})

    def test_newB_correctValues(self):
        # "Should be 20 possible moves at start")
        self._assertEqLists(self.bNewEnum,
                            [(ChessPosn(0, 1), ChessPosn(2, 0)),
                             (ChessPosn(0, 1), ChessPosn(2, 2)),
                             (ChessPosn(0, 6), ChessPosn(2, 5)),
                             (ChessPosn(0, 6), ChessPosn(2, 7)),
                             (ChessPosn(1, 0), ChessPosn(2, 0)),
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
                             (ChessPosn(1, 7), ChessPosn(3, 7))])

    def test_newB_correctLen(self):
        self.assertEqual(20, len(self.bNewEnum))

    def test_newB_onlyLegalMoves(self):
        self._onlyLegalMoves(self.bNew, ChessBoard.WHITE, self.bNewEnum)

    def test_newB_allLegalMoves(self):
        self._allLegalMoves(self.bNew, ChessBoard.WHITE, self.bNewEnum)

    def test_bWD4_correctValues(self):
        self._assertEqLists(self.bWD4Enum,
                            [(ChessPosn(6, 0), ChessPosn(5, 0)),
                             (ChessPosn(6, 0), ChessPosn(4, 0)),
                             (ChessPosn(6, 1), ChessPosn(5, 1)),
                             (ChessPosn(6, 1), ChessPosn(4, 1)),
                             (ChessPosn(6, 2), ChessPosn(5, 2)),
                             (ChessPosn(6, 2), ChessPosn(4, 2)),
                             (ChessPosn(6, 3), ChessPosn(5, 3)),
                             (ChessPosn(6, 3), ChessPosn(4, 3)),
                             (ChessPosn(6, 4), ChessPosn(5, 4)),
                             (ChessPosn(6, 4), ChessPosn(4, 4)),
                             (ChessPosn(6, 5), ChessPosn(5, 5)),
                             (ChessPosn(6, 5), ChessPosn(4, 5)),
                             (ChessPosn(6, 6), ChessPosn(5, 6)),
                             (ChessPosn(6, 6), ChessPosn(4, 6)),
                             (ChessPosn(6, 7), ChessPosn(5, 7)),
                             (ChessPosn(6, 7), ChessPosn(4, 7)),
                             (ChessPosn(7, 1), ChessPosn(5, 0)),
                             (ChessPosn(7, 1), ChessPosn(5, 2)),
                             (ChessPosn(7, 6), ChessPosn(5, 5)),
                             (ChessPosn(7, 6), ChessPosn(5, 7))])

    def test_bWD4_correctLen(self):
        self.assertEqual(20, len(self.bWD4Enum))

    def test_bWD4_onlyLegalMoves(self):
        self._onlyLegalMoves(self.bWD4, ChessBoard.BLACK, self.bWD4Enum)

    def test_bWD4_allLegalMoves(self):
        self._allLegalMoves(self.bWD4, ChessBoard.BLACK, self.bWD4Enum)

    @unittest.expectedFailure  # TODO: legalMoves is broken
    def test_bCmplx_white_allLegalMoves(self):
        enum = MaverickAI.enumBoardMoves(self.bCmplx, ChessBoard.WHITE)
        self._allLegalMoves(self.bCmplx, ChessBoard.WHITE, enum)

    @unittest.expectedFailure  # TODO: legalMoves is broken
    def test_bCmplx_black_allLegalMoves(self):
        enum = MaverickAI.enumBoardMoves(self.bCmplx, ChessBoard.BLACK)
        self._allLegalMoves(self.bCmplx, ChessBoard.BLACK, enum)

    #@unittest.expectedFailure  # TODO:  randomly discovered bug
    def test_bRand1_LegalWhiteKingMove(self):
        self.assertTrue(self.bRand1.isLegalMove(ChessBoard.WHITE,
                                                ChessPosn(1, 3),
                                                ChessPosn(2, 3)))

    def test_bRand2_LegalBlackQueenMove(self):
        self.assertTrue(self.bRand2.isLegalMove(ChessBoard.BLACK,
                                                ChessPosn(4, 2),
                                                ChessPosn(2, 2)))
if __name__ == "__main__":
    unittest.main()
