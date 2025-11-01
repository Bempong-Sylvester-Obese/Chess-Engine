import chess

__all__ = ['MoveSuggester']
class MoveSuggester:
    def __init__(self):
        self.material_values = {
            chess.PAWN: 1.0,
            chess.KNIGHT: 3.0,
            chess.BISHOP: 3.0,
            chess.ROOK: 5.0,
            chess.QUEEN: 9.0,
            chess.KING: 100.0
        }
    
    def evaluate_position(self, board):
        if board.is_game_over():
            if board.is_checkmate():
                return -10000.0 if board.turn else 10000.0
            return 0.0
        
        score = 0.0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece is None:
                continue
            value = self.material_values[piece.piece_type]
            if piece.color:
                score += value
            else:
                score -= value
        return score
    
    def suggest_moves(self, board):
        if board.is_game_over():
            return []
        
        moves = []
        for move in board.legal_moves:
            board.push(move)
            eval_score = -self.evaluate_position(board)
            board.pop()
            moves.append((move, eval_score, "Heuristic evaluation"))
        
        moves.sort(key=lambda x: x[1], reverse=True)
        return moves[:5]
    
    def get_move_suggestions(self, board):
        current_eval = self.evaluate_position(board)
        move_suggestions = self.suggest_moves(board)
        
        formatted_suggestions = []
        for move, eval_score, comment in move_suggestions:
            formatted_suggestions.append({
                "move": move.uci(),
                "san": board.san(move),
                "evaluation": eval_score,
                "comment": comment
            })
        
        return {
            "current_evaluation": current_eval,
            "is_check": board.is_check(),
            "is_checkmate": board.is_checkmate(),
            "is_stalemate": board.is_stalemate(),
            "is_insufficient_material": board.is_insufficient_material(),
            "suggested_moves": formatted_suggestions
        }

if __name__ == "__main__":
    board = chess.Board()
    suggester = MoveSuggester()
    suggestions = suggester.get_move_suggestions(board)
    
    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")
    
    print("\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}") 