#!/usr/bin/env python3

import chess
import pickle
import numpy as np
import sys
import os
import time

# Add the parent directory to the path to import the engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import evaluate_position
from Engine.move_suggestion import suggest_moves

def extract_features(board):
    """Extract features from a chess position for the trained model."""
    features = []
    
    # Material count for each piece type
    piece_values = {
        chess.PAWN: 1.0,
        chess.KNIGHT: 3.0,
        chess.BISHOP: 3.0,
        chess.ROOK: 5.0,
        chess.QUEEN: 9.0,
        chess.KING: 100.0
    }
    
    # Count material for each piece type
    for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
        # White pieces
        white_count = len(board.pieces(piece_type, chess.WHITE))
        features.append(white_count * piece_values[piece_type])
        
        # Black pieces
        black_count = len(board.pieces(piece_type, chess.BLACK))
        features.append(-black_count * piece_values[piece_type])
    
    # Mobility (number of legal moves)
    mobility = len(list(board.legal_moves))
    features.append(mobility if board.turn else -mobility)
    
    # King safety (distance from center)
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    
    if white_king_square is not None:
        white_king_file = chess.square_file(white_king_square)
        white_king_rank = chess.square_rank(white_king_square)
        white_king_center_distance = abs(3.5 - white_king_file) + abs(3.5 - white_king_rank)
        features.append(-white_king_center_distance)
    else:
        features.append(0)
    
    if black_king_square is not None:
        black_king_file = chess.square_file(black_king_square)
        black_king_rank = chess.square_rank(black_king_square)
        black_king_center_distance = abs(3.5 - black_king_file) + abs(3.5 - black_king_rank)
        features.append(black_king_center_distance)
    else:
        features.append(0)
    
    # Pawn structure (doubled pawns, isolated pawns)
    doubled_pawns = 0
    isolated_pawns = 0
    
    for file in range(8):
        white_pawns_in_file = len(board.pieces(chess.PAWN, chess.WHITE) & chess.BB_FILES[file])
        black_pawns_in_file = len(board.pieces(chess.PAWN, chess.BLACK) & chess.BB_FILES[file])
        
        if white_pawns_in_file > 1:
            doubled_pawns += white_pawns_in_file - 1
        if black_pawns_in_file > 1:
            doubled_pawns -= black_pawns_in_file - 1
    
    features.append(doubled_pawns)
    features.append(isolated_pawns)
    
    # Game phase (opening, middlegame, endgame)
    total_pieces = len(board.piece_map())
    features.append(total_pieces / 32.0)  # Normalized to [0, 1]
    
    return np.array(features)

def load_model(file_path='Data/trained_model.pkl'):
    """Load the trained model from a file."""
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Model file {file_path} not found")
        return None

class EnhancedChessSuggester(ChessSuggester):
    """Enhanced chess suggester that uses the trained model for evaluation."""
    
    def __init__(self, model_path='Data/trained_model.pkl'):
        """Initialize the enhanced chess suggester."""
        super().__init__()
        self.model = load_model(model_path)
        self.use_model = self.model is not None
    
    def evaluate_position(self, board):
        """Evaluate a position using the trained model if available."""
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0
        
        if self.use_model:
            # Extract features and use the model
            features = extract_features(board)
            model_eval = self.model.predict([features])[0]
            
            # Combine with material evaluation (weighted average)
            material_eval = super().evaluate_position(board)
            combined_eval = 0.7 * model_eval + 0.3 * material_eval
            
            return combined_eval
        else:
            # Fall back to the original evaluation
            return super().evaluate_position(board)
    
    def suggest_moves(self, board):
        """Suggest moves using the enhanced evaluation function."""
        if board.is_game_over():
            return []
        
        moves = []
        for move in board.legal_moves:
            board.push(move)
            eval_score = -self.evaluate_position(board)
            board.pop()
            moves.append((move, eval_score, "Enhanced evaluation"))
        
        moves.sort(key=lambda x: x[1], reverse=True)
        return moves[:5]

