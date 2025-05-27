#!/opt/homebrew/lib python3

import tkinter as tk
from tkinter import ttk, messagebox
import chess
from PIL import Image, ImageTk
import os
from Engine.board import Board
from Engine.evaluation import evaluate_position, get_best_move
from API.endpoints import router

class ChessGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Chess Engine")
        
        # Initialize game state
        self.board = Board()
        self.selected_square = None
        self.valid_moves = []
        
        # Create main frame
        self.main_frame = ttk.Frame(root, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Create board canvas
        self.canvas = tk.Canvas(self.main_frame, width=400, height=400)
        self.canvas.grid(row=0, column=0, padx=5, pady=5)
        
        # Create control panel
        self.control_frame = ttk.Frame(self.main_frame)
        self.control_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.N)
        
        # Add buttons
        ttk.Button(self.control_frame, text="New Game", command=self.new_game).pack(pady=5)
        ttk.Button(self.control_frame, text="Undo Move", command=self.undo_move).pack(pady=5)
        ttk.Button(self.control_frame, text="Get Best Move", command=self.show_best_move).pack(pady=5)
        
        # Add evaluation label
        self.eval_label = ttk.Label(self.control_frame, text="Evaluation: 0.0")
        self.eval_label.pack(pady=5)
        
        # Load piece images
        self.piece_images = {}
        self.load_pieces()
        
        # Bind canvas events
        self.canvas.bind("<Button-1>", self.handle_click)
        
        # Draw initial board
        self.draw_board()
        
    def load_pieces(self):
        """Load chess piece images."""
        piece_mapping = {
            'p': 'bP', 'r': 'bR', 'n': 'bN', 'b': 'bB', 'q': 'bQ', 'k': 'bK',
            'P': 'wP', 'R': 'wR', 'N': 'wN', 'B': 'wB', 'Q': 'wQ', 'K': 'wK'
        }
        for piece, filename in piece_mapping.items():
            try:
                image = Image.open(f"assets/pieces/{filename}.png")
                image = image.resize((50, 50), Image.Resampling.LANCZOS)
                self.piece_images[piece] = ImageTk.PhotoImage(image)
            except Exception as e:
                print(f"Error loading piece image {piece}: {e}")
                # Create a simple colored rectangle as fallback
                img = Image.new('RGB', (50, 50), 'white' if piece.isupper() else 'black')
                self.piece_images[piece] = ImageTk.PhotoImage(img)
                
    def draw_board(self):
        """Draw the chess board and pieces."""
        self.canvas.delete("all")
        
        # Draw squares
        for row in range(8):
            for col in range(8):
                x1, y1 = col * 50, row * 50
                x2, y2 = x1 + 50, y1 + 50
                color = "#DDB88C" if (row + col) % 2 == 0 else "#A66D4F"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="")
                
        # Draw pieces
        for square in chess.SQUARES:
            piece = self.board.get_piece_at(square)
            if piece:
                file_idx = chess.square_file(square)
                rank_idx = 7 - chess.square_rank(square)
                x = file_idx * 50
                y = rank_idx * 50
                piece_char = piece.symbol()
                if piece_char in self.piece_images:
                    self.canvas.create_image(x, y, image=self.piece_images[piece_char], anchor=tk.NW)
                    
        # Highlight selected square and valid moves
        if self.selected_square is not None:
            file_idx = chess.square_file(self.selected_square)
            rank_idx = 7 - chess.square_rank(self.selected_square)
            x1, y1 = file_idx * 50, rank_idx * 50
            x2, y2 = x1 + 50, y1 + 50
            self.canvas.create_rectangle(x1, y1, x2, y2, outline="yellow", width=2)
            
            for move in self.valid_moves:
                file_idx = chess.square_file(move.to_square)
                rank_idx = 7 - chess.square_rank(move.to_square)
                x1, y1 = file_idx * 50, rank_idx * 50
                x2, y2 = x1 + 50, y1 + 50
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="green", width=2)
                
    def handle_click(self, event):
        """Handle mouse clicks on the board."""
        if self.board.is_game_over():
            return
            
        # Convert canvas coordinates to chess square
        file_idx = event.x // 50
        rank_idx = 7 - (event.y // 50)
        square = chess.square(file_idx, rank_idx)
        
        # If a square is already selected
        if self.selected_square is not None:
            # Try to make a move
            move = chess.Move(self.selected_square, square)
            if move in self.valid_moves:
                self.board.make_move(move)
                self.selected_square = None
                self.valid_moves = []
                self.draw_board()
                self.update_evaluation()
                
                # Check for game over
                if self.board.is_game_over():
                    result = self.board.get_game_result()
                    messagebox.showinfo("Game Over", f"Game Over: {result}")
            else:
                # Select new square if it has a piece of the current player's color
                piece = self.board.get_piece_at(square)
                if piece and piece.color == self.board.get_turn():
                    self.selected_square = square
                    self.valid_moves = self.board.get_legal_moves()
                else:
                    self.selected_square = None
                    self.valid_moves = []
        else:
            # Select square if it has a piece of the current player's color
            piece = self.board.get_piece_at(square)
            if piece and piece.color == self.board.get_turn():
                self.selected_square = square
                self.valid_moves = self.board.get_legal_moves()
                
        self.draw_board()
        
    def new_game(self):
        """Start a new game."""
        self.board = Board()
        self.selected_square = None
        self.valid_moves = []
        self.draw_board()
        self.update_evaluation()
        
    def undo_move(self):
        """Undo the last move."""
        if self.board.undo_move():
            self.selected_square = None
            self.valid_moves = []
            self.draw_board()
            self.update_evaluation()
            
    def show_best_move(self):
        """Show the best move in the current position."""
        if not self.board.is_game_over():
            move, score = self.board.get_best_move()
            messagebox.showinfo("Best Move", f"Best move: {move.uci()}\nEvaluation: {score:+.2f}")
            
    def update_evaluation(self):
        """Update the position evaluation display."""
        eval_score = self.board.get_evaluation()
        self.eval_label.config(text=f"Evaluation: {eval_score:+.2f}")

def main():
    root = tk.Tk()
    app = ChessGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
