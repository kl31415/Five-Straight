import sys
import numpy as np
import random as rand
import AIPlayer
import random
import logging
import tensorflow as tf

# Disable TensorFlow warning messages
tf.get_logger().setLevel(logging.ERROR)

stats = {'win': 0, 'lose': 0, 'tie': 0}

class FiveStraight:

    rowNum=10
    columnNum=10
    imgPath='imgs'

    def __init__(self):

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

        self.refreshGame()

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

        # AI2 = AIPlayer.RLPlayer('magenta')
        # AI2.load_model("ep=50_rew=focus_model")
        # AI1 = AIPlayer.RLPlayer('blue')
        # AI1.load_model("ep=50_rew=focus_model")
        AI1 = AIPlayer.FollowYouPlayer('blue')
        AI2 = AIPlayer.FollowYouPlayer('magenta')

        nextTurnPlayer = 'blue'
        lastAction = False
        while 1:
            if nextTurnPlayer=='blue':
                # action1 = AI1.predictAction(self.boardStateMrx)

                action1 = AI1.nextAction(self.boardStateMrx, lastAction)

                # action1 = AI1.randomAction(self.boardStateMrx)

                action1 = (action1[1], action1[0])
                lastAction = action1
                flag = self.nextStep(nextTurnPlayer, action1)

            else:
                # action2 = AI2.predictAction(self.boardStateMrx)

                action2 = AI2.nextAction(self.boardStateMrx, lastAction)

                # action2 = AI2.randomAction(self.boardStateMrx)

                action2 = (action2[1], action2[0])
                lastAction = action2
                flag = self.nextStep(nextTurnPlayer, action2)

            result = self.checkGameState(nextTurnPlayer)
            if result:
                self.over(result)
                break

            if flag:
                if nextTurnPlayer == 'magenta':
                    nextTurnPlayer = 'blue'

                else:
                    nextTurnPlayer = 'magenta'


    def over(self,result):
        if result=='tie':
            stats['tie'] += 1

        elif result=='blue':
            stats['win'] += 1

        else:
            stats['lose'] += 1

        # while 1:
        #     breakFlag = False
        #     for event in pygame.event.get():
        #         if event.type == pygame.QUIT: sys.exit()

        #         if event.type == pygame.KEYDOWN:
        #             if pygame.key.get_pressed()[pygame.K_r]==1:
        #                 breakFlag=True
        #                 break

        #     if breakFlag:
        #         break

        # self.refreshGame()
        print(stats)

    def refreshGame(self):
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

if __name__ == '__main__':
    import warnings
    warnings.filterwarnings('ignore')
    for i in range(5):
        game=FiveStraight()
        game.start('ReinforcementAI')
    print(stats)