import chess
import chess.engine
import unittest

class TestBlunderDetection(unittest.TestCase):
    def setUp(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        self.threshold = -3.0  # Only flag drops >3 pawns as blunders
        self.analysis_limit = chess.engine.Limit(depth=16)
        self.multipv = 5  # Check against top 5 moves

    def tearDown(self):
        self.engine.quit()

    def is_blunder(self, board, move):
        """Ultra-reliable blunder detection"""
        # Get evaluation before move
        info_before = self.engine.analyse(board, self.analysis_limit)
        score_before = info_before["score"].white().score(mate_score=10000)
        
        # Make the move and evaluate
        board.push(move)
        info_after = self.engine.analyse(board, self.analysis_limit)
        score_after = info_after["score"].white().score(mate_score=10000)
        board.pop()

        if None in (score_before, score_after):
            return False

        eval_diff = (score_after - score_before)/100  # Convert to pawns
        print(f"Eval change for {move}: {eval_diff:.2f} pawns")
        
        # Get top engine moves
        analysis = self.engine.analyse(board, self.analysis_limit, multipv=self.multipv)
        top_moves = [line["pv"][0] for line in analysis]
        print(f"Top {self.multipv} moves: {top_moves}")
        
        # Only blunder if both conditions met:
        return (eval_diff < self.threshold) and (move not in top_moves)

    def test_castling_not_blunder(self):
        """Test that castling is never flagged as a blunder"""
        # Position where castling is clearly best
        board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 6")
        castling_move = chess.Move.from_uci("e1g1")
        
        # Verify with Stockfish
        result = self.engine.play(board, self.analysis_limit)
        print(f"Stockfish recommends: {result.move}")
        
        self.assertFalse(
            self.is_blunder(board, castling_move),
            f"Castling was incorrectly flagged as a blunder. "
            f"Stockfish recommends: {result.move}"
        )

if __name__ == "__main__":
    # Create test suite and add celebration
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBlunderDetection)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    # CELEBRATION TIME! 🎉
    if result.wasSuccessful():
        print("\n" + "="*50)
        print("🎉🎉🎉 BLUNDER TESTS PASSED! PERFECT CHESS! 🎉🎉🎉")
        print("="*50)
        print("   Congratulations on your chess engine mastery!")
        print("   All tests verified by Stockfish at depth 16!")
        print("="*50 + "\n")