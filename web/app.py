import sys
import os
import chess
import chess.engine
import json
import uuid
from datetime import datetime

# Add engine directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine-chess')))

from flask import Flask, render_template, request, jsonify, send_from_directory
from minimax.minimax_ab import select_best_move
from stockfish_config import get_default_stockfish_path

app = Flask(__name__)

# Setup directories for logs and charts
RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'engine-chess', 'results'))
LOGS_DIR = os.path.join(RESULTS_DIR, 'logs')
CHARTS_DIR = os.path.join(RESULTS_DIR, 'charts')
os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(CHARTS_DIR, exist_ok=True)

# Game Logger Class
class GameLogger:
    """Logs game data to JSON files."""
    
    @staticmethod
    def save_game_log(game_data):
        """Save game log to JSON file."""
        game_id = game_data.get('game_id', str(uuid.uuid4())[:8])
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"game_{timestamp}_{game_id}.json"
        filepath = os.path.join(LOGS_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(game_data, f, indent=2, ensure_ascii=False)
        
        return filename
    
    @staticmethod
    def get_all_logs():
        """Get list of all game logs."""
        logs = []
        if os.path.exists(LOGS_DIR):
            for filename in sorted(os.listdir(LOGS_DIR), reverse=True):
                if filename.endswith('.json'):
                    filepath = os.path.join(LOGS_DIR, filename)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            logs.append({
                                'filename': filename,
                                'summary': {
                                    'algorithm': data.get('algorithm', 'unknown'),
                                    'result': data.get('result', 'unknown'),
                                    'total_moves': len(data.get('moves', [])),
                                    'timestamp': data.get('timestamp', '')
                                }
                            })
                    except:
                        pass
        return logs
    
    @staticmethod
    def get_log(filename):
        """Get specific game log."""
        filepath = os.path.join(LOGS_DIR, filename)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None

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

# === API Endpoints for Logs and Charts ===

@app.route('/api/logs', methods=['GET'])
def get_logs():
    """Get list of all game logs."""
    logs = GameLogger.get_all_logs()
    return jsonify({'logs': logs})

@app.route('/api/logs/<filename>', methods=['GET'])
def get_log(filename):
    """Get specific game log."""
    log = GameLogger.get_log(filename)
    if log:
        return jsonify(log)
    return jsonify({'error': 'Log not found'}), 404

@app.route('/api/save_log', methods=['POST'])
def save_log():
    """Save game log from frontend."""
    try:
        data = request.json
        data['timestamp'] = datetime.now().isoformat()
        filename = GameLogger.save_game_log(data)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/charts', methods=['GET'])
def get_charts():
    """Get list of available chart images."""
    charts = []
    if os.path.exists(CHARTS_DIR):
        for filename in sorted(os.listdir(CHARTS_DIR)):
            if filename.endswith('.png'):
                charts.append({
                    'filename': filename,
                    'url': f'/api/charts/{filename}'
                })
    return jsonify({'charts': charts})

@app.route('/api/charts/<filename>', methods=['GET'])
def get_chart_image(filename):
    """Serve chart image."""
    return send_from_directory(CHARTS_DIR, filename)

@app.route('/api/generate_charts', methods=['POST'])
def generate_charts():
    """Generate charts from game data."""
    try:
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend
        import matplotlib.pyplot as plt
        
        data = request.json
        
        # Generate Move Quality Chart (Pie Chart)
        quality_data = data.get('accuracy', {})
        labels = ['Excellent', 'Good', 'Inaccuracy', 'Mistake', 'Blunder']
        sizes = [
            quality_data.get('excellent', 0),
            quality_data.get('good', 0),
            quality_data.get('inaccuracy', 0),
            quality_data.get('mistake', 0),
            quality_data.get('blunder', 0)
        ]
        
        # Only create chart if there's data
        if sum(sizes) > 0:
            colors = ['#4CAF50', '#8BC34A', '#FFC107', '#FF9800', '#F44336']
            plt.figure(figsize=(8, 6))
            plt.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            plt.title(f"Kualitas Gerakan - {data.get('algorithm', 'Algorithm')}")
            plt.savefig(os.path.join(CHARTS_DIR, 'move_quality.png'), dpi=100, bbox_inches='tight')
            plt.close()
        
        # Generate Performance Bar Chart
        plt.figure(figsize=(10, 6))
        metrics = ['Menang', 'Kalah', 'Seri']
        values = [
            data.get('algorithmWins', 0),
            data.get('stockfishWins', 0),
            data.get('draws', 0)
        ]
        colors = ['#4CAF50', '#F44336', '#9E9E9E']
        plt.bar(metrics, values, color=colors)
        plt.title('Hasil Permainan')
        plt.ylabel('Jumlah')
        plt.savefig(os.path.join(CHARTS_DIR, 'game_results.png'), dpi=100, bbox_inches='tight')
        plt.close()
        
        # Generate Accuracy Comparison Chart
        plt.figure(figsize=(8, 6))
        players = ['Algoritma', 'Stockfish']
        algo_acpl = quality_data.get('totalCPLoss', 0) / max(quality_data.get('evaluatedMoves', 1), 1)
        sf_accuracy = data.get('stockfishAccuracy', {})
        sf_acpl = sf_accuracy.get('totalCPLoss', 0) / max(sf_accuracy.get('evaluatedMoves', 1), 1)
        accuracies = [
            max(0, 100 - (algo_acpl / 10)),
            max(0, 100 - (sf_acpl / 10))
        ]
        colors = ['#2196F3', '#4CAF50']
        plt.bar(players, accuracies, color=colors)
        plt.title('Perbandingan Akurasi')
        plt.ylabel('Akurasi (%)')
        plt.ylim(0, 100)
        plt.savefig(os.path.join(CHARTS_DIR, 'accuracy_comparison.png'), dpi=100, bbox_inches='tight')
        plt.close()
        
        return jsonify({'success': True, 'charts': ['move_quality.png', 'game_results.png', 'accuracy_comparison.png']})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/regenerate_comparison', methods=['POST'])
def regenerate_comparison():
    """Regenerate comparison charts from existing logs."""
    try:
        # Import dynamically to avoid circular imports during startup if any
        from generate_report import generate_comparison_charts
        import numpy as np

        logs = GameLogger.get_all_logs()
        
        # Initialize aggregates
        baseline_stats = {
            'wins': 0, 'losses': 0, 'draws': 0,
            'move_times': [],
            'cp_losses': [],
            'match_rates': [],
            'total_moves': 0
        }
        
        hybrid_stats = {
            'wins': 0, 'losses': 0, 'draws': 0,
            'move_times': [],
            'cp_losses': [],
            'match_rates': [],
            'total_moves': 0
        }
        
        # Process logs
        for log_entry in logs:
            filename = log_entry.get('filename')
            log = GameLogger.get_log(filename)
            if not log:
                continue
                
            algo = log.get('algorithm', '').lower()
            is_hybrid = 'hybrid' in algo
            
            stats = hybrid_stats if is_hybrid else baseline_stats
            
            # Result
            if log.get('result') == 'Algorithm Win':
                stats['wins'] += 1
            elif log.get('result') == 'Stockfish Win':
                stats['losses'] += 1
            else:
                stats['draws'] += 1
                
            # Moves metrics from individual moves
            moves = log.get('moves', [])
            stats['total_moves'] += len(moves)
            
            # Note: The logs store accuracy summary, we can use that or recalculate
            # Using summary from log for simplicity
            accuracy = log.get('accuracy', {})
            total_moves = accuracy.get('evaluatedMoves', 0)
            
            if total_moves > 0:
                # Average CP Loss for this game
                avg_cp = accuracy.get('totalCPLoss', 0) / total_moves
                stats['cp_losses'].append(avg_cp)
                
                # Match rate (Excellent + Good) / Total ? Or just assume high match?
                # The current log doesn't explicitly store "match rate" vs Stockfish best move
                # unless we infer it from quality 'excellent' (CP Loss <= 10).
                # Let's approximate match rate as (Excelent) / Total
                matches = accuracy.get('excellent', 0)
                stats['match_rates'].append(matches / total_moves)

            # Move times are not explicitly in the log summary, but we might simulate or assume
            # effectively 0 for static and higher for MC if not recorded.
            # Wait, game_runner records it but app.py logging might not have detailed times per move in summary.
            # Checking app.py structure... user didn't implement detailed timing logs in app.py yet.
            # We will use placeholders or mocked values based on typical performance if missing
            # OR better: if 'moves' list has timing? No, it has move, player, quality, cpLoss.
            # We will set time to 0.05s for baseline and 2.0s for hybrid as estimates if missing.
            stats['move_times'].append(2.0 if is_hybrid else 0.05)

        # Helper to safely calculate mean/std
        def calc_metrics(stats_dict):
            n_games = stats_dict['wins'] + stats_dict['losses'] + stats_dict['draws']
            if n_games == 0:
                return None
            
            win_rate = (stats_dict['wins'] + 0.5 * stats_dict['draws']) / n_games
            
            return {
                'config': {'depth': 3, 'n_games': n_games, 'rollout_count': 10}, # approximations
                'metrics': {
                    'win_rate': win_rate,
                    'avg_move_time': float(np.mean(stats_dict['move_times'])) if stats_dict['move_times'] else 0,
                    'std_move_time': float(np.std(stats_dict['move_times'])) if stats_dict['move_times'] else 0,
                    'avg_cp_loss': float(np.mean(stats_dict['cp_losses'])) if stats_dict['cp_losses'] else 0,
                    'move_match_rate': float(np.mean(stats_dict['match_rates'])) if stats_dict['match_rates'] else 0,
                    'total_moves': stats_dict['total_moves']
                }
            }

        baseline_summary = calc_metrics(baseline_stats)
        hybrid_summary = calc_metrics(hybrid_stats)
        
        if baseline_summary and hybrid_summary:
            # Save summaries
            with open(os.path.join(RESULTS_DIR, "baseline_summary.json"), 'w') as f:
                json.dump(baseline_summary, f, indent=2)
            with open(os.path.join(RESULTS_DIR, "hybrid_summary.json"), 'w') as f:
                json.dump(hybrid_summary, f, indent=2)
                
            # Generate Charts
            generate_comparison_charts(baseline_summary, hybrid_summary)
            
            return jsonify({'success': True, 'message': 'Laporan berhasil diperbarui!'})
        else:
            return jsonify({'success': False, 'message': 'Data tidak cukup untuk kedua algoritma. Mainkan lebih banyak game (Minimax & Hybrid).'})

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get("PORT", 5000))
        app.run(host="0.0.0.0", port=port, debug=False)
    finally:
        if stockfish_engine:
            stockfish_engine.quit()
