# capture.py
# ----------
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


# capture.py
# ----------
# Licensing Information: Please do not distribute or publish solutions to this
# project.  You are free to use and extend these projects for educational
# purposes.  The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html
"""
Capture.py holds the logic for Pacman capture the flag.

  (i)  Your interface to the pacman world:
          Pacman is a complex environment.  You probably don't want to
          read through all of the code we wrote to make the game runs
          correctly.  This section contains the parts of the code
          that you will need to understand in order to complete the
          project.  There is also some code in game.py that you should
          understand.

  (ii)  The hidden secrets of pacman:
          This section contains all of the logic code that the pacman
          environment uses to decide who can move where, who dies when
          things collide, etc.  You shouldn't need to read this section
          of code, but you can if you want.

  (iii) Framework to start a game:
          The final section contains the code for reading the command
          you use to set up the game, then starting up a new game, along with
          linking in all the external parts (agent functions, graphics).
          Check this section out to see all the options available to you.

To play your first game, type 'python capture.py' from the command line.
The keys are
  P1: 'a', 's', 'd', and 'w' to move
  P2: 'l', ';', ',' and 'p' to move
"""
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning) 
from game import GameStateData
from game import Game
from game import Directions
from game import Actions
from util import nearestPoint
from util import manhattanDistance
from game import Grid
from game import Configuration
from game import Agent
from game import reconstituteGrid
import sys
import util
import types
import time
import random
import imp
import keyboardAgents

# If you change these, you won't affect the server, so you can't cheat
SIGHT_RANGE = 3 # Manhattan distance


###################################################
# YOUR INTERFACE TO THE PACMAN WORLD: A GameState #
###################################################
class ObeservedState():
    def __init__(self,position,target,sensor,radar,score):
        self.position = position
        self.target = target
        self.sensor = sensor
        self.radar = radar
        self.score = score # score so far
class GameState:
  """
  A GameState specifies the full game state, including the food, capsules,
  agent configurations and score changes.

  GameStates are used by the Game object to capture the actual state of the game and
  can be used by agents to reason about the game.

  Much of the information in a GameState is stored in a GameStateData object.  We
  strongly suggest that you access that data via the accessor methods below rather
  than referring to the GameStateData object directly.
  """

  ####################################################
  # Accessor methods: use these to access state data #
  ####################################################

  def getLegalActions(self, agentIndex=0):
    """
    Returns the legal actions for the agent specified.
    """
    return AgentRules.getLegalActions(self, agentIndex)

  def generateSuccessor(self, agentIndex, action):
    """
    Returns the successor state (a GameState object) after the specified agent takes the action.
    """
    # Copy current state
    state = GameState(self)

    # Find appropriate rules for the agent
    AgentRules.applyAction(state, action, agentIndex)
    AgentRules.checkDeath(state, agentIndex)

    # Book keeping
    state.data._agentMoved = agentIndex
    
  

    state.data.timeleft = self.data.timeleft - 1
    return state

  def getAgentState(self, index):
    return self.data.agentStates[index]

  def getAgentPosition(self, index):
    """
    Returns a location tuple if the agent with the given index is observable;
    if the agent is unobservable, returns None.
    """
    agentState = self.data.agentStates[index]
    ret = agentState.getPosition()
    if ret:
      return tuple(int(x) for x in ret)
    return ret

  def getNumAgents(self):
    return len(self.data.agentStates)

  def getScore(self):
    """
    Returns a number corresponding to the current score.
    """
    return self.data.score


  def getWalls(self):
    """
    Just like getFood but for walls
    """
    return self.data.layout.walls

  def hasWall(self, x, y):
    """
    Returns true if (x,y) has a wall, false otherwise.
    """
    return self.data.layout.walls[x][y]

  def isOver(self):
    return self.data._win




  #############################################
  #             Helper methods: #
  # You shouldn't need to call these directly #
  #############################################

  def __init__(self, prevState=None):
    """
    Generates a new state by copying information from its predecessor.
    """
    if prevState != None: # Initial state
      self.data = GameStateData(prevState.data)
      self.data.timeleft = prevState.data.timeleft

      self.agentDistances = prevState.agentDistances
    else:
      self.data = GameStateData()
      self.agentDistances = []

  def deepCopy(self):
    state = GameState(self)
    state.data = self.data.deepCopy()
    state.data.timeleft = self.data.timeleft

    state.agentDistances = self.agentDistances[:]
    return state


  def makeObservation(self, index):
    state = self.deepCopy()
    agentState = state.getAgentState(index)

    # current position of agent
    myPos = agentState.getPosition()
    myPos = (myPos[0],myPos[1])

    # a list of position of food ([(x,y)] or [])
    foodPos,eaten = state.data.foodPositions[index]
    targets = [(foodPos[0],foodPos[1])] if not eaten else []

    # sensor of walls, start from northwest, north,..., west
    sensors = Actions.getSensor(agentState.configuration,state.data.layout.walls)[:]

    # a list of positions of other agents within the sight range
    radar = []
    otherAgents = [i for i in range(len(state.data.agentStates)) if i != index]
    for enemy in otherAgents:
      enemyPos = state.getAgentPosition(enemy)
      if util.manhattanDistance(enemyPos, myPos) <= SIGHT_RANGE:
        radar.append((enemyPos[0],enemyPos[1]))

    # the score so far
    score = self.getScore()[index]
    obeservedState = ObeservedState(myPos,targets,sensors,radar,score)
    return obeservedState

  def __eq__(self, other):
    """
    Allows two states to be compared.
    """
    if other == None: return False
    return self.data == other.data

  def __hash__(self):
    """
    Allows states to be keys of dictionaries.
    """
    return int(hash(self.data))

  def __str__(self):

    return str(self.data)

  def initialize(self, layout, numAgents):
    """
    Creates an initial game state from a layout array (see layout.py).
    """
    self.data.initialize(layout, numAgents)





