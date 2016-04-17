import sys
import os
sys.path.append(os.getcwd())

from neuralnet import NeuralNet, RELU_FUN, SOFTMAX_FUN
#import pokerlib 
import numpy as np

class PokerNet(object):
    def __init__(self):
	pass
    def save_params(self, fname):
	raise NotImplementedError
    def train(self, input_file, validation_file, max_epochs = 1000):
	raise NotImplemented
    def cost(self, validation_file):
	raise NotImplemented
    def eval(self, nplayers, cardfeatures, potfeatures, chipfeatures):
	raise NotImplemented

class PokerNetLimit(PokerNet):
    '''Limit Holdem Neural Net'''
    def __init__(self, maxn=10):
        self.maxn = maxn
        # nets is a series of networks mapping nplayers to corresponding nnet
        self.nets = {}
        for i in xrange(2, maxn+1):
            self.nets[i] = NeuralNet(layers=[9, 5, i, 5, 8, 4], input_layers=[0, 1, 2], output_layers=[5],
                         wiring=[(None, None), (None, None), (None, None), ([0], RELU_FUN), ([1, 2, 3], RELU_FUN), ([4], SOFTMAX_FUN)],
                         learning_rate=0.00001, L2REG=0.001, build=False)

        # To prevent overfitting, share weights between the networks
        # as much as possible
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

        self.nets[2].rebuild()

    def save_params(self, fname):
        np.savez_compressed('pokernet-params/param-%s.npz' % fname,
                 self.nets[2]._vweights[3].get_value(),
                 self.nets[2]._vbiases[3].get_value(),
                 self.nets[2]._vweights[5].get_value(),
                 self.nets[2]._vbiases[5].get_value(),
                 *([self.nets[i]._vweights[4].get_value() for i in self.nets] + [self.nets[i]._vbiases[4].get_value() for i in xrange(2, self.maxn+1)]))

    def load_params(self, fname):
        with np.load(fname) as data:
            self.nets[2]._vweights[3].set_value(data['arr_0'])
            self.nets[2]._vbiases[3].set_value(data['arr_1'])
            self.nets[2]._vweights[5].set_value(data['arr_2'])
            self.nets[2]._vbiases[5].set_value(data['arr_3'])
            for i in xrange(2, self.maxn+1):
                self.nets[i]._vweights[4].set_value(data['arr_%d' % (2 + i)])

            for i in xrange(2, self.maxn+1):
                # XXX
                self.nets[i]._vbiases[4].set_value(data['arr_%d' % (self.maxn+1 + i)])

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
                            np.array(parts[-4 :]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-4 ])/sum(parts[15:-4 ])]))
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
                            np.array(parts[-4:]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-4])/sum(parts[15:-4])]))
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
                    self.save_params(counter)

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
                            np.array(parts[-4:]),
                            [np.array(parts[1: 10]), np.array(parts[10:15]), np.array(parts[15:-4])/sum(parts[15:-4])]))
                    except Exception as e:
                        pass

        errs = []
        for j in range(2, self.maxn+1):
            err = self.nets[j].cost([e[0] for e in validation[j]], [e[1] for e in validation[j]]) / float(len(validation[j]))
            errs.append(err)

        return errs

    def eval(self, nplayers, cardfeatures, potfeatures, chipfeatures):
        return self.nets[nplayers].eval([np.array(cardfeatures), np.array(potfeatures), np.array(chipfeatures)])

if __name__ == '__main__':
    p = PokerNetLimit()
    p.train(sys.argv[1], sys.argv[2])
