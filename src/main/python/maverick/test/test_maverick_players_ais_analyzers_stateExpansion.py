'''
Created on Nov 13, 2012

@author: mattsh
'''
import unittest

from maverick.data.structs import ChessBoard as _Board
from maverick.data.structs import ChessPosn as _Posn
from maverick.data.utils import enumMoves

from maverick.test.common import getBoardNew, getBoardWD4, getBoardComplex
from maverick.test.common import getBoard1, getBoard2, getBoard3, getBoard4
from maverick.test.common import getBoard5, getBoard6, getBoard7

_w = _Board.WHITE
_b = _Board.BLACK


class Test_maverick_data_utils(unittest.TestCase):

    def _assertListsEq(self, expected, actual):
#        print "expected"
#        for item in expected:
#            print "\t{}".format(item)
#        print "actual"
#        for item in actual:
#            print "\t{}".format(item)

        strF = "item not in {}: {}"
        for item in expected:
            self.assertTrue(item in actual, strF.format("actual", item))
        for item in actual:
            self.assertTrue(item in expected, strF.format("expected", item))

    def _onlyLegalMoves(self, board, color, enums):
        self.assertNotIn(False,
                         map(lambda m: board.isLegalMove(color, m[0], m[1]),
                             enums),
                         "all moves should be valid")

    def _allLegalMoves(self, board, color, actualEnums):
        mvs = []
        for rNF in range(_Board.BOARD_LAYOUT_SIZE):
            for fNF in range(_Board.BOARD_LAYOUT_SIZE):
                fromPosn = _Posn(rNF, fNF)
                piece = board[fromPosn]
                if (piece is not None and
                    piece.color == color):
                    for rNT in range(_Board.BOARD_LAYOUT_SIZE):
                        for fNT in range(_Board.BOARD_LAYOUT_SIZE):
                            toPosn = _Posn(rNT, fNT)
                            if board.isLegalMove(color, fromPosn, toPosn):
                                mvs.append((fromPosn, toPosn))
        self._assertListsEq(mvs, actualEnums)

    def test_newB_correctValues(self):
        # "Should be 20 possible moves at start")
        self._assertListsEq([(_Posn(0, 1), _Posn(2, 0)),
                             (_Posn(0, 1), _Posn(2, 2)),
                             (_Posn(0, 6), _Posn(2, 5)),
                             (_Posn(0, 6), _Posn(2, 7)),
                             (_Posn(1, 0), _Posn(2, 0)),
                             (_Posn(1, 0), _Posn(3, 0)),
                             (_Posn(1, 1), _Posn(2, 1)),
                             (_Posn(1, 1), _Posn(3, 1)),
                             (_Posn(1, 2), _Posn(2, 2)),
                             (_Posn(1, 2), _Posn(3, 2)),
                             (_Posn(1, 3), _Posn(2, 3)),
                             (_Posn(1, 3), _Posn(3, 3)),
                             (_Posn(1, 4), _Posn(2, 4)),
                             (_Posn(1, 4), _Posn(3, 4)),
                             (_Posn(1, 5), _Posn(2, 5)),
                             (_Posn(1, 5), _Posn(3, 5)),
                             (_Posn(1, 6), _Posn(2, 6)),
                             (_Posn(1, 6), _Posn(3, 6)),
                             (_Posn(1, 7), _Posn(2, 7)),
                             (_Posn(1, 7), _Posn(3, 7))],
                            enumMoves(getBoardNew(), _w))

    def test_newB_correctLen(self):
        self.assertEqual(20, len(enumMoves(getBoardNew(), _w)))

    def test_newB_onlyLegalMoves(self):
        self._onlyLegalMoves(getBoardNew(), _w, enumMoves(getBoardNew(), _w))

    def test_newB_allLegalMoves(self):
        self._allLegalMoves(getBoardNew(), _w, enumMoves(getBoardNew(), _w))

    def test_bWD4_correctValues(self):
        self._assertListsEq([(_Posn(6, 0), _Posn(5, 0)),
                             (_Posn(6, 0), _Posn(4, 0)),
                             (_Posn(6, 1), _Posn(5, 1)),
                             (_Posn(6, 1), _Posn(4, 1)),
                             (_Posn(6, 2), _Posn(5, 2)),
                             (_Posn(6, 2), _Posn(4, 2)),
                             (_Posn(6, 3), _Posn(5, 3)),
                             (_Posn(6, 3), _Posn(4, 3)),
                             (_Posn(6, 4), _Posn(5, 4)),
                             (_Posn(6, 4), _Posn(4, 4)),
                             (_Posn(6, 5), _Posn(5, 5)),
                             (_Posn(6, 5), _Posn(4, 5)),
                             (_Posn(6, 6), _Posn(5, 6)),
                             (_Posn(6, 6), _Posn(4, 6)),
                             (_Posn(6, 7), _Posn(5, 7)),
                             (_Posn(6, 7), _Posn(4, 7)),
                             (_Posn(7, 1), _Posn(5, 0)),
                             (_Posn(7, 1), _Posn(5, 2)),
                             (_Posn(7, 6), _Posn(5, 5)),
                             (_Posn(7, 6), _Posn(5, 7))],
                            enumMoves(getBoardWD4(), _b))

    def test_bWD4_correctLen(self):
        self.assertEqual(28, len(enumMoves(getBoardWD4(), _w)))

    def test_bWD4_onlyLegalMoves(self):
        self._onlyLegalMoves(getBoardWD4(), _b, enumMoves(getBoardWD4(), _b))

    def test_bWD4_allLegalMoves(self):
        self._allLegalMoves(getBoardWD4(), _b, enumMoves(getBoardWD4(), _b))

    def test_bCmplx_allLegalMoves_white(self):
        b = getBoardComplex()
        self._allLegalMoves(b, _w, enumMoves(b, _w))

    def test_bCmplx_allLegalMoves_black(self):
        b = getBoardComplex()
        self._allLegalMoves(b, _b, enumMoves(b, _b))

    def test_b1_LegalWhiteKingMove(self):
        self.assertTrue(getBoard1().isLegalMove(_w, _Posn(1, 3), _Posn(2, 3)))

    def test_b2_LegalBlackQueenMove(self):
        self.assertTrue(getBoard2().isLegalMove(_b, _Posn(4, 2), _Posn(2, 2)))

    def test_b3_LegalBlackPawnMove(self):
        self.assertTrue(getBoard3().isLegalMove(_b, _Posn(4, 2), _Posn(3, 2)))

    def test_b4_LegalWhiteBishopMove(self):
        self.assertTrue(getBoard4().isLegalMove(_w, _Posn(4, 5), _Posn(6, 3)))

    def test_b5_LegalWhiteBishopMove(self):
        self.assertTrue(getBoard5().isLegalMove(_b, _Posn(3, 3), _Posn(2, 3)))

    # TODO (mattsh): Should this and some other tests be elsewhere?
    def test_b6_WhiteInCheckmate(self):
        self.assertFalse(getBoard6().isKingCheckmated(_w))

    def test_b7_BlackInCheck(self):
        self.assertIsNotNone(getBoard7().pieceCheckingKing(_b))


if __name__ == "__main__":
    unittest.main()
