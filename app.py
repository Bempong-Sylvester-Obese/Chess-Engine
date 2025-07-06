from flask import Flask, render_template, request, jsonify, send_from_directory
import chess
import os

app = Flask(__name__, 
           static_folder='UI/chesswebapp/static',
           template_folder='UI/chesswebapp/templates')

# Initialize board
board = chess.Board()

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

if __name__ == '__main__':
    # Use a more efficient configuration for development
    app.run(debug=True, host='0.0.0.0', port=5001, threaded=True)
