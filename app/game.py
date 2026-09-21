from typing import Optional


WINNING_COMBINATIONS = [
    (0, 1, 2),
    (3, 4, 5),
    (6, 7, 8),
    (0, 3, 6),
    (1, 4, 7),
    (2, 5, 8),
    (0, 4, 8),
    (2, 4, 6),
]


def create_board():
    return [""] * 9


def get_available_moves(board):
    return [
        index
        for index, value in enumerate(board)
        if value == ""
    ]


def check_winner(board) -> Optional[str]:
    for a, b, c in WINNING_COMBINATIONS:
        if (
            board[a]
            and board[a] == board[b]
            and board[a] == board[c]
        ):
            return board[a]

    return None


def is_draw(board):
    return (
        check_winner(board) is None
        and all(cell != "" for cell in board)
    )


def game_over(board):
    winner = check_winner(board)

    if winner:
        return True, winner

    if is_draw(board):
        return True, "draw"

    return False, None


def validate_move(board, position):
    if position < 0 or position > 8:
        return False

    if board[position] != "":
        return False

    return True


def apply_move(board, position, player):
    if not validate_move(board, position):
        raise ValueError("Invalid move")

    board[position] = player

    return board