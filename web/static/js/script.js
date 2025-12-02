var board = null
var game = new Chess()
var $status = $('#status')
var $thinking = $('#thinking')
var isDemoRunning = false
var demoTimeout = null
var skipMode = false
var batchResults = {
    total: 0,
    algorithmWins: 0,
    stockfishWins: 0,
    draws: 0,
    totalMoves: 0,
    longestGame: 0,
    shortestGame: 999,
    startTime: null,
    accuracy: {
        excellent: 0,
        good: 0,
        inaccuracy: 0,
        mistake: 0,
        blunder: 0,
        totalCPLoss: 0,
        evaluatedMoves: 0
    },
    stockfishAccuracy: {
        excellent: 0,
        good: 0,
        inaccuracy: 0,
        mistake: 0,
        blunder: 0,
        totalCPLoss: 0,
        evaluatedMoves: 0
    }
}
var currentBatchGame = 0
var totalBatchGames = 1
var currentGameMoves = 0

function onDragStart (source, piece, position, orientation) {
  return false
}

function makeAIMove() {
    if (game.game_over() || !isDemoRunning) return

    $thinking.removeClass('hidden')
    
    var depth = $('#depth').val()
    var rollout = $('#rollout').val()
    var algorithmColor = $('#colorSelect').val()
    var currentTurn = game.turn() === 'w' ? 'white' : 'black'
    
    if (currentTurn === algorithmColor) {
        var mode = $('#algorithmSelect').val()
        
        $.ajax({
            url: '/move',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                fen: game.fen(),
                depth: depth,
                mode: mode,
                rollout: rollout,
                evaluate: true
            }),
            success: function(response) {
                handleMoveResponse(response)
            },
            error: function(error) {
                handleError(error)
            }
        })
    } else {
        $.ajax({
            url: '/stockfish_move',
            type: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                fen: game.fen(),
                time_limit: 0.1,
                evaluate: true
            }),
            success: function(response) {
                handleMoveResponse(response)
            },
            error: function(error) {
                handleError(error)
            }
        })
    }
}

function handleMoveResponse(response) {
    $thinking.addClass('hidden')
    
    if (response.move) {
        var algorithmColor = $('#colorSelect').val()
        var currentTurn = game.turn() === 'w' ? 'white' : 'black'
        var isAlgorithmMove = (currentTurn === algorithmColor)
        
        game.move({
            from: response.from,
            to: response.to,
            promotion: response.promotion || 'q'
        })
        board.position(game.fen())
        currentGameMoves++
        
        // Track move quality if evaluation is available
        if (response.evaluation && response.evaluation.quality) {
            var quality = response.evaluation.quality
            
            if (isAlgorithmMove) {
                // Algorithm move
                batchResults.accuracy[quality]++
                batchResults.accuracy.evaluatedMoves++
                
                if (response.evaluation.cp_loss !== null) {
                    batchResults.accuracy.totalCPLoss += Math.abs(response.evaluation.cp_loss)
                }
            } else {
                // Stockfish move
                batchResults.stockfishAccuracy[quality]++
                batchResults.stockfishAccuracy.evaluatedMoves++
                
                if (response.evaluation.cp_loss !== null) {
                    batchResults.stockfishAccuracy.totalCPLoss += Math.abs(response.evaluation.cp_loss)
                }
            }
        }
        
        updateStatus()
        
        if (isDemoRunning && !game.game_over()) {
            updateGameStatus('running', game.turn())
        }
        
        if (!game.game_over() && isDemoRunning) {
            var delay = skipMode ? 10 : 800
            demoTimeout = setTimeout(makeAIMove, delay)
        } else if (game.game_over()) {
            isDemoRunning = false
            handleGameEnd()
        }
    } else if (response.game_over) {
        isDemoRunning = false
        handleGameEnd()
    }
}

function handleError(error) {
    $thinking.addClass('hidden')
    isDemoRunning = false
    console.error("Error:", error)
    alert("Error berkomunikasi dengan engine. Silakan periksa console.")
}

function handleGameEnd() {
    var algorithmColor = $('#colorSelect').val()
    var winner = null
    
    if (game.in_checkmate()) {
        winner = game.turn() === 'w' ? 'black' : 'white'
    }
    
    batchResults.total++
    batchResults.totalMoves += currentGameMoves
    
    if (currentGameMoves > batchResults.longestGame) {
        batchResults.longestGame = currentGameMoves
    }
    if (currentGameMoves < batchResults.shortestGame) {
        batchResults.shortestGame = currentGameMoves
    }
    
    if (winner === algorithmColor) {
        batchResults.algorithmWins++
    } else if (winner && winner !== algorithmColor) {
        batchResults.stockfishWins++
    } else {
        batchResults.draws++
    }
    
    currentBatchGame++
    currentGameMoves = 0
    
    if (currentBatchGame < totalBatchGames) {
        game.reset()
        board.position('start')
        updateGameStatus('running', game.turn())
        setTimeout(function() {
            isDemoRunning = true
            makeAIMove()
        }, skipMode ? 10 : 500)
    } else {
        showFinalResults()
    }
}

