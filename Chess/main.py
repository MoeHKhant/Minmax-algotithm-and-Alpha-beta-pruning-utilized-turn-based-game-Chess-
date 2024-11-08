import pygame as py
import sys
import engine, ai
from board import *

# Global dictionary for images.
IMAGES = {}

def loadImages():
    pieces = ['wP', 'wR', 'wN', 'wB', 'wQ', 'wK', 'bP', 'bR', 'bN', 'bB', 'bQ', 'bK']
    for piece in pieces:
        image = py.image.load("images/" + piece + ".png")
        new_size = (int(SQ_SIZE * 0.8), int(SQ_SIZE * 0.8))
        IMAGES[piece] = py.transform.scale(image, new_size)

# The main driver
def main():
    py.init()
    py.display.set_caption('Chess')
    screen = py.display.set_mode((WIDTH + SIDEBAR_WIDTH, HEIGHT))
    clock = py.time.Clock()
    moveLogFont = py.font.SysFont("Arial", 12, False, False)
    gs = engine.GameState()
    validMoves = gs.getValidMove()
    animate = False
    moveMade = False
    loadImages()
    running = True
    selectedSQ = ()
    playerClick = []
    gameOver = False
    player1 =  True#if a human is playing it is true
    player2 = True

    while running:
        humanTurn = (gs.whiteMove and player1) or (not gs.whiteMove and player2)
        for event in py.event.get():
            if event.type == py.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = py.mouse.get_pos()
                    if WIDTH < location[0] < WIDTH + SIDEBAR_WIDTH:
                        if 0 < location[1] < BUTTON_HEIGHT:  # Undo moves
                            gs.undoMove()
                            moveMade = True
                            animate = False
                            gameOver = False
                            validMoves = gs.getValidMove()
                        elif BUTTON_HEIGHT < location[1] < 2 * BUTTON_HEIGHT:  # Reset function
                            gs = engine.GameState()  # Reset the game state
                            validMoves = gs.getValidMove()
                            selectedSQ = ()
                            playerClick = []
                            moveMade = False
                            animate = False
                            gameOver = False
                    else:
                        col = location[0] // SQ_SIZE
                        row = location[1] // SQ_SIZE
                        if selectedSQ == (row, col):
                            selectedSQ = ()
                            playerClick = []
                        else:
                            selectedSQ = (row, col)
                            playerClick.append(selectedSQ)

                        if len(playerClick) == 2:
                            move = engine.Move(playerClick[0], playerClick[1], gs.board)
                            print(move.getChessNotation())
                            for i in range(len(validMoves)):
                                if move == validMoves[i]:
                                    gs.makeMove(validMoves[i])
                                    moveMade = True
                                    animate = True
                                    selectedSQ = ()
                                    playerClick = []

                            if not moveMade:
                                playerClick = [selectedSQ]

           #AI move finder
        if not gameOver and not humanTurn:
            AIMove = ai.findBestMove(gs, validMoves)
            if AIMove == None:
                AIMove = ai.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True


        if moveMade:
            if animate:
                animateMove(gs.move_log[-1], screen, gs.board, clock)
            validMoves = gs.getValidMove()
            moveMade = False
            animate = False
        if event.type == py.QUIT:
                running = False
        drawGameState(screen, gs, validMoves, selectedSQ, moveLogFont)

        
        if gs.checkmate or gs.stalemate:
            gameOver = True
            if gs.checkmate:
                winner = 'w' if not gs.whiteMove else 'b'
                drawText(screen, f"{winner} wins by checkmate!", py.Color('red'), WIDTH / 2, HEIGHT / 2)
            elif gs.stalemate:
                drawText(screen, "Stalemate!", py.Color('red'), WIDTH / 2, HEIGHT / 2)

        py.display.flip()
        clock.tick(60)
    py.quit()
    sys.exit()


