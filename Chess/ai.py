import copy
import random


# Constants
pieceScore = {"K": 0, "Q": 10, "R": 5, "B": 3, "N": 3, "P": 1}
CHECKMATE = 1000
STALEMATE = 0
DEPTH = 2  # Increased depth for better evaluation

# Piece-square tables
pieceSquareTables = {
    'P': [[0, 0, 0, 0, 0, 0, 0, 0],
          [5, 5, 5, 5, 5, 5, 5, 5],
          [1, 1, 2, 3, 3, 2, 1, 1],
          [0.5, 0.5, 1, 2.5, 2.5, 1, 0.5, 0.5],
          [0, 0, 0, 2, 2, 0, 0, 0],
          [0.5, -0.5, -1, 0, 0, -1, -0.5, 0.5],
          [0.5, 1, 1, -2, -2, 1, 1, 0.5],
          [0, 0, 0, 0, 0, 0, 0, 0]],
    'N': [[-5, -4, -3, -3, -3, -3, -4, -5],
          [-4, -2, 0, 0, 0, 0, -2, -4],
          [-3, 0, 1, 1.5, 1.5, 1, 0, -3],
          [-3, 0.5, 1.5, 2, 2, 1.5, 0.5, -3],
          [-3, 0, 1.5, 2, 2, 1.5, 0, -3],
          [-3, 0.5, 1, 1.5, 1.5, 1, 0.5, -3],
          [-4, -2, 0, 0.5, 0.5, 0, -2, -4],
          [-5, -4, -3, -3, -3, -3, -4, -5]],
    'B': [[-2, -1, -1, -1, -1, -1, -1, -2],
          [-1, 0, 0, 0, 0, 0, 0, -1],
          [-1, 0, 0.5, 1, 1, 0.5, 0, -1],
          [-1, 0.5, 0.5, 1, 1, 0.5, 0.5, -1],
          [-1, 0, 1, 1, 1, 1, 0, -1],
          [-1, 1, 1, 1, 1, 1, 1, -1],
          [-1, 0.5, 0, 0, 0, 0, 0.5, -1],
          [-2, -1, -1, -1, -1, -1, -1, -2]],
    'R': [[0, 0, 0, 0, 0, 0, 0, 0],
          [0.5, 1, 1, 1, 1, 1, 1, 0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [-0.5, 0, 0, 0, 0, 0, 0, -0.5],
          [0, 0, 0, 0.5, 0.5, 0, 0, 0]],
    'Q': [[-2, -1, -1, -0.5, -0.5, -1, -1, -2],
          [-1, 0, 0, 0, 0, 0, 0, -1],
          [-1, 0, 0.5, 0.5, 0.5, 0.5, 0, -1],
          [-0.5, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
          [0, 0, 0.5, 0.5, 0.5, 0.5, 0, -0.5],
          [-1, 0.5, 0.5, 0.5, 0.5, 0.5, 0, -1],
          [-1, 0, 0.5, 0, 0, 0, 0, -1],
          [-2, -1, -1, -0.5, -0.5, -1, -1, -2]],
    'K': [[2, 3, 1, 0, 0, 1, 3, 2],
          [2, 3, 1, 0, 0, 1, 3, 2],
          [1, 2, 0, 0, 0, 0, 2, 1],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [0, 0, 0, 0, 0, 0, 0, 0],
          [1, 2, 0, 0, 0, 0, 2, 1],
          [2, 3, 1, 0, 0, 1, 3, 2],
          [2, 3, 1, 0, 0, 1, 3, 2]]
}

# Transposition table
transposition_table = {}

def scoreMaterial(board):
    score = 0
    for rowIndex, row in enumerate(board):
        for colIndex, square in enumerate(row):
            if square != "--":
                piece = square[1]
                if square[0] == 'w':
                    score += pieceScore[piece]
                    score += pieceSquareTables[piece][rowIndex][colIndex] * 0.1
                elif square[0] == 'b':
                    score -= pieceScore[piece]
                    score -= pieceSquareTables[piece][7-rowIndex][7-colIndex] * 0.1
    return score

def evaluateBoard(gs):
    score = scoreMaterial(gs.board)   
    return score

def minimaxAlphaBeta(gs, validMoves, depth, alpha, beta, isMaximizing):
    board_hash = hash(str(gs.board))
    if board_hash in transposition_table:
        print(f"Cache hit: {board_hash}")
        return transposition_table[board_hash]

    if depth == 0 or gs.checkmate or gs.stalemate:
        score = evaluateBoard(gs)
        transposition_table[board_hash] = score
        return score

    if isMaximizing:
        maxScore = -CHECKMATE
        for move in validMoves:
            # Deep copy game state for this move
            gs_copy = copy.deepcopy(gs)
            gs_copy.makeMove(move)
            score = minimaxAlphaBeta(gs_copy, gs_copy.getValidMove(), depth-1, alpha, beta, False)
            maxScore = max(maxScore, score)
            alpha = max(alpha, score)
            if beta <= alpha:
                break
        transposition_table[board_hash] = maxScore
        return maxScore
    else:
        minScore = CHECKMATE
        for move in validMoves:
            # Deep copy game state for this move
            gs_copy = copy.deepcopy(gs)
            gs_copy.makeMove(move)
            score = minimaxAlphaBeta(gs_copy, gs_copy.getValidMove(), depth-1, alpha, beta, True)
            minScore = min(minScore, score)
            beta = min(beta, score)
            if beta <= alpha:
                break
        transposition_table[board_hash] = minScore
        return minScore


def findBestMove(gs, validMoves):
    bestMove = None
    bestScore = -CHECKMATE if gs.whiteMove else CHECKMATE
    alpha = -CHECKMATE
    beta = CHECKMATE

    random.shuffle(validMoves)  # Shuffle to ensure randomness in move ordering

    for move in validMoves:
        # Deep copy game state for this move
        gs_copy = copy.deepcopy(gs)
        gs_copy.makeMove(move)
        score = minimaxAlphaBeta(gs_copy, gs_copy.getValidMove(), DEPTH-1, alpha, beta, not gs.whiteMove)

        if (gs.whiteMove and score > bestScore) or (not gs.whiteMove and score < bestScore):
            bestScore = score
            bestMove = move

    return bestMove


def findRandomMoves(validMoves):
    return random.choice(validMoves) if validMoves else None
