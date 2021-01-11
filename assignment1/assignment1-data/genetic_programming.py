# coding:utf-8

# Name: LI, Suyi
# Student ID: 20628597
#

import numpy as np
from os import popen, chdir
import random
import math

global data, gts


def read_dataset(file_name):
    data = []
    gts = []
    with open(file_name, "r") as fr:
        for line in fr:
            items = [ float(_) for _ in line.strip().split(",") ]
            data.append(items[:-1]+[1])
            gts.append(items[-1])
    return np.array(data), np.array(gts)


def fitness(data, gts, theta):
    return math.sqrt( sum([ (np.dot(data[i, ], theta) - gts[i])**2 for i in range(data.shape[0]) ] )) / data.shape[0]


def cross_over(g1, g2, point_num=2):
    '''
    Do cross-over precess
    '''
    rand_vec = np.zeros(len(g1))
    rand_vec[:point_num] = 1
    random.shuffle(rand_vec)
    g1_new = [g1[i] if rand_vec[i] else g2[i] for i in range(len(g1))]
    g2_new = [g2[i] if rand_vec[i] else g1[i] for i in range(len(g2))]
    return g1_new, g2_new

def mutation(g, point_num):
    '''
    Do mutation for one weight vector/rule
    A Gaussian noise will be added to the bits mutated.
    '''
    # Init mutation mask
    rand_vec = np.zeros(len(g))
    rand_vec[:point_num] = 1
    random.shuffle(rand_vec)
    # generate new genome
    new_g = [g[i] + random.gauss(np.mean(g), np.var(g)) if rand_vec[i] else g[i] for i in range(len(g))] 
    return new_g


def train_genetic_programe(dataset, gts, group_size=100, iter_num=1500):
    '''
    Do genetic programming here.
    Group with group_size different individuals, update for iter_num epochs.
    '''
    remain_frac = 0.7
    new_frac = 0.1
    group = np.random.randn(group_size, data.shape[1])

    for i in range(iter_num):
        score = np.array([fitness(dataset, gts, group[x, ]) for x in range(group.shape[0])])
        idx_ = score.argsort()

        data_to_remain = group[idx_[:int(0.1 * group_size)], ]
        data_to_change = group[idx_[:int(remain_frac * group_size)], ]

        copy_op = np.copy(data_to_remain)  # Copy operator
        copy_op = np.vstack((copy_op, np.random.randn(int(new_frac * group_size), data.shape[1])))
        
        while copy_op.shape[0] < group_size:
            rand_idx = random.uniform(0, 1)

            d2c = data_to_change.copy()
            np.random.shuffle(d2c)
            a1 = d2c[:2, ]
            if rand_idx < 0.5:  # Crossover op
                g1, _ = cross_over(a1[0], a1[1], 5)
            else:
                g1 = mutation(a1[0], 4)  # Mutation op
            copy_op = np.vstack((copy_op, g1))

        group = copy_op
        if i % 100 == 0:
            print i, np.mean(score[idx_[:4]]), group[idx_[0],]

    return group[idx_[0], ], score[idx_[0]]


if __name__ == '__main__':
    data, gts = read_dataset("gp-training-set.csv")
    print("data shape", data.shape)
    top_rule, top_score = train_genetic_programe(data, gts, 100, 1500)
    top_result = [1 if abs(np.dot(data[i, ], top_rule) - gts[i]) < 0.5 else 0 for i in range(data.shape[0]) ]
    print(sum(top_result)) 