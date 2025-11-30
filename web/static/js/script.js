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
    // Determine which algorithm to use based on turn
    var mode = (game.turn() === 'w') ? $('#whiteAlgorithm').val() : $('#blackAlgorithm').val();
    
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
            $thinking.addClass('hidden');
            
            if (response.move) {
                game.move({
                    from: response.from,
                    to: response.to,
                    promotion: response.promotion || 'q'
                });
                board.position(game.fen());
                updateStatus();
                
                // Schedule next move if game is not over
                if (!game.game_over() && isDemoRunning) {
                    demoTimeout = setTimeout(makeAIMove, 800); // 800ms delay for better viewing
                } else if (game.game_over()) {
                    isDemoRunning = false;
                    showGameOver();
                }
            } else if (response.game_over) {
                isDemoRunning = false;
                showGameOver();
            }
        },
        error: function(error) {
            $thinking.addClass('hidden');
            isDemoRunning = false;
            console.error("Error:", error);
            alert("Error berkomunikasi dengan engine. Silakan periksa console.");
        }
    });
}

function showGameOver() {
    var result = '';
    if (game.in_checkmate()) {
        result = game.turn() === 'w' ? '🎉 Hitam Menang dengan Skakmat!' : '🎉 Putih Menang dengan Skakmat!';
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
    
    // Show a nice alert after a short delay
    setTimeout(function() {
        alert(result + '\n\nKlik "Reset Permainan" untuk memulai simulasi baru.');
    }, 500);
}

function updateStatus() {
    var status = ''
    var moveColor = 'Putih'
    if (game.turn() === 'b') {
        moveColor = 'Hitam'
    }

    // checkmate?
    if (game.in_checkmate()) {
        status = '🏁 Permainan selesai - ' + moveColor + ' terkena skakmat'
    }
    // draw?
    else if (game.in_draw()) {
        status = '🤝 Permainan selesai - posisi seri'
    }
    // game still on
    else {
        var algo = (game.turn() === 'w') ? $('#whiteAlgorithm option:selected').text() : $('#blackAlgorithm option:selected').text();
        status = moveColor + ' akan bergerak (' + algo + ')'

        // check?
        if (game.in_check()) {
            status += ' - ⚠️ Skak!'
        }
    }

    $status.html(status)
}

var config = {
    draggable: false,
    position: 'start',
    onDragStart: onDragStart,
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
}
board = Chessboard('board', config)

updateStatus()

$('#newGameBtn').on('click', function() {
    isDemoRunning = false;
    if (demoTimeout) clearTimeout(demoTimeout);
    game.reset();
    board.start();
    $status.html('Siap untuk memulai');
    $thinking.addClass('hidden');
});

$('#startGameBtn').on('click', function() {
    if (isDemoRunning) return;
    
    if (game.game_over()) {
        game.reset();
        board.start();
    }
    
    isDemoRunning = true;
    updateStatus();
    makeAIMove();
});