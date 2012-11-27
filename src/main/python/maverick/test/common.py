'''
Created on Nov 16, 2012

@author: mattsh
'''
from maverick.data import ChessBoard
from maverick.data import ChessPosn
from maverick.data import ChessPiece

_w = ChessBoard.WHITE
_b = ChessBoard.BLACK


def getBoardNew():
    return ChessBoard()


def getBoardWD4():
    return ChessBoard().getPlyResult(ChessPosn(1, 3), ChessPosn(3, 3))


def getBoardComplex():
    return ChessBoard(startLayout=[[ChessPiece(_w, ChessBoard.ROOK),
                                    ChessPiece(_w, "N"),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_b, "R"),
                                    None,
                                    ChessPiece(_w, "B"),
                                    None,
                                    None],
                                   [ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    ChessPiece(_w, "K"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P")],
                                   [None,
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    None,
                                    None],
                                   [None,
                                    None,
                                    ChessPiece(_w, "Q"),
                                    ChessPiece(_w, "R"),
                                    None,
                                    None,
                                    ChessPiece(_b, "N"),
                                    None],
                                   [None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "N"),
                                    None,
                                    None,
                                    None,
                                    None],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    None],
                                   [ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P")],
                                   [ChessPiece(_b, "R"),
                                    ChessPiece(_b, "N"),
                                    None,
                                    ChessPiece(_b, "Q"),
                                    ChessPiece(_b, "K"),
                                    ChessPiece(_b, "B"),
                                    None,
                                    None]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (False, False),
                                           _w: (True, False)})


def getBoardRand1():
    return ChessBoard(startLayout=[[ChessPiece(_w, ChessBoard.ROOK),
                                   ChessPiece(_w, "N"),
                                   ChessPiece(_w, "B"),
                                   ChessPiece(_w, "Q"),
                                   None,
                                   ChessPiece(_w, "B"),
                                   ChessPiece(_w, "N"),
                                   ChessPiece(_w, "R")],
                                  [None,
                                   ChessPiece(_w, "P"),
                                   None,
                                   ChessPiece(_w, "K"),
                                   ChessPiece(_w, "P"),
                                   ChessPiece(_w, "P"),
                                   ChessPiece(_w, "P"),
                                   ChessPiece(_w, "P")],
                                  [ChessPiece(_w, "P"),
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   None],
                                  [None,
                                   None,
                                   ChessPiece(_w, "P"),
                                   None,
                                   None,
                                   None,
                                   None,
                                   None],
                                  [None,
                                   None,
                                   ChessPiece(_w, "P"),
                                   None,
                                   ChessPiece(_b, "P"),
                                   None,
                                   None,
                                   ChessPiece(_b, "P")],
                                  [None,
                                   ChessPiece(_b, "P"),
                                   None,
                                   None,
                                   None,
                                   None,
                                   None,
                                   ChessPiece(_b, "R")],
                                  [ChessPiece(_b, "P"),
                                   None,
                                   ChessPiece(_b, "P"),
                                   ChessPiece(_b, "P"),
                                   None,
                                   ChessPiece(_b, "P"),
                                   ChessPiece(_b, "P"),
                                   None],
                                  [ChessPiece(_b, "R"),
                                   ChessPiece(_b, "N"),
                                   ChessPiece(_b, "B"),
                                   ChessPiece(_b, "Q"),
                                   ChessPiece(_b, "K"),
                                   None,
                                   ChessPiece(_b, "N"),
                                   None]],
                     startEnpassantFlags={_b: [False] * 8,
                                          _w: [False] * 8},
                     startCanCastleFlags={_b: (True, False),
                                          _w: (False, False)})


def getBoardRand2():
    return ChessBoard(startLayout=[[None,
                                    None,
                                    None,
                                    ChessPiece(_w, "N"),
                                    ChessPiece(_w, "R"),
                                    None,
                                    ChessPiece(_w, "N"),
                                    None],
                                   [ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "K"),
                                    ChessPiece(_w, "Q"),
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "B"),
                                   ChessPiece(_w, "R")],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P")],
                                   [None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                   None],
                                   [None,
                                    None,
                                    ChessPiece(_b, "Q"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    None],
                                   [None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_b, "P"),
                                   ChessPiece(_b, "B"),
                                    ChessPiece(_w, "B"),
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_b, "P")],
                                   [ChessPiece(_b, "R"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_b, "K"),
                                    ChessPiece(_b, "B"),
                                    ChessPiece(_b, "N"),
                                    ChessPiece(_b, "R")]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (True, True),
                                           _w: (False, False)})


