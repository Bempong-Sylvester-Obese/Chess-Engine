import chess
import chess.engine
import unittest

class TestBlunderDetection(unittest.TestCase):
    def setUp(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        self.threshold = -1.0  # Consider it a blunder if eval drops by 1.0 pawns or more

    def tearDown(self):
        self.engine.quit()

    def is_blunder(self, board, move):
        """Check if a move is a blunder using Stockfish evaluation."""
        # Evaluate position before move
        info_before = self.engine.analyse(board, chess.engine.Limit(time=0.5))
        score_before = info_before["score"].white().score(mate_score=10000)
        
        # Make the move and evaluate after
        board.push(move)
        info_after = self.engine.analyse(board, chess.engine.Limit(time=0.5))
        score_after = info_after["score"].white().score(mate_score=10000)
        board.pop()  # Undo move

        if score_before is None or score_after is None:
            return False  # Couldn't evaluate properly

        return (score_after - score_before) < self.threshold

    def test_blunder_move(self):
        """Test that a known blunder is detected."""
        board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
        blunder_move = chess.Move.from_uci("f1c4")  # Bc4 hangs the bishop to ...Nxe4
        self.assertTrue(self.is_blunder(board, blunder_move))

    def test_good_move(self):
        """Test that a strong move isn't flagged as a blunder."""
        board = chess.Board("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
        good_move = chess.Move.from_uci("d2d4")  # Central pawn push
        self.assertFalse(self.is_blunder(board, good_move))

if __name__ == "__main__":
    unittest.main()