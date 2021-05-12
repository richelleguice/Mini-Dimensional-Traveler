#################################################
# TERM PROJECT: Tomb of the Mask Game
# name: Richelle Guice
# andrew id: rguice
#################################################

from cmu_112_graphics import *
import random, string, math, time

#print('Hello World')

#https://www.cs.cmu.edu/~112/notes/notes-2d-lists.html
def make2dList(rows, cols, color):
    return [ ([(color, 0)] * cols) for row in range(rows) ]

def gameDimensions():
    rows = 126
    cols = 11
    cellSize = 25
    margin = 40
    return (rows, cols, cellSize, margin)

def appStarted(app):
    app.isGameStart = True
    app.typeName = True
    app.userName = ''
    app.leaderboardChanged = False
    app.leaderboard = []

    app.score = 0
    app.scrollD = 0

    # set game colors
    app.backgroundColor = 'magenta'
    app.emptyColor = 'black'
    app.mazeColor = 'magenta'
    app.playerColor = 'black'
    app.spikeColor = 'black' 
    app.coinColor = 'yellow'
    # create board wit dimensions
    (rows, cols, cellSize, margin) = gameDimensions()
    app.rows = rows
    app.cols = cols
    app.cellSize = cellSize
    app.margin = margin
    # make board
    app.board = make2dList(app.rows, app.cols, app.emptyColor)

    # Travel Boy and scaled
    # https://tomb-of-the-mask.fandom.com/wiki/Masks
    app.character = app.loadImage('travel_boy_new.png')
    app.character = app.scaleImage(app.character, 1/8)
    app.playerRow = 0
    app.playerCol = 5
    
    # Missile obstacle and scaled
    # https://tomb-of-the-mask.fandom.com/wiki/Masks
    app.missile = app.loadImage('missile.jpg')
    app.missile = app.scaleImage(app.missile, 1/2)    
    app.missileColor = 'cyan'
    app.missileShootTimer = 0
    app.missileList = []
    app.missileCollision = False

    # Spike obtacle and scaled
    # https://tomb-of-the-mask.fandom.com/wiki/Masks
    app.spike = app.loadImage('spike.png')
    app.spike = app.scaleImage(app.spike, 1/4)
    app.spikeRef = app.loadImage('spikeRef.png')
    app.spikeRef = app.scaleImage(app.spikeRef, 1/4)
    app.spikeCollision = False

    # Pause and Play button (scaled)
    # https://tomb-of-the-mask.fandom.com/wiki/Masks
    app.pauseButton = app.loadImage('pause.png')
    app.pauseButton = app.scaleImage(app.pauseButton, 1/4)
    app.playButton = app.loadImage('play.png')
    app.paused = False
    app.pauseScreen = False

    # Exit = victory
    # https://tomb-of-the-mask.fandom.com/wiki/Masks
    app.exitDoor = app.loadImage('exitDoor.png')
    app.exitDoor = app.scaleImage(app.exitDoor, 1/3)
    app.exitColor = 'pink'

    app.wallRow = []
    app.wallCol = []
    app.exitSpace = []

    app.coinRow = 1
    app.coinCol = 5
    
    app.lavaScroll = 0
    app.lavaCollision = False

    app.newIncrease = app.rows/3
    app.level = 1


    codeMaze(app)
    makeMaze(app)
    placeExit(app)
    placeObstacleMissile(app)

    app.gameOver = False

# trigger game to start
def mousePressed(app, event):
    if app.isGameStart == True:
        app.isGameStart = False
    
    if app.typeName: 
        name = app.getUserInput('Type a username...')
        app.userName = name
        app.typeName = not app.typeName

    gameWidth = (2 * app.margin) + (app.cellSize*app.cols)
    if (gameWidth-(3*app.margin/4) <= event.x <= gameWidth-(app.margin/4)
                        and app.margin/2 - 10 <= event.y <= app.margin/2 + 10):
        app.paused = not app.paused
        app.pauseScreen = True
    half = app.cellSize/2
    if (app.pauseScreen and 
        (app.margin+(5*app.cellSize)-9 <= event.x <= app.margin+(6*app.cellSize)+9 
        and app.margin+(9*app.cellSize)+20 <= event.y <= app.margin+(11*app.cellSize)+7)):
        app.paused = not app.paused
        app.pauseScreen = not app.pauseScreen

