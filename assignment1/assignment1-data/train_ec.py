import numpy as np

def train(training_x, label):
    weights = np.zeros(training_x.shape[1])
    train_num = training_x.shape[0]
    count = 0
    while count < train_num:
        for i in range(train_num):
            f_d = (np.dot(weights, training_x[i]) >= 0) - label[i]
            if f_d:
                weights = weights - 0.1 * f_d * training_x[i]
                count = 0
            else:
                count += 1
    return weights

def train_all(filenames):
    weight_sets = []
    for f_name in filenames:
        training_set = np.genfromtxt(f_name, delimiter=',')
        label = training_set[:, -1].copy()
        training_set[:, -1] = np.ones(training_set.shape[0])
        weight_sets.append(train(training_set, label))
    return np.array(weight_sets)

def print_weights(weight_sets):
    print("[", end="")
    for row in weight_sets:
        print("[", row[0], end = "")
        for i in range(1, len(row)):
            print(",", row[i], end="")
        print(" ], ", end = "")
    print("]")

def decide(weights, inputs):
    return np.dot(weights, np.append(inputs, 1)) >= 0

if __name__ == "__main__":
    ws = train_all(['north.csv', 'east.csv', 'south.csv', 'west.csv'])
    print_weights(ws)