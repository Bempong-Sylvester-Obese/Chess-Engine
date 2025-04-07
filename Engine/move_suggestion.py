#!/usr/bin/env python3

import chess
import chess.engine
from typing import Optional, List, Tuple, Dict, Any
import logging
import random

class MoveSuggester:
    """
    A class for suggesting moves in chess positions.
    This class can use a chess engine (like Stockfish) for strong move suggestions
    or fall back to simple heuristics when no engine is available.
    """
    
    def __init__(self, engine_path: Optional[str] = None, max_depth: int = 15, 
                 max_moves: int = 5, randomness: float = 0.0):
        """
        Initialize the move suggester.
        
        Args:
            engine_path: Path to a UCI chess engine (like Stockfish). If None, will use simple heuristics.
            max_depth: Maximum search depth for the engine.
            max_moves: Maximum number of moves to suggest.
            randomness: Amount of randomness to add to move suggestions (0.0 to 1.0).
                        0.0 means always suggest the best move, 1.0 means completely random.
        """
        self.engine_path = engine_path
        self.max_depth = max_depth
        self.max_moves = max_moves
        self.randomness = max(0.0, min(1.0, randomness))  # Clamp between 0 and 1
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
        
        # Piece-square tables for positional evaluation
        self.pawn_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            50, 50, 50, 50, 50, 50, 50, 50,
            10, 10, 20, 30, 30, 20, 10, 10,
            5,  5, 10, 25, 25, 10,  5,  5,
            0,  0,  0, 20, 20,  0,  0,  0,
            5, -5,-10,  0,  0,-10, -5,  5,
            5, 10, 10,-20,-20, 10, 10,  5,
            0,  0,  0,  0,  0,  0,  0,  0
        ]
        
        self.knight_table = [
            -50,-40,-30,-30,-30,-30,-40,-50,
            -40,-20,  0,  0,  0,  0,-20,-40,
            -30,  0, 10, 15, 15, 10,  0,-30,
            -30,  5, 15, 20, 20, 15,  5,-30,
            -30,  0, 15, 20, 20, 15,  0,-30,
            -30,  5, 10, 15, 15, 10,  5,-30,
            -40,-20,  0,  5,  5,  0,-20,-40,
            -50,-40,-30,-30,-30,-30,-40,-50
        ]
        
        self.bishop_table = [
            -20,-10,-10,-10,-10,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5, 10, 10,  5,  0,-10,
            -10,  5,  5, 10, 10,  5,  5,-10,
            -10,  0, 10, 10, 10, 10,  0,-10,
            -10, 10, 10, 10, 10, 10, 10,-10,
            -10,  5,  0,  0,  0,  0,  5,-10,
            -20,-10,-10,-10,-10,-10,-10,-20
        ]
        
        self.rook_table = [
            0,  0,  0,  0,  0,  0,  0,  0,
            5, 10, 10, 10, 10, 10, 10,  5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            -5,  0,  0,  0,  0,  0,  0, -5,
            0,  0,  0,  5,  5,  0,  0,  0
        ]
        
        self.queen_table = [
            -20,-10,-10, -5, -5,-10,-10,-20,
            -10,  0,  0,  0,  0,  0,  0,-10,
            -10,  0,  5,  5,  5,  5,  0,-10,
            -5,  0,  5,  5,  5,  5,  0, -5,
            0,  0,  5,  5,  5,  5,  0, -5,
            -10,  5,  5,  5,  5,  5,  0,-10,
            -10,  0,  5,  0,  0,  0,  0,-10,
            -20,-10,-10, -5, -5,-10,-10,-20
        ]
        
        self.king_middle_table = [
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -30,-40,-40,-50,-50,-40,-40,-30,
            -20,-30,-30,-40,-40,-30,-30,-20,
            -10,-20,-20,-20,-20,-20,-20,-10,
            20, 20,  0,  0,  0,  0, 20, 20,
            20, 30, 10,  0,  0, 10, 30, 20
        ]
        
        self.king_end_table = [
            -50,-40,-30,-20,-20,-30,-40,-50,
            -30,-20,-10,  0,  0,-10,-20,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 30, 40, 40, 30,-10,-30,
            -30,-10, 20, 30, 30, 20,-10,-30,
            -30,-30,  0,  0,  0,  0,-30,-30,
            -50,-30,-30,-30,-30,-30,-30,-50
        ]
    
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
        # If we have an engine, use it for evaluation
        if self.engine:
            try:
                result = self.engine.analyse(board, chess.engine.Limit(depth=self.max_depth))
                return result["score"].white().score(mate_score=10000) / 100.0
            except Exception as e:
                logging.error(f"Engine evaluation failed: {e}")
                # Fall back to simple evaluation
        
        # Simple material and positional evaluation
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0  # Draw
        
        score = 0.0
        
        # Material evaluation
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
                
            # Material value
            value = self.material_values[piece.piece_type]
            if piece.color:
                score += value
            else:
                score -= value
            
            # Positional value
            if piece.piece_type == chess.PAWN:
                if piece.color:
                    score += self.pawn_table[square] / 100.0
                else:
                    score -= self.pawn_table[chess.square_mirror(square)] / 100.0
            elif piece.piece_type == chess.KNIGHT:
                if piece.color:
                    score += self.knight_table[square] / 100.0
                else:
                    score -= self.knight_table[chess.square_mirror(square)] / 100.0
            elif piece.piece_type == chess.BISHOP:
                if piece.color:
                    score += self.bishop_table[square] / 100.0
                else:
                    score -= self.bishop_table[chess.square_mirror(square)] / 100.0
            elif piece.piece_type == chess.ROOK:
                if piece.color:
                    score += self.rook_table[square] / 100.0
                else:
                    score -= self.rook_table[chess.square_mirror(square)] / 100.0
            elif piece.piece_type == chess.QUEEN:
                if piece.color:
                    score += self.queen_table[square] / 100.0
                else:
                    score -= self.queen_table[chess.square_mirror(square)] / 100.0
            elif piece.piece_type == chess.KING:
                # Use different tables for middle and end game
                if self._is_endgame(board):
                    if piece.color:
                        score += self.king_end_table[square] / 100.0
                    else:
                        score -= self.king_end_table[chess.square_mirror(square)] / 100.0
                else:
                    if piece.color:
                        score += self.king_middle_table[square] / 100.0
                    else:
                        score -= self.king_middle_table[chess.square_mirror(square)] / 100.0
        
        # Mobility evaluation (simplified)
        mobility = len(list(board.legal_moves))
        if board.turn:
            score += mobility * 0.01
        else:
            score -= mobility * 0.01
        
        return score
    
    def _is_endgame(self, board: chess.Board) -> bool:
        """
        Determine if the current position is an endgame.
        
        Args:
            board: The chess board to evaluate.
            
        Returns:
            True if the position is an endgame, False otherwise.
        """
        # Count pieces
        piece_count = 0
        for square in chess.SQUARES:
            if board.piece_at(square):
                piece_count += 1
        
        # Consider it an endgame if there are 12 or fewer pieces
        return piece_count <= 12
    
    def suggest_moves(self, board: chess.Board) -> List[Tuple[chess.Move, float, str]]:
        """
        Suggest moves for the current position.
        
        Args:
            board: The chess board to analyze.
            
        Returns:
            A list of tuples containing (move, evaluation, comment).
        """
        if board.is_game_over():
            return []
        
        # If we have an engine, use it for move suggestions
        if self.engine:
            try:
                result = self.engine.analyse(board, chess.engine.Limit(depth=self.max_depth))
                moves = []
                
                # Get the principal variation
                pv = result.get("pv", [])
                if pv:
                    moves.append((pv[0], result["score"].white().score(mate_score=10000) / 100.0, "Principal variation"))
                
                # Get other top moves
                for move in result.get("multipv", []):
                    if move["pv"] and move["pv"][0] not in [m[0] for m in moves]:
                        moves.append((move["pv"][0], move["score"].white().score(mate_score=10000) / 100.0, "Engine suggestion"))
                
                # Add randomness if requested
                if self.randomness > 0 and len(moves) > 1:
                    # Shuffle moves with probability based on randomness
                    for i in range(len(moves) - 1, 0, -1):
                        if random.random() < self.randomness:
                            j = random.randint(0, i)
                            moves[i], moves[j] = moves[j], moves[i]
                
                return moves[:self.max_moves]
            except Exception as e:
                logging.error(f"Engine move suggestion failed: {e}")
                # Fall back to simple move suggestion
        
        # Simple move suggestion based on evaluation
        moves = []
        for move in board.legal_moves:
            # Make the move
            board.push(move)
            
            # Evaluate the resulting position
            eval_score = -self.evaluate_position(board)  # Negate because we're evaluating from opponent's perspective
            
            # Undo the move
            board.pop()
            
            # Add the move to the list
            moves.append((move, eval_score, "Heuristic evaluation"))
        
        # Sort moves by evaluation (descending)
        moves.sort(key=lambda x: x[1], reverse=True)
        
        # Add randomness if requested
        if self.randomness > 0 and len(moves) > 1:
            # Shuffle moves with probability based on randomness
            for i in range(len(moves) - 1, 0, -1):
                if random.random() < self.randomness:
                    j = random.randint(0, i)
                    moves[i], moves[j] = moves[j], moves[i]
        
        return moves[:self.max_moves]
    
    def get_move_suggestions(self, board: chess.Board) -> Dict[str, Any]:
        """
        Get move suggestions for the current position.
        
        Args:
            board: The chess board to analyze.
            
        Returns:
            A dictionary containing move suggestions and position information.
        """
        # Get the current evaluation
        current_eval = self.evaluate_position(board)
        
        # Get move suggestions
        move_suggestions = self.suggest_moves(board)
        
        # Format the suggestions
        formatted_suggestions = []
        for move, eval_score, comment in move_suggestions:
            formatted_suggestions.append({
                "move": move.uci(),
                "san": board.san(move),
                "evaluation": eval_score,
                "comment": comment
            })
        
        # Return the results
        return {
            "current_evaluation": current_eval,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "suggested_moves": formatted_suggestions
        }


# Example usage
if __name__ == "__main__":
    # Create a chess board
    board = chess.Board()
    
    # Create the move suggester
    suggester = MoveSuggester()
    
    # Get move suggestions
    suggestions = suggester.get_move_suggestions(board)
    
    # Print the suggestions
    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")
    
    print("\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}")
