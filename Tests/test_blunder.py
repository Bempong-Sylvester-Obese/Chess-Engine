import chess
import chess.engine
import unittest

class TestBlunderDetection(unittest.TestCase):
    def setUp(self):
        self.engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")

    def tearDown(self):
        self.engine.quit()

    def is_blunder(self, board, move, threshold=-2.0):
        # Evaluate before move
        info_before = self.engine.analyse(board, chess.engine.Limit(time=0.1))
        score_before = info_before["score"].white().score(mate_score=10000)

        board.push(move)

        # Evaluate after move
        info_after = self.engine.analyse(board, chess.engine.Limit(time=0.1))
        score_after = info_after["score"].white().score(mate_score=10000)

        board.pop()  # Revert move

        if score_before is None or score_after is None:
            return False  # Can't evaluate properly

        # A blunder is when evaluation drops significantly
        return (score_after - score_before) < threshold

    def test_blunder_move(self):
        board = chess.Board()
        board.set_fen("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
        move = chess.Move.from_uci("f1c4")  # Let's assume this is a blunder

        self.assertTrue(self.is_blunder(board, move), "Should detect as a blunder")

    def test_good_move(self):
        board = chess.Board()
        board.set_fen("r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3")
        move = chess.Move.from_uci("d2d4")  # A strong centralizing move

        self.assertFalse(self.is_blunder(board, move), "Should not detect as a blunder")

if __name__ == "__main__":
    unittest.main()
