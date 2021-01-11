# mazeGenerator.py
# ----------------
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


import random, sys
import util
from layout import pacman_char

"""
maze generator code

algorithm:
start with an empty grid
draw a wall with gaps, dividing the grid in 2
repeat recursively for each sub-grid

pacman details:
player 1 always start in the bottom left; 2 in the top right
food is placed in dead ends and then randomly (though not too close to the pacmen starting positions)

notes:
the final map includes a symmetric, flipped copy
the first wall has k gaps, the next wall has k/2 gaps, etc. (min=1)

@author: Dan Gillick
@author: Jie Tang
"""
mapSize=(8,8)

W = '%'
F = '.'
C = 'o'
E = ' '
P = 'p'

class Map:

  def __init__(self, rows, cols, anchor=(0, 0), root=None):
    """
    generate an empty maze
    anchor is the top left corner of this grid's position in its parent grid
    """
    self.r = rows
    self.c = cols
    self.grid = [[E for col in range(cols)] for row in range(rows)]
    self.anchor = anchor
    self.rooms = []
    self.root = root
    if not self.root: self.root = self

  def to_map(self):
    """
    add a border
    """

    ## add a border
    for row in range(self.r):
      self.grid[row] = [W] + self.grid[row] + [W]
    self.c += 2
    self.grid.insert(0, [W for c in range(self.c)])
    self.grid.append([W for c in range(self.c)])
    self.r += 2

  def __str__(self):
    s = ''
    for row in range(self.r):
      for col in range(self.c):
        s += self.grid[row][col]
      s += '\n'
    return s[:-1]

  

def add_pacman_stuff(maze, n_pacman=2):
  """
  add pacmen starting position
  add food 
  """

  agentMinDist=3
  mazeDiameter=maze.r+maze.c
  foodToAgentMinDist=mazeDiameter//3


  max_food=n_pacman
  positions=[]
  ## random pacmen starting position
  total_pacman=0
  while total_pacman < n_pacman:
    row = random.randint(1, maze.r-1)
    col = random.randint(1, maze.c-1)

    if total_pacman>0 and min([util.manhattanDistance((row,col),otherAgentPos) for otherAgentPos in positions])<agentMinDist:
        continue
    if maze.grid[row][col] == E:
        maze.grid[row][col] = pacman_char[total_pacman]
        positions.append((col,maze.r-1-row))
        total_pacman += 1

  ## random food
  foodPositions=[]
  total_food=0
  while total_food < max_food:
    row = random.randint(1, maze.r-1)
    col = random.randint(1, maze.c-1)
    if util.manhattanDistance((row,col),positions[total_food])>foodToAgentMinDist:
        if maze.grid[row][col] == E:
          maze.grid[row][col] = F
          foodPositions.append((col,maze.r-1-row))
          total_food += 1
  return positions, foodPositions
MAX_DIFFERENT_MAZES = 10000

def generateMaze(seed = None,n_agents=2):
  if not seed:
    seed = random.randint(1,MAX_DIFFERENT_MAZES)
  random.seed(seed)
  maze = Map(mapSize[0],mapSize[1])
  maze.to_map()
  positions, foodPositions=add_pacman_stuff(maze, n_agents)
  return str(maze),positions, foodPositions

if __name__ == '__main__':
  seed = None
  if len(sys.argv) > 1:
    seed = int(sys.argv[1])
  print(generateMaze(seed))

