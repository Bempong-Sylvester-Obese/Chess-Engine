#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_piece_image(piece_type, color, size=50):
    """Create a simple chess piece image."""
    # Create a new image with transparency
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