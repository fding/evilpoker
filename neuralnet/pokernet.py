from neuralnet import NeuralNet, RELU_FUN, SOFTMAX_FUN
import numpy as np

class PokerNet(object):
    def __init__(self):
        # nets is a series of networks mapping nplayers to corresponding nnet
        self.nets = {
            2: NeuralNet(layers=[9, 5, 2, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            3: NeuralNet(layers=[9, 5, 3, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            4: NeuralNet(layers=[9, 5, 4, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            5: NeuralNet(layers=[9, 5, 5, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            6: NeuralNet(layers=[9, 5, 6, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            7: NeuralNet(layers=[9, 5, 7, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            8: NeuralNet(layers=[9, 5, 8, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            9: NeuralNet(layers=[9, 5, 9, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001),
            10: NeuralNet(layers=[9, 5, 10, 5, 8, 3], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None),
                                 ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001)
        }

        # To prevent overfitting, share weights between the networks
        # as much as possible
        for i in range(3, 11):
            assert self.nets[i]._vweights[3].get_value().shape == self.nets[2]._vweights[3].get_value().shape
            assert self.nets[i]._vbiases[3].get_value().shape == self.nets[2]._vbiases[3].get_value().shape
            assert self.nets[i]._vweights[5].get_value().shape == self.nets[2]._vweights[5].get_value().shape
            assert self.nets[i]._vbiases[5].get_value().shape == self.nets[2]._vbiases[5].get_value().shape
            self.nets[i]._vweights[3] = self.nets[2]._vweights[3]
            self.nets[i]._vbiases[3] = self.nets[2]._vbiases[3]
            self.nets[i]._vweights[5] = self.nets[2]._vweights[5]
            self.nets[i]._vbiases[5] = self.nets[2]._vbiases[5]
            self.nets[i].rebuild()

    def train(self, input_file, max_epochs = 100000):
        data = {}
        current_batch = {}
        for i in range(2, 11):
            data[i] = []
            current_batch[i] = 0
        with open(input_file) as f:
            for line in f:
                if line.strip():
                    parts = map(float, line.strip().split())
                    if len(parts[15:-3]) != int(parts[0]):
                        print 'Bad input'
                        continue
                    data[int(parts[0])].append((
                        np.array(parts[-3:]),
                        [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-3])/sum(parts[15:-3])]))

        batchsize = 500
        for _ in range(max_epochs):
            for i in range(2, 11):
                examples = data[i][current_batch[i]: current_batch[i] + batchsize]
                self.nets[i].train([e[0] for e in examples],
                                   [e[1] for e in examples],
                                   max_epochs = 1,
                                   batch_size=batchsize)
                current_batch[i] = current_batch[i] + batchsize
                if current_batch[i] > len(data[i]):
                    current_batch[i] = 0
