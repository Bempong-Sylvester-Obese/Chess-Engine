#!/usr/bin/env python3

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import chess
from Engine.board import Board
from Engine.evaluation import evaluate_position, get_best_move

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
    """Make a move on the board."""
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
    """Get the current game state."""
    return GameState(
        fen=board.get_fen(),
        is_game_over=board.is_game_over(),
        result=board.get_game_result(),
        evaluation=evaluate_position(board.board),
        legal_moves=[move.uci() for move in board.get_legal_moves()]
    )

@router.get("/best-move")
async def get_best_move(depth: int = 15):
    """Get the best move in the current position."""
    move, score = get_best_move(board.board, depth)
    return {
        "move": move.uci(),
        "evaluation": score
    }

@router.post("/reset")
async def reset_game():
    """Reset the game to the initial position."""
    board = Board()
    return {"status": "success", "fen": board.get_fen()}
