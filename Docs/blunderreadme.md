# Chess Engine Blunder Detection

This module provides blunder detection capabilities for chess engines. It can identify potential blunders (serious mistakes) in chess positions and suggest better moves.

## Features

- Detect blunders in chess positions
- Evaluate positions using a chess engine (like Stockfish) or simple heuristics
- Find better alternative moves when a blunder is detected
- Analyze positions for various game states (check, checkmate, stalemate, etc.)
- Integrate with existing chess applications

## Requirements

- Python 3.6+
- [python-chess](https://python-chess.readthedocs.io/) library
- (Optional) A UCI chess engine like [Stockfish](https://stockfishchess.org/download/)

## Installation

1. Make sure you have Python 3.6+ installed
2. Install the required dependencies:

```bash
pip install python-chess
```

3. (Optional) Install Stockfish:
   - Download from [Stockfish website](https://stockfishchess.org/download/)
   - Add it to your system PATH or specify the path when initializing the BlunderDetector


### Basic Usage

```python
import chess
from blunder_detection import BlunderDetector

# Create a chess board
board = chess.Board()

# Create a blunder detector (without an engine)
detector = BlunderDetector()

# Or with a chess engine
# detector = BlunderDetector(engine_path="/path/to/stockfish")

# Analyze a position
analysis = detector.analyze_position(board)
print(analysis)

# Check if a specific move is a blunder
move = chess.Move.from_uci("e2e4")
is_blunder, eval_before, eval_after = detector.is_blunder(board, move)
print(f"Is blunder: {is_blunder}")
print(f"Evaluation before: {eval_before}")
print(f"Evaluation after: {eval_after}")

# Find better moves
better_moves = detector.find_better_moves(board, move)
print(better_moves)
```

### Integration Example

See `blunder_integration.py` for an example of how to integrate blunder detection with a chess game.

```python
from blunder_integration import ChessGameWithBlunderDetection

# Create a game with blunder detection
game = ChessGameWithBlunderDetection(engine_path="/path/to/stockfish")

# Make a move and check for blunders
move = chess.Move.from_uci("e2e4")
result = game.make_move(move)

if result["is_blunder"]:
    print("Blunder detected!")
    print(f"Better moves: {result['better_moves']}")

# Get the current analysis
analysis = game.get_current_analysis()
print(analysis)
```

### Example Script

Run the example script to see blunder detection in action:

```bash
python test_blunder.py
```

## How It Works

The blunder detection works by:

1. Evaluating the current position
2. Evaluating the position after a potential move
3. Comparing the evaluations to determine if the move is a blunder
4. Finding better alternative moves if a blunder is detected

When a chess engine is available, it uses the engine for evaluation. Otherwise, it falls back to a simple material and positional evaluation.

## Customization

You can customize the blunder detection by:

- Adjusting the evaluation threshold (default: -2.0)
- Using a different chess engine
- Implementing your own evaluation function

## License

This module is part of the Chess Engine project and is subject to the same license terms.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. 