from flask import Flask, render_template, request, jsonify
import chess
import math
import random

app = Flask(__name__)

class ChessAI:
    def __init__(self, difficulty):
        self.difficulty = int(difficulty)
        # Standard pure material values for evaluation and UI
        self.PIECE_VALUES = {chess.PAWN: 10, chess.KNIGHT: 30, chess.BISHOP: 30, 
                             chess.ROOK: 50, chess.QUEEN: 90, chess.KING: 900}

    def evaluate_board(self, board):
        """Pure material evaluation - strictly checks what pieces are alive."""
        if board.is_checkmate():
            return -9999 if board.turn else 9999
        score = 0
        for square in chess.SQUARES:
            piece = board.piece_at(square)
            if piece:
                val = self.PIECE_VALUES.get(piece.piece_type, 0)
                score += val if piece.color == chess.WHITE else -val
        return score if board.turn == chess.WHITE else -score

    def minimax(self, board, depth, alpha, beta, maximizing):
        """Standard Minimax algorithm with Alpha-Beta Pruning."""
        if depth == 0 or board.is_game_over():
            return self.evaluate_board(board), None
        
        best_move = None
        if maximizing:
            max_eval = -math.inf
            for move in board.legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, False)
                board.pop()
                if eval_score > max_eval:
                    max_eval, best_move = eval_score, move
                alpha = max(alpha, eval_score)
                if beta <= alpha: break
            return max_eval, best_move
        else:
            min_eval = math.inf
            for move in board.legal_moves:
                board.push(move)
                eval_score, _ = self.minimax(board, depth - 1, alpha, beta, True)
                board.pop()
                if eval_score < min_eval:
                    min_eval, best_move = eval_score, move
                beta = min(beta, eval_score)
                if beta <= alpha: break
            return min_eval, best_move

def get_graveyard(board):
    """Calculates exactly which pieces have been defeated by comparing to a starting board."""
    start_counts = {chess.PAWN: 8, chess.KNIGHT: 2, chess.BISHOP: 2, chess.ROOK: 2, chess.QUEEN: 1}
    symbols = {chess.PAWN: 'P', chess.KNIGHT: 'N', chess.BISHOP: 'B', chess.ROOK: 'R', chess.QUEEN: 'Q'}
    
    white_captured = []
    black_captured = []
    
    for pt, count in start_counts.items():
        w_missing = count - len(board.pieces(pt, chess.WHITE))
        b_missing = count - len(board.pieces(pt, chess.BLACK))
        
        # Format for chessboard.js (e.g., 'wP' for White Pawn)
        white_captured.extend(['w' + symbols[pt]] * w_missing)
        black_captured.extend(['b' + symbols[pt]] * b_missing)
        
    return {'white_defeated': white_captured, 'black_defeated': black_captured}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.json
    fen = data.get('fen')
    difficulty = data.get('difficulty', 3)
    
    board = chess.Board(fen)
    ai = ChessAI(difficulty)
    
    # AI Decision Making
    if difficulty == 1:
        move = random.choice(list(board.legal_moves)) if list(board.legal_moves) else None
    else:
        depth = 2 if difficulty == 2 else 3
        _, move = ai.minimax(board, depth, -math.inf, math.inf, True)
    
    # Apply the move physically to the board state
    if move:
        board.push(move)
        
    # Calculate absolute evaluation (always White perspective for the UI display)
    eval_raw = ai.evaluate_board(board)
    absolute_eval = eval_raw if board.turn == chess.WHITE else -eval_raw
    
    return jsonify({
        'move': move.uci() if move else None,
        'evaluation': round(absolute_eval / 10.0, 1),
        'graveyard': get_graveyard(board)
    })

if __name__ == '__main__':
    app.run(debug=True)