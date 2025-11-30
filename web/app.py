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
    rollout = int(data.get('rollout', 10))
    
    board = chess.Board(fen)
    
    if board.is_game_over():
        return jsonify({'game_over': True, 'result': board.result()})

    use_mc = (mode == 'hybrid')
    
    # Optimize parameters for Hybrid mode to prevent timeout
    if use_mc:
        # Cap depth at 2 for Hybrid mode because MC is slow
        depth = min(depth, 2)
        # Use rollout from user input
        rollout_count = rollout
    else:
        rollout_count = 30

    # Run engine
    best_move = select_best_move(board, depth=depth, use_mc=use_mc, rollout_count=rollout_count)
    
    if best_move:
        uci = best_move.uci()
        return jsonify({
            'move': uci, 
            'from': uci[:2], 
            'to': uci[2:4],
            'promotion': uci[4:] if len(uci) > 4 else None
        })
    else:
        return jsonify({'error': 'No move found'})

if __name__ == '__main__':
    app.run(debug=True)
