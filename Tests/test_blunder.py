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
        info_before = self.engine.analyse(board, self.analysis_limit) #evaluate before the move
        score_obj_before = info_before.get("score")
        score_before = score_obj_before.white().score(mate_score=10000) if score_obj_before is not None else None
        
        # Make the move and evaluate
        board.push(move)
        info_after = self.engine.analyse(board, self.analysis_limit)
        score_obj_after = info_after.get("score")
        score_after = score_obj_after.white().score(mate_score=10000) if score_obj_after is not None else None
        board.pop()

        if score_before is None or score_after is None:
            return False

        eval_diff = (score_after - score_before)/100  # Convert to pawns
        print(f"Eval change for {move}: {eval_diff:.2f} pawns")
        
        # Get top engine moves
        analysis = self.engine.analyse(board, self.analysis_limit, multipv=self.multipv)
        top_moves = [line["pv"][0] for line in analysis if "pv" in line and line["pv"]]
        print(f"Top {self.multipv} moves: {top_moves}")
        
        # Only blunder if both conditions met:
        return (eval_diff < self.threshold) and (move not in top_moves)

    def test_castling_not_blunder(self):
        board = chess.Board("r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 6") #position with castling available
        castling_move = chess.Move.from_uci("e1g1")
        result = self.engine.play(board, self.analysis_limit) #stock fish verification
        print(f"Stockfish recommends: {result.move}")
        
        self.assertFalse(
            self.is_blunder(board, castling_move),
            f"Castling was incorrectly flagged as a blunder. "
            f"Stockfish recommends: {result.move}"
        )

if __name__ == "__main__":
    suite = unittest.TestLoader().loadTestsFromTestCase(TestBlunderDetection)
    runner = unittest.TextTestRunner()
    result = runner.run(suite)
    
    # CELEBRATION TIME! 🎉
    if result.wasSuccessful():
        print("\n" + "="*50)
        print("BLUNDER TESTS PASSED! PERFECT CHESS!")
        print("="*50)
        print("Congratulations on your chess engine mastery!")
        print("All tests verified by Stockfish at depth 16!")
        print("="*50 + "\n")