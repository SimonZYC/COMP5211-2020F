# myTeam.py
# ---------
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


from captureAgents import CaptureAgent
import random, time, util
from game import Directions
import game

#################
# Team creation #
#################

def createTeam(index,
               agent = 'SimpleAgent'):
	"""
	The `agent` argument specifies which class to use.
	"""

	return [eval(agent)(index)]

##########
# Agents #
##########

class DummyAgent(CaptureAgent):
	"""
	A Dummy agent to serve as an example of the necessary agent structure.
	You should look at baselineTeam.py for more details about how to
	create an agent as this is the bare minimum.
	"""

	def registerInitialState(self, state):
		"""
		This method handles the initial setup of the
		agent to populate useful fields (such as what team
		we're on).


		IMPORTANT: This method may run for at most 15 seconds.
		"""


		CaptureAgent.registerInitialState(self, state)

		'''
		Your initialization code goes here, if you need any.
		'''


	def chooseAction(self, state):
		"""
		Picks among actions randomly.
		"""
		actions =  self.getLegalActions(state)
		position = state.position
		target = state.target
		sensor = state.sensor
		radar = state.radar
		score = state.score
		'''
		You should change this in your own agent.
		'''

		return random.choice(actions)

class SimpleAgent(CaptureAgent):
	def registerInitialState(self, state):
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
		print("action:", action, "features:", features)
		# print("weights:", weights)

		return features * weights
	
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

		dx, dy = self.ActionVector[action]
		pos = (x + dx, y + dy)

		if len(target) > 0:
			foodPos = target[0]
			features['distanceToFood'] = util.manhattanDistance(pos,foodPos)

		if len(target) == 0:
			if action == Directions.STOP:
				features['stopCondition'] = 1
			else:
				features['stopCondition'] = 0

		avgDistanceToEnemy = 0
		if len(radar) > 0:
			for enemy in radar:
				for enemyAction in self.ActionVector.values():
					enemyExpectPos = (enemy[0] + enemyAction[0], enemy[1] + enemyAction[1])
					avgDistanceToEnemy += util.manhattanDistance(pos, enemyExpectPos)
		features['distanceToEnemy'] = avgDistanceToEnemy / 5

		return features

	def getWeights(self, state, action):
		"""
		Normally, weights do not depend on the gamestate.  They can be either
		a counter or a dictionary.
		"""
		return {'distanceToFood': -1.0, 'stopCondition': 9999, 'distanceToEnemy': 2}