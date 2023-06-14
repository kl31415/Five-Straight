import pygame
import sys
import numpy as np
import random as rand
import AIPlayer
import random

class FiveStraight:

    rowNum=10
    columnNum=10
    imgPath='imgs'

    def __init__(self):

        pygame.init()

        self.size = width, height = 800, 880
        self.screen = pygame.display.set_mode(self.size)
        self.card = pygame.image.load("%s/card.png"%FiveStraight.imgPath)
        self.card = pygame.transform.scale(self.card, (60, 70))
        self.bigfont = pygame.font.SysFont("Arial", 72)
        self.smallfont = pygame.font.SysFont("Arial", 24)

        pygame.display.set_caption('Five Straight')

        self.board = pygame.image.load("%s/fivestraightboard.png"%FiveStraight.imgPath)
        self.board = pygame.transform.scale(self.board, (width, height))

        self.arrangement = np.array([
            [73, 72, 71, 70, 69, 68, 67, 66, 65,  0],
            [74, 57, 58, 59, 60, 61, 62, 63, 64, 99],
            [75, 56, 21, 20, 19, 18, 17, 36, 37, 98],
            [76, 55, 22, 13, 14, 15, 16, 35, 38, 97],
            [77, 54, 23, 12,  1,  4,  5, 34, 39, 96],
            [78, 53, 24, 11,  2,  3,  6, 33, 40, 95],
            [79, 52, 25, 10,  9,  8,  7, 32, 41, 94],
            [80, 51, 26, 27, 28, 29, 30, 31, 42, 93],
            [81, 50, 49, 48, 47, 46, 45, 44, 43, 92],
            [82, 83, 84, 85, 86, 87, 88, 89, 90, 91]
        ])

        self.allcards = list(range(0, 100))
        rand.shuffle(self.allcards)

        self.hands = {'blue': np.sort(self.allcards[:4]), 'magenta': np.sort(self.allcards[4:8])}
        self.cardindex = 8

        pygame.mouse.set_cursor(*pygame.cursors.broken_x)
        self.refreshGame()

    def __distance(self,pos1,pos2):
        return np.sqrt(pow(pos1[0]-pos2[0],2)+pow(pos1[1]-pos2[1],2))

    def __accuratePosi(self,pos):
        row = (pos[0] - self.topLeftPos[0]) // self.cellLen
        column = (pos[1] - self.topLeftPos[1]) // self.cellLen
        rowList = [row - 1, row, row + 1]
        columnList = [column - 1, column, column + 1]
        minDis = 9999999
        closestPos = [-1, -1]

        for i in range(3):
            for j in range(3):
                tempRow = rowList[i]
                tempColumn = columnList[j]
                if tempRow < game.rowNum and tempRow >= 0 and tempColumn >= 0 and tempColumn < game.columnNum:
                    crossPos = self.boardGridPointPosMrx[tempRow][tempColumn]
                    tempDis = self.__distance(crossPos, pos)
                    if tempDis < minDis:
                        minDis = tempDis
                        closestPos = [tempRow, tempColumn]
        return closestPos
    
    def displayInfo(self, player):
        otherPlayer = 'magenta'
        if (player == 'magenta'):
            otherPlayer = 'blue'

        self.screen.fill(pygame.Color("blue"), (720, 805, 80, 75))
        self.oppnum = self.bigfont.render(str(len(self.hands[otherPlayer])), 1, "white")
        self.screen.blit(self.oppnum, (740, 800))

        for i in range(len(self.hands[player])):
            self.screen.blit(self.card, (170+80*i, 805))
            self.screen.blit(self.smallfont.render(str(self.hands[player][i]), 1, "black"), (187+80*i, 826))
        for i in range(4-len(self.hands[player])):
            self.screen.blit(self.card, (170+80*(3-i), 805))     

    def findSmallest(self, player):
        smallest = np.min(self.hands[player])  
        valid_actions = []

        for row in range(10):
            for col in range(10):
                if self.arrangement[row][col] >= smallest and self.boardStateMrx[row][col] == 'null':
                    valid_actions.append((row, col))

        valid_nums = [self.arrangement[indices] for indices in valid_actions]
        if (valid_nums != []):
            return valid_nums
        return []
    
    def checkDead(self, player):
        return self.findSmallest(player) == []

    def play(self, player, row, col, index):
        if type(row) is not int:
            row = row[0]
        if type(col) is not int:
            col = col[0]

        modified = list(self.hands[player])
        del modified[index]
        self.hands[player] = modified

        modified = list(self.hands[player])
        modified.append(self.allcards[self.cardindex])
        self.hands[player] = np.sort(modified)
        self.cardindex += 1

        self.boardStateMrx[col][row] = player
        piece=pygame.transform.scale(pygame.image.load("%s/%s_peg.png"%(FiveStraight.imgPath,player)),(self.board.get_width()*3//100,self.board.get_height()*3//112.5))
        self.screen.blit(piece,(self.boardGridPointPosMrx[row][col][0]-piece.get_width()/2,self.boardGridPointPosMrx[row][col][1]-piece.get_height()/2))

        pygame.display.flip()
        self.displayInfo(player)

    def findNeighbor(self, row, column):
        if (self.boardStateMrx[column][row]!='null'):
            occupiablePosiList = []
            x, y = row, column

            if x - 1 >= 0 and self.boardStateMrx[x - 1][y] == 'null':
                occupiablePosiList.append((x - 1, y))

            if x + 1 < 10 and self.boardStateMrx[x + 1][y] == 'null':
                occupiablePosiList.append((x + 1, y))

            if y - 1 >= 0 and self.boardStateMrx[x][y - 1] == 'null':
                occupiablePosiList.append((x, y - 1))

            if y + 1 < 10 and self.boardStateMrx[x][y + 1] == 'null':
                occupiablePosiList.append((x, y + 1))

            if occupiablePosiList:
                loc = random.choice(occupiablePosiList)
                return (loc[0], loc[1])
            
        return (row, column)

    def nextStep(self,player,posIndex):
        row,column=posIndex

        if self.checkDead(player):
            self.over('win')
            return False
        
        loc = self.findNeighbor(row, column)

        if self.boardStateMrx[loc[1]][loc[0]]=='null' and self.arrangement[loc[1]][loc[0]] >= np.min(self.hands[player]):
            index = np.amax(np.where(self.hands[player] <= self.arrangement[column][row]))
            self.play(player, row, column, index)
            return True
        
        loc = None
        index = 0
        for i in reversed(range(4)):
            indices = np.where(self.findSmallest(player) >= self.hands[player][i])[0]
            nums = [list(self.findSmallest(player))[i] for i in indices]

            if (nums != []):
                np.sort(nums)
                index = i
                loc = np.min(nums)
                break

        indices = np.where(self.arrangement == loc)
        row, col = (indices[1], indices[0])
        self.play(player, row, col, index)
        return True


    def checkGameState(self,player):
        occupiedCount=0
        for i in range(FiveStraight.rowNum):
            for j in range(FiveStraight.columnNum):
                piece=self.boardStateMrx[i][j]

                if piece!='null':
                    occupiedCount+=1
                    result=self.checkNInARow((i,j),5,player)

                    if result:
                       return result

        if occupiedCount==self.columnNum*self.rowNum:
            return 'tie'

        return False

    def checkNInARow(self,pos,N,player):
        x,y=pos

        directionList=['right','down','down-left','down-right']
        for direction in directionList:
            count = 0
            tempx = x
            tempy = y
            
            while tempx<FiveStraight.rowNum and tempy < FiveStraight.columnNum:
                if self.boardStateMrx[tempx][tempy]==player:
                    count+=1
                    if count == N:
                        return self.boardStateMrx[x][y]
                    
                else:
                    break

                if direction == 'right':
                    tempx += 1

                elif direction == 'down':
                    tempy += 1

                elif direction == 'down-left':
                    tempx -= 1
                    tempy += 1

                elif direction == 'down-right':
                    tempx += 1
                    tempy += 1

        return False

    def start(self,gameMode):

        humanPlayerPieceType='blue'
        if not gameMode:
            gameMode=self.chooseGameMode()

        self.humanPlayerPieceType=humanPlayerPieceType
        print('gameMode:%s'%gameMode)
        if gameMode=='SimpleAI' or gameMode=='ReinforcementAI':
            # AI=AIPlayer.FollowYouPlayer('magenta')
            AI = AIPlayer.RLPlayer('magenta')
            AI.load_model("ep=50_rew=focus_model")

            nextTurnPlayer = humanPlayerPieceType
            while 1:
                if nextTurnPlayer==humanPlayerPieceType:
                    event = pygame.event.wait()

                    if event.type == pygame.QUIT:
                        sys.exit()

                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        nextPos = pygame.mouse.get_pos()
                        posIndex = self.__accuratePosi(nextPos)
                        lastAction = (posIndex[1], posIndex[0])
                        flag = self.nextStep(nextTurnPlayer, posIndex)

                    elif event.type == pygame.KEYDOWN:
                        while (pygame.key.get_pressed()[pygame.K_r] == 0 or pygame.key.get_pressed()[pygame.K_s] == 0):
                            continue

                        if pygame.key.get_pressed()[pygame.K_r] == 1:
                            self.refreshGame()

                        elif pygame.key.get_pressed()[pygame.K_s] == 1:
                            self.chooseGameMode()

                    else:
                        continue

                else:
                    action = AI.predictAction(self.boardStateMrx)
                    # action = AI.nextAction(self.boardStateMrx, lastAction)
                    action = (action[1], action[0])
                    flag = self.nextStep(nextTurnPlayer, action)

                result = self.checkGameState(nextTurnPlayer)
                if result:
                    self.over(result)

                if flag:
                    if nextTurnPlayer == 'magenta':
                        nextTurnPlayer = 'blue'

                    else:
                        nextTurnPlayer = 'magenta'

        elif gameMode=='DoublePlayer':
            turnIndex = 0
            while 1:
                event = pygame.event.wait()
                if event.type == pygame.QUIT:
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_r] == 1:
                        self.refreshGame()
                    elif pygame.key.get_pressed()[pygame.K_s] == 1:
                        self.chooseGameMode()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    nextTurnPlayer = ('blue', 'magenta')[turnIndex % 2]
                    nextPos = pygame.mouse.get_pos()
                    posIndex = self.__accuratePosi(nextPos)
                    flag = self.nextStep(nextTurnPlayer, posIndex)
                    if flag:
                        turnIndex += 1

                    result = self.checkGameState(nextTurnPlayer)
                    if result:
                        self.over(result)

    def over(self,result):
        if result=='tie':
            resultImg = pygame.image.load('%s/tie.jpeg'%FiveStraight.imgPath)

        elif result==self.humanPlayerPieceType:
            resultImg = pygame.image.load('%s/win.jpeg'%FiveStraight.imgPath)

        else:
            resultImg = pygame.image.load('%s/lose.jpeg'%FiveStraight.imgPath)

        speed = [0.5, 0.8]
        resultImg=pygame.transform.scale(resultImg,(400,400))
        resultImgRect = resultImg.get_rect()

        pygame.display.flip()
        while 1:
            breakFlag = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

                if event.type == pygame.KEYDOWN:
                    if pygame.key.get_pressed()[pygame.K_r]==1:
                        breakFlag=True
                        break

            if breakFlag:
                break
            resultImgRect = resultImgRect.move(speed)

            if resultImgRect.left < 0 or resultImgRect.right > self.size[0]:
                speed[0] = -speed[0]

            if resultImgRect.top < 0 or resultImgRect.bottom > self.size[1]:
                speed[1] = -speed[1]

            self.screen.blit(resultImg, (resultImgRect[0] + 200, resultImgRect[1] + 200))
            pygame.display.flip()

        self.refreshGame()

    def refreshGame(self):
        self.screen.blit(self.board, (0, 0))
        self.boardStateMrx = [['null'] * FiveStraight.rowNum for i in range(FiveStraight.rowNum)]
        self.topLeftPos = [40, 40]
        self.cellLen = 80
        self.boardGridPointPosMrx = []

        for i in range(FiveStraight.rowNum):
            self.boardGridPointPosMrx.append([])
            for j in range(FiveStraight.columnNum):
                self.boardGridPointPosMrx[i].append([])

        for i in range(FiveStraight.rowNum):
            for j in range(FiveStraight.columnNum):
                self.boardGridPointPosMrx[i][j] = [self.topLeftPos[0] + self.cellLen * i,
                                                   self.topLeftPos[1] + self.cellLen * j]

        pygame.display.flip()

    def chooseGameMode(self):
        self.interface = pygame.image.load("%s/interface.png" % FiveStraight.imgPath)
        self.interface = pygame.transform.scale(self.interface, (800, 880))
        self.interface_rect = self.interface.get_rect()
        self.screen.blit(self.interface, (0,0))
        pygame.display.flip()

        while 1:
            event = pygame.event.wait()
            if event.type==pygame.KEYDOWN:
                if pygame.key.get_pressed()[pygame.K_p] == 1:
                    gameMode='DoublePlayer'
                    break

                elif pygame.key.get_pressed()[pygame.K_b] == 1:
                    gameMode = 'SimpleAI'
                    break

                elif pygame.key.get_pressed()[pygame.K_t] == 1:
                    gameMode = 'ReinforcementAI'
                    break
                
        self.screen.blit(self.board, (0, 0))
        self.displayInfo('blue')
        pygame.display.flip()
        game.start(gameMode)

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    game=FiveStraight()
    game.start(None)