############################################################################
#                     THE HIDDEN SECRETS OF PACMAN #
#                                                                          #
# You shouldn't need to look through the code in this section of the file.  #
############################################################################
COLLISION_TOLERANCE = 0.7 # How close ghosts must be to Pacman to kill
class CaptureRules:
  """
  These game rules manage the control flow of a game, deciding when
  and how the game starts and ends.
  """

  def __init__(self, quiet=False):
    self.quiet = quiet

  def newGame(self, layout, agents, display, length, muteAgents, catchExceptions):
    initState = GameState()
    initState.initialize(layout, len(agents))
    starter = random.randint(0,1)
    print('%s team starts' % ['Red', 'Blue'][starter])
    game = Game(agents, display, self, startingIndex=starter, muteAgents=muteAgents, catchExceptions=catchExceptions)
    game.state = initState
    game.length = length


    game.state.data.timeleft = length
    if 'drawCenterLine' in dir(display):
      display.drawCenterLine()
    return game

  def process(self, state, game):
    """
    Checks to see whether it is time to end the game.
    """
    if 'moveHistory' in dir(game):
      if len(game.moveHistory) == game.length:
        state.data._win = True

    if state.isOver():
      game.gameOver = True
      if not game.rules.quiet:
        foodEaten = [eaten for (foodPos,eaten) in state.data.foodPositions]
        

        for i in range(len(foodEaten)):
            if ((not foodEaten[i]) and (state.data.score[i] != -1)):
                state.data.score[i] = 0
        for i in range(len(state.data.score)):
            print('Team %d scores %.2f.' % (i, state.data.score[i]))

  def getProgress(self, game):
    blue = 1.0 - (game.state.getBlueFood().count() / float(self._initBlueFood))
    red = 1.0 - (game.state.getRedFood().count() / float(self._initRedFood))
    moves = len(self.moveHistory) / float(game.length)

    # return the most likely progress indicator, clamped to [0, 1]
    return min(max(0.75 * max(red, blue) + 0.25 * moves, 0.0), 1.0)

  def agentCrash(self, game, agentIndex):
      print("Agent %d crashed" % agentIndex)
      game.state.data.score[agentIndex] = -1

  def getMaxTotalTime(self, agentIndex):
    return 900  # Move limits should prevent this from ever happening

  def getMaxStartupTime(self, agentIndex):
    return 15 # 15 seconds for registerInitialState

  def getMoveWarningTime(self, agentIndex):
    return 1  # One second per move

  def getMoveTimeout(self, agentIndex):
    return 3  # Three seconds results in instant forfeit

  def getMaxTimeWarnings(self, agentIndex):
    return 2  # Third violation loses the game
