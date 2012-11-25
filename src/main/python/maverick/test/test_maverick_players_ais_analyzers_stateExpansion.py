'''
Created on Nov 13, 2012

@author: mattsh
'''
import unittest

from maverick.data import ChessBoard
from maverick.data import ChessPosn
from maverick.players.ais.analyzers.stateExpansion import enumPossBoardMoves
from maverick.test import common as commonTest


class Test_maverick_players_ais_common(unittest.TestCase):

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
        pass

    def test_newB_correctValues(self):
        # "Should be 20 possible moves at start")
        enum = enumPossBoardMoves(commonTest.getBoardNew(), ChessBoard.WHITE)
        self._assertEqLists(enum,
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
        enum = enumPossBoardMoves(commonTest.getBoardNew(), ChessBoard.WHITE)
        self.assertEqual(20, len(enum))

    def test_newB_onlyLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardNew(), ChessBoard.WHITE)
        self._onlyLegalMoves(commonTest.getBoardNew(), ChessBoard.WHITE, enum)

    def test_newB_allLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardNew(), ChessBoard.WHITE)
        self._allLegalMoves(commonTest.getBoardNew(), ChessBoard.WHITE, enum)

    def test_bWD4_correctValues(self):
        enum = enumPossBoardMoves(commonTest.getBoardWD4(), ChessBoard.BLACK)
        self._assertEqLists(enum,
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
        enum = enumPossBoardMoves(commonTest.getBoardWD4(), ChessBoard.WHITE)
        self.assertEqual(28, len(enum))

    def test_bWD4_onlyLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardWD4(), ChessBoard.BLACK)
        self._onlyLegalMoves(commonTest.getBoardWD4(), ChessBoard.BLACK, enum)

    def test_bWD4_allLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardWD4(), ChessBoard.BLACK)
        self._allLegalMoves(commonTest.getBoardWD4(), ChessBoard.BLACK, enum)

    def test_bCmplx_white_allLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardComplex(),
                                  ChessBoard.WHITE)
        self._allLegalMoves(commonTest.getBoardComplex(),
                            ChessBoard.WHITE,
                            enum)

    def test_bCmplx_black_allLegalMoves(self):
        enum = enumPossBoardMoves(commonTest.getBoardComplex(),
                                  ChessBoard.BLACK)
        self._allLegalMoves(commonTest.getBoardComplex(),
                            ChessBoard.BLACK,
                            enum)

    def test_bRand1_LegalWhiteKingMove(self):
        b = commonTest.getBoardRand1()
        self.assertTrue(b.isLegalMove(ChessBoard.WHITE,
                                      ChessPosn(1, 3),
                                      ChessPosn(2, 3)))

    def test_bRand2_LegalBlackQueenMove(self):
        b = commonTest.getBoardRand2()
        self.assertTrue(b.isLegalMove(ChessBoard.BLACK,
                                      ChessPosn(4, 2),
                                      ChessPosn(2, 2)))

    def test_bRand3_LegalBlackPawnMove(self):
        b = commonTest.getBoardRand3()
        self.assertTrue(b.isLegalMove(ChessBoard.BLACK,
                                      ChessPosn(4, 2),
                                      ChessPosn(3, 2)))

    def test_bRand4_LegalWhiteBishopMove(self):
        b = commonTest.getBoardRand4()
        self.assertTrue(b.isLegalMove(ChessBoard.WHITE,
                                      ChessPosn(4, 5),
                                      ChessPosn(6, 3)))

    def test_bRand5_LegalWhiteBishopMove(self):
        b = commonTest.getBoardRand5()
        self.assertTrue(b.isLegalMove(ChessBoard.BLACK,
                                      ChessPosn(3, 3),
                                      ChessPosn(2, 3)))

    def test_bRand6_WhiteInCheckmate(self):
        b = commonTest.getBoardRand6()
        self.assertFalse(b.isKingCheckmated(ChessBoard.WHITE))

    def test_bRand7_BlackInCheck(self):
        b = commonTest.getBoardRand7()
        self.assertTrue(b.isKingInCheck(ChessBoard.BLACK)[0])


if __name__ == "__main__":
    unittest.main()
