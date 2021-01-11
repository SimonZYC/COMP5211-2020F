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
from game import Directions, Actions
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


class SimpleAgent(CaptureAgent):
	def registerInitialState(self, state):
		CaptureAgent.registerInitialState(self, state)
		self.enemyPosHistory = []
		self.dirCounter = util.Counter()
		self.dirCounter.incrementAll([Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST, Directions.STOP], 1)
		self.stopCounter = 0
		self.enemyStopCounter = 0

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
		actValPair = dict(zip(actions, values))
		maxValue = max(values)
		bestActions = [a for a, v in actValPair.items() if v == maxValue]

		act = random.choice(bestActions)
		if act == Directions.STOP:
			self.stopCounter += 1
		else:
			self.stopCounter = 0

		if self.stopCounter > 2:
			actValPair.pop(Directions.STOP)
			maxValue = max(actValPair.values())
			bestActions = [a for a, v in actValPair.items() if v == maxValue]
			act = random.choice(bestActions)
			self.stopCounter = 0

		return act

	def evaluate(self, state, action): 
		return self.getValue(state, action)


	def getValue(self, state, action):
		x, y = state.position
		target = state.target
		sensor = state.sensor
		radar = state.radar
		score = state.score

		dx, dy = Actions.directionToVector(action)
		expectPos = (x + dx, y + dy)

		value = 0.0

		# whether the food has been eaten
		if len(target) == 0:
			if action == Directions.STOP:
				value += 999

		# distance to the target food
		if len(target) > 0:
			foodPos = target[0]
			value += util.manhattanDistance(expectPos, foodPos) * (-10.0)
			
			# chance of changing directions on shortest path  
			x_left = abs(target[0][0] - expectPos[0])
			y_left = abs(target[0][1] - expectPos[1])
			value += min(x_left, y_left) * 0.5

		# distance to the nearest enemy in sight
		# when 1v1
		if len(radar) == 1:
			value += util.manhattanDistance(expectPos, radar[0]) * (1.0)
			self.enemyPosHistory.append(radar[0])
			eph = self.enemyPosHistory
			detectedCounts = len(eph)
			if detectedCounts > 1:
				currentDirection = Actions.vectorToDirection((radar[0][0] - eph[detectedCounts - 2][0], radar[0][1] - eph[detectedCounts - 2][1]))
				self.dirCounter[currentDirection] += 4
				self.dirCounter[Directions.LEFT[currentDirection]] += 1
				self.dirCounter[Directions.RIGHT[currentDirection]] += 1
			dirCounterCopy = self.dirCounter.copy()
			dirCounterCopy.normalize()

			for key, prob in dirCounterCopy.items():
				move = Actions.directionToVector(key)
				enemyExpectPos = (radar[0][0] + move[0], radar[0][1] + move[1])
				expectDistValue = util.manhattanDistance(expectPos, enemyExpectPos)
				if expectDistValue == 0:
					expectDistValue = -9999999.9
				else:
					expectDistValue = -expectDistValue
				value += expectDistValue * prob

		elif len(radar) > 1: # more than 2 players	
			dist2Enemy = []
			for enemy in radar:
				dist2Enemy.append(util.manhattanDistance(expectPos, enemy))
			
			value += min(dist2Enemy) * (1.0)
		
		return value
		