# draw pause and play button
def drawPauseButton(app, canvas):
    gameWidth = (2 * app.margin) + (app.cellSize*app.cols)
    canvas.create_rectangle(gameWidth-(3*app.margin/4), app.margin/2 - 10, 
                            gameWidth-(app.margin/4), app.margin/2 + 10, 
                                                                fill='black')
    canvas.create_image(gameWidth-app.margin/2, app.margin/2, image=ImageTk.PhotoImage(app.pauseButton))
    if app.paused:
        # draw play
        half = app.cellSize/2
        canvas.create_rectangle(app.margin+(2*app.cellSize), app.margin+(7*app.cellSize), 
                                app.margin+(9*app.cellSize), app.margin+(12*app.cellSize), 
                                fill='yellow', width=5)
        level = f'LEVEL:{app.level}'
        canvas.create_text(app.margin+(6*app.cellSize)-half, app.margin+(8*app.cellSize)+half, text=level, fill='black',
                        font='Terminal 12 bold')        
        canvas.create_image(app.margin+(6*app.cellSize)-half, app.margin+(10*app.cellSize)+half, image=ImageTk.PhotoImage(app.playButton))

# actions so user can actually play
# player only moves in 'hard' directions
def keyPressed(app, event):
    key = event.key.upper()
    if key == 'LEFT' or key == 'A':
        while movePlayerPiece(app, 0, -1) == True:
            movePlayerPiece(app, 0, -1)
            detectSpikeCollision(app)
    elif key == 'UP' or key == 'W':
        while movePlayerPiece(app, -1, 0) == True:
            movePlayerPiece(app, -1, 0)
    elif key == 'RIGHT' or key == 'D':
        while movePlayerPiece(app, 0, 1) == True: 
            movePlayerPiece(app, 0, 1)
            detectSpikeCollision(app)
    elif key == 'DOWN' or key == 'S':
        while movePlayerPiece(app, 1, 0) == True:
            movePlayerPiece(app, 1, 0)
    elif key == 'R':
        appStarted(app)
    elif key == 'SPACE':
        if app.isGameStart == True:
            name = app.getUserInput('Type a username...')
            app.userName = name
            app.typeName = not app.typeName

            app.isGameStart = False

    scrollRow(app)
    newLevel(app)
    death(app)

# TIMER FIRED
def timerFired(app):
    if app.isGameStart == False and app.paused == False and app.typeName == False:
        app.lavaScroll += 2
        app.missileShootTimer += (20 * app.level)
        missileRepeat(app)
        detectMissileCollision(app)
        lava(app)

# return True if is legal move
def playerMoveIsLegal(app):
    newRow = app.playerRow
    newCol = app.playerCol
    #check if within the bounds of board
    if newRow < 0 or newRow >= app.rows:
        return False
    elif newCol < 0 or newCol >= app.cols:
        return False   
    # runs into maze, cannot go through
    elif app.board[newRow][newCol][0] == app.mazeColor:
        return False
    # runs into missile, cannot go through but does not die yet
    elif app.board[newRow][newCol][0] == app.missileColor:
        return False
    runIntoCoin(app)
    return True

# returns True if player can move there
def movePlayerPiece(app, drow, dcol):
    #set a variable for the original if illegal move 
    startingPlayerRow = app.playerRow
    startingPlayerCol = app.playerCol

    app.playerRow += drow
    app.playerCol += dcol

    if not playerMoveIsLegal(app):
        app.playerRow = startingPlayerRow
        app.playerCol = startingPlayerCol
        return False
    return True

###############################################################################
# LEADERBOARD
###############################################################################
#https://www.cs.cmu.edu/~112/notes/notes-strings.html#basicFileIO
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def getLeaderboard(app):
    leaderboardFile = readFile("leaderboard.txt")
    leaderboardData = leaderboardFile.splitlines()
    leaderboard = []
    for score in leaderboardData:
        playerData = score.split(" ")
        player = playerData[0]
        score = int(playerData[1])
        leaderboard.append((player,score))
    return leaderboard

