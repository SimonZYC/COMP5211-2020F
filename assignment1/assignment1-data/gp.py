#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Yunchuan ZHENG
# UST id: 20614209

import numpy as np
import math
from pathlib import Path

LOCAL_PATH = Path(__file__).resolve().parents[0]
train_set = np.genfromtxt(LOCAL_PATH / "gp-training-set.csv", delimiter=',')

max_fitness = train_set.shape[0]
max_iter = 100
generation_size = 5000
weight_num = 9
weight_range = 2
th_range = 3
copy_num = math.ceil(generation_size * 0.1)
crossover_num = generation_size - copy_num
tournament_num = math.floor(generation_size / copy_num)
mutate_size = math.floor(generation_size * 0.01)

def init_gen0():
    perceptron = np.random.uniform(-weight_range, weight_range, generation_size * weight_num).reshape(generation_size, weight_num)

    th = np.random.uniform(-th_range, th_range, generation_size).reshape(-1, 1)

    return np.concatenate((perceptron, th), axis = 1)

def fitness(gen):
    
    sum_matrix = ((train_set[:, :weight_num] @ (gen[:, :weight_num].T)) > gen[:, weight_num].reshape(1, -1)).astype(int)
    scores = np.equal(sum_matrix, train_set[:, weight_num].reshape(-1, 1)).astype(int).sum(axis = 0)
    
    return scores

def copy(old_gen, fitness_arr):
    
    idx_to_copy = np.argpartition(-fitness_arr, copy_num)[:copy_num]
    to_copy = old_gen[idx_to_copy]
    old_gen = np.delete(old_gen, idx_to_copy)

    return to_copy

def mutation(old_gen):
    mutate_idx = np.random.randint(0, old_gen.shape[0] - 1, mutate_size)
    st = np.random.randint(0, weight_num - 1, mutate_size)
    old_gen[mutate_idx, -1] = np.random.uniform(-th_range, th_range, mutate_size)
    for i in range(mutate_size):
        old_gen[mutate_idx[i]][st[i]:-1] = np.random.uniform(-weight_range, weight_range, old_gen[mutate_idx[i]][st[i]:-1].shape[0])    

def crossover(old_gen, fitness_arr):
    crossovered = np.empty((crossover_num, weight_num + 1))
    for i in range(0, crossover_num, 2):
        idx_2parents = np.argpartition(-np.random.choice(fitness_arr, size = tournament_num, replace = False), 2)[:2]
        pos = np.random.randint(1, weight_num)
        old_gen[[0, 1]], old_gen[idx_2parents] = old_gen[idx_2parents], old_gen[[0, 1]]
        crossovered[i] = np.concatenate([old_gen[0][:pos], old_gen[1][pos:]])
        crossovered[i + 1] = np.concatenate([old_gen[1][:pos], old_gen[0][pos:]])
        old_gen = old_gen[2:]
    
    return crossovered

def reproduce(old_gen):
    new_gen = copy(old_gen, fitness(old_gen))
    mutation(old_gen)
    new_gen = np.concatenate([new_gen, crossover(old_gen, fitness(old_gen))])
    return new_gen

if __name__ == "__main__":

    gen = init_gen0()
    best = np.empty(weight_num + 1)
    best_fitness = 0
    best_gen_num = 0

    for i in range(max_iter):
        print("Current generation:", i)
        gen = reproduce(gen)
        fitness_arr = fitness(gen)
        idx_cur_best = np.argmax(fitness_arr)
        if fitness_arr[idx_cur_best] > best_fitness:
            best = gen[idx_cur_best]
            best_fitness = fitness_arr[idx_cur_best]
            best_gen_num = i
            print("\tImproved best fitness:", best_fitness)
            if best_fitness == max_fitness: break
        else:
            print("\tBest fitness:", fitness_arr[idx_cur_best])

    print("\nBest perceptron found in generation", best_gen_num)
    print("Output of the Genetic Programming System:")
    print(best)
    print("Best fitness:", best_fitness)