#!/usr/bin/env python3

import chess
import sys
import os
from Engine.position_detection import BlunderDetector

def print_board(board):
    """Print the chess board in a readable format."""
    print(board)

def print_analysis(analysis):
    """Print the analysis results in a readable format."""
    print("\n=== Position Analysis ===")
    print(f"Current evaluation: {analysis['current_evaluation']:.2f}")
    print(f"Check: {analysis['is_check']}")
    print(f"Checkmate: {analysis['is_checkmate']}")
    print(f"Stalemate: {analysis['is_stalemate']}")
    print(f"Insufficient material: {analysis['is_insufficient_material']}")
    
    if analysis['potential_blunders']:
        print("\n=== Potential Blunders ===")
        for i, blunder in enumerate(analysis['potential_blunders'], 1):
            print(f"\nBlunder {i}:")
            print(f"  Move: {blunder['move']}")
            print(f"  Evaluation before: {blunder['eval_before']:.2f}")
            print(f"  Evaluation after: {blunder['eval_after']:.2f}")
            
            if blunder['better_moves']:
                print("  Better moves:")
                for move, eval_score in blunder['better_moves']:
                    print(f"    {move}: {eval_score:.2f}")
    else:
        print("\nNo blunders detected in the current position.")

def main():
    # Create a chess board
    board = chess.Board()
    
    # Path to Stockfish engine (if available)
    # You can download Stockfish from https://stockfishchess.org/download/
    engine_path = None
    
    # Check if Stockfish is in the PATH
    if sys.platform == "win32":
        # Windows
        for path in os.environ["PATH"].split(os.pathsep):
            stockfish_path = os.path.join(path, "stockfish.exe")
            if os.path.isfile(stockfish_path):
                engine_path = stockfish_path
                break
    else:
        # macOS/Linux
        for path in os.environ["PATH"].split(os.pathsep):
            stockfish_path = os.path.join(path, "stockfish")
            if os.path.isfile(stockfish_path):
                engine_path = stockfish_path
                break
    
    # Create the blunder detector
    detector = BlunderDetector(engine_path=engine_path)
    
    # Example 1: Starting position
    print("\n=== Example 1: Starting Position ===")
    print_board(board)
    analysis = detector.analyze_position(board)
    print_analysis(analysis)
    
    # Example 2: A position with a potential blunder
    # This is the famous "Scholar's Mate" position
    board = chess.Board()
    moves = ["e4", "e5", "Bc4", "Nc6", "Qh5", "Nf6", "Qxf7#"]
    
    print("\n=== Example 2: Scholar's Mate ===")
    for i, move in enumerate(moves):
        if i % 2 == 0:
            print(f"\nMove {i//2 + 1}: White plays {move}")
        else:
            print(f"Move {i//2 + 1}: Black plays {move}")
        
        board.push_san(move)
        print_board(board)
        
        # Analyze after each move
        analysis = detector.analyze_position(board)
        print_analysis(analysis)
        
        # Stop after checkmate
        if board.is_checkmate():
            break
    
    # Example 3: A position with a potential blunder (if Stockfish is available)
    if engine_path:
        print("\n=== Example 3: Position with Blunder (requires Stockfish) ===")
        board = chess.Board()
        # This is a position where Black has a winning advantage but can blunder
        fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 2"
        board.set_fen(fen)
        print_board(board)
        analysis = detector.analyze_position(board)
        print_analysis(analysis)
    else:
        print("\nStockfish not found. Skipping Example 3.")

if __name__ == "__main__":
    main() 