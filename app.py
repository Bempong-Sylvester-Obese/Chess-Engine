from flask import Flask, render_template, request, jsonify, send_from_directory
import chess
import os
import sys
from Engine.chess_suggester import ChessSuggester

sys.path.append(os.path.join(os.path.dirname(__file__), 'Engine'))

app = Flask(__name__, 
           static_folder='UI/chesswebapp/static',
           template_folder='UI/chesswebapp/templates')

# Initialize board and chess suggester
# Note: In production, these should be per-request instances to avoid state issues
board = chess.Board()
chess_suggester = ChessSuggester()

# CORS headers for frontend
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    return response

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/test-static')
def test_static():
    static_path = os.path.join(os.getcwd(), 'UI', 'chesswebapp', 'static')
    return f"Static folder path: {static_path}<br>Exists: {os.path.exists(static_path)}"

@app.route('/move', methods=['POST'])
def move():
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        move_uci = request.json.get('move')
        fen = request.json.get('fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        
        if not move_uci:
            return jsonify({'status': 'error', 'message': 'No move provided'}), 400
            
        temp_board = chess.Board(fen)
        
        if len(move_uci) != 4:
            return jsonify({'status': 'error', 'message': 'Invalid move format'}), 400
        
        move = chess.Move.from_uci(move_uci)

        if move in temp_board.legal_moves:
            temp_board.push(move)
            return jsonify({'status': 'ok', 'fen': temp_board.fen()})
        else:
            return jsonify({'status': 'illegal'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/reset', methods=['POST'])
def reset():
    try:
        temp_board = chess.Board()
        return jsonify({'status': 'reset', 'fen': temp_board.fen()})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/suggest', methods=['POST'])
def suggest_moves():
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        fen = request.json.get('fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        
        temp_board = chess.Board(fen)
        
        suggestions = chess_suggester.get_move_suggestions(temp_board)
        
        return jsonify(suggestions)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/analyze', methods=['POST'])
def analyze_position():
    try:
        if not request.is_json or request.json is None:
            return jsonify({'status': 'error', 'message': 'Invalid or missing JSON'}), 400
        
        fen = request.json.get('fen', 'rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1')
        
        temp_board = chess.Board(fen)
        
        analysis = chess_suggester.get_move_suggestions(temp_board)
        
        return jsonify(analysis)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@app.route('/position', methods=['GET'])
def get_position():
    try:
        temp_board = chess.Board()
        return jsonify({
            'fen': temp_board.fen(),
            'is_check': temp_board.is_check(),
            'is_checkmate': temp_board.is_checkmate(),
            'is_stalemate': temp_board.is_stalemate(),
            'is_insufficient_material': temp_board.is_insufficient_material(),
            'turn': 'white' if temp_board.turn else 'black'
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
