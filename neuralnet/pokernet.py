from neuralnet import NeuralNet, RELU_FUN, SOFTMAX_FUN
import pokerlib 
import numpy as np

import sys

class PokerNet(object):
    '''Limit Holdem Neural Net'''
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

    def save_params(self, fname):
        np.savez_compressed('pokernet-params/param-%s.npz' % fname,
                 self.nets[2]._vweights[3].get_value(),
                 self.nets[2]._vbiases[3].get_value(),
                 self.nets[2]._vweights[5].get_value(),
                 self.nets[2]._vbiases[5].get_value(),
                 *([self.nets[i]._vweights[4].get_value() for i in self.nets] + [self.nets[i]._vbiases[4].get_value() for i in self.nets]))

    def load_params(self, fname):
        with np.load(fname) as data:
            self.nets[2]._vweights[3].set_value(data['arr_0'])
            self.nets[2]._vbiases[3].set_value(data['arr_1'])
            self.nets[2]._vweights[5].set_value(data['arr_2'])
            self.nets[2]._vbiases[5].set_value(data['arr_3'])
            for i in range(2, 11):
                self.nets[i]._vweights[4].set_value(data['arr_%d' % (2 + i)])

            for i in range(2, 11):
                self.nets[i]._vbiases[4].set_value(data['arr_%d' % (11 + i)])

    def train(self, input_file, validation_file, max_epochs = 1000):
        data = {}
        validation = {}
        current_batch = {}
        for i in range(2, 11):
            data[i] = []
            validation[i] = []
            current_batch[i] = 0

        bad_training = 0
        with open(input_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-3]) != int(parts[0]):
                            bad_training += 1
                            continue
                        data[int(parts[0])].append((
                            np.array(parts[-3:]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-3])/sum(parts[15:-3])]))
                    except Exception as e:
                        bad_training += 1

        bad_validation = 0
        with open(validation_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-3]) != int(parts[0]):
                            bad_validation += 1
                            continue
                        validation[int(parts[0])].append((
                            np.array(parts[-3:]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-3])/sum(parts[15:-3])]))
                    except Exception as e:
                        bad_validation += 1

        print 'Finished loading data. %d bad training examples, %d bad validation examples' % (bad_training, bad_validation)
        batchsize = 500
        counter = 0
        validation_freq = 500
        for _ in range(max_epochs * max(map(len, data.values()))):
            for i in range(2, 11):
                counter += 1
                examples = data[i][current_batch[i]: current_batch[i] + batchsize]
                self.nets[i].train([e[0] for e in examples],
                                   [e[1] for e in examples],
                                   max_epochs = 1,
                                   batch_size=batchsize,
                                   log=False
                                  )
                current_batch[i] = current_batch[i] + batchsize
                if current_batch[i] > len(data[i]):
                    current_batch[i] = 0

                if counter % validation_freq == 0:
                    for j in range(2, 11):
                        err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]])
                        print 'Validation error for net %d after %d batches: %.4f' % (j, counter, err)
                    self.save_params(counter)

    def cost(self, validation_file):
        validation = {}
        for i in range(2, 11):
            validation[i] = []

        with open(validation_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-3]) != int(parts[0]):
                            continue
                        validation[int(parts[0])].append((
                            np.array(parts[-3:]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-3])/sum(parts[15:-3])]))
                    except Exception as e:
                        pass

        errs = []
        for j in range(2, 11):
            err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]]) / float(len(validation[j]))
            errs.append(err)

        return errs

    def eval(self, nplayers, cardfeatures, potfeatures, chipfeatures):
        return self.nets[nplayers].eval([cardfeatures, potfeatures, chipfeatures])

if __name__ == '__main__':
    p = PokerNet()
    p.train(sys.argv[1], sys.argv[2])
