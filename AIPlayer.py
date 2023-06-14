import abc
import random
import numpy as np
from keras.models import Sequential
from keras.models import load_model
from keras.layers import Dense
from keras.layers import BatchNormalization
from keras.layers import Dropout
from keras.layers import Conv2D, MaxPooling2D, Flatten, Reshape
from keras.optimizers.legacy import Adam
from keras.callbacks import TensorBoard

class AIPlayer:
    @staticmethod
    def newAIPlayer(type,pieceType):
        if type=='FollowYouPlayer':
            return FollowYouPlayer(pieceType)
        else:
            return None

    def __init__(self,pieceType):
        self.pieceType=pieceType
        pieceTypeList=['magenta','blue']
        pieceTypeList.remove(self.pieceType)
        self.adversarialPieceType=pieceTypeList[0]

        self.mustMode=['XXOXX','XXXOX','XOXXX','XXXXO','OXXXX',['.X...','.X...','XOX_X','.X...','.X...']]
        self.cautionMode=['_OXXX_','_XXXO_','_XXOX_','_XOXX_',
                          ['...._','XXXO_','..X..','.X...','X....'],['...._','XXXO_','..X..','.X...','_....'],
                          ['..._.','XXXO_','...X.','...X.','..._.'],['X...X','X..X.','X.X..','__...','O....'],
                          ['X....','X....','X....','_....','O_XXX'],['._....','_O_XX_','.X....','.X....','._....']]
        # , ['_.....', '_O_XX_', '..X...', '...X..', '...._.']
        self.usefulMode=['_XXO_','_OXX_','XXXOO','OOXXX','XXOXO','OXOXX','_XOX_','_XOOX_',
                         ['._...','_OXX_','.X...','.X...','._...'],['..._.','XXXO_','...X.','...X.','...X.'],
                         ['_._..','.XX..','..O..','..XX.','.._._'],['.O.','XXX','.O.']]

    @abc.abstractmethod
    def nextAction(self,boardStateMrx):
        pass

    # Notice: XX.XX is also considered 4-in-a-row, X.XX or XX.X is also considered 3-in-a-row
    def detectNInARow(self,N,pieceType,boardStateMrx):
        NRowList=[]

        rowNum=len(boardStateMrx)
        columnNum=len(boardStateMrx[0])
        for i in range(rowNum):
            for j in range(columnNum):
                if boardStateMrx[i][j]==pieceType:
                    directionList = ['right', 'down', 'down-left', 'down-right']
                    for direction in directionList:
                        count = 0
                        tempx = i
                        tempy = j

                        temp=0
                        while tempx < rowNum and tempx >=0 and tempy < columnNum and tempy>=0:
                            temp+=1
                            if boardStateMrx[tempx][tempy] == pieceType:
                                count += 1

                            if temp==5:
                                if count==N:
                                    NRowList.append((direction,[i, j]))
                                break

                            if direction == 'down':
                                tempy += 1

                            elif direction == 'right':
                                tempx += 1

                            elif direction == 'down-left':
                                tempx -= 1
                                tempy += 1

                            elif direction == 'down-right':
                                tempx += 1
                                tempy += 1

        if NRowList:
            return NRowList
        
        else:
            return False

    def getNextDirectionPos(self,startPos,direction):
        x,y=startPos
        directionMap={}
        directionMap['right']=(1,0)
        directionMap['reverse-right'] = (-1, 0)
        directionMap['down'] = (0, 1)
        directionMap['reverse-down'] = (0, -1)
        directionMap['down-left'] = (-1, 1)
        directionMap['reverse-down-left'] = (1, -1)
        directionMap['down-right'] = (1, 1)
        directionMap['reverse-down-right'] = (-1, -1)

        x += directionMap[direction][0]
        y += directionMap[direction][1]

        return (x,y)

    def detectMode(self,boardStateMrx,pieceType,modeList):
        for mode in modeList:
            for i in range(len(boardStateMrx)):
                for j in range(len(boardStateMrx)):
                    for direction in ['right','down','down-left','down-right']:
                        if self.fitMode(mode,boardStateMrx,(i,j),direction,pieceType):
                            # if isinstance(mode,list):
                                # print('find complicated mode：')
                                # print(mode)
                                # print((i,j))
                                # print(direction)
                            return (mode,(i,j),direction)
        return None



    def fitMode(self,mode,boardStateMrx,startPoint,direction,pieceType):
        if isinstance(mode,list):
            if direction=='right':
                turnDirection='down'

            elif direction=='down':
                turnDirection = 'reverse-right'

            elif direction=='down-left':
                turnDirection = 'down-right'

            elif direction=='down-right':
                turnDirection = 'reverse-down-left'

            for modeLine in mode:
                tempx, tempy = startPoint
                for i in range(len(modeLine)):
                    modeChar = modeLine[i]
                    if modeChar == '_' or modeChar=='O':
                        if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                            if boardStateMrx[tempx][tempy] != 'null':
                                return False
                            
                        else:
                            return False
                        
                    elif modeChar == 'X':
                        if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                            if boardStateMrx[tempx][tempy] != pieceType:
                                return False
                            
                        else:
                            return False

                    tempx, tempy = self.getNextDirectionPos((tempx, tempy), direction)

                startPoint=self.getNextDirectionPos(startPoint,turnDirection)
                tempx,tempy=startPoint
        else:
            tempx,tempy=startPoint
            for i in range(len(mode)):
                modeChar=mode[i]
                if modeChar=='_' or modeChar=='O':
                    if tempx>=0 and tempx<len(boardStateMrx) and tempy>=0 and tempy<len(boardStateMrx):
                        if boardStateMrx[tempx][tempy] != 'null':
                            return False
                        
                    else:
                        return False
                    
                elif modeChar=='X':
                    if tempx>=0 and tempx<len(boardStateMrx) and tempy>=0 and tempy<len(boardStateMrx):
                        if boardStateMrx[tempx][tempy] != pieceType:
                            return False
                        
                    else:
                        return False

                tempx,tempy=self.getNextDirectionPos((tempx,tempy),direction)

        return True

    def getChoosablePosi(self, NRowList, boardStateMrx, N):
        for rowList in NRowList:
            direction = rowList[0]
            firstPoint = rowList[1]

            x, y = self.getNextDirectionPos(firstPoint, 'reverse-%s' % direction)
            if x >= 0 and x < len(boardStateMrx) and y >= 0 and y < len(boardStateMrx):
                tempPoint = (x, y)

            else:
                tempPoint = firstPoint

            tempx, tempy = tempPoint
            detectStep = N + 2
            slot = []
            for i in range(detectStep):
                if tempx >= 0 and tempx < len(boardStateMrx) and tempy >= 0 and tempy < len(boardStateMrx):
                    if boardStateMrx[tempx][tempy] == 'null':
                        slot.append([tempx, tempy])

                nextPos = self.getNextDirectionPos((tempx, tempy), direction)
                tempx, tempy = nextPos

            if len(slot) == N - 1:
                return slot[1]

        return None
    