def returnLeaderboard(app, leaderboard):
    contents = ""
    for player, score in leaderboard:
        contents += player + " " + str(score) + "\n" 
    contents = contents.strip()
    writeFile("leaderboard.txt", contents)

###############################################################################
# PLAYER
###############################################################################

# place the player on board
def placePlayer(app):
    boardRow = row + app.playerRow
    boardCol = col + app.playerCol
    app.board[boardRow][boardCol] = app.playerColor

# draw player
def drawPlayer(app, canvas):
    drawCell(app, canvas, app.playerRow, app.playerCol, app.playerColor)
    # put 'Travel Boy' of character on top
    cellWidth = app.cellSize/2
    centerX = cellWidth + app.margin + (app.playerCol * app.cellSize)
    centerY = cellWidth + app.margin + ((app.playerRow+app.scrollD) * app.cellSize)
    canvas.create_image(centerX, centerY, image=ImageTk.PhotoImage(app.character))

###############################################################################
# NEW LEVEL
###############################################################################

def newLevel(app):
    if (app.playerRow) >= app.newIncrease:
        app.newIncrease *= 2
        app.level += 1

###############################################################################
# COINS
###############################################################################

# make coins properly disappear if collected
def runIntoCoin(app):
    color, status = app.board[app.playerRow][app.playerCol]
    if status == 1:
        # coins change worth per level increase
        app.score += 1 * app.level
        app.board[app.playerRow][app.playerCol] = (app.emptyColor, 0)

# draw coins to collect 
def drawCoins(app, canvas):
    cellWidth = app.cellSize/2
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color, status = app.board[row][col]
            if status == 1:
                centerX = app.margin + cellWidth + app.cellSize * col
                centerY = app.margin + cellWidth + app.cellSize * (row+app.scrollD) 
                canvas.create_oval(centerX-1.5, centerY-1.5, centerX+1.5, centerY+1.5, 
                                    fill=app.coinColor, outline=app.coinColor)

###############################################################################
# OBSTACLE: MISSILE
###############################################################################

# place the missile obstacle
def placeObstacleMissile(app):
    for row in range(1, len(app.board)-1):
        for col in range(1):
            if (app.board[row][col][0] != app.mazeColor) and (app.board[row+1][col][0] != app.mazeColor):
                app.board[row][col] = (app.missileColor, 0)

# draw missile obstacle
def drawObstacleMissile(app, canvas):
    for row in range(1, len(app.board)-1):
        for col in range(1):
            if (app.board[row][col][0] != app.mazeColor) and (app.board[row+1][col][0] != app.mazeColor):
                drawCell(app, canvas, row, col, app.missileColor)
                cellWidth = app.cellSize/2
                centerX = app.margin + cellWidth + (app.cellSize * col)
                centerY = app.margin + cellWidth + (app.cellSize * (row+app.scrollD)) 
                canvas.create_image(centerX, centerY, image=ImageTk.PhotoImage(app.missile))

# get the missile/bullet to repeatedly shoot
def missileRepeat(app):
    app.missileList = []
    (centerX, centerY) = (0, 0)
    bounds = app.margin + (app.cellSize * app.cols)
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color, status = app.board[row][col]
            if color == app.missileColor and (centerX+4) <= bounds:
                cellWidth = app.cellSize/2
                centerX = cellWidth + app.margin + (app.cellSize * col) + app.missileShootTimer
                centerY = cellWidth + app.margin + (app.cellSize * (row+app.scrollD)) 
                app.missileList.append((centerX, centerY))
            # make it re-shoot missile constantly
            elif color == app.missileColor and centerX+4 > bounds: 
                app.missileShootTimer = 0

# draw missiles/bullets
def drawMissileShoot(app, canvas):
    for (centerX, centerY) in app.missileList:
        canvas.create_oval(centerX-4, centerY-4, centerX+4, centerY+4, fill=app.missileColor)