'''
Highlight squares
'''
def highlightSquares(screen, gs, validMoves, selectedSQ):
    if selectedSQ != ():
        r, c = selectedSQ
        if gs.board[r][c][0] == ('w' if gs.whiteMove else 'b'):  # for a piece that can be moved
            surface = py.Surface((SQ_SIZE, SQ_SIZE))
            surface.set_alpha(150)  # transparency value (0-255)
            surface.fill(('red'))
            screen.blit(surface, (c * SQ_SIZE, r * SQ_SIZE))
            # highlight moves
            surface.fill(py.Color('light green'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(surface, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

# Current Game State
def drawGameState(screen, gs, validMoves, selectedSQ, moveLogFont):
    # Draw the entire screen (board and sidebar)
    drawBoard(screen)  # Draw the squares on the board
    highlightSquares(screen, gs, validMoves, selectedSQ)
    drawPieces(screen, gs.board)  # Draw the pieces on top of those squares
    drawSidebar(screen)  # Draw the sidebar
    drawMoveLog(screen, gs, moveLogFont, WIDTH + 10, 2 * BUTTON_HEIGHT + 20)

def drawBoard(screen):
    global colors
    colors = [py.Color("grey"), py.Color("white")]
    font = py.font.SysFont(None, 24)
    for r in range(DM):
        for c in range(DM):
            color = colors[(r + c) % 2]
            py.draw.rect(screen, color, py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
            if c == 0:  # Draw row indicators
                label = font.render(str(8-r), True, py.Color('black'))
                screen.blit(label, (5, r * SQ_SIZE + 5))
            if r == 7:  # Draw column indicators
                label = font.render(chr(c + ord('a')), True, py.Color('black'))
                screen.blit(label, (c * SQ_SIZE + SQ_SIZE - 20, HEIGHT - 20))

def drawPieces(screen, board):
    for r in range(DM):
        for c in range(DM):
            piece = board[r][c]
            if piece != "--":  # Not an empty square
                piece_image = IMAGES[piece]
                piece_rect = piece_image.get_rect(center=(c * SQ_SIZE + SQ_SIZE // 2, r * SQ_SIZE + SQ_SIZE // 2))
                screen.blit(piece_image, piece_rect)

def drawSidebar(screen):
    # Draw the sidebar background
    py.draw.rect(screen, py.Color('black'), py.Rect(WIDTH, 0, SIDEBAR_WIDTH, HEIGHT))

    # Draw the undo button
    font = py.font.SysFont(None, 36)
    undo_button_rect = py.Rect(WIDTH + 10, 10, SIDEBAR_WIDTH - 20, BUTTON_HEIGHT - 20)
    py.draw.rect(screen, py.Color('gray'), undo_button_rect)
    undo_label = font.render('Undo', True, py.Color('black'))
    label_rect = undo_label.get_rect(center=undo_button_rect.center)
    screen.blit(undo_label, label_rect)

    # Draw the reset button
    reset_button_rect = py.Rect(WIDTH + 10, BUTTON_HEIGHT + 10, SIDEBAR_WIDTH - 20, BUTTON_HEIGHT - 20)
    py.draw.rect(screen, py.Color('gray'), reset_button_rect)
    reset_label = font.render('Reset', True, py.Color('black'))
    reset_label_rect = reset_label.get_rect(center=reset_button_rect.center)
    screen.blit(reset_label, reset_label_rect)

def drawMoveLog(screen, gs, font, x, y):
    moveLogRect = py.Rect(x, y, SIDEBAR_WIDTH - 20, HEIGHT - (2 * BUTTON_HEIGHT + 20))
    py.draw.rect(screen, py.Color('white'), moveLogRect)
    moveLog = gs.move_log
    moveTexts = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + ". " + moveLog[i].getChessNotation() + " "
        if i + 1 < len(moveLog):  # Make sure black made a move too
            moveString += moveLog[i + 1].getChessNotation()
        moveTexts.append(moveString)

    moveTexts = ["{}.".format(i//2+1) + " " + moveLog[i].getChessNotation() + " " + (moveLog[i+1].getChessNotation() if i+1 < len(moveLog) else "") for i in range(0, len(moveLog), 2)]
    
    padding = 5
    line_spacing = 2
    text_y = moveLogRect.top + padding
    for i, text in enumerate(moveTexts):
        textObject = font.render(text, True, py.Color('black'))
        textLocation = moveLogRect.move(padding, text_y + i * (textObject.get_height() + line_spacing))
        screen.blit(textObject, textLocation)

'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 5  # 10 frames to move one square
    frameCount = (abs(dR) + abs(dC))* framesPerSquare
    for frame in range(frameCount + 1):
        r, c = ((move.startRow + dR * frame / frameCount, move.startCol + dC * frame / frameCount))
        drawBoard(screen)
        drawPieces(screen, board)
        # erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = py.Rect(move.endCol * SQ_SIZE, move.endRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
        py.draw.rect(screen, color, endSquare)
        # draw captured piece
        if move.pieceCaptured != '--':
            if move.enPassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow -1
                endSquare = py.Rect(move.endCol * SQ_SIZE, enPassantRow * SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        # draw moving piece
        screen.blit(IMAGES[move.pieceMoved], py.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))
        py.display.flip()
        clock.tick(60)

def drawText(screen, text, color, x, y):
    font = py.font.SysFont('arial', 32, True, False)
    textObject = font.render(text, True, color)
    textRect = textObject.get_rect(center=(x, y))
    screen.blit(textObject, textRect)

if __name__ == "__main__":
    main()
