import chess
from move_suggestion import MoveSuggester

def main():
    # Create a chess board
    board = chess.Board()
    
    # Create the move suggester
    suggester = MoveSuggester()
    
    # Get move suggestions
    suggestions = suggester.get_move_suggestions(board)
    
    # Print the suggestions
    print(f"Current evaluation: {suggestions['current_evaluation']:.2f}")
    print(f"Check: {suggestions['is_check']}")
    print(f"Checkmate: {suggestions['is_checkmate']}")
    print(f"Stalemate: {suggestions['is_stalemate']}")
    print(f"Insufficient material: {suggestions['is_insufficient_material']}")
    
    print("\nSuggested moves:")
    for i, move in enumerate(suggestions['suggested_moves'], 1):
        print(f"{i}. {move['san']} (evaluation: {move['evaluation']:.2f}) - {move['comment']}")

if __name__ == "__main__":
    main() 