# return rol, col of a missile bullet
def missileRowCol(app, cx, cy):
    col = math.ceil((cx-app.margin) // app.cellSize)
    row = math.ceil((cy-app.margin) // app.cellSize)
    return row, col  

# OBSTACLE COLLISION = DEATH; return True if collided
def detectMissileCollision(app):
    (missileRow, missileCol) = (-1, -1)
    for missileCx, missileCy in app.missileList:
        (missileRow, missileCol) = missileRowCol(app, missileCx, missileCy)
        if (app.playerRow + app.scrollD, app.playerCol) == (missileRow, missileCol):
            app.missileCollision = True

###############################################################################
# OBSTACLE: SPIKE
###############################################################################

# draw spike (was alr coded in randomized maze)
def drawSpike(app, canvas):
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color, status = app.board[row][col]
            if (color, status) == (app.spikeColor, 2):
                if col > 5:
                    cellWidth = app.cellSize/2
                    centerX = app.margin + cellWidth + (app.cellSize * col)
                    centerY = app.margin + cellWidth + (app.cellSize * (row+app.scrollD))
                    canvas.create_image(centerX, centerY, image=ImageTk.PhotoImage(app.spike))
                if col < 5:
                    cellWidth = app.cellSize/2
                    centerX = app.margin + cellWidth + (app.cellSize * col)
                    centerY = app.margin + cellWidth + (app.cellSize * (row+app.scrollD))
                    canvas.create_image(centerX, centerY, image=ImageTk.PhotoImage(app.spikeRef))

# detect spike colliison
def detectSpikeCollision(app):
    if app.board[app.playerRow][app.playerCol] == (app.spikeColor, 2):
        app.spikeCollision = True

###############################################################################
# OBSTACLE: CHASING LAVA
###############################################################################
        
def lava(app):
    lavaRow = math.ceil((app.lavaScroll - app.margin)/ app.cellSize)-1
    if (app.playerRow + app.scrollD) == lavaRow:
        app.lavaCollision = True

def drawLava(app, canvas):
    canvas.create_rectangle(app.margin, 0, app.width - app.margin, app.lavaScroll, 
                                    fill='cyan', outline = 'cyan')

###############################################################################
# EXIT DOOR & DEATH
###############################################################################

# exit door
def placeExit(app):
    app.board[0][3] = (app.mazeColor, 0)
    app.board[0][4] = (app.mazeColor, 0)
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            if row == app.rows-1:
                app.board[row][col] = (app.exitColor, 3)

# draw exit portals
def drawExitPortals(app, canvas):
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color, status = app.board[row][col]
            if status == (3):
                cellWidth = app.cellSize/2
                centerX = app.margin + cellWidth + (app.cellSize * col)
                centerY = app.margin + cellWidth + (app.cellSize * (row+app.scrollD))
                canvas.create_image(centerX, centerY, image=ImageTk.PhotoImage(app.exitDoor))

# verify death to trigger gameOver
def death(app):
    if app.board[app.playerRow][app.playerCol] == (app.exitColor, 3):
        app.gameOver = True
        if app.leaderboardChanged == False:
            app.leaderboard = changeLeaderboard(app)
            returnLeaderboard(app, app.leaderboard)
            app.leaderboardChanged = True

###############################################################################
# MAZE
###############################################################################

# randomizes all rows and cols and exitSpace
def codeMaze(app):
    sumWallRows = 0
    while sumWallRows <= (len(app.board)):
        newNum = random.randint(2, 3)
        app.wallRow.append(newNum)
        app.wallCol.append(random.randint(1, 10))
        app.exitSpace.append(random.randint(1, 3))
        sumWallRows += newNum

# randomized maze 
def makeMaze(app):
    row = 0
    iCol = len(app.board[row])// 2
    walls = copy.deepcopy(app.wallRow)
    floatingCopy = copy.deepcopy(app.wallRow)
    for i in range(len(app.wallRow)):
        while walls[i] > 0:
            if row < len(app.board):
                # draw empty row
                for col in range(len(app.board[row])):
                    app.board[row][col] = (app.emptyColor, 1)
            walls[i] -= 1
            row += 1
        # draw walls
        if row < len(app.board):
            # left side of wall
            for col in range(app.wallCol[i]):
                app.board[row][col] = (app.mazeColor, 0)
            # right side of wall
            for col in range(len(app.board[row]) - app.wallCol[i] - app.exitSpace[i]):
                app.board[row][app.wallCol[i] + app.exitSpace[i] + col] = (app.mazeColor, 0)

            # draw VERTICAL blocks to bounce off of
            # if gap is on the left of imaginary player--- add block above left wall
            if iCol >= (app.wallCol[i] + app.exitSpace[i]):
                app.board[row-1][app.wallCol[i]-1] = (app.mazeColor, 0)

                oppSideD = app.cols - (app.wallCol[i]) - app.exitSpace[i]
                # place SPIKE since it is opposite of correct side does not limit character
                if oppSideD != 0:
                    app.board[row-1][app.wallCol[i] + app.exitSpace[i] + oppSideD - 1] = (app.spikeColor, 2)

                # place free-floating maze walls
                if (oppSideD >= 3) and (floatingCopy[i] == 3):
                    floatingWall = oppSideD - 1
                    while floatingWall > 1:
                        app.board[row-2][app.wallCol[i] + app.exitSpace[i] + oppSideD - floatingWall] = (app.mazeColor, 0)
                        floatingWall -= 1

                iCol = app.wallCol[i]

            # if gap is on right of imaginary player--- add block above right wall ONLY if in bounds
            if iCol < app.wallCol[i]:
                if (app.wallCol[i] + app.exitSpace[i]) < len(app.board[row]):
                    app.board[row-1][app.wallCol[i] + app.exitSpace[i]] = (app.mazeColor, 0)
                    app.board[row-1][0] = (app.spikeColor, 2)
                    iCol = app.wallCol[i] + app.exitSpace[i] - 1
                else:
                    iCol = len(app.board[row])
        row += 1

###############################################################################
# CELLs, BOARD, STARTING SCREEN, SCORE, DEATH, VICTORY
###############################################################################

# vertical side scrolling
def scrollRow(app):
    middleRowVal = 10
    startingPlayerRow = app.playerRow
    if app.playerRow > middleRowVal:
      app.scrollD = middleRowVal - app.playerRow
      # reset the middleRowVal to starting row of app.playerRow
      middleRowVal = startingPlayerRow

# draw each cell
def drawCell(app, canvas, row, col, color):
    x = app.margin + app.cellSize * col
    y = app.margin + app.cellSize * (row + app.scrollD)
    width = 0
    canvas.create_rectangle(x, y, x + app.cellSize, y + app.cellSize, 
                            fill=color, width=width, outline=color)

# draw world
def drawBoard(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill=app.backgroundColor)
    for row in range(len(app.board)):
        for col in range(len(app.board[row])):
            color, status = app.board[row][col]
            drawCell(app, canvas, row, col, color)

# introduction screen wit rules
def drawStartingScreen(app, canvas):
    canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill='black')
    y = app.height
    canvas.create_text(app.width/2, y/2 - 50, text='Mini Dimensional Traveler',
                        fill='gold', font='Terminal 17 bold')
    canvas.create_text(app.width/2, y/2 -18, text='Directions:',
                        fill='magenta', font='Terminal 11')
    canvas.create_text(app.width/2, y/2, text='Avoid obstacles and reach a portal for safety',
                        fill='magenta', font='Terminal 8 bold')
    canvas.create_text(app.width/2, y/2 + 30, text='Click Anywhere or Press the Spacebar to Play...',
                            fill='lightBlue', font='Terminal 8 bold')

# draw SCORE and LEVEL
def drawScoreAndLevel(app, canvas):
    canvas.create_rectangle(app.margin, app.margin/2 - 12, app.margin+(app.cols*app.cellSize), app.margin/2 + 12, 
                                fill='black', outline='yellow')
    level = f'Level: {app.level}'
    canvas.create_text(app.margin + 60, app.margin/2, text=level, fill='yellow',
                        font='Terminal 12 bold')
    score = f'Score: {app.score}' 
    canvas.create_text(app.width/2+70, app.margin/2, text=score, fill='yellow',
                        font='Terminal 12 bold')

# died to MISSILE
def drawMissileDeath(app, canvas):
    if app.missileCollision:
        canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill='black')
        y = app.height
        canvas.create_text(app.width/2, y/2 - 50, text='DIED to MISSILE',
                            fill='red', font='Terminal 15 bold')
        score = f'Score: {app.score}'
        canvas.create_text(app.width/2, y/2, text=score,
                            fill='magenta', font='Terminal 15 bold')
        canvas.create_text(app.width/2, y/2 + 50, text='Press R to Restart',
                            fill='magenta', font='Terminal 15 bold')

