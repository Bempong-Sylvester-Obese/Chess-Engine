from flask import Flask, render_template, request, jsonify
import chess

app = Flask(__name__)
board = chess.Board()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    global board
    move_uci = request.json.get('move')
    move = chess.Move.from_uci(move_uci)

    if move in board.legal_moves:
        board.push(move)
        return jsonify({'status': 'ok', 'fen': board.fen()})
    else:
        return jsonify({'status': 'illegal'})

@app.route('/reset', methods=['POST'])
def reset():
    global board
    board.reset()
    return jsonify({'status': 'reset', 'fen': board.fen()})

if __name__ == '__main__':
    app.run(debug=True)