class AgentRules:
  """
  These functions govern how each agent interacts with her environment.
  """

  def getLegalActions(state, agentIndex):
    """
    Returns a list of legal actions (which are both possible & allowed)
    """
    agentState = state.getAgentState(agentIndex)
    conf = agentState.configuration
    possibleActions = Actions.getPossibleActions(conf, state.data.layout.walls)
    return AgentRules.filterForAllowedActions(agentState, possibleActions)
  getLegalActions = staticmethod(getLegalActions)

  def filterForAllowedActions(agentState, possibleActions):
    return possibleActions
  filterForAllowedActions = staticmethod(filterForAllowedActions)


  def applyAction(state, action, agentIndex):
    """
    Edits the state to reflect the results of the action.
    """

    foodEaten = [eaten for (foodPos,eaten) in state.data.foodPositions]
    nAgents = len(state.data.agentStates)
    isCollided = [state.data.score[i] == -1 for i in range(nAgents)]
    isfinished = [(foodEaten[i] or isCollided[i]) for i in range(nAgents)]
    if all(isfinished):
        state.data._win = True
        return
    if isCollided[agentIndex]:
        return


    state.data.stepsTaken[agentIndex]+=1

    if not foodEaten[agentIndex]:
        stepsTaken = state.data.stepsTaken[agentIndex]
        if stepsTaken > state.data.initDist[agentIndex]:
            state.data.score[agentIndex] = state.data.initDist[agentIndex] * 1.0 / stepsTaken




    legal = AgentRules.getLegalActions(state, agentIndex)
    if action not in legal:
      raise Exception("Illegal action " + str(action))

    # Update Configuration
    agentState = state.data.agentStates[agentIndex]
    speed = 1.0
    # if agentState.isPacman: speed = 0.5
    vector = Actions.directionToVector(action, speed)
    oldConfig = agentState.configuration
    agentState.configuration = oldConfig.generateSuccessor(vector)

    # Eat
    next = agentState.configuration.getPosition()
    nearest = nearestPoint(next)

    if manhattanDistance(nearest, next) <= 0.9 :
      AgentRules.consume(nearest, state, agentIndex)
  applyAction = staticmethod(applyAction)

  def consume(position, state, agentIndex):

    x,y = position

    foodPos, eaten = state.data.foodPositions[agentIndex]
    if eaten:
        return

      
    if foodPos == (x,y):
        state.data.foodPositions = state.data.foodPositions[:]
        state.data.foodPositions[agentIndex] = (foodPos, True)
        state.data._foodEaten = position
        #if (isRed and state.getBlueFood().count() == MIN_FOOD) or (not isRed
        #and state.getRedFood().count() == MIN_FOOD):
        #  state.data._win = True


  consume = staticmethod(consume)



  def checkDeath(state, agentIndex):
    if state.data.score[agentIndex] == -1:
        return
    agentState = state.data.agentStates[agentIndex]

    otherAgentsIndex = [i for i in range(len(state.data.agentStates)) if i != agentIndex]
    for index in otherAgentsIndex:
      otherAgentState = state.data.agentStates[index]
      otherPosition = otherAgentState.getPosition()
      if otherPosition == None: continue
      if manhattanDistance(otherPosition, agentState.getPosition()) <= COLLISION_TOLERANCE:
        state.data.score[agentIndex] = -1
        state.data.score[index] = -1

  checkDeath = staticmethod(checkDeath)

  def placeGhost(state, ghostState):
    ghostState.configuration = ghostState.start
  placeGhost = staticmethod(placeGhost)