class FollowYouPlayer(AIPlayer):
    def nextAction(self,boardStateMrx,adversarialLastPosi):
        selfResult= self.detectMode(boardStateMrx,self.pieceType,self.mustMode)
        action = self.__reactToMode(selfResult)
        if action:
            # print('%s:must win' % self.pieceType)
            return random.choice(action)

        adversarialResult = self.detectMode(boardStateMrx,self.adversarialPieceType,self.mustMode)
        action = self.__reactToMode(adversarialResult)
        if action:
            # print('%s:must stop' % self.pieceType)
            return random.choice(action)

        selfResult = self.detectMode(boardStateMrx, self.pieceType, self.cautionMode)
        action = self.__reactToMode(selfResult)
        if action:
            # print('%s:try to win' % self.pieceType)
            return random.choice(action)

        adversarialResult = self.detectMode(boardStateMrx, self.adversarialPieceType, self.cautionMode)
        action=self.__reactToMode(adversarialResult)
        if action:
            # print('%s:try to stop'%self.pieceType)
            return random.choice(action)

        selfResult = self.detectMode(boardStateMrx, self.pieceType, self.usefulMode)
        action=self.__reactToMode(selfResult)
        if action:
            # print('%s:try to extend'%self.pieceType)
            return random.choice(action)

        # print('%s:randomChoice'%self.pieceType)
        return self.randomAction(boardStateMrx,adversarialLastPosi)

    def __reactToMode(self,modeDetectResult):
        actionList=[]
        if modeDetectResult:
            mode = modeDetectResult[0]
            firstPoint = modeDetectResult[1]
            x,y=firstPoint
            direction = modeDetectResult[2]

            if isinstance(mode,list):
                # print('find complicated mode!')

                if direction == 'right':
                    turnDirection = 'down'

                elif direction == 'down':
                    turnDirection = 'reverse-right'

                elif direction == 'down-left':
                    turnDirection = 'down-right'

                elif direction == 'down-right':
                    turnDirection = 'reverse-down-left'

                for modeLine in mode:
                    for char in modeLine:
                        if char == 'O':
                            actionList.append((x,y))

                        else:
                            x, y = self.getNextDirectionPos((x, y), direction)

                    firstPoint=self.getNextDirectionPos(firstPoint,turnDirection)
                    x,y=firstPoint
            else:
                for char in mode:
                    if char == 'O':
                        actionList.append((x, y))

                    else:
                        x, y = self.getNextDirectionPos((x, y), direction)

        return actionList


    def randomAction(self, boardStateMrx, adverasialLastPosi):
        if not adverasialLastPosi:
            return (len(boardStateMrx)//2,len(boardStateMrx)//2)

        occupiablePosiList = []
        x, y = adverasialLastPosi
        if x - 1 >= 0 and boardStateMrx[x - 1][y] == 'null':
            occupiablePosiList.append((x - 1, y))

        if x + 1 < len(boardStateMrx) and boardStateMrx[x + 1][y] == 'null':
            occupiablePosiList.append((x + 1, y))

        if y - 1 >= 0 and boardStateMrx[x][y - 1] == 'null':
            occupiablePosiList.append((x, y - 1))

        if y + 1 < len(boardStateMrx[0]) and boardStateMrx[x][y + 1] == 'null':
            occupiablePosiList.append((x, y + 1))

        if occupiablePosiList:
            nextPos = random.choice(occupiablePosiList)

        else:
            nextPos=self.getRandomPosiOnBoard(boardStateMrx)

        return nextPos

    def getRandomPosiOnBoard(self, boardStateMrx):
        x = random.randint(0,9)
        y = random.randint(0,9)
        
        while boardStateMrx[x][y]!='null':
            x = random.randint(0, 9)
            y = random.randint(0, 9)

        return (x,y)

class NaivePlayer(AIPlayer):
    def judge(self,boardStateMrx):
        pass
    def nextAction(self,boardStateMrx):
        pass

class RLPlayer(AIPlayer):
    def __init__(self, pieceType):
        super().__init__(pieceType)
        self.model = self.build_model3()
        self.target_model = self.build_model3()
        self.memory = []  # Replay memory for experience replay
        self.gamma = 0.9  # Discount factor
        self.epsilon = 1.0  # Exploration rate
        self.epsilon_decay = 0.95  # Decay rate for exploration rate
        self.epsilon_min = 0.1  # Minimum exploration rate
        self.batch_size = 50  # Batch size for training the neural network

        self.boardStateMrx = []
        self.tensorboard = TensorBoard(log_dir="logs", histogram_freq=1)

    def initialize_board_state(self):
        self.boardStateMrx = [['null']*10 for i in range(10)]

    def checkGameState(self,player):
        occupiedCount=0
        for i in range(10):
            for j in range(10):
                piece=self.boardStateMrx[i][j]

                if piece!='null':
                    occupiedCount+=1
                    result=self.checkNInARow((i,j),5,player)

                    if result:
                       return result
                    
        if occupiedCount==100:
            return 'tie'
        
        return False

    def checkNInARow(self,pos,N,player):
        x,y=pos
        directionList=['right','down','down-left','down-right']
        for direction in directionList:
            count = 0
            tempx = x
            tempy = y

            while tempx < 10 and tempy < 10:
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
    
    def count_lines(self, m):
        count = 0
        for i in range(10):
            for j in range(11 - m):
                is_homogeneous = True
                color = self.boardStateMrx[i][j]

                for k in range(1, m):
                    if self.boardStateMrx[i][j + k] != color:
                        is_homogeneous = False
                        break

                if is_homogeneous:
                    count += 1

        for i in range(11 - m):
            for j in range(10):
                is_homogeneous = True
                color = self.boardStateMrx[i][j]

                for k in range(1, m):
                    if self.boardStateMrx[i + k][j] != color:
                        is_homogeneous = False
                        break

                if is_homogeneous:
                    count += 1

        for i in range(11 - m):
            for j in range(11 - m):
                is_homogeneous = True
                color = self.boardStateMrx[i][j]

                for k in range(1, m):
                    if self.boardStateMrx[i + k][j + k] != color:
                        is_homogeneous = False
                        break

                if is_homogeneous:
                    count += 1

        for i in range(11 - m):
            for j in range(m - 1, 10):
                is_homogeneous = True
                color = self.boardStateMrx[i][j]

                for k in range(1, m):
                    if self.boardStateMrx[i + k][j - k] != color:
                        is_homogeneous = False
                        break

                if is_homogeneous:
                    count += 1

        return count
    
    def count_homogeneous_lines(self, m, color):
        count = 0
        for i in range(10):
            for j in range(11 - m):
                line = self.boardStateMrx[i][j:j+m]
                if all(piece == color for piece in line):
                    count += 1

        for i in range(11 - m):
            for j in range(10):
                line = [self.boardStateMrx[x][j] for x in range(i, i+m)]
                if all(piece == color for piece in line):
                    count += 1

        for i in range(11 - m):
            for j in range(11 - m):
                line = [self.boardStateMrx[i+x][j+x] for x in range(m)]
                if all(piece == color for piece in line):
                    count += 1

        for i in range(11 - m):
            for j in range(9, m-2, -1):
                line = [self.boardStateMrx[i+x][j-x] for x in range(m)]
                if all(piece == color for piece in line):
                    count += 1

        return count
    
    def calculate_board_reward(self, done):
        empty = np.count_nonzero(np.asarray(self.boardStateMrx) == 'null')
        if (done):
            return empty
        return 0
        
    def calculate_self_line_reward(self, player):
        threes = self.count_homogeneous_lines(3, player)
        fours = self.count_homogeneous_lines(4, player)
        return 2 * threes + 5 * fours

    def calculate_all_line_reward(self, player, otherPlayer):
        threes = self.count_homogeneous_lines(3, player) - self.count_homogeneous_lines(3, otherPlayer)
        fours = self.count_homogeneous_lines(4, player) - self.count_homogeneous_lines(4, otherPlayer)
        return 2 * threes + 5 * fours

    def take_action(self, action):
        row, col = action
        self.boardStateMrx[row][col] = self.pieceType
        done = self.checkGameState(self.pieceType)

        # reward = self.calculate_board_reward(done)
        # reward = self.calculate_board_reward(done) + self.calculate_self_line_reward(self.pieceType)
        reward = self.calculate_board_reward(done) + self.calculate_all_line_reward(self.pieceType, self.adversarialPieceType)
        next_state = self.boardStateMrx
        return next_state, reward, done
    
    def build_model(self):
        model = Sequential()
        model.add(Dense(50, input_shape=(100,), activation='relu'))
        model.add(Dense(100, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=0.001))
        return model
    
    def build_model2(self):
        model = Sequential()
        model.add(Dense(200, input_shape=(100,), activation='relu'))
        model.add(Dense(500, input_shape=(200,), activation='relu'))
        model.add(Dense(200, input_shape=(500,), activation='relu'))
        model.add(Dense(100, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=0.01))
        return model
    
    def build_model3(self):
        model = Sequential()
        model.add(Dense(50, input_shape=(100,), activation='relu'))
        model.add(Dense(20, input_shape=(50,), activation='relu'))
        model.add(Dense(50, input_shape=(20,), activation='relu'))
        model.add(Dense(100, activation='linear'))
        model.compile(loss='mse', optimizer=Adam(learning_rate=0.01))
        return model

    def randomAction(self, boardStateMrx):
        nextPos=self.getRandomPosiOnBoard(boardStateMrx)
        return nextPos

    def getRandomPosiOnBoard(self, boardStateMrx):
        x = random.randint(0,9)
        y = random.randint(0,9)

        while boardStateMrx[x][y]!='null':
            x = random.randint(0, 9)
            y = random.randint(0, 9)

        return (x,y)
    
    def nextAction(self, boardStateMrx):
        if np.random.rand() <= self.epsilon:
            return self.randomAction(boardStateMrx)
        
        else:
            return self.predictAction(boardStateMrx)
        
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done))

    def replay(self):
        if len(self.memory) < self.batch_size:
            return 0

        minibatch = random.sample(self.memory, self.batch_size)

        states = []
        targets = []
        losses = []
        for state, action, reward, next_state, done in minibatch:
            target = reward

            if not done:
                next_state = np.array(next_state).reshape(10, 10)
                target = reward + self.gamma * np.amax(self.target_model.predict(self.boardStateToNumeric(next_state), verbose=False))

            target_f = self.model.predict(self.boardStateToNumeric(state), verbose=False).reshape(10, 10)
            target_f[action] = target

            states.append(state)
            targets.append(target_f)

            history = self.model.fit(np.asarray(self.boardStateToNumeric(state)).reshape(1, 100), np.asarray(target_f).reshape(1, 100), verbose=False, callbacks=[self.tensorboard])
            losses.append(history.history['loss'])

        avg_loss = np.mean(losses)
        return avg_loss

    def update_target_model(self):
        self.target_model.set_weights(self.model.get_weights())

    def predictAction(self, boardStateMrx):
        state = self.boardStateToNumeric(boardStateMrx)
        q_values = self.model.predict(state, verbose=False)[0]

        valid_actions = self.get_valid_actions(boardStateMrx)
        q_values_valid = [q_values[action] for action in valid_actions]

        action_index = valid_actions[np.argmax(q_values_valid)]
        return self.index_to_action(boardStateMrx, action_index)
    
    def boardStateToNumeric(self, boardStateMrx):
        mapping = {
            'null': 0.0,
            self.pieceType: 1.0,
            self.adversarialPieceType: -1.0
        }

        numeric_state = [[mapping[value] for value in row] for row in boardStateMrx]
        return np.array(numeric_state).reshape(1, -1)

    def index_to_action(self, boardStateMrx, index):
        row = index // len(boardStateMrx[0])
        col = index % len(boardStateMrx[0])
        return row, col
    
    def get_valid_actions(self, boardStateMrx):
        valid_actions = []
        for row in range(len(boardStateMrx)):
            for col in range(len(boardStateMrx[0])):
                if boardStateMrx[row][col] == 'null': 
                    valid_actions.append(row * len(boardStateMrx[0]) + col)

        return valid_actions

    def save_model(self, filename):
        self.model.save(filename + ".h5")
        print("Model saved successfully.")

    def load_model(self, filename):
        self.model = load_model(filename + ".h5")
        # print("Model loaded successfully.")

