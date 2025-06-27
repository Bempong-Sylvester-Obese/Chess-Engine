from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chess
from Engine.board import Board
from Engine.evaluation import evaluate_position, get_best_move as engine_get_best_move

router = APIRouter()
board = Board()

class MoveRequest(BaseModel):
    move: str  # UCI format (e.g., "e2e4")

class GameState(BaseModel):
    fen: str
    is_game_over: bool
    result: Optional[str]
    evaluation: float
    legal_moves: List[str]

@router.post("/move")
async def make_move(move_request: MoveRequest):
    try:
        move = chess.Move.from_uci(move_request.move)
        if board.make_move(move):
            return {"status": "success", "fen": board.get_fen()}
        else:
            raise HTTPException(status_code=400, detail="Illegal move")
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid move format")

@router.get("/state")
async def get_state():
    return GameState(
        fen=board.get_fen(),
        is_game_over=board.is_game_over(),
        result=board.get_game_result(),
        evaluation=evaluate_position(board.board),
        legal_moves=[move.uci() for move in board.get_legal_moves()]
    )

@router.get("/best-move")
async def get_best_move_endpoint(depth: int = 15):
    move, score = engine_get_best_move(board.board, depth)
    if move is None:
        raise HTTPException(status_code=404, detail="No legal moves available")
    return {
        "move": move.uci(),
        "evaluation": score
    }

@router.post("/reset")
async def reset_game():
    board = Board()
    return {"status": "success", "fen": board.get_fen()}
