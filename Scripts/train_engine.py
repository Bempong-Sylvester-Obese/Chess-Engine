#!/usr/bin/env python3

import pandas as pd
import numpy as np
import chess
import sys
import os
import pickle
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score

# Add the parent directory to the path to import the engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import evaluate_position

def extract_features(board):
    """Extract features from a chess position for training."""
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

def prepare_training_data(data, max_samples=10000):
    """Prepare training data from the CSV file."""
    if data is None:
        return None, None
    
    # Limit the number of samples to avoid memory issues
    if len(data) > max_samples:
        data = data.sample(max_samples, random_state=42)
    
    X = []
    y = []
    
    for _, row in data.iterrows():
        try:
            board = chess.Board(row['position_fen'])
            features = extract_features(board)
            X.append(features)
            y.append(row['position_evaluation'])
        except Exception as e:
            print(f"Error processing position: {str(e)}")
    
    return np.array(X), np.array(y)

def train_model(X, y):
    """Train a linear regression model on the features."""
    # Split the data into training and validation sets
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Train the model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate the model
    y_pred = model.predict(X_val)
    mse = mean_squared_error(y_val, y_pred)
    r2 = r2_score(y_val, y_pred)
    
    print(f"Mean Squared Error: {mse:.4f}")
    print(f"R² Score: {r2:.4f}")
    
    return model

def save_model(model, file_path='Data/trained_model.pkl'):
    """Save the trained model to a file."""
    with open(file_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {file_path}")

def load_model(file_path='Data/trained_model.pkl'):
    """Load a trained model from a file."""
    try:
        with open(file_path, 'rb') as f:
            model = pickle.load(f)
        print(f"Model loaded from {file_path}")
        return model
    except FileNotFoundError:
        print(f"Model file {file_path} not found")
        return None

def main():
    """Main function to train the engine using the training data."""
    print("Training chess engine using synthetic data...")
    
    # Load the data
    data = pd.read_csv('Data/training_data.csv')
    if data is None:
        return
    
    # Prepare the training data
    X, y = prepare_training_data(data)
    if X is None or y is None:
        return
    
    # Train the model
    model = train_model(X, y)
    
    # Save the model
    save_model(model)
    
    print("Training complete.")

if __name__ == "__main__":
    main() 