# died to SPIKE
def drawSpikeDeath(app, canvas):
    if app.spikeCollision: 
        canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill='black')
        y = app.height
        canvas.create_text(app.width/2, y/2 - 50, text='DIED to SPIKE TRAP',
                            fill='red', font='Terminal 15 bold')
        score = f'Score: {app.score}'
        canvas.create_text(app.width/2, y/2, text=score,
                            fill='magenta', font='Terminal 15 bold')
        canvas.create_text(app.width/2, y/2 + 50, text='Press R to Restart',
                            fill='magenta', font='Terminal 15 bold')

# died to LAVA
def drawLavaDeath(app, canvas):
    if app.lavaCollision: 
        canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill='black')
        y = app.height
        canvas.create_text(app.width/2, y/2 - 50, text='DIED to LAVA',
                            fill='red', font='Terminal 15 bold')
        score = f'Score: {app.score}'
        canvas.create_text(app.width/2, y/2, text=score,
                            fill='magenta', font='Terminal 15 bold')
        canvas.create_text(app.width/2, y/2 + 50, text='Press R to Restart',
                            fill='magenta', font='Terminal 15 bold')

def changeLeaderboard(app):
    leaderboard = getLeaderboard(app)
    for i in range(len(leaderboard)):
        if app.score >= leaderboard[i][1]:
            leaderboard.insert(i, (app.userName, app.score))
            leaderboard.pop()
            break
    return leaderboard

