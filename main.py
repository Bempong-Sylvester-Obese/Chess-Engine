#!/usr/bin/env python3

import chess
import pygame
import sys
from typing import Optional
from PIL import Image, ImageDraw

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.screen_size = (800, 800)
        self.square_size = self.screen_size[0] // 8
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Chess Engine")
        
        # Load chess piece images
        self.pieces = {}
        self.load_pieces()
        
    def create_piece_image(self, color: str, piece_type: str) -> pygame.Surface:
        """Create a simple chess piece image."""
        size = self.square_size
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)
        
        # Set piece color
        piece_color = (255, 255, 255) if color == 'w' else (0, 0, 0)
        
        # Draw piece based on type
        if piece_type == 'P':  # Pawn
            draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], fill=piece_color)
            draw.rectangle([size//3, size//2, 2*size//3, 3*size//4], fill=piece_color)
        elif piece_type == 'R':  # Rook
            draw.rectangle([size//4, size//4, 3*size//4, 3*size//4], fill=piece_color)
            draw.rectangle([size//3, size//6, 2*size//3, size//4], fill=piece_color)
        elif piece_type == 'N':  # Knight
            draw.polygon([(size//4, 3*size//4), (size//2, size//4), 
                         (3*size//4, 3*size//4), (size//2, size//2)], fill=piece_color)
        elif piece_type == 'B':  # Bishop
            draw.polygon([(size//2, size//4), (3*size//4, 3*size//4),
                         (size//4, 3*size//4)], fill=piece_color)
        elif piece_type == 'Q':  # Queen
            draw.ellipse([size//4, size//4, 3*size//4, 3*size//4], fill=piece_color)
            draw.polygon([(size//2, size//6), (3*size//4, size//3),
                         (size//4, size//3)], fill=piece_color)
        elif piece_type == 'K':  # King
            draw.rectangle([size//4, size//4, 3*size//4, 3*size//4], fill=piece_color)
            draw.rectangle([size//3, size//6, 2*size//3, size//4], fill=piece_color)
            draw.rectangle([size//2-5, size//6, size//2+5, size//4], fill=(255, 0, 0))
        
        # Convert PIL image to Pygame surface
        mode = image.mode
        size = image.size
        data = image.tobytes()
        py_image = pygame.image.fromstring(data, size, mode)
        return py_image
        
    def load_pieces(self):
        """Load chess piece images."""
        for color in ['w', 'b']:
            for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
                self.pieces[f"{color}{piece}"] = self.create_piece_image(color, piece)
        
    def draw_board(self):
        """Draw the chess board."""
        for row in range(8):
            for col in range(8):
                # Calculate square color
                color = (240, 217, 181) if (row + col) % 2 == 0 else (181, 136, 99)
                
                # Draw square
                pygame.draw.rect(
                    self.screen,
                    color,
                    (col * self.square_size, row * self.square_size, 
                     self.square_size, self.square_size)
                )
                
                # Draw piece if present
                square = chess.square(col, 7-row)  # Flip row because chess ranks are bottom-to-top
                piece = self.board.piece_at(square)
                if piece:
                    piece_key = f"{'w' if piece.color else 'b'}{piece.symbol().upper()}"
                    piece_surface = self.pieces[piece_key]
                    self.screen.blit(piece_surface, 
                                   (col * self.square_size, row * self.square_size))
                
    def handle_click(self, pos: tuple[int, int]) -> Optional[chess.Move]:
        """Handle mouse clicks and return a move if valid."""
        x, y = pos
        file_idx = x // self.square_size
        rank_idx = 7 - (y // self.square_size)  # Flip because chess ranks are bottom-to-top
        
        if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
            square = chess.square(file_idx, rank_idx)
            # TODO: Implement move selection logic
            return None
        return None
        
    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    move = self.handle_click(event.pos)
                    if move and move in self.board.legal_moves:
                        self.board.push(move)
            
            # Draw the current state
            self.draw_board()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
