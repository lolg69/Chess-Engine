'''
The main block consist of all the inputs that we will give to the engine .Also it will keep an eye on the gamestop.
'''
from tkinter import font
import pygame as p
import ChessEngine
import SmartMoveFinder

WIDTH = HEIGHT = 512 #width and height should be same as it is square board.
                     #512 is max that we could achieve as so that the picture would look good
DIMENSION = 8 # the dimensions of a chess board are 8x8
SQ_SIZE = HEIGHT // DIMENSION #As 512 is in the power of 8 it makes sense
MAX_FPS = 15 # for animations
IMAGES = {} # we create a dictionary for our images
'''now we are going to define a method that will initialize a global dictionary of images'''
'''loading images is an expensive operation so we only do this one time'''

def load_images():
    pieces = ['wp','wR','wN','wB','wQ','wK','bp','bR','bN','bB','bQ','bK']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"),(SQ_SIZE,SQ_SIZE)) # pygame.image.load helps us load the images.
        # now we can access the images by just typing IMAGES['wp']

'''This is the main driver of our code . This is where we will handle user input and updating the graphics'''
def main():
    p.init()
    screen = p.display.set_mode((WIDTH,HEIGHT)) #creates a window for us.
    clock = p.time.Clock() # Exploiting the clock feature of pygame
    screen.fill(p.Color("white"))
    gs = ChessEngine.GameState()
    validMoves =gs.getValidMoves()
    moveMade = False #flag variable for when a move is made
    animate = False #flag variable for when we should animate a move
    load_images() # we will load this only once as it is very costly
    running = True
    sqSelected = () # no square is selected initially , keep track of the last click of the user.
    playerClicks = [] #keep track of player clicks , containing two tuples [(6,4)(4,4)]
    gameOver = False  
    playerOne = True # If a human is playing white then this is true , if an AI is playing then it is false 
    playerTwo = False # Same as above but for black
    while running:
        humanTurn = (gs.whiteToMove and playerOne) or (not gs.whiteToMove and playerTwo)
        for e in p.event.get(): #because we need the event continuosly to display the board
            if e.type == p.QUIT:
                running = False
            #mouse handlers
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver and humanTurn:
                    location = p.mouse.get_pos() # (x,y) location of the mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row,col): # this means the user clicked on the same spot twice
                        sqSelected =() #deselect
                        playerClicks = [] # clearing player clicks
                    else:
                        sqSelected = (row,col)
                        playerClicks.append(sqSelected) # appending both 1st and 2nd click
                    if len(playerClicks) == 2 : #after 2nd click
                        move = ChessEngine.Move(playerClicks[0],playerClicks[1],gs.board)
                        print(move.getChessNotation())
                        for i in range(len(validMoves)):
                            if move == validMoves[i]:
                                gs.makeMove(validMoves[i])   
                                moveMade = True
                                animate = True
                                sqSelected = () # reset user clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]

            #key handlers
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed 
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    validMoves = gs.getValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    animate = False
                    gameOver = False

        #AI move finder
        if not gameOver and not humanTurn:
            AIMove = SmartMoveFinder.findBestMove(gs, validMoves)
            if AIMove is None:
                AIMove = SmartMoveFinder.findRandomMove(validMoves)
            gs.makeMove(AIMove)
            moveMade = True
            animate = True

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            validMoves = gs.getValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen ,gs ,validMoves , sqSelected)

        if gs.checkmate:
            gameOver = True
            if gs.whiteToMove:
                drawText(screen, 'Black wins by checkmate')
            else:
                drawText(screen, 'White wins by checkmate')
        elif gs.stalemate:
            gameOver = True
            drawText(screen, 'Stalemate')


        clock.tick(MAX_FPS) #it calculates the amount milliseconds passed before the last frame was updated
        p.display.flip() #This will update the contents of the entire screen

'''
Highlight the square selected and moves for piece selected
'''

def highlightSquares(screen, gs, validMoves, sqSelected):
    if sqSelected != ():
        r,c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteToMove else 'b'):#sqSelected is a piece that can be moved
            #highlight the selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) #transparency value -> 0 transparent -> 255 opaque
            s.fill(p.Color('blue'))
            screen.blit(s, (c*SQ_SIZE, r*SQ_SIZE))
            #highlight moves from that square
            s.fill(p.Color('yellow'))
            for move in validMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol*SQ_SIZE, move.endRow*SQ_SIZE))
                    


'''Responsible for all the graphics within the current game state'''
def drawGameState(screen,gs,validMoves, sqSelected):
    drawBoard(screen) #draw squares on the board
    highlightSquares(screen, gs, validMoves, sqSelected)
    drawPieces(screen,gs.board) #draw pieces on top of those squares


''' Draw squares on the board'''
def drawBoard(screen):
    global colors
    colors = [p.Color("white") , p.Color("gray")]
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            color = colors[((r+c) % 2)]
            p.draw.rect(screen,color,p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE,SQ_SIZE))

'''Draw pieces on the board using the current gamestate on the board'''
def drawPieces(screen,board):
    for r in range(DIMENSION):
        for c in range(DIMENSION):
            piece = board[r][c]
            if piece != "--": #not empty square
                screen.blit(IMAGES[piece],p.Rect(c*SQ_SIZE,r*SQ_SIZE,SQ_SIZE,SQ_SIZE))


'''
Animating a move
'''
def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c =(move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol) % 2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        # draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw the moveing piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)        

def drawText(screen , text):
    font = p.font.SysFont("Helvitca", 32, True, False)
    textObject = font.render(text, 0, p.Color('Gray'))
    textLocation = p.Rect(0, 0, WIDTH, HEIGHT).move(WIDTH/2 - textObject.get_width()/2,HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0 , p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))



if __name__ == "__main__": '''This is generally called in python because the it helps in the ok lol'''
main()                                                                        
















