#!/usr/bin/env python3

import chess
import chess.engine
from typing import Optional, List, Tuple, Dict, Any
import logging

class BlunderDetector:
    """
    A class for detecting blunders in chess positions.
    A blunder is typically defined as a serious mistake that leads to a significant disadvantage.
    """
    
    def __init__(self, engine_path: Optional[str] = None, evaluation_threshold: float = -2.0):
        """
        Initialize the blunder detector.
        
        Args:
            engine_path: Path to a UCI chess engine (like Stockfish). If None, will use simple heuristics.
            evaluation_threshold: The evaluation threshold below which a move is considered a blunder.
                                 Negative values indicate advantage for the opponent.
        """
        self.engine_path = engine_path
        self.evaluation_threshold = evaluation_threshold
        self.engine = None
        
        # Initialize the engine if path is provided
        if engine_path:
            try:
                self.engine = chess.engine.SimpleEngine.popen_uci(engine_path)
                logging.info(f"Chess engine initialized from {engine_path}")
            except Exception as e:
                logging.error(f"Failed to initialize chess engine: {e}")
                self.engine = None
        
        # Material values for simple evaluation
        self.material_values = {
            chess.PAWN: 1.0,
            chess.KNIGHT: 3.0,
            chess.BISHOP: 3.0,
            chess.ROOK: 5.0,
            chess.QUEEN: 9.0,
            chess.KING: 100.0  # High value to prioritize king safety
        }
    
    def __del__(self):
        """Clean up resources when the object is destroyed."""
        if self.engine:
            try:
                self.engine.quit()
            except:
                pass
    
    def evaluate_position(self, board: chess.Board) -> float:
        """
        Evaluate the current position.
        
        Args:
            board: The chess board to evaluate.
            
        Returns:
            A float representing the evaluation. Positive values favor White, negative values favor Black.
        """
        # If engine is available, use it for evaluation
        if self.engine:
            try:
                result = self.engine.analyse(board, chess.engine.Limit(time=0.1))
                return result["score"].white().score(mate_score=10000) / 100.0
            except Exception as e:
                logging.warning(f"Engine evaluation failed: {e}. Falling back to simple evaluation.")
        
        # Simple material evaluation as fallback
        score = 0.0
        
        # Count material
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                value = self.material_values[piece.piece_type]
                if piece.color == chess.WHITE:
                    score += value
                else:
                    score -= value
        
        # Add positional bonuses/penalties
        # This is a very simple implementation and could be expanded
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                # Bonus for controlling center
                if square in [chess.E4, chess.E5, chess.D4, chess.D5]:
                    bonus = 0.1
                    if piece.color == chess.WHITE:
                        score += bonus
                    else:
                        score -= bonus
                
                # Penalty for exposed king
                if piece.piece_type == chess.KING:
                    # Check if king is castled
                    if (piece.color == chess.WHITE and 
                        (square == chess.G1 or square == chess.C1)):
                        if piece.color == chess.WHITE:
                            score += 0.5
                        else:
                            score -= 0.5
                    # Penalty for king in the middle
                    elif square in [chess.E1, chess.E2, chess.D1, chess.D2, 
                                   chess.E8, chess.E7, chess.D8, chess.D7]:
                        if piece.color == chess.WHITE:
                            score -= 0.3
                        else:
                            score += 0.3
        
        return score
    
    def is_blunder(self, board: chess.Board, move: chess.Move) -> Tuple[bool, float, float]:
        """
        Check if a move is a blunder.
        
        Args:
            board: The current chess board.
            move: The move to evaluate.
            
        Returns:
            A tuple containing:
            - Boolean indicating if the move is a blunder
            - Evaluation before the move
            - Evaluation after the move
        """
        # Get evaluation before the move
        eval_before = self.evaluate_position(board)
        
        # Make the move
        board.push(move)
        
        # Get evaluation after the move
        eval_after = self.evaluate_position(board)
        
        # Undo the move
        board.pop()
        
        # Determine if it's a blunder
        # For White: if eval_before > eval_after - threshold, it's a blunder
        # For Black: if eval_before < eval_after + threshold, it's a blunder
        is_blunder = False
        if board.turn == chess.WHITE:
            is_blunder = (eval_before - eval_after) > abs(self.evaluation_threshold)
        else:
            is_blunder = (eval_after - eval_before) > abs(self.evaluation_threshold)
        
        return is_blunder, eval_before, eval_after
    
    def find_better_moves(self, board: chess.Board, move: chess.Move, 
                         max_moves: int = 3) -> List[Tuple[chess.Move, float]]:
        """
        Find better alternative moves than the given move.
        
        Args:
            board: The current chess board.
            move: The move to compare against.
            max_moves: Maximum number of alternative moves to return.
            
        Returns:
            A list of tuples containing (move, evaluation) for better moves.
        """
        # Get evaluation of the given move
        _, _, eval_after_move = self.is_blunder(board, move)
        
        # Find all legal moves
        better_moves = []
        
        for legal_move in board.legal_moves:
            if legal_move == move:
                continue
                
            # Make the move
            board.push(legal_move)
            
            # Get evaluation
            eval_after = self.evaluate_position(board)
            
            # Undo the move
            board.pop()
            
            # Check if this move is better
            if board.turn == chess.WHITE:
                if eval_after > eval_after_move:
                    better_moves.append((legal_move, eval_after))
            else:
                if eval_after < eval_after_move:
                    better_moves.append((legal_move, eval_after))
        
        # Sort by evaluation (best first)
        if board.turn == chess.WHITE:
            better_moves.sort(key=lambda x: x[1], reverse=True)
        else:
            better_moves.sort(key=lambda x: x[1])
        
        return better_moves[:max_moves]
    
    def analyze_position(self, board: chess.Board) -> Dict[str, Any]:
        """
        Analyze the current position and return information about potential blunders.
        
        Args:
            board: The current chess board.
            
        Returns:
            A dictionary containing analysis information.
        """
        result = {
            "current_evaluation": self.evaluate_position(board),
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "legal_moves": list(board.legal_moves),
            "potential_blunders": []
        }
        
        # Check each legal move for blunders
        for move in board.legal_moves:
            is_blunder, eval_before, eval_after = self.is_blunder(board, move)
            
            if is_blunder:
                better_moves = self.find_better_moves(board, move)
                
                blunder_info = {
                    "move": move,
                    "eval_before": eval_before,
                    "eval_after": eval_after,
                    "better_moves": better_moves
                }
                
                result["potential_blunders"].append(blunder_info)
        
        return result
