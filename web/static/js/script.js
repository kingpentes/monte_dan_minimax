var board = null
var game = new Chess()
var $status = $('#status')
var $fen = $('#fen')
var $pgn = $('#pgn')
var $thinking = $('#thinking')

function onDragStart (source, piece, position, orientation) {
  // do not pick up pieces if the game is over
  if (game.game_over()) return false

  // only pick up pieces for the side to move
  if ((game.turn() === 'w' && piece.search(/^b/) !== -1) ||
      (game.turn() === 'b' && piece.search(/^w/) !== -1)) {
    return false
  }
}

function onDrop (source, target) {
  // see if the move is legal
  var move = game.move({
    from: source,
    to: target,
    promotion: 'q' // NOTE: always promote to a queen for example simplicity
  })

  // illegal move
  if (move === null) return 'snapback'

  updateStatus()
  
  // Make AI move
  makeAIMove()
}

function makeAIMove() {
    $thinking.removeClass('hidden');
    
    var depth = $('#depth').val();
    var mode = $('#algorithm').val();
    
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
                    promotion: 'q'
                });
                board.position(game.fen());
                updateStatus();
            } else if (response.game_over) {
                alert("Game Over! Result: " + response.result);
            }
        },
        error: function(error) {
            $thinking.addClass('hidden');
            console.error("Error:", error);
            alert("Error communicating with engine.");
        }
    });
}

// update the board position after the piece snap
// for castling, en passant, pawn promotion
function onSnapEnd () {
  board.position(game.fen())
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
  draggable: true,
  position: 'start',
  onDragStart: onDragStart,
  onDrop: onDrop,
  onSnapEnd: onSnapEnd,
  pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
}
board = Chessboard('board', config)

updateStatus()

$('#newGameBtn').on('click', function() {
    game.reset();
    board.start();
    updateStatus();
});
