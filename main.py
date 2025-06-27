import chess
import pygame
import sys
from typing import Optional, List, Tuple, cast, Literal
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
        
        # Game state
        self.selected_square = None
        self.valid_moves = []
        self.move_history = []
        
    def create_piece_image(self, color: str, piece_type: str) -> pygame.Surface:
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
        valid_modes = {'P', 'RGB', 'RGBX', 'RGBA', 'ARGB', 'BGRA'}
        mode = image.mode if image.mode in valid_modes else 'RGBA'
        size = image.size
        data = image.tobytes()
        py_image = pygame.image.fromstring(data, size, cast(Literal['P', 'RGB', 'RGBX', 'RGBA', 'ARGB', 'BGRA'], mode))
        return py_image
        
    def load_pieces(self):
        for color in ['w', 'b']:
            for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
                self.pieces[f"{color}{piece}"] = self.create_piece_image(color, piece)
    
    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        file_idx = x // self.square_size
        rank_idx = 7 - (y // self.square_size)  # Flip because chess ranks are bottom-to-top
        
        if 0 <= file_idx < 8 and 0 <= rank_idx < 8:
            return chess.square(file_idx, rank_idx)
        return None
    
    def get_valid_moves(self, square: int) -> List[chess.Move]:
        valid_moves = []
        for move in self.board.legal_moves:
            if move.from_square == square:
                valid_moves.append(move)
        return valid_moves
    
    def highlight_square(self, square: int, color: Tuple[int, int, int, int] = (255, 255, 0, 128)):
        file_idx = chess.square_file(square)
        rank_idx = 7 - chess.square_rank(square)  # Flip because chess ranks are bottom-to-top
        
        # Create a semi-transparent surface for highlighting
        highlight = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
        pygame.draw.rect(highlight, color, highlight.get_rect())
        
        # Draw the highlight
        self.screen.blit(highlight, (file_idx * self.square_size, rank_idx * self.square_size))
        
    def draw_board(self):
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
        
        # Highlight selected square
        if self.selected_square is not None:
            self.highlight_square(self.selected_square, (255, 255, 0, 128))  # Yellow highlight
            
            # Highlight valid moves
            for move in self.valid_moves:
                self.highlight_square(move.to_square, (0, 255, 0, 128))  # Green highlight
                
    def handle_click(self, pos: tuple[int, int]) -> Optional[chess.Move]:
        square = self.get_square_from_pos(pos)
        if square is None:
            return None
            
        # If a square is already selected
        if self.selected_square is not None:
            # Check if the clicked square is a valid move
            for move in self.valid_moves:
                if move.to_square == square:
                    # Make the move
                    self.board.push(move)
                    self.move_history.append(move)
                    
                    # Reset selection
                    self.selected_square = None
                    self.valid_moves = []
                    return move
                    
            # If clicked on a different piece of the same color, select that piece instead
            piece = self.board.piece_at(square)
            if piece and piece.color == self.board.turn:
                self.selected_square = square
                self.valid_moves = self.get_valid_moves(square)
                return None
                
            # If clicked elsewhere, deselect
            self.selected_square = None
            self.valid_moves = []
            return None
            
        # If no square is selected, select the clicked square if it has a piece of the current player's color
        piece = self.board.piece_at(square)
        if piece and piece.color == self.board.turn:
            self.selected_square = square
            self.valid_moves = self.get_valid_moves(square)
            
        return None
        
    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_click(event.pos)
            
            # Draw the current state
            self.draw_board()
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
