import sys
import os
import chess
import chess.engine

# Add engine directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine-chess')))

from flask import Flask, render_template, request, jsonify
from minimax.minimax_ab import select_best_move
from stockfish_config import get_default_stockfish_path

app = Flask(__name__)

# Initialize Stockfish
stockfish_path = get_default_stockfish_path()
stockfish_engine = None

if stockfish_path:
    try:
        stockfish_engine = chess.engine.SimpleEngine.popen_uci(stockfish_path)
        print(f"✓ Stockfish loaded from: {stockfish_path}")
    except Exception as e:
        print(f"✗ Failed to load Stockfish: {e}")
else:
    print("✗ Stockfish not found")

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
    evaluate_move = data.get('evaluate', False)
    
    board = chess.Board(fen)
    
    if board.is_game_over():
        return jsonify({'game_over': True, 'result': board.result()})

    # Get evaluation before move (if requested and Stockfish available)
    eval_before = None
    if evaluate_move and stockfish_engine:
        try:
            info = stockfish_engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info.get('score')
            if score:
                eval_before = score.relative.score(mate_score=10000) if score.relative else 0
        except:
            eval_before = None

    use_mc = (mode == 'hybrid')
    
    # Optimize parameters for Hybrid mode to prevent timeout
    if use_mc:
        depth = min(depth, 2)
        rollout_count = rollout
    else:
        rollout_count = 30

    # Run engine
    best_move = select_best_move(board, depth=depth, use_mc=use_mc, rollout_count=rollout_count)
    
    if best_move:
        # Get evaluation after move (if requested and Stockfish available)
        eval_after = None
        move_quality = None
        
        if evaluate_move and stockfish_engine and eval_before is not None:
            try:
                board.push(best_move)
                info = stockfish_engine.analyse(board, chess.engine.Limit(time=0.1))
                score = info.get('score')
                if score:
                    # Flip perspective since we moved
                    eval_after = -(score.relative.score(mate_score=10000) if score.relative else 0)
                    
                    # Calculate centipawn loss
                    cp_loss = eval_before - eval_after
                    
                    # Classify move quality
                    if cp_loss <= 10:
                        move_quality = 'excellent'
                    elif cp_loss <= 25:
                        move_quality = 'good'
                    elif cp_loss <= 50:
                        move_quality = 'inaccuracy'
                    elif cp_loss <= 100:
                        move_quality = 'mistake'
                    else:
                        move_quality = 'blunder'
                
                board.pop()
            except:
                eval_after = None
                move_quality = None
        
        uci = best_move.uci()
        response = {
            'move': uci, 
            'from': uci[:2], 
            'to': uci[2:4],
            'promotion': uci[4:] if len(uci) > 4 else None
        }
        
        if evaluate_move:
            response['evaluation'] = {
                'before': eval_before,
                'after': eval_after,
                'quality': move_quality,
                'cp_loss': eval_before - eval_after if (eval_before is not None and eval_after is not None) else None
            }
        
        return jsonify(response)
    else:
        return jsonify({'error': 'No move found'})

@app.route('/stockfish_move', methods=['POST'])
def stockfish_move():
    if not stockfish_engine:
        return jsonify({'error': 'Stockfish not available'}), 500
    
    data = request.json
    fen = data.get('fen')
    time_limit = float(data.get('time_limit', 0.1))
    evaluate_move = data.get('evaluate', False)
    
    board = chess.Board(fen)
    
    if board.is_game_over():
        return jsonify({'game_over': True, 'result': board.result()})
    
    # Get evaluation before move (if requested)
    eval_before = None
    if evaluate_move:
        try:
            info = stockfish_engine.analyse(board, chess.engine.Limit(time=0.1))
            score = info.get('score')
            if score:
                eval_before = score.relative.score(mate_score=10000) if score.relative else 0
        except:
            eval_before = None
    
    try:
        result = stockfish_engine.play(board, chess.engine.Limit(time=time_limit))
        if result.move:
            # Get evaluation after move (if requested)
            eval_after = None
            move_quality = None
            
            if evaluate_move and eval_before is not None:
                try:
                    board.push(result.move)
                    info = stockfish_engine.analyse(board, chess.engine.Limit(time=0.1))
                    score = info.get('score')
                    if score:
                        # Flip perspective since we moved
                        eval_after = -(score.relative.score(mate_score=10000) if score.relative else 0)
                        
                        # Calculate centipawn loss
                        cp_loss = eval_before - eval_after
                        
                        # Classify move quality
                        if cp_loss <= 10:
                            move_quality = 'excellent'
                        elif cp_loss <= 25:
                            move_quality = 'good'
                        elif cp_loss <= 50:
                            move_quality = 'inaccuracy'
                        elif cp_loss <= 100:
                            move_quality = 'mistake'
                        else:
                            move_quality = 'blunder'
                    
                    board.pop()
                except:
                    eval_after = None
                    move_quality = None
            
            uci = result.move.uci()
            response = {
                'move': uci,
                'from': uci[:2],
                'to': uci[2:4],
                'promotion': uci[4:] if len(uci) > 4 else None
            }
            
            if evaluate_move:
                response['evaluation'] = {
                    'before': eval_before,
                    'after': eval_after,
                    'quality': move_quality,
                    'cp_loss': eval_before - eval_after if (eval_before is not None and eval_after is not None) else None
                }
            
            return jsonify(response)
        else:
            return jsonify({'error': 'No move found'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        app.run(debug=True)
    finally:
        if stockfish_engine:
            stockfish_engine.quit()
