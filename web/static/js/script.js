var board = null
var game = new Chess()
var $status = $('#status')
var $thinking = $('#thinking')
var isDemoRunning = false;
var demoTimeout = null;

function onDragStart (source, piece, position, orientation) {
  // Disable dragging for demo mode
  return false
}

function makeAIMove() {
    if (game.game_over() || !isDemoRunning) return;

    $thinking.removeClass('hidden');
    
    var depth = $('#depth').val();
    var rollout = $('#rollout').val();
    var algorithmColor = $('#colorSelect').val();
    var currentTurn = game.turn() === 'w' ? 'white' : 'black';
    
    // Determine if it's algorithm's turn or Stockfish's turn
    if (currentTurn === algorithmColor) {
        // Algorithm's turn
        var mode = $('#algorithmSelect').val();
        
        $.ajax({
            url: '/move',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                fen: game.fen(),
                depth: depth,
                mode: mode,
                rollout: rollout
            }),
            success: function(response) {
                handleMoveResponse(response);
            },
            error: function(error) {
                handleError(error);
            }
        });
    } else {
        // Stockfish's turn
        $.ajax({
            url: '/stockfish_move',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                fen: game.fen(),
                time_limit: 0.1
            }),
            success: function(response) {
                handleMoveResponse(response);
            },
            error: function(error) {
                handleError(error);
            }
        });
    }
}

function handleMoveResponse(response) {
    $thinking.addClass('hidden');
    
    if (response.move) {
        game.move({
            from: response.from,
            to: response.to,
            promotion: response.promotion || 'q'
        });
        board.position(game.fen());
        updateStatus();
        
        // Update turn indicator
        if (isDemoRunning && !game.game_over()) {
            updateGameStatus('running', game.turn());
        }
        
        // Schedule next move if game is not over
        if (!game.game_over() && isDemoRunning) {
            demoTimeout = setTimeout(makeAIMove, 800);
        } else if (game.game_over()) {
            isDemoRunning = false;
            showGameOver();
        }
    } else if (response.game_over) {
        isDemoRunning = false;
        showGameOver();
    }
}

function handleError(error) {
    $thinking.addClass('hidden');
    isDemoRunning = false;
    console.error("Error:", error);
    alert("Error berkomunikasi dengan engine. Silakan periksa console.");
}

function showGameOver() {
    var result = '';
    var algorithmColor = $('#colorSelect').val();
    var winner = null;
    
    if (game.in_checkmate()) {
        winner = game.turn() === 'w' ? 'black' : 'white';
        if (winner === algorithmColor) {
            result = '🎉 Algoritma Anda Menang dengan Skakmat!';
        } else {
            result = '😔 Stockfish Menang dengan Skakmat';
        }
    } else if (game.in_draw()) {
        result = '🤝 Permainan Seri';
    } else if (game.in_stalemate()) {
        result = '🤝 Stalemate - Seri';
    } else if (game.in_threefold_repetition()) {
        result = '🤝 Seri karena Pengulangan';
    } else {
        result = '🏁 Permainan Selesai';
    }
    
    $status.html(result);
    
    // Unlock parameters and update status
    lockParameters(false);
    updateGameStatus('finished');
    toggleRolloutInput();
    
    setTimeout(function() {
        alert(result + '\n\nKlik "Reset Permainan" untuk memulai simulasi baru.');
    }, 500);
}

function updateStatus() {
    var status = ''
    var algorithmColor = $('#colorSelect').val();
    var currentTurn = game.turn() === 'w' ? 'white' : 'black';
    var moveColor = game.turn() === 'w' ? 'Putih' : 'Hitam';
    
    if (game.in_checkmate()) {
        status = '🏁 Permainan selesai - ' + moveColor + ' terkena skakmat'
    }
    else if (game.in_draw()) {
        status = '🤝 Permainan selesai - posisi seri'
    }
    else {
        if (currentTurn === algorithmColor) {
            var algo = $('#algorithmSelect option:selected').text();
            status = 'Giliran Algoritma (' + algo + ')';
        } else {
            status = 'Giliran Stockfish';
        }

        if (game.in_check()) {
            status += ' - ⚠️ Skak!'
        }
    }

    $status.html(status)
}

