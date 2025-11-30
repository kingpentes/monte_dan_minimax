"""
Static evaluator based on material count.
Values: Pawn=10, Knight=30, Bishop=30, Rook=50, Queen=90, King=900
"""

import chess

# Material values based on standard simplified evaluation
PIECE_VALUES = {
    chess.PAWN: 10,
    chess.KNIGHT: 30,
    chess.BISHOP: 30,
    chess.ROOK: 50,
    chess.QUEEN: 90,
    chess.KING: 900
}

def evaluate_static(board: chess.Board) -> int:
    """
    Calculates the material score of the board.
    Positive for White advantage, negative for Black advantage.
    """
    if board.is_game_over():
        if board.is_checkmate():
            return -9999 if board.turn == chess.WHITE else 9999
        return 0 # Draw

    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            value = PIECE_VALUES[piece.piece_type]
            if piece.color == chess.WHITE:
                score += value
            else:
                score -= value
    return score
