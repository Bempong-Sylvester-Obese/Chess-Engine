import chess
import pygame
import sys
import os
from typing import Optional, List, Tuple, cast, Literal
from PIL import Image, ImageDraw
import pathlib

sys.path.append(os.path.join(os.path.dirname(__file__), 'Engine'))

from Engine.enhanced_engine import EnhancedChessSuggester
from Engine.chess_suggester import ChessSuggester

class ChessGame:
    def __init__(self):
        self.board = chess.Board()
        self.screen_size = (1000, 800)  # Increased width to accommodate analysis panel
        self.square_size = 700 // 8  # Chess board is 700x700
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode(self.screen_size)
        pygame.display.set_caption("Chess Engine with Real-time Analysis")
        
        # Initialize fonts for analysis display
        self.font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 18)
        self.large_font = pygame.font.Font(None, 32)
        
        # Load chess piece images
        self.pieces = {}
        self.load_pieces()
        
        # Initialize chess engines for analysis
        self.enhanced_engine = EnhancedChessSuggester()
        self.basic_engine = ChessSuggester()
        
        # Game state
        self.selected_square = None
        self.valid_moves = []
        self.move_history = []
        self.analysis_data = None
        
        # Analysis panel dimensions
        self.analysis_panel_x = 720
        self.analysis_panel_width = 280
        
        # Update analysis on initialization
        self.update_analysis()
        
    def load_pieces(self):
        piece_image_map = {
            'P': 'wP.png', 'N': 'wN.png', 'B': 'wB.png', 'R': 'wR.png', 'Q': 'wQ.png', 'K': 'wK.png',
            'p': 'bP.png', 'n': 'bN.png', 'b': 'bB.png', 'r': 'bR.png', 'q': 'bQ.png', 'k': 'bK.png',
        }
        # Use the Wikipedia set from chessboardjs-1
        base_path = pathlib.Path(__file__).parent / 'UI' / 'chesswebapp' / 'static' / 'chessboardjs-1' / 'img' / 'chesspieces' / 'wikipedia'
        for symbol, filename in piece_image_map.items():
            try:
                image_path = (base_path / filename).resolve()
                print(f"Trying to load: {image_path}")  # Debug print
                image = pygame.image.load(str(image_path))
                image = pygame.transform.smoothscale(image, (self.square_size, self.square_size))
                self.pieces[symbol] = image
            except Exception as e:
                print(f"Error loading image {symbol} from {image_path}: {e}")
                self.pieces[symbol] = pygame.Surface((self.square_size, self.square_size), pygame.SRCALPHA)
    
    def update_analysis(self):
        try:
            self.analysis_data = self.enhanced_engine.get_move_suggestions(self.board)
        except Exception as e:
            print(f"Error updating analysis: {e}")
            # Fallback to basic engine
            self.analysis_data = self.basic_engine.get_move_suggestions(self.board)
    
    def get_square_from_pos(self, pos: Tuple[int, int]) -> Optional[int]:
        x, y = pos
        # Only process clicks within the chess board area
        if x >= self.square_size * 8:
            return None
            
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
                    symbol = piece.symbol()
                    piece_surface = self.pieces.get(symbol)
                    if piece_surface:
                        self.screen.blit(piece_surface, (col * self.square_size, row * self.square_size))
        
        # Highlight selected square
        if self.selected_square is not None:
            self.highlight_square(self.selected_square, (255, 255, 0, 128))  # Yellow highlight
            
            # Highlight valid moves
            for move in self.valid_moves:
                self.highlight_square(move.to_square, (0, 255, 0, 128))  # Green highlight
    
    def draw_right_panel(self):
        # Draw right panel background
        panel_x = self.square_size * 8
        panel_width = self.screen_size[0] - panel_x
        pygame.draw.rect(self.screen, (40, 40, 40), (panel_x, 0, panel_width, self.screen_size[1]))

        y_offset = 30
        # Draw avatar placeholder (circle with initials)
        avatar_center = (panel_x + panel_width // 2, y_offset + 40)
        pygame.draw.circle(self.screen, (200, 150, 100), avatar_center, 40)
        initials = self.large_font.render('P', True, (255, 255, 255))
        initials_rect = initials.get_rect(center=avatar_center)
        self.screen.blit(initials, initials_rect)
        y_offset += 90

        # Draw evaluation bar below avatar
        bar_x = panel_x + panel_width // 2 - 10
        bar_y = y_offset
        bar_width = 20
        bar_height = 200
        # Clamp evaluation to range for visualization
        eval_score = self.analysis_data['current_evaluation'] if self.analysis_data else 0
        capped_eval = max(min(eval_score, 5), -5)  # Range: -5 (Black) to +5 (White)
        white_ratio = (capped_eval + 5) / 10  # 0 (all black) to 1 (all white)
        white_height = int(bar_height * white_ratio)
        black_height = bar_height - white_height
        # Draw white part (top)
        pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, white_height))
        # Draw black part (bottom)
        pygame.draw.rect(self.screen, (0, 0, 0), (bar_x, bar_y + white_height, bar_width, black_height))
        # Draw border
        pygame.draw.rect(self.screen, (200, 200, 200), (bar_x, bar_y, bar_width, bar_height), 2)
        # Draw W/B labels
        w_label = self.small_font.render('W', True, (255, 255, 255))
        b_label = self.small_font.render('B', True, (0, 0, 0))
        self.screen.blit(w_label, (bar_x + bar_width + 5, bar_y - 5))
        self.screen.blit(b_label, (bar_x + bar_width + 5, bar_y + bar_height - 15))
        y_offset += bar_height + 30

        # Draw move list header
        header = self.font.render(' ', True, (255, 255, 255))
        self.screen.blit(header, (panel_x + 30, y_offset))
        y_offset += 10

        # Draw move list in two columns
        moves = self.move_history
        col1_x = panel_x + 30
        col2_x = panel_x + panel_width // 2
        row_height = 32
        for i in range(0, len(moves), 2):
            move_num = (i // 2) + 1
            move1 = moves[i].uci() if i < len(moves) else ''
            move2 = moves[i+1].uci() if i+1 < len(moves) else ''
            # Highlight last move
            highlight = (i == len(moves)-2) or (i+1 == len(moves)-1)
            font1 = self.large_font if highlight and i == len(moves)-2 else self.font
            font2 = self.large_font if highlight and i+1 == len(moves)-1 else self.font
            move_num_text = self.small_font.render(f'{move_num}.', True, (180, 180, 180))
            self.screen.blit(move_num_text, (col1_x - 25, y_offset + (i//2)*row_height))
            move1_text = font1.render(move1, True, (255, 255, 255))
            self.screen.blit(move1_text, (col1_x, y_offset + (i//2)*row_height))
            move2_text = font2.render(move2, True, (255, 255, 255))
            self.screen.blit(move2_text, (col2_x, y_offset + (i//2)*row_height))

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
                    
                    # Update analysis after move
                    self.update_analysis()
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
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:  # Reset game with 'R' key
                        self.board = chess.Board()
                        self.selected_square = None
                        self.valid_moves = []
                        self.move_history = []
                        self.update_analysis()
                    elif event.key == pygame.K_u:  # Undo move with 'U' key
                        if self.move_history:
                            self.board.pop()
                            self.move_history.pop()
                            self.selected_square = None
                            self.valid_moves = []
                            self.update_analysis()
            
            # Clear screen
            self.screen.fill((30, 30, 30))
            
            # Draw the current state
            self.draw_board()
            self.draw_right_panel()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