#############################
# FRAMEWORK TO START A GAME #
#############################

def parseAgentArgs(str):
  if str == None or str == '': return {}
  pieces = str.split(',')
  opts = {}
  for p in pieces:
    if '=' in p:
      key, val = p.split('=')
    else:
      key,val = p, 1
    opts[key] = val
  return opts

def readCommand(argv):
  """
  Processes the command used to run pacman from the command line.
  """
  from argparse import ArgumentParser
  usageStr = """
  USAGE:      python pacman.py <options>
  EXAMPLES:   (1) python capture.py
                  - starts a game with two baseline agents
              (2) python capture.py --keys0
                  - starts a two-player interactive game where the arrow keys control agent 0, and all other agents are baseline agents
              (3) python capture.py --agent baselineTeam baselineTeam
                  - starts a fully automated game where the red team is a baseline team and blue team is myTeam
  """
  parser = ArgumentParser(usageStr)

  parser.add_argument("--agents",nargs="*",  help='A list of .py files', default=['baselineTeam','baselineTeam'])
  parser.add_argument('--keys0', help='Make agent 0 (red player) a keyboard agent', action='store_true',default=False)
  parser.add_argument('--keys1', help='Make agent 1 (blue player) a keyboard agent', action='store_true',default=False)
  parser.add_argument('-l', '--layout', dest='layout',
                    help='the LAYOUT_FILE from which to load the map layout; use RANDOM for a random maze; use RANDOM<seed> to use a specified random seed, e.g., RANDOM23',
                    metavar='LAYOUT_FILE', default='defaultCapture')
  parser.add_argument('-t', '--textgraphics', action='store_true', dest='textgraphics',
                    help='Display output as text only', default=False)

  parser.add_argument('-q', '--quiet', action='store_true',
                    help='Display minimal output and no graphics', default=False)

  parser.add_argument('-Q', '--super-quiet', action='store_true', dest="super_quiet",
                    help='Same as -q but agent output is also suppressed', default=False)

  parser.add_argument('-z', '--zoom', type=float, dest='zoom',
                    help='Zoom in the graphics', default=1.0)
  parser.add_argument('-i', '--time', type=int, dest='time',
                    help='TIME limit of a game in moves', default=100, metavar='TIME')
  parser.add_argument('-n', '--numGames', type=int,
                    help='Number of games to play', default=1)
  parser.add_argument('-f', '--fixRandomSeed', action='store_true',
                    help='Fixes the random seed to always play the same game', default=False)
  parser.add_argument('--record', action='store_true',
                    help='Writes game histories to a file (named by the time they were played)', default=False)
  parser.add_argument('--replay', default=None,
                    help='Replays a recorded game file.')
  parser.add_argument('-x', '--numTraining', dest='numTraining', type=int,
                    help='How many episodes are training (suppresses output)', default=0)
  parser.add_argument('-c', '--catchExceptions', action='store_true', default=False,
                    help='Catch exceptions and enforce time limits')

  options, otherjunk = parser.parse_known_args(argv)
  assert len(otherjunk) == 0, "Unrecognized options: " + str(otherjunk)
  args = dict()

  # Choose a display format
  #if options.pygame:
  #   import pygameDisplay
  #    args['display'] = pygameDisplay.PacmanGraphics()
  if options.textgraphics:
    import textDisplay
    args['display'] = textDisplay.PacmanGraphics()
  elif options.quiet:
    import textDisplay
    args['display'] = textDisplay.NullGraphics()
  elif options.super_quiet:
    import textDisplay
    args['display'] = textDisplay.NullGraphics()
    args['muteAgents'] = True
  else:
    import captureGraphicsDisplay
    # Hack for agents writing to the display
    captureGraphicsDisplay.FRAME_TIME = 0
    args['display'] = captureGraphicsDisplay.PacmanGraphics(options.agents[0], options.agents[1], options.zoom, 0, capture=True)
    import __main__
    __main__.__dict__['_display'] = args['display']


  args['redTeamName'] = 'RED'
  args['blueTeamName'] = 'BLUE'

  if options.fixRandomSeed: random.seed('COMP5211')

  # Special case: recorded games don't use the runGames method or args
  # structure
  if options.replay != None:
    print('Replaying recorded game %s.' % options.replay)
    import pickle
    recorded = pickle.load(open(options.replay,'rb'))
    recorded['display'] = args['display']
    replayGame(**recorded)
    sys.exit(0)

  nokeyboard = options.textgraphics or options.quiet or options.numTraining > 0
  print('%d teams to be loaded' % len(options.agents))
  print(*enumerate(options.agents),sep='\n')

  n_agents = len(options.agents)
  allAgents = []
  for i in range(n_agents):
    print('\nTeam %d %s ready.' % (i,options.agents[i]))
    allAgents.append(loadAgents(i, options.agents[i], nokeyboard, []))

  args['agents'] = sum([list(el) for el in zip(*allAgents)],[]) # list of agents

  numKeyboardAgents = 0
  for index, val in enumerate([options.keys0, options.keys1]):
    if not val: continue
    if numKeyboardAgents == 0:
      agent = keyboardAgents.KeyboardAgent(index)
    elif numKeyboardAgents == 1:
      agent = keyboardAgents.KeyboardAgent2(index)
    else:
      raise Exception('Max of two keyboard agents supported')
    numKeyboardAgents += 1
    args['agents'][index] = agent

  # Choose a layout
  import layout
  layouts = []
  for i in range(options.numGames):
    if options.layout == 'RANDOM':
      lay, positions, foodPositions = randomLayout(n_agents=n_agents)
      l = layout.Layout(lay.split('\n'))
      sortedPostions=[pos[1] for pos in l.agentPositions]
      sortedIndexes=[sortedPostions.index(pos) for pos in positions]
      l.positions = sortedPostions
      l.foodPositions = [foodPositions[index] for index in sortedIndexes]
    elif options.layout.startswith('RANDOM'):
      lay, positions, foodPositions = randomLayout(int(options.layout[6:]),n_agents=n_agents)
      l = layout.Layout(lay.split('\n'))
      sortedPostions=[pos[1] for pos in l.agentPositions]
      sortedIndexes=[sortedPostions.index(pos) for pos in positions]
      l.positions = sortedPostions
      l.foodPositions = [foodPositions[index] for index in sortedIndexes]
    elif options.layout.lower().find('capture') == -1:
      raise Exception('You must use a capture layout with capture.py')
    else:
      l = layout.getLayout(options.layout)
      l.positions = [pos[1] for pos in l.agentPositions]
      l.foodPositions = l.food.asList()[0:2]
      l.foodPositions.reverse()
    if l == None: raise Exception("The layout " + options.layout + " cannot be found")
    
    layouts.append(l)
    
  args['layouts'] = layouts
  args['length'] = options.time
  args['numGames'] = options.numGames
  args['numTraining'] = options.numTraining
  args['record'] = options.record
  args['catchExceptions'] = options.catchExceptions
  return args

