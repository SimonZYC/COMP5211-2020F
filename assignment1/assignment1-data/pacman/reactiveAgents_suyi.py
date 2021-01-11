# reactiveAgents.py
# ---------------
# Licensing Information: You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC
# Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search

class NaiveAgent(Agent):
    "An agent that goes West until it can't."

    def getAction(self, state):
        "The agent receives a GameState (defined in pacman.py)."
        sense = state.getPacmanSensor()
        if sense[7]:
            action = Directions.STOP
        else:
            action = Directions.WEST
        return action

class PSAgent(Agent):
    "An agent that follows the boundary using production system."

    def getAction(self, state):
        sense = state.getPacmanSensor()
        x = [sense[1] or sense[2] , sense[3] or sense[4] ,
        sense[5] or sense[6] , sense[7] or sense[0]]
        if x[0] and not x[1]:
            action = Directions.EAST
        elif x[1] and not x[2]:
            action = Directions.SOUTH
        elif x[2] and not x[3]:
            action = Directions.WEST
        elif x[3] and not x[0]:
            action = Directions.NORTH
        else:
            action = Directions.NORTH
        return action

class ECAgent(Agent):
    "An agent that follows the boundary using error-correction."
    def getAction(self, state):
        ''' Your code goes here! '''
        ''' [ northwest 0, north 1, northeast 2, east 3, southeast 4, south 5, southwest 6, west 7 ] '''

        north = [0.1, -0.2, -0.2, 0.0, 0.0, 0.0, 0.0, 0.1]
        south = [0.0, 0.0, 0.0, 0.1, 0.1, -0.2, -0.2, 0.0]
        west = [-0.2, 0.0, 0.0, 0.0, 0.0, 0.1, 0.1, -0.2]
        east = [0.0, 0.1, 0.1, -0.2, -0.2, 0.0, 0.0, 0.0]

        sense = state.getPacmanSensor();
        dir_weights = [north, south, west, east]
        # Dir north, south, west, east
        can_dir = []
        for idx, dir_ in enumerate(dir_weights):
            tmp = 0
            for i, j in zip(sense, dir_): 
                tmp += (i * j)
            if tmp > 0:
                can_dir.append(1)
            else:
                can_dir.append(0)

        if can_dir[0]:
            chosen_dir = Directions.NORTH
        if can_dir[1]:
            chosen_dir = Directions.SOUTH
        if can_dir[2]:
            chosen_dir = Directions.WEST
        if can_dir[3]:
            chosen_dir = Directions.EAST

        valid = sum(can_dir)
        if valid == 1:
            return chosen_dir;

        else:
            if can_dir[0] == 1:
                return Directions.NORTH;
            elif can_dir[1] == 1:
                return Directions.EAST;
            elif can_dir[2] == 1:
                return Directions.SOUTH;
            elif can_dir[3] == 1:
                return Directions.WEST;
            else:
                return Directions.NORTH;

class SMAgent(Agent):
    "An sensory-impaired agent that follows the boundary using state machine."
    def registerInitialState(self,state):
        "The agent receives the initial GameState (defined in pacman.py)."
        sense = state.getPacmanImpairedSensor() 
        self.prevAction = Directions.STOP
        self.prevSense = sense

    def getAction(self, state):
        '''@TODO: Your code goes here! ''' 
        sense = state.getPacmanImpairedSensor() 
        features = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
        for idx in (1,3,5,7):
           features[idx] = sense[idx/2]

        if self.prevAction == Directions.EAST and self.prevSense[0] == 1:
            features[0] = 1

        if self.prevAction == Directions.SOUTH and self.prevSense[1] == 1:
            features[2] = 1

        if self.prevAction == Directions.WEST and self.prevSense[2] == 1:
            features[4] = 1

        if self.prevAction == Directions.NORTH and self.prevSense[3] == 1:
            features[6] = 1

        self.prevSense = sense

        if (features[1] and (not features[3])):
            self.prevAction = Directions.EAST
            return Directions.EAST

        if (features[3] and (not features[5])):
            self.prevAction = Directions.SOUTH
            return Directions.SOUTH

        if (features[5] and (not features[7])):
            self.prevAction = Directions.WEST
            return Directions.WEST

        if (features[7] and (not features[1])):
            self.prevAction = Directions.NORTH
            return Directions.NORTH

        if features[0]:
            self.prevAction = Directions.NORTH
            return Directions.NORTH            

        if features[2]:
            self.prevAction = Directions.EAST
            return Directions.EAST 

        if features[4]:
            self.prevAction = Directions.SOUTH
            return Directions.SOUTH

        if features[6]:
            self.prevAction = Directions.WEST
            return Directions.WEST

        self.prevAction = Directions.NORTH
        return Directions.NORTH
