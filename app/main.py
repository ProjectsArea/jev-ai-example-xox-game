import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from .game import (
    create_board,
    get_available_moves,
    check_winner,
    is_draw,
    apply_move,
)

from .jev_service import JevService

load_dotenv()

logger = logging.getLogger("jev-tictactoe")

BASE_DIR = Path(__file__).resolve().parent
STATIC_DIR = BASE_DIR / "static"


app = FastAPI(
    title="Human vs Jev Tic-Tac-Toe",
    version="1.0.0",
)


app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


jev = JevService()


class MoveRequest(BaseModel):
    board: list[str]
    position: int


class JevMoveRequest(BaseModel):
    board: list[str]


@app.get("/")
def home():
    return FileResponse(
        STATIC_DIR / "index.html"
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "jev-tictactoe",
    }


@app.post("/api/player-move")
def player_move(request: MoveRequest):

    board = request.board.copy()
    position = request.position

    print(
        f"[player-move] received board={board!r} position={position!r}",
        flush=True,
    )
    logger.info(
        "player-move received board=%s position=%s",
        board,
        position,
    )

    if len(board) != 9:
        reason = "Board must contain exactly 9 cells."
        print(f"[player-move] validation failed: {reason}", flush=True)
        logger.warning("player-move rejected: %s", reason)
        raise HTTPException(
            status_code=400,
            detail=reason,
        )

    if any(
        cell not in ("", "X", "O")
        for cell in board
    ):
        reason = "Invalid board."
        print(f"[player-move] validation failed: {reason}", flush=True)
        logger.warning("player-move rejected: %s", reason)
        raise HTTPException(
            status_code=400,
            detail=reason,
        )

    if position < 0 or position > 8:
        reason = "Position must be between 0 and 8."
        print(f"[player-move] validation failed: {reason}", flush=True)
        logger.warning("player-move rejected: %s", reason)
        raise HTTPException(
            status_code=400,
            detail=reason,
        )

    if board[position] != "":
        reason = (
            "Cell is already occupied. "
            "Send the board BEFORE applying X; "
            f"received cell[{position}]={board[position]!r}."
        )
        print(f"[player-move] validation failed: {reason}", flush=True)
        logger.warning("player-move rejected: %s", reason)
        raise HTTPException(
            status_code=400,
            detail="Cell is already occupied.",
        )

    board = apply_move(
        board,
        position,
        "X",
    )

    print(
        f"[player-move] accepted; applied X at {position}; board={board!r}",
        flush=True,
    )

    winner = check_winner(board)

    if winner:
        return {
            "board": board,
            "game_over": True,
            "winner": winner,
        }

    if is_draw(board):
        return {
            "board": board,
            "game_over": True,
            "winner": "draw",
        }

    return {
        "board": board,
        "game_over": False,
    }


@app.post("/api/jev-move")
def jev_move(request: JevMoveRequest):

    board = request.board.copy()

    print(
        f"[jev-move] received board={board!r}",
        flush=True,
    )

    if len(board) != 9:
        reason = "Board must contain exactly 9 cells."
        print(f"[jev-move] validation failed: {reason}", flush=True)
        raise HTTPException(
            status_code=400,
            detail=reason,
        )

    available_moves = get_available_moves(board)

    if not available_moves:
        return {
            "board": board,
            "game_over": True,
            "winner": "draw",
        }

    try:

        print(
            f"[jev-move] calling TypeSafe Jev; available={available_moves}",
            flush=True,
        )

        decision = jev.get_move(
            board,
            available_moves,
        )

        print(
            f"[jev-move] Jev decision={decision!r}",
            flush=True,
        )

        move = decision["move"]

        if move not in available_moves:
            raise ValueError(
                f"Jev selected invalid move: {move}"
            )

        board = apply_move(
            board,
            move,
            "O",
        )

        winner = check_winner(board)

        if winner:
            return {
                "board": board,
                "game_over": True,
                "winner": winner,
                "jev": decision,
            }

        if is_draw(board):
            return {
                "board": board,
                "game_over": True,
                "winner": "draw",
                "jev": decision,
            }

        return {
            "board": board,
            "game_over": False,
            "winner": None,
            "jev": decision,
        }

    except Exception as exc:

        print(f"[jev-move] Jev error: {exc}", flush=True)
        raise HTTPException(
            status_code=500,
            detail=f"Jev error: {str(exc)}",
        )