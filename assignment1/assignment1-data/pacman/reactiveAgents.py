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

# Yunchuan ZHENG
# UST id: 20614209
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

    def canMove(self, sense, weight):
    	sum = 0
    	for i, j in zip(sense, weight):
    		sum = sum + (i * j)
    	# return 1 if sum > 0 else 0
        return 1 if sum >= 0 else 0

    def getAction(self, state):
        weight_sets = [[ 0.1, -0.2, -0.2, 0.0, 0.0, 0.0, 0.0, 0.1, -0.1 ], [ 0.0, 0.1, 0.1, -0.2, -0.2, 0.0, 0.0, 0.0, -0.1 ], [ 0.0, 0.0, 0.0, 0.1, 0.1, -0.2, -0.2, 0.0, -0.1 ], [ -0.2, 0.0, 0.0, 0.0, 0.0, 0.1, 0.1, -0.2, -0.1 ]]
        sense = state.getPacmanSensor()
        sense.append(1)
        decisions = [self.canMove(sense, weight) for weight in weight_sets]
        if decisions[0]:
            return Directions.NORTH
        elif decisions[1]:
            return Directions.EAST
        elif decisions[2]:
            return Directions.SOUTH
        elif decisions[3]:
            return Directions.WEST
        else:
            return Directions.NORTH

class SMAgent(Agent):
    "An sensory-impaired agent that follows the boundary using state machine."
    def registerInitialState(self,state):
        "The agent receives the initial GameState (defined in pacman.py)."
        sense = state.getPacmanImpairedSensor() 
        self.prevAction = Directions.STOP
        self.prevSense = sense

    def getAction(self, state):
        sense = state.getPacmanImpairedSensor()
        w1 = 1 if self.prevSense[0] and self.prevAction == Directions.EAST else 0
        w3 = 1 if self.prevSense[1] and self.prevAction == Directions.SOUTH else 0
        w5 = 1 if self.prevSense[2] and self.prevAction == Directions.WEST else 0
        w7 = 1 if self.prevSense[3] and self.prevAction == Directions.NORTH else 0
        w2, w4, w6, w8 = sense
        
        if w2 and not w4: currentAction = Directions.EAST
        elif w4 and not w6: currentAction = Directions.SOUTH
        elif w6 and not w8: currentAction = Directions.WEST
        elif w8 and not w2: currentAction = Directions.NORTH
        elif w1: currentAction = Directions.NORTH
        elif w3: currentAction = Directions.EAST
        elif w5: currentAction = Directions.SOUTH
        elif w7: currentAction = Directions.WEST
        else: currentAction = Directions.NORTH
        
        self.prevSense = sense
        self.prevAction = currentAction

        return currentAction
