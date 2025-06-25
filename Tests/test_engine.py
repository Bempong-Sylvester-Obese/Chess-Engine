#!/usr/bin/env python3
import unittest
import chess
import pandas as pd
import numpy as np
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Engine.chess_suggester import ChessSuggester
from Engine.evaluation import evaluate_position
from Engine.move_suggestion import suggest_moves

class TestChessEngine(unittest.TestCase):
    
    def setUp(self):
        self.board = chess.Board()
        self.suggester = ChessSuggester()
        
        try:
            self.training_data = pd.read_csv('Data/training_data.csv', nrows=100)
        except FileNotFoundError:
            print("Warning: training_data.csv not found. Running tests without training data.")
            self.training_data = None
    
    def test_initial_position(self):
        eval_score = evaluate_position(self.board)
        self.assertIsInstance(eval_score, float)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Initial position should be roughly equal
    
    def test_material_evaluation(self):
        # Test a position with a pawn advantage
        self.board = chess.Board('rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1')
        eval_score = evaluate_position(self.board)
        self.assertGreater(eval_score, 0)  # White should be better
        self.board = chess.Board('rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1') #position with queen advantage
        self.board.remove_piece_at(chess.E4)  # Remove a pawn
        eval_score = evaluate_position(self.board)
        self.assertLess(eval_score, 0)  # Black should be better
    
    def test_move_suggestions(self):
        suggestions = suggest_moves(self.board)
        self.assertIsInstance(suggestions, list)
        self.assertGreater(len(suggestions), 0)
        for move, eval_score, comment in suggestions:
            self.assertIsInstance(move, chess.Move)
            self.assertIsInstance(eval_score, float)
            self.assertIsInstance(comment, str)
    
    def test_chess_suggester(self):
        result = self.suggester.get_move_suggestions(self.board)
        expected_keys = ['current_evaluation', 'is_check', 'is_checkmate', 
                         'is_stalemate', 'is_insufficient_material', 'suggested_moves']
        for key in expected_keys:
            self.assertIn(key, result)
        self.assertIsInstance(result['suggested_moves'], list)
        
        for move_data in result['suggested_moves']:
            self.assertIn('move', move_data)
            self.assertIn('san', move_data)
            self.assertIn('evaluation', move_data)
            self.assertIn('comment', move_data)
    
    def test_training_data_compatibility(self):
        if self.training_data is None:
            self.skipTest("Training data not available")
        
        for _, row in self.training_data.head(5).iterrows():
            try:
                board = chess.Board(row['position_fen'])
                suggestions = suggest_moves(board)
                self.assertGreater(len(suggestions), 0)
                eval_score = evaluate_position(board)
                self.assertIsInstance(eval_score, float)
                suggester_result = self.suggester.get_move_suggestions(board)
                self.assertIn('suggested_moves', suggester_result)
                self.assertGreater(len(suggester_result['suggested_moves']), 0)
            except Exception as e:
                self.fail(f"Failed to process position: {row['position_fen']} - {str(e)}")
    
    def test_checkmate_detection(self):
        self.board = chess.Board() #fool's mate position
        self.board.push_san("f3")
        self.board.push_san("e5")
        self.board.push_san("g4")
        self.board.push_san("Qh4")
        self.assertTrue(self.board.is_checkmate())
        eval_score = evaluate_position(self.board)
        self.assertLess(eval_score, -1000) 
    
    def test_stalemate_detection(self):
        self.board = chess.Board("k7/8/8/8/8/8/8/K7 w - - 0 1") #stalemate position
        self.assertTrue(self.board.is_stalemate())
        eval_score = evaluate_position(self.board)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Stalemate should be a draw
    
    def test_insufficient_material(self):
        self.board = chess.Board("k7/8/8/8/8/8/8/K7 w - - 0 1") #King Vs King position
        self.assertTrue(self.board.is_insufficient_material())
        eval_score = evaluate_position(self.board)
        self.assertAlmostEqual(eval_score, 0.0, places=1)  # Insufficient material=draw

if __name__ == '__main__':
    unittest.main()
