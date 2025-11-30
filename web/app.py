import sys
import os
import chess

# Add engine directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine-chess')))

from flask import Flask, render_template, request, jsonify
from minimax.minimax_ab import select_best_move

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def move():
    data = request.json
    fen = data.get('fen')
    depth = int(data.get('depth', 3))
    mode = data.get('mode', 'minimax')
    
    board = chess.Board(fen)
    
    if board.is_game_over():
        return jsonify({'game_over': True, 'result': board.result()})

    use_mc = (mode == 'hybrid')
    
    # Run engine
    best_move = select_best_move(board, depth=depth, use_mc=use_mc, rollout_count=30)
    
    if best_move:
        return jsonify({'move': best_move.uci(), 'from': best_move.uci()[:2], 'to': best_move.uci()[2:]})
    else:
        return jsonify({'error': 'No move found'})

if __name__ == '__main__':
    app.run(debug=True)
