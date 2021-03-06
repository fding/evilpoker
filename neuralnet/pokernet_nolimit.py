import sys
import os
sys.path.append(os.getcwd())

from neuralnet import NeuralNet, RELU_FUN, SOFTMAX_FUN, LINEAR_FUN
#import pokerlib 
import numpy as np
from pokernet import PokerNet

class PokerNetNoLimit(PokerNet):
    '''No Limit Holdem Neural Net'''
    def __init__(self, maxn=2):
        # Only supports 2 player
        self.maxn = maxn
        # nets is a series of networks mapping nplayers to corresponding nnet
        self.nets = {}
        for i in xrange(2, self.maxn+1):
            self.nets[i] = NeuralNet(layers=[9, 5, 8, 3, 1], input_layers=[0, 1], output_layers=[3, 4],
                         wiring=[(None, None), (None, None), ([0, 1], RELU_FUN), ([2], SOFTMAX_FUN), ([2, 3], LINEAR_FUN)],
                         learning_rate=0.00001, L2REG=0.001, build=False)

        # To prevent overfitting, share weights between the networks
        # as much as possible
        '''
        for i in xrange(3, self.maxn+1):
            assert self.nets[i]._vweights[3].get_value().shape == self.nets[2]._vweights[3].get_value().shape
            assert self.nets[i]._vbiases[3].get_value().shape == self.nets[2]._vbiases[3].get_value().shape
            assert self.nets[i]._vweights[5].get_value().shape == self.nets[2]._vweights[5].get_value().shape
            assert self.nets[i]._vbiases[5].get_value().shape == self.nets[2]._vbiases[5].get_value().shape
            self.nets[i]._vweights[3] = self.nets[2]._vweights[3]
            self.nets[i]._vbiases[3] = self.nets[2]._vbiases[3]
            self.nets[i]._vweights[5] = self.nets[2]._vweights[5]
            self.nets[i]._vbiases[5] = self.nets[2]._vbiases[5]
            self.nets[i].rebuild()
        '''

        self.nets[2].rebuild()
        self.nets[2]._vbiases[4].set_value(np.array([1.5]))

    # Performs backpropagation.
    # input_array should be an array of features and targets, as they would be in an input_file.
    def backprop(self, input_array):
        data = {}
        for i in range(2, self.maxn+1):
            data[i] = []
        # Process data as we would in self.train
        for parts in input_array:            
            data[parts[0]].append((np.array(parts[-4 : -1] + [max(1.0, parts[-1] / 200.0)]), [np.array(parts[1: 10]), np.array([p * 0.01 for p in parts[10:12]] + parts[12:15])]))
            
        for i in range(2, self.maxn+1):
            examples = data[i]
            self.nets[i].train([e[0] for e in examples],
                               [e[1] for e in examples],
                               max_epochs = 1,
                               batch_size=len(examples),
                               log=False)
        
    def train(self, input_file, validation_file, max_epochs = 1000):
        data = {}
        validation = {}
        current_batch = {}
        for i in range(2, self.maxn+1):
            data[i] = []
            validation[i] = []
            current_batch[i] = 0

        bad_training = 0
        with open(input_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-4]) != int(parts[0]):
                            bad_training += 1
                            continue
                        data[int(parts[0])].append((
                            np.array(parts[-4 : -1] + [max(1.0, parts[-1] / 200.0)]),
                            [np.array(parts[1: 10]), np.array([p * 0.01 for p in parts[10:12]] + parts[12:15])]))
                    except Exception as e:
                        bad_training += 1

        bad_validation = 0
        with open(validation_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-4 ]) != int(parts[0]):
                            bad_validation += 1
                            continue
                        validation[int(parts[0])].append((
                            np.array(parts[-4:-1] + [max(1.0, parts[-1]/200.0)]),
                            [np.array(parts[1: 10]), np.array([p * 0.01 for p in parts[10:12]] + parts[12:15])]))
                    except Exception as e:
                        bad_validation += 1

        print 'Finished loading data. %d bad training examples, %d bad validation examples' % (bad_training, bad_validation)
        batchsize = 500
        counter = 0
        validation_freq = 500
        for _ in xrange(max_epochs * len(data[2])):
            for i in range(2, self.maxn+1):
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
                    for j in range(2, self.maxn+1):
                        err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]]) / len(validation[j])
                        print 'Validation error for net %d after %d batches: %.4f' % (j, counter, err)
                    self.save_params(counter, dirname="agent_params_nolimit")

    # Computes cost from array of data points, validation_array
    # Note: only works for maxn=2, 2 player
    # Returns a single integer error value
    def cost_array(self, validation_array):
        validation = {}
        for i in range(2, self.maxn+1):
            validation[i] = []
        # Process data as we would in self.train
        for parts in validation_array:            
            validation[parts[0]].append((np.array(parts[-4 : -1] + [max(1.0, parts[-1] / 200.0)]), [np.array(parts[1: 10]), np.array([p * 0.01 for p in parts[10:12]] + parts[12:15])]))
            
        for j in range(2, self.maxn+1):
            err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]]) / len(validation[j])
        return err
    
    # Computes cost from validation file.               
    def cost(self, validation_file):
        validation = {}
        for i in range(2, self.maxn+1):
            validation[i] = []

        with open(validation_file) as f:
            for line in f:
                if line.strip():
                    try:
                        parts = map(float, line.strip().split())
                        if len(parts[15:-4]) != int(parts[0]):
                            continue
                        validation[int(parts[0])].append((
                            np.array(parts[-4:-1] + [max(1.0, parts[-1] / 200)]),
                            [np.array(parts[1: 10]), np.array([p * 0.01 for p in parts[10:12]] + parts[12:15])]))
                    except Exception as e:
                        pass

        errs = []
        for j in range(2, self.maxn+1):
            err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]]) / float(len(validation[j]))
            errs.append(err)

        return errs

if __name__ == '__main__':
    p = PokerNetNoLimit()
    p.train(sys.argv[1], sys.argv[2])