# VICTORY SCREEN
def drawGameOver(app, canvas):
    if app.gameOver == True:
        canvas.create_rectangle(0, 0, app.width, app.height, 
                                fill='black')
        y = app.height
        canvas.create_text(app.width/2, y/2 - 150, text='You made it to safety.',
                            fill='gold', font='Terminal 20 bold')
        score = f'Score: {app.score}'
        canvas.create_text(app.width/2, y/2 - 100, text=score,
                            fill='orange', font='Terminal 17 bold')
        canvas.create_text(app.width/2, y/2 - 50, text='Press R to restart',
                            fill='magenta', font='Terminal 15 bold')
        
        # draw LEADERBOARD
        canvas.create_text(app.width/2, y/2 + 25, text='LEADERBOARD',
                            fill='magenta', font='Terminal 11 bold')
        dy = 50
        num = 1
        for player, score in app.leaderboard:
            canvas.create_text(app.width/2, y/2 + dy, text=f"{num}. {player}: {score}",
                            fill='lightBlue', font='Terminal 10')
            dy += 25
            num += 1
        
# redrawAll
def redrawAll(app, canvas):
    if app.isGameStart:
        drawStartingScreen(app, canvas)
    else:
        drawBoard(app, canvas)
        drawExitPortals(app, canvas)
        drawCoins(app, canvas)
        drawPlayer(app, canvas)
        drawObstacleMissile(app, canvas)
        drawMissileShoot(app, canvas)
        drawSpike(app, canvas)
        drawLava(app, canvas)
        drawScoreAndLevel(app, canvas)
        drawPauseButton(app, canvas)
        drawMissileDeath(app, canvas)
        drawSpikeDeath(app, canvas)
        drawLavaDeath(app, canvas)
        drawGameOver(app, canvas)

# set up dimensions
def playTombOfTheMask():
    (rows, cols, cellSize, margin) = gameDimensions()
    width = cols * cellSize + 2* (margin)
    height = (rows//6) * cellSize + (margin)
    runApp(width = width, height = height)

playTombOfTheMask()