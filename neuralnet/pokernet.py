import sys
import os
sys.path.append(os.getcwd())

from neuralnet import NeuralNet, RELU_FUN, SOFTMAX_FUN
#import pokerlib 
import numpy as np

class PokerNet(object):
    def __init__(self, maxn=10):
	self.maxn = maxn
        
    def save_params(self, fname, dirname="agent_params_nolimit"):
        extra_params = []
        for i in xrange(2, self.maxn+1):
            for j, (t, _) in enumerate(self.nets[2].wiring):
                if t is not None:
                    extra_params.append(self.nets[i]._vweights[j].get_value())
                    extra_params.append(self.nets[i]._vbiases[j].get_value())
        np.savez_compressed('%s/param-%s.npz' % (dirname, fname),
                 *extra_params)

    def load_params(self, fname):
        with np.load(fname) as data:
            count = 0
            for i in xrange(2, self.maxn+1):
                for j, (t, _) in enumerate(self.nets[2].wiring):
                    if t is not None:
                        self.nets[i]._vweights[j].set_value(data['arr_%d' % (count)])
                        count += 1
                        self.nets[i]._vbiases[j].set_value(data['arr_%d' % (count)])
                        count += 1

    def train(self, input_file, validation_file, max_epochs = 1000):
	    raise NotImplemented
    def cost(self, validation_file):
	    raise NotImplemented
    def eval(self, nplayers, cardfeatures, potfeatures, chipfeatures):
        ret = self.nets[nplayers].eval([np.array(cardfeatures), np.array([p * 0.01 for p in potfeatures[:3]] + potfeatures[3:])])
        ret[:, -1] *= 200
        return ret