function showFinalResults() {
    var result = ''
    var elapsedTime = batchResults.startTime ? ((Date.now() - batchResults.startTime) / 1000).toFixed(1) : 0
    
    if (totalBatchGames === 1) {
        if (batchResults.algorithmWins > 0) {
            result = '🎉 Algoritma Anda Menang dengan Skakmat!'
        } else if (batchResults.stockfishWins > 0) {
            result = '😔 Stockfish Menang dengan Skakmat'
        } else {
            result = '🤝 Permainan Seri'
        }
        
        $status.html(result)
    }
    
    // Calculate ACPL (Average Centipawn Loss) for both players
    var algoACPL = batchResults.accuracy.evaluatedMoves > 0 ? 
        (batchResults.accuracy.totalCPLoss / batchResults.accuracy.evaluatedMoves) : 0
    var stockfishACPL = batchResults.stockfishAccuracy.evaluatedMoves > 0 ? 
        (batchResults.stockfishAccuracy.totalCPLoss / batchResults.stockfishAccuracy.evaluatedMoves) : 0
    
    // Calculate Accuracy % using Chess.com formula: Accuracy = max(0, 100 - (ACPL / 10))
    var algorithmAccuracy = Math.max(0, 100 - (algoACPL / 10)).toFixed(1)
    var stockfishAccuracy = Math.max(0, 100 - (stockfishACPL / 10)).toFixed(1)
    
    // Always show statistics (for both single and batch games)
    var avgMoves = batchResults.total > 0 ? (batchResults.totalMoves / batchResults.total).toFixed(1) : 0
    var avgCPLoss = algoACPL.toFixed(1)
    
    $('#totalGames').text(batchResults.total)
    $('#algorithmAccuracy').text(algorithmAccuracy + '%')
    $('#stockfishAccuracy').text(stockfishAccuracy + '%')
    $('#algorithmWins').text(batchResults.algorithmWins)
    $('#stockfishWins').text(batchResults.stockfishWins)
    $('#draws').text(batchResults.draws)
    $('#avgMoves').text(avgMoves)
    $('#totalMoves').text(batchResults.totalMoves + ' gerakan')
    $('#totalTime').text(elapsedTime + ' detik')
    $('#longestGame').text(batchResults.longestGame + ' gerakan')
    $('#shortestGame').text(batchResults.shortestGame === 999 ? '0' : batchResults.shortestGame + ' gerakan')
    
    // Accuracy statistics (Algorithm only)
    $('#excellentMoves').text(batchResults.accuracy.excellent)
    $('#goodMoves').text(batchResults.accuracy.good)
    $('#inaccuracyMoves').text(batchResults.accuracy.inaccuracy)
    $('#mistakeMoves').text(batchResults.accuracy.mistake)
    $('#blunderMoves').text(batchResults.accuracy.blunder)
    $('#avgCPLoss').text(avgCPLoss)
    
    // Show and expand stats collapse
    $('#statsCollapse').removeClass('hidden').addClass('expanded')
    $('#statsBadge').text(batchResults.total + ' Game' + (batchResults.total > 1 ? 's' : ''))
    
    // Scroll to stats
    setTimeout(function() {
        document.getElementById('statsCollapse').scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)
    
    lockParameters(false)
    updateGameStatus('finished')
    toggleRolloutInput()
    $('#skipBtn').addClass('hidden')
}

function updateStatus() {
    var status = ''
    var algorithmColor = $('#colorSelect').val()
    var currentTurn = game.turn() === 'w' ? 'white' : 'black'
    var moveColor = game.turn() === 'w' ? 'Putih' : 'Hitam'
    
    if (game.in_checkmate()) {
        status = '🏁 Permainan selesai - ' + moveColor + ' terkena skakmat'
    }
    else if (game.in_draw()) {
        status = '🤝 Permainan selesai - posisi seri'
    }
    else {
        if (currentTurn === algorithmColor) {
            var algo = $('#algorithmSelect option:selected').text()
            status = 'Giliran Algoritma (' + algo + ')'
        } else {
            status = 'Giliran Stockfish'
        }

        if (game.in_check()) {
            status += ' - ⚠️ Skak!'
        }
    }

    $status.html(status)
}

function updateGameStatus(status, currentTurn) {
    var $badge = $('#gameStatusBadge')
    var $text = $('#gameStatusText')
    var $whitePiece = $('.white-piece')
    var $blackPiece = $('.black-piece')
    
    $badge.removeClass('ready running finished')
    
    if (status === 'ready') {
        $badge.addClass('ready')
        $text.text('Siap Dimulai')
        $whitePiece.removeClass('hidden')
        $blackPiece.addClass('hidden')
    } else if (status === 'running') {
        $badge.addClass('running')
        
        if (currentTurn === 'w') {
            $whitePiece.removeClass('hidden')
            $blackPiece.addClass('hidden')
            
            var algorithmColor = $('#colorSelect').val()
            if (algorithmColor === 'white') {
                $text.text('Giliran Algoritma (Putih)')
            } else {
                $text.text('Giliran Stockfish (Putih)')
            }
        } else {
            $whitePiece.addClass('hidden')
            $blackPiece.removeClass('hidden')
            
            var algorithmColor = $('#colorSelect').val()
            if (algorithmColor === 'black') {
                $text.text('Giliran Algoritma (Hitam)')
            } else {
                $text.text('Giliran Stockfish (Hitam)')
            }
        }
    } else if (status === 'finished') {
        $badge.addClass('finished')
        $text.text('Permainan Selesai')
        $whitePiece.removeClass('hidden')
        $blackPiece.addClass('hidden')
    }
}

function lockParameters(lock) {
    $('#algorithmSelect').prop('disabled', lock)
    $('#colorSelect').prop('disabled', lock)
    $('#depth').prop('disabled', lock)
    $('#gameCount').prop('disabled', lock)
    
    if (lock || $('#algorithmSelect').val() !== 'hybrid') {
        $('#rollout').prop('disabled', true)
    } else {
        $('#rollout').prop('disabled', false)
    }
    
    if (lock) {
        $('.config-section').css('opacity', '0.6')
        $('.batch-config').css('opacity', '0.6')
    } else {
        $('.config-section').css('opacity', '1')
        $('.batch-config').css('opacity', '1')
    }
}

function toggleRolloutInput() {
    var algorithm = $('#algorithmSelect').val()
    var $rolloutInput = $('#rollout')
    
    if (isDemoRunning) {
        return
    }
    
    if (algorithm === 'hybrid') {
        $rolloutInput.prop('disabled', false)
        $rolloutInput.parent().parent().css('opacity', '1')
    } else {
        $rolloutInput.prop('disabled', true)
        $rolloutInput.parent().parent().css('opacity', '0.5')
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

toggleRolloutInput()
updateGameStatus('ready')

$('#algorithmSelect').on('change', toggleRolloutInput)

$('#newGameBtn').on('click', function() {
    isDemoRunning = false
    skipMode = false
    if (demoTimeout) clearTimeout(demoTimeout)
    game.reset()
    board.start()
    $status.html('Siap untuk memulai')
    $thinking.addClass('hidden')
    
    batchResults = {
        total: 0,
        algorithmWins: 0,
        stockfishWins: 0,
        draws: 0,
        totalMoves: 0,
        longestGame: 0,
        shortestGame: 999,
        startTime: null,
        accuracy: {
            excellent: 0,
            good: 0,
            inaccuracy: 0,
            mistake: 0,
            blunder: 0,
            totalCPLoss: 0,
            evaluatedMoves: 0
        },
        stockfishAccuracy: {
            excellent: 0,
            good: 0,
            inaccuracy: 0,
            mistake: 0,
            blunder: 0,
            totalCPLoss: 0,
            evaluatedMoves: 0
        }
    }
    currentBatchGame = 0
    currentGameMoves = 0
    $('#statsCollapse').removeClass('expanded').addClass('hidden')
    $('#skipBtn').addClass('hidden')
    
    lockParameters(false)
    updateGameStatus('ready')
    toggleRolloutInput()
})

$('#skipBtn').on('click', function() {
    skipMode = true
    $(this).prop('disabled', true).text('Skipping...')
})

$('#startGameBtn').on('click', function() {
    if (isDemoRunning) return
    
    game.reset()
    board.start()
    skipMode = false
    
    totalBatchGames = parseInt($('#gameCount').val()) || 1
    currentBatchGame = 0
    currentGameMoves = 0
    batchResults = {
        total: 0,
        algorithmWins: 0,
        stockfishWins: 0,
        draws: 0,
        totalMoves: 0,
        longestGame: 0,
        shortestGame: 999,
        startTime: Date.now(),
        accuracy: {
            excellent: 0,
            good: 0,
            inaccuracy: 0,
            mistake: 0,
            blunder: 0,
            totalCPLoss: 0,
            evaluatedMoves: 0
        },
        stockfishAccuracy: {
            excellent: 0,
            good: 0,
            inaccuracy: 0,
            mistake: 0,
            blunder: 0,
            totalCPLoss: 0,
            evaluatedMoves: 0
        }
    }
    
    $('#resultsSection').addClass('hidden')
    
    isDemoRunning = true
    
    $('#skipBtn').removeClass('hidden').prop('disabled', false).text('Skip')
    
    lockParameters(true)
    $('#gameCount').prop('disabled', true)
    updateGameStatus('running', game.turn())
    
    updateStatus()
    makeAIMove()
})

// Stats toggle handler
$('#statsToggle').on('click', function() {
    $('#statsCollapse').toggleClass('expanded')
})