var board = null
var game = new Chess()
var $status = $('#status')
var $fen = $('#fen')
var $pgn = $('#pgn')
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
    // Determine which algorithm to use based on turn
    var mode = (game.turn() === 'w') ? $('#whiteAlgorithm').val() : $('#blackAlgorithm').val();
    
    $.ajax({
        url: '/move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            fen: game.fen(),
            depth: depth,
            mode: mode
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
                    demoTimeout = setTimeout(makeAIMove, 500); // 500ms delay between moves
                } else if (game.game_over()) {
                    isDemoRunning = false;
                    alert("Game Over! Result: " + (game.in_checkmate() ? (game.turn() === 'w' ? "Black Wins" : "White Wins") : "Draw"));
                }
            } else if (response.game_over) {
                isDemoRunning = false;
                alert("Game Over! Result: " + response.result);
            }
        },
        error: function(error) {
            $thinking.addClass('hidden');
            isDemoRunning = false;
            console.error("Error:", error);
            alert("Error communicating with engine.");
        }
    });
}
function updateStatus () {
  var status = ''
  var moveColor = 'White'
  if (game.turn() === 'b') {
    moveColor = 'Black'
  }
  // checkmate?
  if (game.in_checkmate()) {
    status = 'Game over, ' + moveColor + ' is in checkmate.'
  }
  // draw?
  else if (game.in_draw()) {
    status = 'Game over, drawn position'
  }
  // game still on
  else {
    status = moveColor + ' to move'
    // check?
    if (game.in_check()) {
      status += ', ' + moveColor + ' is in check'
    }
  }
  $status.html(status)
}
var config = {
  draggable: false, // Disable dragging
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
    updateStatus();
    $thinking.addClass('hidden');
});
$('#startGameBtn').on('click', function() {
    if (isDemoRunning) return;
    
    if (game.game_over()) {
        game.reset();
        board.start();
        updateStatus();
    }
    
    isDemoRunning = true;
    makeAIMove();
});