def randomLayout(seed=None,n_agents=2):
  if not seed:
    seed = random.randint(0,99999999)
  # layout = 'layouts/random%08dCapture.lay' % seed
  # print 'Generating random layout in %s' % layout
  import mapGenerator
  lay, positions, foodPositions = mapGenerator.generateMaze(seed,n_agents)
  return lay, positions, foodPositions

import traceback
def loadAgents(agentIndex, factory, textgraphics, cmdLineArgs):
  "Calls agent factories and returns lists of agents"
  try:
    if not factory.endswith(".py"):
      factory += ".py"

    module = imp.load_source('player' + str(int(agentIndex)), factory)
  except (NameError, ImportError):
    print >> sys.stderr, 'Error: The team "' + factory + '" could not be loaded! '
    traceback.print_exc()
    return [None for i in range(1)]

  args = dict()
  args.update(cmdLineArgs)  # Add command line args with priority

  print("Loading Team:", factory)
  print("Arguments:", args)

  # if textgraphics and factoryClassName.startswith('Keyboard'):
  #   raise Exception('Using the keyboard requires graphics (no text display,
  #   quiet or training games)')

  try:
    createTeamFunc = getattr(module, 'createTeam')
  except AttributeError:
    print >> sys.stderr, 'Error: The team "' + factory + '" could not be loaded! '
    traceback.print_exc()
    return [None for i in range(1)]


  return createTeamFunc(agentIndex, **args)

