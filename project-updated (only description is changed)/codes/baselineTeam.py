# baselineTeam.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import random, time, util, sys
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(index,
               agent = 'GoStraightAgent'):
  """
  The `agent` argument specifies which class to use.
  """

  return [eval(agent)(index)]
##########
# Agents #
##########


class ReflexCaptureAgent(CaptureAgent):
  """
  A base class for reflex agents that chooses score-maximizing actions
  """
 
  def registerInitialState(self, state):
    self.start = state.position
    CaptureAgent.registerInitialState(self, state)

  def chooseAction(self, state):
    """
    Picks among the actions with the highest Q(s,a).
    """

    actions = self.getLegalActions(state)
    # print("Legal Actions:", actions)
    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(state, a) for a in actions]
    # print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)
    # print(values)
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    return bestActions[0]
 


  def evaluate(self, state, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(state, action)
    weights = self.getWeights(state, action)
    # print("features:", features)
    # print("weights:", weights)

    return features * weights

  def getFeatures(self, state, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    features['successorScore'] = 1
    return features

  def getWeights(self, state, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}



class GoStraightAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """
  ActionVector = {Directions.NORTH: (0, 1),
                Directions.SOUTH: (0, -1),
                Directions.EAST:  (1, 0),
                Directions.WEST:  (-1, 0),
                Directions.STOP:  (0, 0)}


  def getFeatures(self, state, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()    
    
    x,y=state.position
    target=state.target
    sensor=state.sensor
    radar=state.radar
    score=state.score
    
    # print("position: ", state.position, end = " ")
    # print("sensor: ", sensor, end="  ")
    # print("radar: ", radar, end="  ")
    # print("target: ", target)
    dx,dy=self.ActionVector[action]

    if len(target)>0:
        foodPos=target[0]
        pos=(x+dx,y+dy)
        features['distanceToFood'] = util.manhattanDistance(pos,foodPos)

    if len(target)==0:
        if action==Directions.STOP:
            features['stopCondition']=1
        else:
            features['stopCondition']=0

    return features

  def getWeights(self, state, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'distanceToFood': -1.0,'stopCondition': 9999}