# Chess Engine

A sophisticated chess engine and game interface built with Python, featuring both GUI and CLI interfaces, position analysis, and blunder detection capabilities.

## Features

- Interactive GUI using Pygame
- Command-line interface for quick games
- Position evaluation and analysis
- Blunder detection system
- Stockfish integration for advanced analysis
- REST API for remote access
- Machine learning-based move suggestions

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/chess-engine.git
cd chess-engine
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install Stockfish (required for analysis):
- On macOS: `brew install stockfish`
- On Ubuntu: `sudo apt-get install stockfish`
- On Windows: Download from [official Stockfish website](https://stockfishchess.org/download/)

## Usage

### GUI Mode
```bash
python main.py
```

### CLI Mode
```bash
python UI/cli.py
```

### API Server
```bash
python API/server.py
```

## Project Structure

- `Engine/`: Core chess engine logic
- `API/`: REST API implementation
- `UI/`: User interfaces (GUI and CLI)
- `Tests/`: Unit tests
- `Data/`: Training data and models
- `Scripts/`: Utility scripts
- `Docs/`: Documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [python-chess](https://github.com/niklasf/python-chess) library
- [Stockfish](https://stockfishchess.org/) chess engine
- All contributors and maintainers 