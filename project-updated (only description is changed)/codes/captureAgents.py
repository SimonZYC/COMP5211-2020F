# captureAgents.py
# ----------------
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

"""
  Interfaces for capture agents and agent factories
"""

from game import Agent,Directions
from util import nearestPoint
import util


class RandomAgent(Agent):
  """
  A random agent that abides by the rules.
  """
  def __init__(self, index):
    self.index = index

  def getLegalActions(self,state):
    sensor = state.sensor

    legalActions = [Directions.STOP]
    if sensor[1] == 0:
        legalActions.append(Directions.NORTH)
    if sensor[3] == 0:
        legalActions.append(Directions.EAST)
    if sensor[5] == 0:
        legalActions.append(Directions.SOUTH)
    if sensor[7] == 0:
        legalActions.append(Directions.WEST)
    return legalActions

  def getAction(self, state):
    return random.choice(self.getLegalActions())

class CaptureAgent(Agent):
  """
  A base class for capture agents.  The convenience methods herein handle
  some of the complications of a two-team game.

  Recommended Usage:  Subclass CaptureAgent and override chooseAction.
  """

  #############################
  # Methods to store key info #
  #############################

  def __init__(self, index, timeForComputing=.1):
    """
    Lists several variables you can query:
    self.index = index for this agent
    self.red = true if you're on the red team, false otherwise
    self.observationHistory = list of GameState objects that correspond
        to the sequential order of states that have occurred so far this game
    self.timeForComputing = an amount of time to give each turn for computing maze distances
        (part of the provided distance calculator)
    """
    # Agent index for querying state
    self.index = index

    # A history of observations
    self.observationHistory = []

    # Time to spend each turn on computing maze distances
    self.timeForComputing = timeForComputing

    # Access to the graphics
    self.display = None

  def registerInitialState(self, state):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    """

    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display

  def final(self, state):
    self.observationHistory = []


  def observationFunction(self, state):
    " Changing this won't affect pacclient.py, but will affect capture.py "
    return state.makeObservation(self.index)

  def debugDraw(self, cells, color, clear=False):

    if self.display:
      from captureGraphicsDisplay import PacmanGraphics
      if isinstance(self.display, PacmanGraphics):
        if not type(cells) is list:
          cells = [cells]
        self.display.debugDraw(cells, color, clear)

  def debugClear(self):
    if self.display:
      from captureGraphicsDisplay import PacmanGraphics
      if isinstance(self.display, PacmanGraphics):
        self.display.clearDebug()

  #################
  # Action Choice #
  #################
  def getLegalActions(self,state):
    sensor = state.sensor

    legalActions = [Directions.STOP]
    if sensor[1] == 0:
        legalActions.append(Directions.NORTH)
    if sensor[3] == 0:
        legalActions.append(Directions.EAST)
    if sensor[5] == 0:
        legalActions.append(Directions.SOUTH)
    if sensor[7] == 0:
        legalActions.append(Directions.WEST)
    return legalActions

  def getAction(self, state):
    """
    Calls chooseAction on a grid position, but continues on half positions.
    If you subclass CaptureAgent, you shouldn't need to override this method.  It
    takes care of appending the current state on to your observation history
    (so you have a record of the game states of the game) and will call your
    choose action method if you're in a state (rather than halfway through your last
    move - this occurs because Pacman agents move half as quickly as ghost agents).

    """
    self.observationHistory.append(state)
    position=state.position
    if position != nearestPoint(position):
      # We're halfway from one position to the next
      return self.getLegalActions(state)[0]
    else:
      return self.chooseAction(state)

  def chooseAction(self, state):
    """
    Override this method to make a good agent. It should return a legal action within
    the time limit (otherwise a random legal action will be chosen for you).
    """
    util.raiseNotDefined()


  def getPreviousObservation(self):
    """
    Returns the GameState object corresponding to the last state this agent saw
    (the observed state of the game last time this agent moved - this may not include
    all of your opponent's agent locations exactly).
    """
    if len(self.observationHistory) == 1: return None
    else: return self.observationHistory[-2]

  def getCurrentObservation(self):
    """
    Returns the GameState object corresponding this agent's current observation
    (the observed state of the game - this may not include
    all of your opponent's agent locations exactly).
    """
    return self.observationHistory[-1]


class TimeoutAgent(Agent):
  """
  A random agent that takes too much time. Taking
  too much time results in penalties and random moves.
  """
  def __init__(self, index):
    self.index = index

  def getLegalActions(self,state):
    sensor = state.sensor

    legalActions = [Directions.STOP]
    if sensor[1] == 0:
        legalActions.append(Directions.NORTH)
    if sensor[3] == 0:
        legalActions.append(Directions.EAST)
    if sensor[5] == 0:
        legalActions.append(Directions.SOUTH)
    if sensor[7] == 0:
        legalActions.append(Directions.WEST)
    return legalActions

  def getAction(self, state):
    import random
    import time
    time.sleep(2.0)
    return random.choice(self.getLegalActions())