def replayGame(layout, agents, actions, display, length, redTeamName, blueTeamName):
    rules = CaptureRules()
    game = rules.newGame(layout, agents, display, length, False, False)
    state = game.state
    display.redTeam = redTeamName
    display.blueTeam = blueTeamName
    display.initialize(state.data)

    for action in actions:
      # Execute the action
      state = state.generateSuccessor(*action)
      # Change the display
      time.sleep(0.5)
      display.update(state.data)
      # Allow for game specific conditions (winning, losing, etc.)
      rules.process(state, game)
    display.update(state.data)
    display.finish()

def runGames(layouts, agents, display, length, numGames, record, numTraining, redTeamName, blueTeamName, muteAgents=False, catchExceptions=False):

  rules = CaptureRules()
  games = []

  if numTraining > 0:
    print('Playing %d training games' % numTraining)

  for i in range(numGames):
    beQuiet = i < numTraining
    layout = layouts[i]
    if beQuiet:
        # Suppress output and graphics
        import textDisplay
        gameDisplay = textDisplay.NullGraphics()
        rules.quiet = True
    else:
        gameDisplay = display
        rules.quiet = False
    g = rules.newGame(layout, agents, gameDisplay, length, muteAgents, catchExceptions)
    g.run()
    if not beQuiet: games.append(g)

    if record:
      import time
      import pickle
      import game
      #fname = ('recorded-game-%d' % (i + 1)) + '-'.join([str(t) for t in
      #time.localtime()[1:6]])
      #f = file(fname, 'w')
      components = {'layout': layout, 'agents': [game.Agent() for a in agents], 'actions': g.moveHistory, 'length': length, 'redTeamName': redTeamName, 'blueTeamName':blueTeamName }
      #f.close()
      print("recorded")
      fname='replay-%d' % i
      pickle.dump(components, open(fname,'wb'))


  if numGames > 1:
    scores_breakdown = [[game.state.data.score[i] for game in games] for i in range(len(agents))]
    total_scores=[]
    for i in range(len(agents)):
        score_i=sum(scores_breakdown[i])
        total_scores.append(score_i)
        print('Total Score (Agent %d) : %.2f' % (i, score_i  ))
    for i in range(len(agents)):
        print('Scores (Agent %d):       ' % i, ', '.join(['%.2f' % (score) for score in scores_breakdown[i]]))

    score_highest=max(total_scores)
    winner=[i for i in range(len(total_scores)) if total_scores[i]==score_highest]
    if len(winner)==1:
        print('Agent %d wins'%winner[0])
    elif len(scores_breakdown)==2:
        print('Tie!')
    else:
        for i in winner:
            print('Agent %d wins'%winner[i])
  return games

def save_score(games):
    with open('score', 'w') as f:
        print(*[','.join([str(score) for score in game.state.data.score]) for game in games],sep='\n',file=f)

if __name__ == '__main__':
  """
  The main function called when pacman.py is run
  from the command line:

  > python capture.py

  See the usage string for more details.

  > python capture.py --help
  """
  options = readCommand(sys.argv[1:]) # Get game components based on input
  games = runGames(**options)

  save_score(games)
  # import cProfile
  # cProfile.run('runGames( **options )', 'profile')
