'''
Created on Nov 16, 2012

@author: mattsh
'''

from maverick.data import ChessBoard
from maverick.data import ChessPosn
from maverick.players.ais.common import MaverickAIException


def __canMoveTo_isOnBoard(posn):
    return (posn.rankN in range(ChessBoard.BOARD_LAYOUT_SIZE) and
            posn.fileN in range(ChessBoard.BOARD_LAYOUT_SIZE))


def __canMoveTo_moveLoop(moves, board, color,
                                fromPosn, translations):
    """Add moves based on translations, stopping when blocked

    WARNING: mutates moves to add relevant moves (returns None)"""
    for translation in translations:
        toPosn = fromPosn.getTranslatedBy(*translation)

        # We worry about self-capture at the end of canMoveTo
        moves.append(toPosn)

        # Stop if blocked by a piece
        if board[toPosn] is not None:
            break


def _canMoveTo_pawn(board, color, fromPosn):
    pawnStartRank = ChessBoard.PAWN_STARTING_RANKS[color]
    pawnDirection = [-1, 1][color == ChessBoard.WHITE]
    oneAhead = fromPosn.getTranslatedBy(pawnDirection, 0)
    twoAhead = fromPosn.getTranslatedBy(pawnDirection * 2, 0)

    moves = []

    if board[oneAhead] is None:
        moves.append(oneAhead)

    if (fromPosn.rankN == pawnStartRank and
        board[oneAhead] is None and
        board[twoAhead] is None):
        moves.append(twoAhead)

    otherColor = ChessBoard.getOtherColor(color)
    otherPawnStartRank = ChessBoard.PAWN_STARTING_RANKS[otherColor]
    for fileDelta in [-1, 1]:
        toPosn = fromPosn.getTranslatedBy(pawnDirection, fileDelta)

        if __canMoveTo_isOnBoard(toPosn):
            enemyP = (board[toPosn] is not None and
                      board[toPosn].color == otherColor)
            enpP = (board[toPosn] is None and
                    board.flag_enpassant[otherColor][toPosn.fileN] and
                    twoAhead.rankN == otherPawnStartRank)
            if enemyP or enpP:
                moves.append(toPosn)

    return moves


def _canMoveTo_rook(board, color, fromPosn):
    moves = []

    rMin = 1
    rMax = ChessBoard.BOARD_LAYOUT_SIZE + 1
    countUp = range(rMin, rMax, 1)
    countDown = range(-rMin, -rMax, -1)
    stayTheCourse = [0] * (ChessBoard.BOARD_LAYOUT_SIZE - 1)

    # Move up (rN+1..7, fN)
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countUp, stayTheCourse))
    # Move down (0..rN-1, fN)
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countDown, stayTheCourse))
    # Move right (rN, fN+1..7)
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(stayTheCourse, countUp))
    # Move left (rN, 0..fN-1)
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(stayTheCourse, countDown))

    return moves


def _canMoveTo_knight(board, color, fromPosn):
    moves = []
    moves.append(fromPosn.getTranslatedBy(2, -1))
    moves.append(fromPosn.getTranslatedBy(2, 1))
    moves.append(fromPosn.getTranslatedBy(1, -2))
    moves.append(fromPosn.getTranslatedBy(1, 2))
    moves.append(fromPosn.getTranslatedBy(-1, -2))
    moves.append(fromPosn.getTranslatedBy(-1, 2))
    moves.append(fromPosn.getTranslatedBy(-2, -1))
    moves.append(fromPosn.getTranslatedBy(-2, 1))
    return moves


def _canMoveTo_bishop(board, color, fromPosn):
    moves = []

    rMin = 1
    rMax = ChessBoard.BOARD_LAYOUT_SIZE + 1
    countUp = range(rMin, rMax, 1)
    countDown = range(-rMin, -rMax, -1)

    # Move top-right
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countUp, countUp))
    # Move top-left
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countUp, countDown))
    # Move down-right
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countDown, countUp))
    # Move down-left
    __canMoveTo_moveLoop(moves, board, color, fromPosn,
                                    zip(countDown, countDown))
    return moves


def _canMoveTo_queen(board, color, fromPosn):
    moves = []
    moves.extend(_canMoveTo_bishop(board, color, fromPosn))
    moves.extend(_canMoveTo_rook(board, color, fromPosn))
    return moves


