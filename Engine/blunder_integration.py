#!/usr/bin/env python3

import chess
import sys
import os
from Engine.position_detection import BlunderDetector

class ChessGameWithBlunderDetection:
    """
    An extension of the ChessGame class that includes blunder detection.
    This class demonstrates how to integrate blunder detection into a chess game.
    """
    
    def __init__(self, engine_path=None):
        """
        Initialize the chess game with blunder detection.
        
        Args:
            engine_path: Path to a UCI chess engine (like Stockfish).
        """
        # Create a chess board
        self.board = chess.Board()
        
        # Initialize the blunder detector
        self.blunder_detector = BlunderDetector(engine_path=engine_path)
        
        # Game state
        self.move_history = []
        self.last_analysis = None
    
    def make_move(self, move):
        """
        Make a move and analyze for blunders.
        
        Args:
            move: The chess move to make.
            
        Returns:
            A dictionary containing information about the move and any blunders.
        """
        # Analyze the position before the move
        analysis_before = self.blunder_detector.analyze_position(self.board)
        
        # Check if the move is a blunder
        is_blunder, eval_before, eval_after = self.blunder_detector.is_blunder(self.board, move)
        
        # Make the move
        self.board.push(move)
        self.move_history.append(move)
        
        # Analyze the position after the move
        analysis_after = self.blunder_detector.analyze_position(self.board)
        
        # Prepare the result
        result = {
            "move": move,
            "is_blunder": is_blunder,
            "eval_before": eval_before,
            "eval_after": eval_after,
            "better_moves": []
        }
        
        # If it's a blunder, find better moves
        if is_blunder:
            result["better_moves"] = self.blunder_detector.find_better_moves(self.board, move)
        
        # Store the latest analysis
        self.last_analysis = analysis_after
        
        return result
    
    def undo_last_move(self):
        """Undo the last move made."""
        if self.move_history:
            self.board.pop()
            self.move_history.pop()
            self.last_analysis = self.blunder_detector.analyze_position(self.board)
            return True
        return False
    
    def get_current_analysis(self):
        """Get the analysis of the current position."""
        if self.last_analysis is None:
            self.last_analysis = self.blunder_detector.analyze_position(self.board)
        return self.last_analysis
    
    def print_position(self):
        """Print the current position."""
        print(self.board)
    
    def print_analysis(self, analysis=None):
        """Print the analysis of the current position."""
        if analysis is None:
            analysis = self.get_current_analysis()
        
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
    """Example usage of the ChessGameWithBlunderDetection class."""
    # Path to Stockfish engine (if available)
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
    
    # Create the game
    game = ChessGameWithBlunderDetection(engine_path=engine_path)
    
    # Example game with some moves
    print("=== Starting a new game ===")
    game.print_position()
    game.print_analysis()
    
    # Make some moves
    moves = [
        chess.Move.from_uci("e2e4"),  # White: e4
        chess.Move.from_uci("e7e5"),  # Black: e5
        chess.Move.from_uci("g1f3"),  # White: Nf3
        chess.Move.from_uci("b8c6"),  # Black: Nc6
        chess.Move.from_uci("f1c4"),  # White: Bc4
        chess.Move.from_uci("g8f6"),  # Black: Nf6
        chess.Move.from_uci("d1h5"),  # White: Qh5
    ]
    
    for i, move in enumerate(moves):
        print(f"\n=== Move {i+1} ===")
        if i % 2 == 0:
            print(f"White plays {move}")
        else:
            print(f"Black plays {move}")
        
        result = game.make_move(move)
        game.print_position()
        
        if result["is_blunder"]:
            print("\n!!! BLUNDER DETECTED !!!")
            print(f"Evaluation before: {result['eval_before']:.2f}")
            print(f"Evaluation after: {result['eval_after']:.2f}")
            
            if result["better_moves"]:
                print("Better moves:")
                for move, eval_score in result["better_moves"]:
                    print(f"  {move}: {eval_score:.2f}")
        
        game.print_analysis()
    
    # Demonstrate undoing a move
    print("\n=== Undoing the last move ===")
    if game.undo_last_move():
        game.print_position()
        game.print_analysis()
    
    # Set up a position with a potential blunder
    print("\n=== Setting up a position with a potential blunder ===")
    game.board = chess.Board()
    fen = "r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 0 2"
    game.board.set_fen(fen)
    game.print_position()
    game.print_analysis()

if __name__ == "__main__":
    main() 