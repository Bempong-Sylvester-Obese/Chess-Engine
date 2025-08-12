import chess
import pickle
import numpy as np
import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import evaluate_position
from Engine.move_suggestion import MoveSuggester

def extract_features(board):
    features = []
    
    # Material count for each piece
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
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Model file {file_path} not found")
        return None

class EnhancedChessSuggester(ChessSuggester):
    
    def __init__(self, model_path='Data/trained_model.pkl'):
        super().__init__()
        self.model = load_model(model_path)
        self.use_model = self.model is not None
    
    def evaluate_position(self, board):
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0
        
        if self.use_model and self.model is not None and hasattr(self.model, 'predict'):
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
    file_path = 'Engine/enhanced_engine.py'
    
    with open(file_path, 'w') as f:
        f.write('#!/usr/bin/env python3\n')
        f.write('# TODO: Implement enhanced engine here.\n')