def _canMoveTo_king(board, color, fromPosn):
    moves = []

    # Add moves to neighbors
    moves.append(fromPosn.getTranslatedBy(1, 1))
    moves.append(fromPosn.getTranslatedBy(1, 0))
    moves.append(fromPosn.getTranslatedBy(1, -1))
    moves.append(fromPosn.getTranslatedBy(0, 1))
    moves.append(fromPosn.getTranslatedBy(0, -1))
    moves.append(fromPosn.getTranslatedBy(-1, 1))
    moves.append(fromPosn.getTranslatedBy(-1, 0))
    moves.append(fromPosn.getTranslatedBy(-1, -1))

    # Add castling moves
    (canCastleQueenSide, canCastleKingSide) = board.flag_canCastle[color]
    kingRank = [7, 0][ChessBoard.WHITE == color]
    if (canCastleQueenSide and
        reduce(bool.__and__,
               [board[ChessPosn(kingRank, fN)] is None
                for fN in [1, 2, 3]])):
        moves.append(fromPosn.getTranslatedBy(0, -2))
    if (canCastleKingSide and
        reduce(bool.__and__,
               [board[ChessPosn(kingRank, fN)] is None
                for fN in [6, 7]])):
        moves.append(fromPosn.getTranslatedBy(0, 2))

    return moves


def canMoveTo(board, fromPosn):
    """Return all possible toPosns for the specified piece on given board

    @return ListOf[toPosn]"""

    # Pull out the color and fromPiece type from the board
    fromPiece = board[fromPosn]
    assert fromPiece is not None

    if fromPiece.pieceType == ChessBoard.PAWN:
        moveGenerator = _canMoveTo_pawn
    elif fromPiece.pieceType == ChessBoard.ROOK:
        moveGenerator = _canMoveTo_rook
    elif fromPiece.pieceType == ChessBoard.KNGT:
        moveGenerator = _canMoveTo_knight
    elif fromPiece.pieceType == ChessBoard.BISH:
        moveGenerator = _canMoveTo_bishop
    elif fromPiece.pieceType == ChessBoard.QUEN:
        moveGenerator = _canMoveTo_queen
    elif fromPiece.pieceType == ChessBoard.KING:
        moveGenerator = _canMoveTo_king
    else:
        raise MaverickAIException("Invalid fromPiece type")

    # Get list of candidate toPosns (some may be invalid)
    toPosns = moveGenerator(board, fromPiece.color, fromPosn)

    # Filter out toPosns that would put a piece off the board
    toPosns = filter(__canMoveTo_isOnBoard, toPosns)

    # Filter out self-capturing toPosns
    toPosns = filter(lambda p: (board[p] is None or
                                board[p].color != fromPiece.color),
                     toPosns)

    # TODO (mattsh): JAMES THIS BLOWS UP IF RUN
    #                We would delete this anyway, but it shouldn't blow up
    #                for legal moves. Either I have a bug (don't think so)
    #                or you do
    #        # TODO delete this after this function is finished (just a stop-gap)
    #        toPosns = filter(lambda p: board.isLegalMove(fromPiece.color,
    #                                                     fromPosn,
    #                                                     p),
    #                         toPosns)

    # Filter out Filter out toPosns that would put player in check
    def selfKingNotInCheck(toPosn):
        resultBoard = board.getResultOfPly(fromPosn, toPosn)
        return not resultBoard.isKingInCheck(fromPiece.color)[0]
    toPosns = filter(selfKingNotInCheck, toPosns)

    return toPosns


def enumPossBoardMoves(board, color):
    """Enumerate all possible immediate moves for the given player

    @return: a set of tuples of the form:
        ListOf[(ChessPiece, fromPosn, toPosn)]"""

    # TODO (mattsh): Modify to use generator pattern

    # List of all possible moves from the given board. Must be filled.
    moves = []

    for rankN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
        for fileN in xrange(ChessBoard.BOARD_LAYOUT_SIZE):
            fromPosn = ChessPosn(rankN, fileN)
            fromPiece = board[fromPosn]

            if fromPiece is not None and fromPiece.color == color:
                moves.extend(map(lambda toPosn: (fromPosn, toPosn),
                                 canMoveTo(board, fromPosn)))
            else:
                pass  # can't move a non-existent piece or one we don't own

    return moves
