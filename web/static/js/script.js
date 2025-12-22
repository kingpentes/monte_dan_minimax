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
var moveHistory = [] // Track moves for display and logging

function onDragStart(source, piece, position, orientation) {
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
            success: function (response) {
                handleMoveResponse(response)
            },
            error: function (error) {
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
            success: function (response) {
                handleMoveResponse(response)
            },
            error: function (error) {
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

        // Add to move history for display
        moveHistory.push({
            number: currentGameMoves,
            move: response.move,
            player: isAlgorithmMove ? 'algorithm' : 'stockfish',
            quality: response.evaluation ? response.evaluation.quality : null,
            cpLoss: response.evaluation ? response.evaluation.cp_loss : null
        })

        // Update move history UI
        updateMoveHistoryUI()

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
        // Use custom FEN for batch games
        var customFEN = getCustomFEN()
        game = new Chess(customFEN)
        board.position(customFEN)
        updateGameStatus('running', game.turn())
        setTimeout(function () {
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
    setTimeout(function () {
        document.getElementById('statsCollapse').scrollIntoView({ behavior: 'smooth', block: 'start' })
    }, 100)

    lockParameters(false)
    updateGameStatus('finished')
    toggleRolloutInput()
    $('#skipBtn').addClass('hidden')

    // Save game log and generate charts
    saveGameLog()
    generateAndDisplayCharts()
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

$('#newGameBtn').on('click', function () {
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

$('#skipBtn').on('click', function () {
    skipMode = true
    $(this).prop('disabled', true).text('Skipping...')
})

$('#startGameBtn').on('click', function () {
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
$('#statsToggle').on('click', function () {
    $('#statsCollapse').toggleClass('expanded')
})

// Piece Selection Functions
function getCustomFEN() {
    // Build FEN string based on selected pieces
    var fenRows = []

    for (var row = 8; row >= 1; row--) {
        var fenRow = ''
        var emptyCount = 0

        for (var col = 0; col < 8; col++) {
            var file = String.fromCharCode(97 + col) // 'a' to 'h'
            var square = file + row
            var $cell = $('.piece-cell[data-square="' + square + '"]')

            if ($cell.hasClass('empty') || $cell.hasClass('removed')) {
                emptyCount++
            } else {
                if (emptyCount > 0) {
                    fenRow += emptyCount
                    emptyCount = 0
                }
                fenRow += $cell.data('piece')
            }
        }

        if (emptyCount > 0) {
            fenRow += emptyCount
        }

        fenRows.push(fenRow)
    }

    // Combine rows with / and add default game state
    return fenRows.join('/') + ' w KQkq - 0 1'
}

function resetPieceSelection() {
    $('.piece-cell').removeClass('removed')
}

function lockPieceConfig(lock) {
    if (lock) {
        $('#pieceBoard').css('pointer-events', 'none').css('opacity', '0.6')
        $('#resetPiecesBtn').prop('disabled', true).css('opacity', '0.6')
    } else {
        $('#pieceBoard').css('pointer-events', 'auto').css('opacity', '1')
        $('#resetPiecesBtn').prop('disabled', false).css('opacity', '1')
    }
}

// Piece cell click handler
$('#pieceBoard').on('click', '.piece-cell', function () {
    var $cell = $(this)

    // Ignore empty cells and locked cells (kings)
    if ($cell.hasClass('empty') || $cell.data('locked')) {
        if ($cell.data('locked')) {
            // Visual feedback for locked cell
            $cell.css('animation', 'shake 0.3s ease')
            setTimeout(function () {
                $cell.css('animation', '')
            }, 300)
        }
        return
    }

    // Toggle removed state
    $cell.toggleClass('removed')
})

// Reset pieces button
$('#resetPiecesBtn').on('click', function () {
    resetPieceSelection()
})

// Add shake animation to CSS dynamically
$('<style>@keyframes shake { 0%, 100% { transform: translateX(0); } 25% { transform: translateX(-3px); } 75% { transform: translateX(3px); } }</style>').appendTo('head')

// Modify newGameBtn to also reset pieces
var originalNewGameClick = $('#newGameBtn').data('events')
$('#newGameBtn').off('click').on('click', function () {
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
    moveHistory = [] // Reset move history
    $('#statsCollapse').removeClass('expanded').addClass('hidden')
    $('#skipBtn').addClass('hidden')

    // Reset move history and charts panels
    $('#moveHistoryGrid').empty()
    $('#moveHistoryCollapse').removeClass('expanded').addClass('hidden')
    $('#chartsCollapse').removeClass('expanded').addClass('hidden')
    $('#moveCountBadge').text('0')

    // Reset chart images
    $('#moveQualityChart').addClass('hidden')
    $('#moveQualityPlaceholder').removeClass('hidden')
    $('#gameResultsChart').addClass('hidden')
    $('#gameResultsPlaceholder').removeClass('hidden')
    $('#accuracyChart').addClass('hidden')
    $('#accuracyPlaceholder').removeClass('hidden')

    // Reset piece selection
    resetPieceSelection()

    lockParameters(false)
    lockPieceConfig(false)
    updateGameStatus('ready')
    toggleRolloutInput()
})

// Modify startGameBtn to use custom FEN
$('#startGameBtn').off('click').on('click', function () {
    if (isDemoRunning) return

    // Get custom FEN from piece selection
    var customFEN = getCustomFEN()

    // Reset game with custom position
    game = new Chess(customFEN)
    board.position(customFEN)

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

    // Reset move history and show panel
    moveHistory = []
    $('#moveHistoryGrid').empty()
    $('#moveHistoryCollapse').removeClass('hidden').addClass('expanded')
    $('#chartsCollapse').removeClass('hidden')
    $('#moveCountBadge').text('0')

    $('#skipBtn').removeClass('hidden').prop('disabled', false).text('Skip')

    lockParameters(true)
    lockPieceConfig(true)
    $('#gameCount').prop('disabled', true)
    updateGameStatus('running', game.turn())

    updateStatus()
    makeAIMove()
})

// === Move History & Charts Functions ===

function updateMoveHistoryUI() {
    var $grid = $('#moveHistoryGrid')
    var lastMove = moveHistory[moveHistory.length - 1]

    if (lastMove) {
        var qualityClass = lastMove.quality ? lastMove.quality : ''
        var qualityIcon = getQualityIcon(lastMove.quality)

        var $item = $('<div class="move-item ' + lastMove.player + '">' +
            '<span class="move-number">' + lastMove.number + '.</span>' +
            '<span class="move-notation">' + lastMove.move + '</span>' +
            '<span class="move-quality ' + qualityClass + '">' + qualityIcon + '</span>' +
            '</div>')

        $grid.append($item)

        // Auto-scroll to bottom
        $grid.scrollTop($grid[0].scrollHeight)

        // Update badge
        $('#moveCountBadge').text(moveHistory.length)
    }
}

function getQualityIcon(quality) {
    switch (quality) {
        case 'excellent': return '⭐'
        case 'good': return '✅'
        case 'inaccuracy': return '⚠️'
        case 'mistake': return '❌'
        case 'blunder': return '💥'
        default: return ''
    }
}

function saveGameLog() {
    var algorithm = $('#algorithmSelect option:selected').text()
    var depth = $('#depth').val()
    var result = ''

    if (batchResults.algorithmWins > batchResults.stockfishWins) {
        result = 'Algorithm Win'
    } else if (batchResults.stockfishWins > batchResults.algorithmWins) {
        result = 'Stockfish Win'
    } else {
        result = 'Draw'
    }

    var logData = {
        game_id: Date.now().toString(36),
        algorithm: algorithm,
        depth: parseInt(depth),
        result: result,
        moves: moveHistory,
        algorithmWins: batchResults.algorithmWins,
        stockfishWins: batchResults.stockfishWins,
        draws: batchResults.draws,
        totalMoves: batchResults.totalMoves,
        accuracy: batchResults.accuracy,
        stockfishAccuracy: batchResults.stockfishAccuracy
    }

    $.ajax({
        url: '/api/save_log',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(logData),
        success: function (response) {
            console.log('Game log saved:', response.filename)
        },
        error: function (error) {
            console.error('Failed to save log:', error)
        }
    })
}

function generateAndDisplayCharts() {
    var algorithm = $('#algorithmSelect option:selected').text()

    var chartData = {
        algorithm: algorithm,
        algorithmWins: batchResults.algorithmWins,
        stockfishWins: batchResults.stockfishWins,
        draws: batchResults.draws,
        accuracy: batchResults.accuracy,
        stockfishAccuracy: batchResults.stockfishAccuracy
    }

    $.ajax({
        url: '/api/generate_charts',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(chartData),
        success: function (response) {
            if (response.success) {
                // Show charts with cache-busting
                var timestamp = Date.now()

                $('#moveQualityChart').attr('src', '/api/charts/move_quality.png?' + timestamp).removeClass('hidden')
                $('#moveQualityPlaceholder').addClass('hidden')

                $('#gameResultsChart').attr('src', '/api/charts/game_results.png?' + timestamp).removeClass('hidden')
                $('#gameResultsPlaceholder').addClass('hidden')

                $('#accuracyChart').attr('src', '/api/charts/accuracy_comparison.png?' + timestamp).removeClass('hidden')
                $('#accuracyPlaceholder').addClass('hidden')

                // Expand charts section
                $('#chartsCollapse').addClass('expanded')
            }
        },
        error: function (error) {
            console.error('Failed to generate charts:', error)
        }
    })
}

// Toggle handlers for new sections
$('#moveHistoryToggle').on('click', function () {
    $('#moveHistoryCollapse').toggleClass('expanded')
})

$('#chartsToggle').on('click', function () {
    $('#chartsCollapse').toggleClass('expanded')
})

$('#offlineReportsToggle').on('click', function () {
    $('#offlineReportsCollapse').toggleClass('expanded')
})

$('#refreshReportsBtn').on('click', function () {
    var $btn = $(this)
    var originalText = $btn.html()

    $btn.prop('disabled', true).html('⏳ Memproses...')

    $.ajax({
        url: '/api/regenerate_comparison',
        type: 'POST',
        success: function (response) {
            if (response.success) {
                // Reload images with cache busting
                var timestamp = Date.now()
                $('.offline-chart').each(function () {
                    var currentSrc = $(this).attr('src').split('?')[0]
                    $(this).attr('src', currentSrc + '?' + timestamp)
                    $(this).show()
                    $(this).next('.chart-placeholder').hide()
                })
                alert(response.message)
            } else {
                alert(response.message)
            }
        },
        error: function (xhr) {
            alert('Gagal memperbarui laporan: ' + (xhr.responseJSON ? xhr.responseJSON.error : xhr.statusText))
        },
        complete: function () {
            $btn.prop('disabled', false).html(originalText)
        }
    })
})

// === Head-to-Head Mode ===
var h2hMode = false
var h2hPlaying = false

// Game mode selector
$('#gameModeSelect').on('change', function () {
    var mode = $(this).val()
    
    if (mode === 'head-to-head') {
        // Switch to H2H mode
        h2hMode = true
        $('#vsHumanConfig').addClass('hidden')
        $('#h2hConfig').removeClass('hidden')
        $('#startDemo').text('🎮 Mulai Head-to-Head')
        
        // Disable board dragging in H2H mode
        if (board) {
            board = null
        }
    } else {
        // Switch to VS Human mode
        h2hMode = false
        $('#vsHumanConfig').removeClass('hidden')
        $('#h2hConfig').addClass('hidden')
        $('#startDemo').text('🎮 Mulai Permainan')
        
        // Re-initialize board
        if (!board) {
            initBoard()
        }
    }
})

// Play H2H Auto Game
function playH2HAutoGame() {
    if (h2hPlaying) {
        return
    }
    
    h2hPlaying = true
    isDemoRunning = true
    
    // Get configurations
    var whiteMode = $('#h2hWhiteAlgo').val()
    var whiteDepth = parseInt($('#h2hWhiteDepth').val())
    var whiteRollout = parseInt($('#h2hWhiteRollout').val())
    
    var blackMode = $('#h2hBlackAlgo').val()
    var blackDepth = parseInt($('#h2hBlackDepth').val())
    var blackRollout = parseInt($('#h2hBlackRollout').val())
    
    // Reset game
    game = new Chess()
    if (board) {
        board.position(game.fen())
    }
    
    currentGameMoves = 0
    moveHistory = []
    
    // Show thinking indicator
    $thinking.removeClass('hidden')
    $('#startDemo').prop('disabled', true)
    $('#stopDemo').prop('disabled', false)
    $('#gameStatusText').text('Pertandingan Sedang Berlangsung...')
    
    // Send request to auto-play endpoint
    $.ajax({
        url: '/h2h/auto_play',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({
            white_mode: whiteMode,
            white_depth: whiteDepth,
            white_rollout: whiteRollout,
            black_mode: blackMode,
            black_depth: blackDepth,
            black_rollout: blackRollout
        }),
        success: function (response) {
            if (response.success) {
                displayH2HResults(response.result)
            } else {
                alert('Error: ' + (response.error || 'Unknown error'))
            }
        },
        error: function (xhr) {
            alert('Gagal menjalankan H2H: ' + (xhr.responseJSON ? xhr.responseJSON.error : xhr.statusText))
        },
        complete: function () {
            $thinking.addClass('hidden')
            h2hPlaying = false
            isDemoRunning = false
            $('#startDemo').prop('disabled', false)
            $('#stopDemo').prop('disabled', true)
        }
    })
}

// Display H2H Results
function displayH2HResults(result) {
    // Update game board to final position
    game.load(result.final_fen)
    if (board) {
        board.position(result.final_fen)
    }
    
    // Update status
    var statusText = ''
    if (result.winner === 'white') {
        statusText = '🤍 Putih Menang! (' + result.white.mode + ')'
    } else if (result.winner === 'black') {
        statusText = '🖤 Hitam Menang! (' + result.black.mode + ')'
    } else {
        statusText = '🤝 Permainan Seri!'
    }
    
    statusText += ' - ' + result.total_moves + ' langkah'
    statusText += ' (' + result.termination + ')'
    
    $('#gameStatusText').text(statusText)
    
    // Show detailed results
    var resultsHTML = '<div class="h2h-results" style="margin-top: 1rem; padding: 1rem; background: #f8fafc; border-radius: 8px;">'
    resultsHTML += '<h4 style="margin-bottom: 0.75rem;">📊 Hasil Head-to-Head</h4>'
    
    resultsHTML += '<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">'
    
    // White stats
    resultsHTML += '<div style="padding: 0.75rem; background: white; border-radius: 8px; border: 2px solid ' + (result.winner === 'white' ? '#10b981' : '#e5e7eb') + ';">'
    resultsHTML += '<div style="font-weight: 700; margin-bottom: 0.5rem;">🤍 Putih (' + result.white.mode + ')</div>'
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Depth: ' + result.white.depth + '</div>'
    if (result.white.mode === 'hybrid') {
        resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Rollout: ' + result.white.rollout + '</div>'
    }
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">Avg Time: ' + result.white.avg_time + 's</div>'
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Total Time: ' + result.white.total_time + 's</div>'
    resultsHTML += '</div>'
    
    // Black stats
    resultsHTML += '<div style="padding: 0.75rem; background: white; border-radius: 8px; border: 2px solid ' + (result.winner === 'black' ? '#10b981' : '#e5e7eb') + ';">'
    resultsHTML += '<div style="font-weight: 700; margin-bottom: 0.5rem;">🖤 Hitam (' + result.black.mode + ')</div>'
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Depth: ' + result.black.depth + '</div>'
    if (result.black.mode === 'hybrid') {
        resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Rollout: ' + result.black.rollout + '</div>'
    }
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b; margin-top: 0.5rem;">Avg Time: ' + result.black.avg_time + 's</div>'
    resultsHTML += '<div style="font-size: 0.875rem; color: #64748b;">Total Time: ' + result.black.total_time + 's</div>'
    resultsHTML += '</div>'
    
    resultsHTML += '</div>'
    
    resultsHTML += '<div style="text-align: center; padding: 0.75rem; background: white; border-radius: 8px;">'
    resultsHTML += '<strong>Total Moves:</strong> ' + result.total_moves + ' | '
    resultsHTML += '<strong>Result:</strong> ' + statusText
    resultsHTML += '</div>'
    
    resultsHTML += '</div>'
    
    // Insert results into page (after controls or in a dedicated section)
    $('.controls-section').after(resultsHTML)
    
    // Scroll to results
    $('html, body').animate({
        scrollTop: $('.h2h-results').offset().top - 100
    }, 500)
}

// Override start demo button for H2H mode
var originalStartDemo = null

$(document).ready(function () {
    // Store original start demo handler
    originalStartDemo = $('#startDemo').prop('onclick')
    
    // Replace with mode-aware handler
    $('#startDemo').off('click').on('click', function () {
        if (h2hMode) {
            playH2HAutoGame()
        } else {
            // Call original handler
            startDemo()
        }
    })
})

function initBoard() {
    var config = {
        draggable: true,
        position: 'start',
        onDragStart: onDragStart
    }
    board = Chessboard('board', config)
}
