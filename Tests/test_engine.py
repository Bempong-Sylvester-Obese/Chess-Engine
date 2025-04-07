#!/usr/bin/env python3

import unittest
import chess
import pandas as pd
import numpy as np
import sys
import os

# Add the parent directory to the path so we can import the engine modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import evaluate_position
from Engine.move_suggestion import suggest_moves

class TestChessEngine(unittest.TestCase):
    """Test suite for the chess engine components."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.board = chess.Board()
        self.suggester = ChessSuggester()
        
        # Load a sample of the training data
        try:
            self.training_data = pd.read_csv('Data/training_data.csv', nrows=100)
        except FileNotFoundError:
            print("Warning: training_data.csv not found. Running tests without training data.")
            self.training_data = None
    
    def test_initial_position(self):
        """Test that the initial position is evaluated correctly."""
        eval_score = evaluate_position(self.board)
        self.assertIsInstance(eval_score, float)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Initial position should be roughly equal
    
    def test_material_evaluation(self):
        """Test that material evaluation works correctly."""
        # Test a position with a pawn advantage
        self.board = chess.Board('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1')
        eval_score = evaluate_position(self.board)
        self.assertGreater(eval_score, 0)  # White should be better
        
        # Test a position with a queen advantage
        self.board = chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        self.board.remove_piece_at(chess.E4)  # Remove a pawn
        eval_score = evaluate_position(self.board)
        self.assertLess(eval_score, 0)  # Black should be better
    
    def test_move_suggestions(self):
        """Test that move suggestions are generated correctly."""
        suggestions = suggest_moves(self.board)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        
        # Check that each suggestion has the expected format
        for move, eval_score, comment in suggestions:
            self.assertIsInstance(move, chess.Move)
            self.assertIsInstance(eval_score, float)
            self.assertIsInstance(comment, str)
    
    def test_chess_suggester(self):
        """Test the ChessSuggester class."""
        result = self.suggester.get_move_suggestions(self.board)
        
        # Check that the result has the expected keys
        expected_keys = ['current_evaluation', 'is_check', 'is_checkmate', 
                         'is_stalemate', 'is_insufficient_material', 'suggested_moves']
        for key in expected_keys:
            self.assertIn(key, result)
        
        # Check that suggested_moves is a list
        self.assertIsInstance(result['suggested_moves'], list)
        
        # Check that each suggested move has the expected format
        for move_data in result['suggested_moves']:
            self.assertIn('move', move_data)
            self.assertIn('san', move_data)
            self.assertIn('evaluation', move_data)
            self.assertIn('comment', move_data)
    
    def test_training_data_compatibility(self):
        """Test that the engine can process positions from the training data."""
        if self.training_data is None:
            self.skipTest("Training data not available")
        
        # Test a few positions from the training data
        for _, row in self.training_data.head(5).iterrows():
            try:
                # Create a board from the FEN
                board = chess.Board(row['position_fen'])
                
                # Get move suggestions
                suggestions = suggest_moves(board)
                self.assertGreater(len(suggestions), 0)
                
                # Evaluate the position
                eval_score = evaluate_position(board)
                self.assertIsInstance(eval_score, float)
                
                # Check that the suggester can handle this position
                suggester_result = self.suggester.get_move_suggestions(board)
                self.assertIn('suggested_moves', suggester_result)
                self.assertGreater(len(suggester_result['suggested_moves']), 0)
            except Exception as e:
                self.fail(f"Failed to process position: {row['position_fen']} - {str(e)}")
    
    def test_checkmate_detection(self):
        """Test that checkmate positions are evaluated correctly."""
        # Fool's mate position
        self.board = chess.Board()
        self.board.push_san("f3")
        self.board.push_san("e5")
        self.board.push_san("g4")
        self.board.push_san("Qh4")
        
        # Check that the position is recognized as checkmate
        self.assertTrue(self.board.is_checkmate())
        
        # Check that the evaluation reflects checkmate
        eval_score = evaluate_position(self.board)
        self.assertLess(eval_score, -1000)  # Black should be winning by a large margin
    
    def test_stalemate_detection(self):
        """Test that stalemate positions are evaluated correctly."""
        # A simple stalemate position
        self.board = chess.Board("k7/8/8/8/8/8/8/K7 w - - 0 1")
        
        # Check that the position is recognized as stalemate
        self.assertTrue(self.board.is_stalemate())
        
        # Check that the evaluation reflects stalemate
        eval_score = evaluate_position(self.board)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Stalemate should be a draw
    
    def test_insufficient_material(self):
        """Test that insufficient material positions are evaluated correctly."""
        # King vs King position
        self.board = chess.Board("k7/8/8/8/8/8/8/K7 w - - 0 1")
        
        # Check that the position is recognized as insufficient material
        self.assertTrue(self.board.is_insufficient_material())
        
        # Check that the evaluation reflects insufficient material
        eval_score = evaluate_position(self.board)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Insufficient material should be a draw

if __name__ == '__main__':
    unittest.main()
