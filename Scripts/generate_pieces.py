#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_piece_image(piece_type, color, size=50):
    """Create a simple chess piece image with improved design."""
    # Create a new image with transparency
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)
    
    # Set piece colors
    if color == 'w':
        main_color = (240, 240, 240)  # Light gray
        accent_color = (200, 200, 200)  # Darker gray
        highlight_color = (255, 255, 255)  # White
    else:
        main_color = (50, 50, 50)  # Dark gray
        accent_color = (30, 30, 30)  # Darker gray
        highlight_color = (100, 100, 100)  # Light gray
    
    # Draw piece based on type
    if piece_type == 'P':  # Pawn
        # Base
        draw.ellipse([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        draw.ellipse([size//3, size//4, 2*size//3, 2*size//3], fill=main_color)
        # Head
        draw.ellipse([size//3, size//6, 2*size//3, size//3], fill=main_color)
        # Highlight
        draw.ellipse([size//3+2, size//6+2, 2*size//3-2, size//3-2], fill=highlight_color)
        
    elif piece_type == 'R':  # Rook
        # Base
        draw.rectangle([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        draw.rectangle([size//3, size//3, 2*size//3, 2*size//3], fill=main_color)
        # Top
        draw.rectangle([size//4, size//4, 3*size//4, size//3], fill=main_color)
        # Crown
        draw.rectangle([size//3, size//6, 2*size//3, size//4], fill=accent_color)
        # Highlight
        draw.rectangle([size//3+2, size//6+2, 2*size//3-2, size//4-2], fill=highlight_color)
        
    elif piece_type == 'N':  # Knight
        # Base
        draw.ellipse([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        points = [
            (size//4, 3*size//4),  # Bottom left
            (size//2, size//4),    # Top middle
            (3*size//4, 3*size//4),  # Bottom right
            (size//2, size//2)     # Middle
        ]
        draw.polygon(points, fill=main_color)
        # Head
        draw.ellipse([size//3, size//6, 2*size//3, size//3], fill=accent_color)
        # Highlight
        draw.ellipse([size//3+2, size//6+2, 2*size//3-2, size//3-2], fill=highlight_color)
        
    elif piece_type == 'B':  # Bishop
        # Base
        draw.ellipse([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        draw.polygon([
            (size//2, size//4),      # Top
            (3*size//4, 3*size//4),  # Bottom right
            (size//4, 3*size//4)     # Bottom left
        ], fill=main_color)
        # Head
        draw.ellipse([size//3, size//6, 2*size//3, size//3], fill=accent_color)
        # Cross
        draw.rectangle([size//2-3, size//6, size//2+3, size//3], fill=highlight_color)
        draw.rectangle([size//3, size//4-3, 2*size//3, size//4+3], fill=highlight_color)
        
    elif piece_type == 'Q':  # Queen
        # Base
        draw.ellipse([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        draw.ellipse([size//3, size//3, 2*size//3, 2*size//3], fill=main_color)
        # Head
        draw.ellipse([size//3, size//6, 2*size//3, size//3], fill=main_color)
        # Crown
        draw.polygon([
            (size//3, size//6),      # Left
            (size//2, size//8),      # Top middle
            (2*size//3, size//6)     # Right
        ], fill=accent_color)
        # Highlight
        draw.ellipse([size//3+2, size//6+2, 2*size//3-2, size//3-2], fill=highlight_color)
        
    elif piece_type == 'K':  # King
        # Base
        draw.ellipse([size//4, 3*size//4, 3*size//4, size-5], fill=main_color)
        # Body
        draw.ellipse([size//3, size//3, 2*size//3, 2*size//3], fill=main_color)
        # Head
        draw.ellipse([size//3, size//6, 2*size//3, size//3], fill=main_color)
        # Crown
        draw.polygon([
            (size//3, size//6),      # Left
            (size//2, size//8),      # Top middle
            (2*size//3, size//6)     # Right
        ], fill=accent_color)
        # Cross
        draw.rectangle([size//2-3, size//6, size//2+3, size//3], fill=(255, 0, 0))
        draw.rectangle([size//3, size//4-3, 2*size//3, size//4+3], fill=(255, 0, 0))
    
    return image

def generate_all_pieces():
    """Generate all chess piece images."""
    # Create output directory if it doesn't exist
    output_dir = "assets/pieces"
    os.makedirs(output_dir, exist_ok=True)
    
    # Generate pieces for both colors
    for color in ['w', 'b']:
        for piece in ['P', 'R', 'N', 'B', 'Q', 'K']:
            # Create the image
            image = create_piece_image(piece, color)
            
            # Save the image
            filename = f"{color}{piece}.png"
            filepath = os.path.join(output_dir, filename)
            image.save(filepath)
            print(f"Generated {filepath}")

if __name__ == "__main__":
    generate_all_pieces()
    print("All chess piece images generated successfully!") 