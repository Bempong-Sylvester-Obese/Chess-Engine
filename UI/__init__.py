"""
Chess Engine UI Package

This package provides user interface implementations, including:
- Command-line interface (CLI)
- Graphical user interface (GUI)
- Web-based interface
"""

from .cli import ChessCLI
from .gui import ChessGUI

__all__ = ['ChessCLI', 'ChessGUI'] 