def getBoardRand3():
    return ChessBoard(startLayout=[[None,
                                    ChessPiece(_w, ChessBoard.ROOK),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_w, "Q"),
                                    None,
                                    None,
                                    ChessPiece(_w, "N"),
                                    ChessPiece(_w, "R")],
                                   [ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    ChessPiece(_w, "B"),
                                    None],
                                   [ChessPiece(_w, "N"),
                                    None,
                                    None,
                                    ChessPiece(_w, "K"),
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "P")],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None],
                                   [None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    None],
                                   [ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_b, "B"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_b, "N")],
                                   [None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "K"),
                                    None,
                                    ChessPiece(_b, "P")],
                                   [ChessPiece(_b, "R"),
                                    ChessPiece(_b, "N"),
                                    None,
                                    ChessPiece(_b, "Q"),
                                    None,
                                    ChessPiece(_b, "B"),
                                    None,
                                    ChessPiece(_b, "R")]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (False, False),
                                           _w: (False, False)})


def getBoardRand4():
    return ChessBoard(startLayout=[[None,
                                    ChessPiece(_w, ChessBoard.ROOK),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_w, "Q"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "R")],
                                   [None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_w, "K"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    None],
                                   [ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    ChessPiece(_w, "P")],
                                   [ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_b, "P")],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_w, "N"),
                                    None],
                                   [ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "B")],
                                   [ChessPiece(_b, "N"),
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_b, "R"),
                                    None],
                                   [ChessPiece(_b, "R"),
                                    None,
                                    ChessPiece(_b, "B"),
                                    ChessPiece(_b, "Q"),
                                    ChessPiece(_b, "K"),
                                    None,
                                    None,
                                    None]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (True, False),
                                           _w: (False, False)})


def getBoardRand5():
    return ChessBoard(startLayout=[[None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece("W", "R"),
                                    ChessPiece("W", "N"),
                                    ChessPiece("W", "R")],
                                   [None,
                                    None,
                                    None,
                                    ChessPiece("W", "K"),
                                    None,
                                    None,
                                    ChessPiece("W", "P"),
                                    None],
                                   [None,
                                    ChessPiece("B", "P"),
                                    ChessPiece("W", "P"),
                                    ChessPiece("W", "P"),
                                    None,
                                    ChessPiece("W", "P"),
                                    None,
                                    None],
                                   [ChessPiece("W", "P"),
                                    None,
                                    None,
                                    ChessPiece("B", "Q"),
                                    None,
                                    None,
                                    ChessPiece("B", "N"),
                                    ChessPiece("W", "P")],
                                   [ChessPiece("B", "P"),
                                    ChessPiece("W", "N"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece("B", "P"),
                                    None,
                                    None],
                                   [None,
                                    ChessPiece("W", "Q"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece("W", "B"),
                                    ChessPiece("B", "P"),
                                    None],
                                   [None,
                                    ChessPiece("B", "P"),
                                    None,
                                    None,
                                    ChessPiece("B", "P"),
                                    ChessPiece("B", "K"),
                                    None,
                                    ChessPiece("B", "P")],
                                   [ChessPiece("B", "R"),
                                    ChessPiece("B", "N"),
                                    ChessPiece("B", "B"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece("B", "R")]],
                      startEnpassantFlags={'B': [False] * 8,
                                           'W': [False] * 8},
                      startCanCastleFlags={'B': [False, False],
                                           'W': [False, False]})


def getBoardRand6():
    return ChessBoard(startLayout=[[None,
                                    None,
                                    ChessPiece(_w, ChessBoard.ROOK),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_b, "Q"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "K"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    None],
                                   [None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [None,
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [None,
                                    None,
                                    None,
                                    ChessPiece(_b, "K"),
                                    None,
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_w, "N"),
                                    None,
                                    ChessPiece(_b, "N"),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_w, "N"),
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "B"),
                                    ChessPiece(_b, "P")],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_b, "B"),
                                    None,
                                    ChessPiece(_b, "R")]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (False, False),
                                           _w: (False, False)})

def getBoardRand7():
    return ChessBoard(startLayout=[[None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_w, "P"),
                                    ChessPiece(_w, "B"),
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_b, "R"),
                                    None,
                                    None,
                                    None],
                                   [ChessPiece(_w, "K"),
                                    ChessPiece(_b, "P"),
                                    None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    ChessPiece(_w, "N")],
                                   [None,
                                    None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    ChessPiece(_b, "N"),
                                    None,
                                    None,
                                    None],
                                   [None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None,
                                    None],
                                   [None,
                                    ChessPiece(_w, "P"),
                                    None,
                                    None,
                                    None,
                                    ChessPiece(_w, "N"),
                                    None,
                                    ChessPiece(_w, "P")],
                                   [None,
                                    ChessPiece(_b, "P"),
                                    None,
                                    None,
                                    ChessPiece(_b, "P"),
                                    ChessPiece(_w, "R"),
                                    None,
                                    ChessPiece(_b, "P")],
                                   [None,
                                    None,
                                    ChessPiece(_b, "Q"),
                                    None,
                                    ChessPiece(_b, "K"),
                                    ChessPiece(_b, "B"),
                                    ChessPiece(_b, "R"),
                                    None]],
                      startEnpassantFlags={_b: [False] * 8,
                                           _w: [False] * 8},
                      startCanCastleFlags={_b: (False, False),
                                           _w: (False, False)})
