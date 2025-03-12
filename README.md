# Bempong Chess Engine

## Overview
Bempong Chess Engine is a Python-based chess engine that evaluates positions, suggests moves, detects blunders, and provides feedback to help beginners and intermediate players improve their game. The engine integrates with Stockfish and uses machine learning for predictive analysis of move efficiency.

## Features
- **Move Evaluation:** Uses Stockfish to analyze the board position.
- **Blunder Detection:** Identifies poor moves and suggests improvements.
- **Move Suggestion:** Recommends the best move based on the current position.
- **Teaching Mode:** Provides feedback on player moves.
- **Graphical Analysis:** Visualizes move efficiency and future predictions.

## Installation
### Prerequisites
- Python 3.7+
- Stockfish chess engine
- Required Python packages:
  ```bash
  pip install numpy matplotlib scikit-learn python-chess
  ```

## Usage
### Initialize the Engine
```python
from bempong_chess_engine import ChessEngine

engine = ChessEngine("path/to/stockfish")
```

### Make a Move
```python
engine.play_move("e2e4")
```

### Visualize Move Efficiency
```python
move_scores = [0.1, 0.3, -0.5, 0.8]
engine.visualize_move_efficiency(move_scores)
```

### Predict Move Outcomes
```python
engine.predict_move_outcomes(move_scores)
```

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License.

