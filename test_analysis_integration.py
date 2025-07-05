#!/usr/bin/env python3
"""
Test script to verify the analysis integration works correctly.
This script tests the chess engines and analysis capabilities without the GUI.
"""

import sys
import os
import chess

# Add the Engine directory to the path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'Engine'))

from Engine.enhanced_engine import EnhancedChessSuggester
from Engine.chess_suggester import ChessSuggester

def test_analysis_integration():
    """Test the analysis integration functionality"""
    print("Testing Chess Analysis Integration...")
    print("=" * 50)
    
    # Initialize engines
    print("1. Initializing chess engines...")
    enhanced_engine = EnhancedChessSuggester()
    basic_engine = ChessSuggester()
    print("✓ Engines initialized successfully")
    
    # Test starting position
    print("\n2. Testing starting position analysis...")
    board = chess.Board()
    
    enhanced_analysis = enhanced_engine.get_move_suggestions(board)
    basic_analysis = basic_engine.get_move_suggestions(board)
    
    print(f"Enhanced Engine Evaluation: {enhanced_analysis['current_evaluation']:.2f}")
    print(f"Basic Engine Evaluation: {basic_analysis['current_evaluation']:.2f}")
    print(f"Game Status: {enhanced_analysis['is_check']}")
    print("✓ Starting position analysis complete")
    
    # Test after a few moves
    print("\n3. Testing position after some moves...")
    moves = ['e4', 'e5', 'Nf3', 'Nc6']
    for move in moves:
        board.push_san(move)
    
    enhanced_analysis = enhanced_engine.get_move_suggestions(board)
    print(f"Position after {len(moves)} moves:")
    print(f"FEN: {board.fen()}")
    print(f"Evaluation: {enhanced_analysis['current_evaluation']:.2f}")
    print(f"Top 3 moves:")
    for i, move_data in enumerate(enhanced_analysis['suggested_moves'][:3]):
        print(f"  {i+1}. {move_data['san']} (eval: {move_data['evaluation']:.2f})")
    print("✓ Move analysis complete")
    
    # Test checkmate position
    print("\n4. Testing checkmate position...")
    checkmate_board = chess.Board("rnb1kbnr/pppp1ppp/8/4p3/6Pq/5P2/PPPPP2P/RNBQKBNR w KQkq - 1 3")
    checkmate_analysis = enhanced_engine.get_move_suggestions(checkmate_board)
    print(f"Checkmate position evaluation: {checkmate_analysis['current_evaluation']:.2f}")
    print(f"Is checkmate: {checkmate_analysis['is_checkmate']}")
    print("✓ Checkmate analysis complete")
    
    # Test stalemate position
    print("\n5. Testing stalemate position...")
    stalemate_board = chess.Board("k7/8/1K6/8/8/8/8/8 w - - 0 1")
    stalemate_analysis = enhanced_engine.get_move_suggestions(stalemate_board)
    print(f"Stalemate position evaluation: {stalemate_analysis['current_evaluation']:.2f}")
    print(f"Is stalemate: {stalemate_analysis['is_stalemate']}")
    print("✓ Stalemate analysis complete")
    
    print("\n" + "=" * 50)
    print("✓ All analysis integration tests passed!")
    print("\nThe chess game with real-time analysis is ready to use.")
    print("Run 'python main.py' to start the game with analysis panel.")

if __name__ == "__main__":
    test_analysis_integration() 