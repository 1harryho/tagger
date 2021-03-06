import chess
import chess.pgn as c_pgn
import collections
import pandas as pd


def column(matrix, i):
    """
    a quality of life function that grabs the i-th column from a matrix
    :param matrix:
    :param i:
    :return:
    """
    return [row[i] if i < len(row) else 0 for row in matrix]


def fen_to_matrix(board):
    """

    :param board:
    :return: board as a matrix of characters
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a chess.Board")

    sfen = str(board.board_fen()).split("/")
    m = []
    for l in sfen:
        row = []
        for item in l:
            if str(item).isalpha():
                row.append(item)
            elif int(item):
                for i in range(int(item)):
                    row.append("0")
        m.append(row)
    return m


def count_isolated_pawns(board):
    """
    evaluates the number of isolated pawns on the board given

    :param board: the board state to be evaluated for isolated pawns
    :return: if no color specified, returns count of all isolated pawns
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a chess.Board")

    m = fen_to_matrix(board)
    white_iso = 0
    black_iso = 0

    for rank in range(len(m)):
        for file in range(len(m[rank])):
            piece = m[rank][file]
            if str(piece) == "p":
                left_file = False
                right_file = False
                if file > 0:
                    left_file = column(m, file - 1)
                if file < 8:
                    right_file = column(m, file + 1)

                left_pawn = "p" in left_file if left_file is not False else None
                right_pawn = "p" in right_file if right_file is not False else None
                black_iso += not (left_pawn or right_pawn)

            elif str(piece) == "P":
                left_file = False
                right_file = False
                if file > 0:
                    left_file = column(m, file - 1)
                if file < 8:
                    right_file = column(m, file + 1)

                left_pawn = "P" in left_file if left_file is not False else None
                right_pawn = "P" in right_file if right_file is not False else None
                white_iso += not (left_pawn or right_pawn)

    return white_iso - black_iso


def count_blocked_pawns(board):
    """
    Returns the count of blocked pawns on the board.
    :param board:
    :return: count of blocked pawns on the board
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a ", type(chess.Board))

    m = fen_to_matrix(board)
    white_blocked = 0
    black_blocked = 0

    for rank in range(len(m)):
        c = column(m, rank)
        # print(c)
        for i in range(1, len(c) - 1):
            piece_c = str(c[i])  # current piece
            piece_n = str(c[i + 1]) if c[i + 1] is not None else None  # next piece
            piece_p = str(c[i - 1]) if c[i - 1] is not None else None  # previous piece
            if piece_c == "p" and piece_n != "0":
                print("black pawn blocked ", c)
                print("c[i]: ", c[i])
                print("c[i + 1]: ", c[i+1])
                black_blocked += 1
            elif piece_c == "P" and piece_p != "0":
                white_blocked += 1

    return white_blocked - black_blocked


def count_doubled_pawns(board):
    """
    Returns the count of doubled pawns on the board. Does not count tripled or quadrupled.
    :param board:
    :return: count of doubled pawns in board
    """
    if not isinstance(board, chess.Board):
        raise TypeError(board, " is not a ", type(chess.Board))

    m = fen_to_matrix(board)

    white_doubled = 0
    black_doubled = 0
    for rank in range(len(m)):
        ctr = collections.Counter()
        c = column(m, rank)
        ctr.update(c)
        if ctr["p"] == 2:
            black_doubled += 1
        if ctr["P"] == 2:
            white_doubled += 1

    return white_doubled - black_doubled


def evaluate(board):
    """
    Claude Shannon's simple symmetric board evaluation.

    f(p) = 200(K-K')
       + 9(Q-Q')
       + 5(R-R')
       + 3(B-B' + N-N')
       + 1(P-P')
       - 0.5(D-D' + S-S' + I-I')
       + 0.1(M-M') + ...

    KQRBNP = number of kings, queens, rooks, bishops, knights and pawns
    D,S,I = doubled, blocked and isolated pawns
    M = Mobility (the number of legal moves)

    :param board: some board state to be evaluated
    :return: an evaluation of the board state via the function given above
    """

    piece_counts = collections.Counter()
    piece_counts.update(str(board.board_fen()))

    v = 200 * (piece_counts["K"] - piece_counts["k"]) \
        + 9 * (piece_counts["Q"] - piece_counts["q"]) \
        + 5 * (piece_counts["R"] - piece_counts["r"]) \
        + 3 * (piece_counts["B"] - piece_counts["b"] + piece_counts["N"] - piece_counts["n"]) \
        + (piece_counts["P"] - piece_counts["p"]) \
        - 0.5 * (count_doubled_pawns(board) + count_blocked_pawns(board) + count_isolated_pawns(board)) \
        + 0.1 * (board.legal_moves.count())

    return v


def main():
    morphy = open("data/aggressive/Morphy.pgn", encoding="utf-8-sig")

    headers = [
        "Event",
        "Site",
        "Date",
        "Round",
        "White",
        "Black",
        "Result",
        "WhiteElo",
        "BlackElo",
        "ECO",
        "Aggro"
    ]
    df = pd.DataFrame(columns=headers)

    g = c_pgn.read_game(morphy)
    while g is not None:
        d = dict(g.headers)
        d["Aggro"] = 1
        df = df.append(d, ignore_index=True)
        g = c_pgn.read_game(morphy)

    print(df.head())


if __name__ == "__main__":
    main()