def create_enhanced_engine_file():
    """Create a new file with the enhanced engine implementation."""
    file_path = 'Engine/enhanced_engine.py'
    
    with open(file_path, 'w') as f:
        f.write('''#!/usr/bin/env python3

import chess
import pickle
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import the engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester

def extract_features(board):
    """Extract features from a chess position for the trained model."""
    features = []
    
    # Material count for each piece type
    piece_values = {
        chess.PAWN: 1.0,
        chess.KNIGHT: 3.0,
        chess.BISHOP: 3.0,
        chess.ROOK: 5.0,
        chess.QUEEN: 9.0,
        chess.KING: 100.0
    }
    
    # Count material for each piece type
    for piece_type in [chess.PAWN, chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN, chess.KING]:
        # White pieces
        white_count = len(board.pieces(piece_type, chess.WHITE))
        features.append(white_count * piece_values[piece_type])
        
        # Black pieces
        black_count = len(board.pieces(piece_type, chess.BLACK))
        features.append(-black_count * piece_values[piece_type])
    
    # Mobility (number of legal moves)
    mobility = len(list(board.legal_moves))
    features.append(mobility if board.turn else -mobility)
    
    # King safety (distance from center)
    white_king_square = board.king(chess.WHITE)
    black_king_square = board.king(chess.BLACK)
    
    if white_king_square is not None:
        white_king_file = chess.square_file(white_king_square)
        white_king_rank = chess.square_rank(white_king_square)
        white_king_center_distance = abs(3.5 - white_king_file) + abs(3.5 - white_king_rank)
        features.append(-white_king_center_distance)
    else:
        features.append(0)
    
    if black_king_square is not None:
        black_king_file = chess.square_file(black_king_square)
        black_king_rank = chess.square_rank(black_king_square)
        black_king_center_distance = abs(3.5 - black_king_file) + abs(3.5 - black_king_rank)
        features.append(black_king_center_distance)
    else:
        features.append(0)
    
    # Pawn structure (doubled pawns, isolated pawns)
    doubled_pawns = 0
    isolated_pawns = 0
    
    for file in range(8):
        white_pawns_in_file = len(board.pieces(chess.PAWN, chess.WHITE) & chess.BB_FILES[file])
        black_pawns_in_file = len(board.pieces(chess.PAWN, chess.BLACK) & chess.BB_FILES[file])
        
        if white_pawns_in_file > 1:
            doubled_pawns += white_pawns_in_file - 1
        if black_pawns_in_file > 1:
            doubled_pawns -= black_pawns_in_file - 1
    
    features.append(doubled_pawns)
    features.append(isolated_pawns)
    
    # Game phase (opening, middlegame, endgame)
    total_pieces = len(board.piece_map())
    features.append(total_pieces / 32.0)  # Normalized to [0, 1]
    
    return np.array(features)

def load_model(file_path='Data/trained_model.pkl'):
    """Load the trained model from a file."""
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Model file {file_path} not found")
        return None

class EnhancedChessSuggester(ChessSuggester):
    """Enhanced chess suggester that uses the trained model for evaluation."""
    
    def __init__(self, model_path='Data/trained_model.pkl'):
        """Initialize the enhanced chess suggester."""
        super().__init__()
        self.model = load_model(model_path)
        self.use_model = self.model is not None
    
    def evaluate_position(self, board):
        """Evaluate a position using the trained model if available."""
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0
        
        if self.use_model:
            # Extract features and use the model
            features = extract_features(board)
            model_eval = self.model.predict([features])[0]
            
            # Combine with material evaluation (weighted average)
            material_eval = super().evaluate_position(board)
            combined_eval = 0.7 * model_eval + 0.3 * material_eval
            
            return combined_eval
        else:
            # Fall back to the original evaluation
            return super().evaluate_position(board)
    
    def suggest_moves(self, board):
        """Suggest moves using the enhanced evaluation function."""
        if board.is_game_over():
            return []
        
        moves = []
        for move in board.legal_moves:
            board.push(move)
            eval_score = -self.evaluate_position(board)
            board.pop()
            moves.append((move, eval_score, "Enhanced evaluation"))
        
        moves.sort(key=lambda x: x[1], reverse=True)
        return moves[:5]
    
    def get_move_suggestions(self, board):
        """Get move suggestions with enhanced evaluation."""
        current_eval = self.evaluate_position(board)
        move_suggestions = self.suggest_moves(board)
        
        formatted_suggestions = []
        for move, eval_score, comment in move_suggestions:
            formatted_suggestions.append({
                "move": move.uci(),
                "san": board.san(move),
                "evaluation": eval_score,
                "comment": comment
            })
        
        return {
            "current_evaluation": current_eval,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "suggested_moves": formatted_suggestions
        }

if __name__ == "__main__":
    # Example usage
    board = chess.Board()
    suggester = EnhancedChessSuggester()
    suggestions = suggester.get_move_suggestions(board)
    
    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")
    
    print("\\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}")
''')
    
    print(f"Created enhanced engine file at {file_path}")

def compare_engines():
    """Compare the original and enhanced engines on a set of positions."""
    # Create a board with a complex position
    board = chess.Board()
    board.push_san("e4")
    board.push_san("e5")
    board.push_san("Nf3")
    board.push_san("Nc6")
    board.push_san("Bc4")
    board.push_san("Bc5")
    board.push_san("b4")
    
    # Create both engines
    original_suggester = ChessSuggester()
    enhanced_suggester = EnhancedChessSuggester()
    
    # Get suggestions from both engines
    original_suggestions = original_suggester.get_move_suggestions(board)
    enhanced_suggestions = enhanced_suggester.get_move_suggestions(board)
    
    # Print comparison
    print("Position:", board.fen())
    print("\nOriginal Engine:")
    print(f"Evaluation: {original_suggestions['current_evaluation']:.2f}")
    print("Top moves:")
    for i, move in enumerate(original_suggestions['suggested_moves'][:3], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f})")
    
    print("\nEnhanced Engine:")
    print(f"Evaluation: {enhanced_suggestions['current_evaluation']:.2f}")
    print("Top moves:")
    for i, move in enumerate(enhanced_suggestions['suggested_moves'][:3], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f})")

def main():
    """Main function to integrate the trained model with the engine."""
    print("Integrating trained model with chess engine...")
    
    # Create the enhanced engine file
    create_enhanced_engine_file()
    
    # Compare the engines
    print("\nComparing original and enhanced engines:")
    compare_engines()
    
    print("\nIntegration complete. You can now use the EnhancedChessSuggester class in your application.")

if __name__ == "__main__":
    main() 