// Update game status indicator with chess piece
function updateGameStatus(status, currentTurn) {
    var $badge = $('#gameStatusBadge');
    var $text = $('#gameStatusText');
    var $whitePiece = $('.white-piece');
    var $blackPiece = $('.black-piece');
    
    $badge.removeClass('ready running finished');
    
    if (status === 'ready') {
        $badge.addClass('ready');
        $text.text('Siap Dimulai');
        $whitePiece.removeClass('hidden');
        $blackPiece.addClass('hidden');
    } else if (status === 'running') {
        $badge.addClass('running');
        
        // Show appropriate piece based on turn
        if (currentTurn === 'w') {
            $whitePiece.removeClass('hidden');
            $blackPiece.addClass('hidden');
            
            var algorithmColor = $('#colorSelect').val();
            if (algorithmColor === 'white') {
                $text.text('Giliran Algoritma (Putih)');
            } else {
                $text.text('Giliran Stockfish (Putih)');
            }
        } else {
            $whitePiece.addClass('hidden');
            $blackPiece.removeClass('hidden');
            
            var algorithmColor = $('#colorSelect').val();
            if (algorithmColor === 'black') {
                $text.text('Giliran Algoritma (Hitam)');
            } else {
                $text.text('Giliran Stockfish (Hitam)');
            }
        }
    } else if (status === 'finished') {
        $badge.addClass('finished');
        $text.text('Permainan Selesai');
        $whitePiece.removeClass('hidden');
        $blackPiece.addClass('hidden');
    }
}

// Lock/unlock all input parameters
function lockParameters(lock) {
    $('#algorithmSelect').prop('disabled', lock);
    $('#colorSelect').prop('disabled', lock);
    $('#depth').prop('disabled', lock);
    
    // Only lock rollout if it's not already disabled by algorithm selection
    if (lock || $('#algorithmSelect').val() !== 'hybrid') {
        $('#rollout').prop('disabled', true);
    } else {
        $('#rollout').prop('disabled', false);
    }
    
    // Visual feedback
    if (lock) {
        $('.config-section').css('opacity', '0.6');
    } else {
        $('.config-section').css('opacity', '1');
    }
}

// Toggle rollout input based on algorithm selection
function toggleRolloutInput() {
    var algorithm = $('#algorithmSelect').val();
    var $rolloutInput = $('#rollout');
    
    // Don't enable if game is running
    if (isDemoRunning) {
        return;
    }
    
    if (algorithm === 'hybrid') {
        $rolloutInput.prop('disabled', false);
        $rolloutInput.parent().parent().css('opacity', '1');
    } else {
        $rolloutInput.prop('disabled', true);
        $rolloutInput.parent().parent().css('opacity', '0.5');
    }
}

var config = {
    draggable: false,
    position: 'start',
    onDragStart: onDragStart,
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
}
board = Chessboard('board', config)

updateStatus()

// Initialize
toggleRolloutInput();
updateGameStatus('ready');

// Listen for algorithm changes
$('#algorithmSelect').on('change', toggleRolloutInput);

$('#newGameBtn').on('click', function() {
    isDemoRunning = false;
    if (demoTimeout) clearTimeout(demoTimeout);
    game.reset();
    board.start();
    $status.html('Siap untuk memulai');
    $thinking.addClass('hidden');
    
    // Unlock parameters and update status
    lockParameters(false);
    updateGameStatus('ready');
    toggleRolloutInput();
});

$('#startGameBtn').on('click', function() {
    if (isDemoRunning) return;
    
    if (game.game_over()) {
        game.reset();
        board.start();
    }
    
    isDemoRunning = true;
    
    // Lock parameters and update status
    lockParameters(true);
    updateGameStatus('running', game.turn());
    
    updateStatus();
    makeAIMove();
});