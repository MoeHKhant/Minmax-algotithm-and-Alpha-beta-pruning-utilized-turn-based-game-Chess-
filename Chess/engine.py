
class CastleRights:
    def __init__(self, wK, bK, wQ, bQ):
        self.wK = wK  # White king-side
        self.bK = bK  # Black king-side
        self.wQ = wQ  # White queen-side
        self.bQ = bQ  # Black queen-side

class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enPassantMove=False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        # pawn promotion
        self.promotion = None
        if self.pieceMoved[1] == 'P' and (self.endRow == 0 or self.endRow == 7):
            self.promotion = self.pieceMoved[0] + 'Q'
        # en passant
        self.enPassantMove = enPassantMove
        if self.enPassantMove:
            self.pieceCaptured = 'wP' if self.pieceMoved == 'bP' else 'bP'
        self.isCastleMove = isCastleMove
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False

    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)

    def getRankFile(self, ro, cl):
        return Move.colsToFiles[cl] + Move.rowsToRanks[ro]

    def isCapture(self):
        return self.pieceCaptured != "--"

class GameState:
    def __init__(self, fen = None):
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {
            "P": self.getPawnMoves, "R": self.getRookMoves, "N": self.getKnightMoves,
            "B": self.getBishopMoves, "Q": self.getQueenMoves, "K": self.getKingMoves
        }
        
        self.whiteMove = True
        self.move_log = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.in_check = False
        self.checkmate = False
        self.stalemate = False
        self.enpassantPossible = ()
        self.enpassantPossibleLog = [self.enpassantPossible]
        self.currentCastlingRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRights.wK, self.currentCastlingRights.bK, self.currentCastlingRights.wQ, self.currentCastlingRights.bQ)]

    def makeMove(self, move):
      
        startRow, startCol = move.startRow, move.startCol
        endRow, endCol = move.endRow, move.endCol
       # print(f"Making move: {move.getChessNotation()} ({startRow},{startCol}) to ({endRow},{endCol})")  # Debug line
        # Make the move on the board
        self.board[startRow][startCol] = "--"
        self.board[endRow][endCol] = move.promotion if move.promotion else move.pieceMoved
        # Log the move
        self.move_log.append(move)

        # Toggle player turn
        self.whiteMove = not self.whiteMove

        # Update the king location if moved
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (endRow, endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (endRow, endCol)

        # En passant move
        if move.enPassantMove:
            self.board[move.startRow][move.endCol] = "--"  # capturing the pawn

        # Update the enpassantPossible variable
        if move.pieceMoved[1] == 'P' and abs(startRow - endRow) == 2:  # only on two squares pawn advance
            self.enpassantPossible = ((startRow + endRow) // 2, startCol)
        else:
            self.enpassantPossible = ()  # no en passant possible

        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # king side castle move
                self.board[move.endRow][move.endCol - 1] = self.board[move.endRow][move.endCol + 1]  # move the rook
                self.board[move.endRow][move.endCol + 1] = "--"
            else:  # queen side castle move
                self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 2]  # move the rook
                self.board[move.endRow][move.endCol - 2] = "--"

        self.enpassantPossibleLog.append(self.enpassantPossible)

        # Update castling rights whenever a rook or king is moved
        self.updateCastlingRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRights.wK, self.currentCastlingRights.bK, self.currentCastlingRights.wQ, self.currentCastlingRights.bQ))

    def undoMove(self):
        if len(self.move_log) != 0:
            move = self.move_log.pop()
            startRow, startCol = move.startRow, move.startCol
            endRow, endCol = move.endRow, move.endCol

            # Undo the move on the board
            self.board[startRow][startCol] = move.pieceMoved
            self.board[endRow][endCol] = move.pieceCaptured

            # Toggle player turn
            self.whiteMove = not self.whiteMove

            if move.pieceMoved == "wK":
                self.whiteKingLocation = (startRow, startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (startRow, startCol)

            # Undo en passant move
            if move.enPassantMove:
                self.board[endRow][endCol] = "--"  # leave the square where the pawn would have ended up
                self.board[startRow][endCol] = move.pieceCaptured  # restore the captured pawn

            self.enpassantPossibleLog.pop()
            self.enpassantPossible = self.enpassantPossibleLog[-1] if self.enpassantPossibleLog else ()

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:  # king side castle
                    self.board[move.endRow][move.endCol + 1] = self.board[move.endRow][move.endCol - 1]
                    self.board[move.endRow][move.endCol - 1] = '--'
                else:  # queen side castle
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.castleRightsLog.pop()
            self.currentCastlingRights = self.castleRightsLog[-1] if self.castleRightsLog else CastleRights(True, True, True, True)
            self.checkmate = False
            self.stalemate = False
            
    def updateCastlingRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastlingRights.wK = False
            self.currentCastlingRights.wQ = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:
                    self.currentCastlingRights.wQ = False
                elif move.startCol == 7:
                    self.currentCastlingRights.wK = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRights.bK = False
            self.currentCastlingRights.bQ = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:
                    self.currentCastlingRights.bQ = False
                elif move.startCol == 7:
                    self.currentCastlingRights.bK = False
                    
    def getValidMove(self):
        tempEnPassantPossible = self.enpassantPossible
        tempCastleRights = CastleRights(self.currentCastlingRights.wK, self.currentCastlingRights.bK, self.currentCastlingRights.wQ, self.currentCastlingRights.bQ)
        
        print("Current board position:")
        self.printBoard()
    
        # 1. Generate all moves
        moves = self.getAllPossibleMoves()
        if self.whiteMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)

        # 2. For each move, make the move
        for i in range(len(moves)-1, -1, -1):
            self.makeMove(moves[i])
            
            # 3. Generate all opponent's moves
            self.whiteMove = not self.whiteMove
            # 4. For each opponent's move, see if they attack our king
            if self.inCheck():
                
                moves.remove(moves[i])
            self.whiteMove = not self.whiteMove
            self.undoMove()

        # 5. Check for checkmate or stalemate
        if len(moves) == 0:  # checkmate or stalemate
            if self.inCheck():
                self.checkmate = True 
                for move in self.move_log:
                    print(move.getChessNotation())
            else:
                self.stalemate = True
                
                self.printBoard()
                
                for move in self.move_log:
                    print(move.getChessNotation())
            print("Board position after considering all moves:")
            self.printBoard()    
        else:
            self.enpassantPossible = tempEnPassantPossible
            self.currentCastlingRights = tempCastleRights

        return moves

    
    def AttackedSquare(self, r, c):
        self.whiteMove = not self.whiteMove
        opponentMoves = self.getAllPossibleMoves()
        self.whiteMove = not self.whiteMove  # switch turns back
        for move in opponentMoves:
            if move.endRow == r and move.endCol == c:  # square is under attack
                return True
        return False


    def inCheck(self):
        if self.whiteMove:
            return self.AttackedSquare(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.AttackedSquare(self.blackKingLocation[0], self.blackKingLocation[1])

    

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):  # Number of rows
            for c in range(len(self.board[r])):  # Number of columns in the selected row
                colour = self.board[r][c][0]
                if (colour == 'w' and self.whiteMove) or (colour == 'b' and not self.whiteMove):
                    piece = self.board[r][c][1]
                    if piece == 'P':
                        self.getPawnMoves(r, c, moves)
                    elif piece == 'R':
                        self.getRookMoves(r, c, moves)
                    elif piece == 'N':
                        self.getKnightMoves(r, c, moves)
                    elif piece == 'B':
                        self.getBishopMoves(r, c, moves)
                    elif piece == 'Q':
                        self.getQueenMoves(r, c, moves)
                    elif piece == 'K':
                        self.getKingMoves(r, c, moves)
        return moves

    def getPawnMoves(self, r, c, moves):
        if self.whiteMove:
            if r - 1 >= 0:
                if self.board[r-1][c] == "--":  # Single step forward
                    moves.append(Move((r, c), (r-1, c), self.board))
                    if r == 6 and self.board[r-2][c] == "--":  # Double step forward
                        moves.append(Move((r, c), (r-2, c), self.board))
                if c - 1 >= 0:
                    if self.board[r-1][c-1][0] == 'b':  # Capture to the left
                        moves.append(Move((r, c), (r-1, c-1), self.board))
                    elif (r-1, c-1) == self.enpassantPossible:  # En passant capture to the left
                        moves.append(Move((r, c), (r-1, c-1), self.board, enPassantMove=True))
                if c + 1 <= 7:
                    if self.board[r-1][c+1][0] == 'b':  # Capture to the right
                        moves.append(Move((r, c), (r-1, c+1), self.board))
                    elif (r-1, c+1) == self.enpassantPossible:  # En passant capture to the right
                        moves.append(Move((r, c), (r-1, c+1), self.board, enPassantMove=True))
        else:
            if r + 1 <= 7:
                if self.board[r+1][c] == "--":  # Single step forward
                    moves.append(Move((r, c), (r+1, c), self.board))
                    if r == 1 and self.board[r+2][c] == "--":  # Double step forward
                        moves.append(Move((r, c), (r+2, c), self.board))
                if c - 1 >= 0:
                    if self.board[r+1][c-1][0] == 'w':  # Capture to the left
                        moves.append(Move((r, c), (r+1, c-1), self.board))
                    elif (r+1, c-1) == self.enpassantPossible:  # En passant capture to the left
                        moves.append(Move((r, c), (r+1, c-1), self.board, enPassantMove=True))
                if c + 1 <= 7:
                    if self.board[r+1][c+1][0] == 'w':  # Capture to the right
                        moves.append(Move((r, c), (r+1, c+1), self.board))
                    elif (r+1, c+1) == self.enpassantPossible:  # En passant capture to the right
                        moves.append(Move((r, c), (r+1, c+1), self.board, enPassantMove=True))

    def getRookMoves(self, r, c, moves):
        direction = ((-1, 0), (0, -1), (1, 0), (0, 1))  # up, left, down, right
        enemyPiece = "b" if self.whiteMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyPiece:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-1, -2), (1, -2), (2, -1), (2, 1), (1, 2), (-1, 2), (-2, 1))
        allyPiece = "w" if self.whiteMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyPiece:
                    moves.append(Move((r, c), (endRow, endCol), self.board))

    def getBishopMoves(self, r, c, moves):
        direction = ((-1, -1), (1, -1), (-1, 1), (1, 1))  # up-left, down-left, up-right, down-right
        enemyPiece = "b" if self.whiteMove else "w"
        for d in direction:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyPiece:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break
                else:
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyPiece = "w" if self.whiteMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyPiece:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
        


    def getCastleMoves(self, r, c, moves):
        if self.AttackedSquare(r,c):
            return #can't castle while we are in check
        if (self.whiteMove and self.currentCastlingRights.wK) or (not self.whiteMove and self.currentCastlingRights.bK):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteMove and self.currentCastlingRights.wQ) or (not self.whiteMove and self.currentCastlingRights.bQ):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c + 1] == "--" and self.board[r][c + 2] == "--":
            if not self.AttackedSquare(r, c + 1) and not self.AttackedSquare(r, c + 2):
                moves.append(Move((r, c), (r, c + 2), self.board, isCastleMove=True))

    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c - 1] == "--" and self.board[r][c - 2] == "--" and self.board[r][c - 3] == "--":
            if not self.AttackedSquare(r, c - 1) and not self.AttackedSquare(r, c - 2):
                moves.append(Move((r, c), (r, c - 2), self.board, isCastleMove=True))
    def printBoard(self):
        for row in self.board:
            print(" ".join(row))
        print()



