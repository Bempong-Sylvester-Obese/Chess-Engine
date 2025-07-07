# BCF Chess Engine

## Overview
BCF Chess Engine is a Python-based chess engine with a graphical interface. It evaluates positions, suggests moves, detects blunders, and provides feedback to help beginners and intermediate players improve their game. The engine integrates machine learning for predictive analysis of move efficiency.

## Features
- **Move Evaluation:** Analyzes the board position using built-in and ML models.
- **Move Suggestion:** Recommends the best move based on the current position.
- **Blunder Detection:** Identifies poor moves and suggests improvements.
- **Graphical Interface:** Play chess with real-time evaluation and move list.

## Installation
### Prerequisites
- Python 3.7+
- [Stockfish chess engine](https://stockfishchess.org/download/)
- Required Python packages (see requirements.txt):
  ```bash
  pip install -r requirements.txt
  ```
- Trained model file: `Data/trained_model.pkl` (should be present; see `train_engine.py` to retrain)
- Chess piece images: Already included in `UI/chesswebapp/static/chessboardjs-1/img/chesspieces/wikipedia/`

## Running the Chess Engine GUI
1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
2. **(Optional) Download and install Stockfish:**
   - Download from [stockfishchess.org](https://stockfishchess.org/download/)
   - Ensure the Stockfish binary is in your PATH if you want to use Stockfish-based features.
3. **Run the graphical chess engine:**
   ```bash
   python main.py
   ```
   This will launch a Pygame window with the chessboard, evaluation bar, and move list.

## Controls
- **Click** pieces and squares to move.
- **R**: Reset the game
- **U**: Undo last move

## Notes
- The engine uses a trained ML model (`Data/trained_model.pkl`). If missing, retrain using `Scripts/train_engine.py`.
- Chess piece images must remain in their current directory for the GUI to display pieces.

## Advanced/API Usage
If you want to use the engine programmatically (e.g., for analysis or integration), see the Python API in `Engine/` and the example usage in `Engine/enhanced_engine.py`.

## Contributing
Contributions are welcome! Feel free to open issues or submit pull requests.

## License
This project is licensed under the MIT License.

