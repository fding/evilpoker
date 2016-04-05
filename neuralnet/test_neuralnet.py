from data_reader import DataReader
from neuralnet import (NeuralNet, RELU_FUN, SOFTMAX_FUN, SIGMOID_FUN)
import numpy as np

training = DataReader.GetImages('training-9k.txt', -1)
test = DataReader.GetImages('test-1k.txt', -1)

net = NeuralNet([196, 40, 10], [0], [2],
                [(None, None), ([0], RELU_FUN), ([1], SOFTMAX_FUN)], learning_rate=0.00001)
def mk_arr(n):
    ls = [0.0] * 10
    ls[n] = 1.0
    return ls

net.train([np.array(mk_arr(img.label)) for img in training],
          [[np.array(sum(img.pixels, []))] for img in training])
