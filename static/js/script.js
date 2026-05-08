var board = null;
var game = new Chess();
var $eval = $('#eval');

// Triggers when a human attempts to move a piece
function onDrop(source, target) {
    // Check if the move is legal
    var move = game.move({
        from: source,
        to: target,
        promotion: 'q' // Always promote to Queen for simplicity
    });

    // If illegal, snap the piece back to where it was
    if (move === null) return 'snapback';

    // If legal, wait 250ms and then ask the AI for its move
    window.setTimeout(makeAiMove, 250);
}

// Sends the board state to Python and waits for a response
function makeAiMove() {
    var difficulty = $('#difficulty').val();
    
    $.ajax({
        url: '/make_move',
        type: 'POST',
        contentType: 'application/json',
        data: JSON.stringify({ fen: game.fen(), difficulty: difficulty }),
        success: function(data) {
            // Apply the AI's move
            if (data.move) {
                game.move(data.move, { sloppy: true });
                board.position(game.fen());
            }
            
            // Update the UI metrics
            $eval.text(data.evaluation);
            renderGraveyard(data.graveyard);
            
            if (game.game_over()) alert("Game Over!");
        },
        error: function(err) {
            console.error("Error communicating with backend:", err);
            alert("Connection error with the Python server.");
        }
    });
}

// Draws the defeated pieces on the screen
function renderGraveyard(graveyardData) {
    if (!graveyardData) return;
    
    var whiteHtml = '';
    var blackHtml = '';
    
    // Base URL to pull piece images from the official CDN
    var baseUrl = 'https://chessboardjs.com/img/chesspieces/wikipedia/';

    graveyardData.white_defeated.forEach(function(piece) {
        whiteHtml += `<img src="${baseUrl}${piece}.png">`;
    });
    
    graveyardData.black_defeated.forEach(function(piece) {
        blackHtml += `<img src="${baseUrl}${piece}.png">`;
    });

    $('#white-graveyard').html(whiteHtml);
    $('#black-graveyard').html(blackHtml);
}

// Resets everything to a fresh game state
function resetGame() {
    game.reset();
    board.start();
    $eval.text("0.0");
    $('#white-graveyard').empty();
    $('#black-graveyard').empty();
}

// Board Configuration
var config = {
    draggable: true,
    position: 'start',
    onDrop: onDrop,
    // Forces the board to download images directly from the internet
    pieceTheme: 'https://chessboardjs.com/img/chesspieces/wikipedia/{piece}.png'
};

// Initialize the board
board = ChessBoard('board', config);