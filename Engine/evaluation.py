#!/usr/bin/env python3

import chess
import chess.engine
from typing import Optional, Tuple
import os

# Piece values in centipawns
PIECE_VALUES = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

class PositionEvaluator:
    def __init__(self):
        self.engine = None
        self.initialize_engine()
        
    def initialize_engine(self):
        """Initialize the Stockfish engine if available."""
        try:
            # Try to find Stockfish in common locations
            stockfish_paths = [
                "/usr/games/stockfish",  # Linux
                "/usr/local/bin/stockfish",  # macOS with Homebrew
                "stockfish.exe",  # Windows
                "./stockfish"  # Local directory
            ]
            
            for path in stockfish_paths:
                if os.path.exists(path):
                    self.engine = chess.engine.SimpleEngine.popen_uci(path)
                    return
                    
            print("Warning: Stockfish not found. Using simple evaluation.")
        except Exception as e:
            print(f"Warning: Could not initialize Stockfish: {e}")
            print("Using simple evaluation instead.")
            
    def material_evaluation(self, board: chess.Board) -> float:
        """Simple material-based position evaluation."""
        if board.is_checkmate():
            return -20000 if board.turn else 20000
            
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is not None:
                value = PIECE_VALUES[piece.piece_type]
                score += value if piece.color else -value
                
        return score / 100.0  # Convert centipawns to pawns
        
    def evaluate_position(self, board: chess.Board, depth: int = 15) -> float:
        """Evaluate the current position using Stockfish if available."""
        if self.engine is not None:
            try:
                result = self.engine.analyse(board, chess.engine.Limit(depth=depth))
                return result["score"].relative.score() / 100.0
            except Exception as e:
                print(f"Warning: Stockfish evaluation failed: {e}")
                return self.material_evaluation(board)
        else:
            return self.material_evaluation(board)
            
    def get_best_move(self, board: chess.Board, depth: int = 15) -> Tuple[chess.Move, float]:
        """Get the best move in the position using Stockfish if available."""
        if self.engine is not None:
            try:
                result = self.engine.play(board, chess.engine.Limit(depth=depth))
                return result.move, self.evaluate_position(board, depth)
            except Exception as e:
                print(f"Warning: Stockfish analysis failed: {e}")
                return self.get_simple_best_move(board)
        else:
            return self.get_simple_best_move(board)
            
    def get_simple_best_move(self, board: chess.Board) -> Tuple[chess.Move, float]:
        """Get the best move using simple evaluation."""
        best_move = None
        best_score = float('-inf')
        
        for move in board.legal_moves:
            board.push(move)
            score = -self.material_evaluation(board)  # Negate because we're evaluating from opponent's perspective
            board.pop()
            
            if score > best_score:
                best_score = score
                best_move = move
                
        return best_move, -best_score  # Negate again to get score from current player's perspective
        
    def __del__(self):
        """Clean up the engine when the evaluator is destroyed."""
        if self.engine is not None:
            self.engine.quit()

# Global evaluator instance
evaluator = PositionEvaluator()

def evaluate_position(board: chess.Board, depth: int = 15) -> float:
    """Evaluate the current position."""
    return evaluator.evaluate_position(board, depth)

def get_best_move(board: chess.Board, depth: int = 15) -> Tuple[chess.Move, float]:
    """Get the best move in the position."""
    return evaluator.get_best_move(board, depth) 