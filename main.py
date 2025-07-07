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
    
    def draw_analysis_panel(self):
        if not self.analysis_data:
            return
            
        # Draw background for analysis panel
        pygame.draw.rect(self.screen, (50, 50, 50), 
                        (self.analysis_panel_x, 0, self.analysis_panel_width, self.screen_size[1]))
        
        y_offset = 20
        
        # Title
        title_text = self.large_font.render("Position Analysis", True, (255, 255, 255))
        self.screen.blit(title_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 40
        
        # Draw evaluation bar
        # Bar dimensions
        bar_x = self.analysis_panel_x + self.analysis_panel_width - 40
        bar_y = 70
        bar_width = 20
        bar_height = 200
        
        # Clamp evaluation to range for visualization
        eval_score = self.analysis_data['current_evaluation']
        capped_eval = max(min(eval_score, 5), -5)  # Range: -5 (Black) to +5 (White)
        # Calculate white portion (from top)
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
        
        # Current evaluation
        eval_score = self.analysis_data['current_evaluation']
        eval_color = (0, 255, 0) if eval_score > 0 else (255, 0, 0) if eval_score < 0 else (255, 255, 255)
        eval_text = self.font.render(f"Evaluation: {eval_score:+.2f}", True, eval_color)
        self.screen.blit(eval_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 30
        
        # Position assessment
        if abs(eval_score) > 3.0:
            assessment = "White is winning" if eval_score > 0 else "Black is winning"
        elif abs(eval_score) > 1.0:
            assessment = "White is better" if eval_score > 0 else "Black is better"
        else:
            assessment = "Equal position"
        
        assessment_text = self.font.render(assessment, True, (255, 255, 255))
        self.screen.blit(assessment_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 40
        
        # Game status
        status_text = self.font.render("Game Status:", True, (255, 255, 255))
        self.screen.blit(status_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 25
        
        if self.analysis_data['is_checkmate']:
            status = "Checkmate!"
            status_color = (255, 0, 0)
        elif self.analysis_data['is_stalemate']:
            status = "Stalemate"
            status_color = (255, 165, 0)
        elif self.analysis_data['is_check']:
            status = "Check"
            status_color = (255, 255, 0)
        elif self.analysis_data['is_insufficient_material']:
            status = "Insufficient Material"
            status_color = (128, 128, 128)
        else:
            status = "Normal"
            status_color = (0, 255, 0)
        
        status_text = self.font.render(status, True, status_color)
        self.screen.blit(status_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 40
        
        # Move suggestions
        suggestions_text = self.font.render("Top Moves:", True, (255, 255, 255))
        self.screen.blit(suggestions_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 25
        
        for i, move_data in enumerate(self.analysis_data['suggested_moves'][:3]):
            move_text = f"{i+1}. {move_data['san']}"
            move_color = (0, 255, 0) if move_data['evaluation'] > 0 else (255, 0, 0) if move_data['evaluation'] < 0 else (255, 255, 255)
            move_surface = self.small_font.render(move_text, True, move_color)
            self.screen.blit(move_surface, (self.analysis_panel_x + 10, y_offset))
            y_offset += 20
            
            eval_text = f"   {move_data['evaluation']:+.2f}"
            eval_surface = self.small_font.render(eval_text, True, (200, 200, 200))
            self.screen.blit(eval_surface, (self.analysis_panel_x + 10, y_offset))
            y_offset += 25
        
        # Move history
        y_offset += 20
        history_text = self.font.render("Move History:", True, (255, 255, 255))
        self.screen.blit(history_text, (self.analysis_panel_x + 10, y_offset))
        y_offset += 25
        
        # Show last 5 moves
        recent_moves = self.move_history[-10:]  # Last 10 moves
        for i in range(0, len(recent_moves), 2):
            move_num = (i // 2) + 1
            move_text = f"{move_num}. {recent_moves[i].uci()}"
            if i + 1 < len(recent_moves):
                move_text += f" {recent_moves[i+1].uci()}"
            
            move_surface = self.small_font.render(move_text, True, (200, 200, 200))
            self.screen.blit(move_surface, (self.analysis_panel_x + 10, y_offset))
            y_offset += 20
            
            if y_offset > self.screen_size[1] - 100:  # Don't overflow
                break
                
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
            self.draw_analysis_panel()
            
            pygame.display.flip()
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = ChessGame()
    game.run()
