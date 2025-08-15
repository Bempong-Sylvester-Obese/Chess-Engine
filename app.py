from flask import Flask, render_template, request, jsonify, send_from_directory
import chess
import os
import sys

# Add the Engine directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'Engine'))

from chess_suggester import ChessSuggester

app = Flask(__name__, 
           static_folder='UI/chesswebapp/static',
           template_folder='UI/chesswebapp/templates')

# Initialize board and chess suggester
board = chess.Board()
chess_suggester = ChessSuggester()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-static')
def test_static():
    static_path = os.path.join(os.getcwd(), 'UI', 'chesswebapp', 'static')
    return f"Static folder path: {static_path}<br>Exists: {os.path.exists(static_path)}"

@app.route('/move', methods=['POST'])
def move():
    global board
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        move_uci = request.json.get('move')
        if not move_uci:
            return jsonify({'status': 'error', 'message': 'No move provided'}), 400
        
        # Validate UCI format
        if len(move_uci) != 4:
            return jsonify({'status': 'error', 'message': 'Invalid move format'}), 400
        
        move = chess.Move.from_uci(move_uci)

        if move in board.legal_moves:
            board.push(move)
            return jsonify({'status': 'ok', 'fen': board.fen()})
        else:
            return jsonify({'status': 'illegal'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    global board
    try:
        board.reset()
        return jsonify({'status': 'reset', 'fen': board.fen()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/suggest', methods=['POST'])
def suggest_moves():
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        fen = request.json.get('fen', board.fen())
        
        # Create a temporary board with the given position
        temp_board = chess.Board(fen)
        
        # Get move suggestions
        suggestions = chess_suggester.get_move_suggestions(temp_board)
        
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_position():
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        fen = request.json.get('fen', board.fen())
        
        # Create a temporary board with the given position
        temp_board = chess.Board(fen)
        
        # Get position analysis
        analysis = chess_suggester.get_move_suggestions(temp_board)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/position', methods=['GET'])
def get_position():
    """Get current board position"""
    try:
        return jsonify({
            'fen': board.fen(),
            'is_check': board.is_check(),
            'is_checkmate': board.is_checkmate(),
            'is_stalemate': board.is_stalemate(),
            'is_insufficient_material': board.is_insufficient_material(),
            'turn': 'white' if board.turn else 'black'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    # Use a more efficient configuration for development
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
