import theano.tensor as T
import theano
import numpy
import math
from theano.compile.nanguardmode import NanGuardMode

'''
Choice of activation functions:

    For output units, use:
        LINEAR_FUN if you want to predict the mean of a Gaussian distribution
        SIGMOID_FUN if you want to predict a Bernoulli variable
        SOFTMAX_FUN if you want to predict a multinomial variable (i.e. a vector of outputs)

    For hidden units, use:
        RELU_FUN by default
'''

LINEAR_FUN = lambda x: x
SIGMOID_FUN = T.nnet.sigmoid
RELU_FUN = lambda x: T.nnet.relu(x, alpha=0.01)
SOFTMAX_FUN = T.nnet.softmax

# theano.config.optimizer = 'None'

class NeuralNet(object):

    def __init__(self, layers, input_layers, output_layers, wiring, learning_rate = 0.00001, L1REG = 1, L2REG = 0.001):
        '''
            NeuralNet(layers, wiring) creates a neural network with a specified topology consisting of N layers that are wired together.
            Layer L_n is a collection of #(L_n) nodes.
            Each non-input layer j takes k layers as input,
            where every node in layer j depends on every node in each of the input layers.
            This dependency is computed by taking a weighted linear combination of the nodes in L_i and applying a specified
            nonlinear function to it.

            :param layers: a list of integers, representing the number of nodes in each layer. The array index into this list is
                           defined to be the layer id.
            :param input_layers: a list of layer ids that together constitute the input of the neural network.
            :param output_layers: a list of layer ids that together constitute the output of the neural network.
            :param wiring: a list of tuples (inputs, f). The i-th element of this list corresponds to layer i.
                           This tuple contains a list of input layers for layer i ([] for input layers of the network).
                           f is the non-linear function to apply.

            Example:
                n = NeuralNet([3, 3, 6, 2], [0, 1], [3], [([], None), ([], None), ([1], RELU_FUN), ([0, 2], RELU_FUN)])
        '''
        self.layers = layers
        self.input_layers = input_layers
        self.output_layers = output_layers
        self.wiring = wiring

        self._vlayers = [None] * len(self.layers)
        for i in self.input_layers:
            self._vlayers[i] = T.matrix()

        self._vweights = [None] * len(self.layers)
        self._vbiases = [None] * len(self.layers)
        for i, (inputs, f) in enumerate(wiring):
            if not inputs:
                assert i in self.input_layers
                continue

            for j in inputs:
                assert self._vlayers[j] is not None
            assert self._vlayers[i] is None

            size = sum(self.layers[j] for j in inputs)

            self._vweights[i] = theano.shared(0.01 / numpy.sqrt(self.layers[i]) * numpy.random.randn(size, self.layers[i]))
            self._vbiases[i] = theano.shared(0.01 * numpy.random.randn(self.layers[i]))
            lin_comb = T.dot(T.concatenate([self._vlayers[j] for j in inputs]), self._vweights[i])
            add_biases = lin_comb + self._vbiases[i]
            self._vlayers[i] = f(add_biases)

        self._output = T.concatenate([self._vlayers[j] for j in self.output_layers])
        self._prediction = theano.function(inputs=[self._vlayers[i] for i in self.input_layers],
                                           outputs=self._output)

        self._target = T.matrix()
        outputp = T.switch(T.eq(self._output, 0), 0.00001, self._output)
        outputpp = T.switch(T.eq(outputp, 1), 0.999999, outputp)
        crossentropy = T.nnet.categorical_crossentropy(self._output, self._target)
        self._cost = (crossentropy.sum() + 
                      L2REG/(self.layers[i]) * sum((weight**2).sum() for weight in self._vweights if weight is not None) + # L2 regularization
                      L2REG/math.sqrt(self.layers[i]) * sum((bias**2).sum() for bias in self._vbiases if bias is not None))  # L2 regularization

        self._derivatives = [None] * len(self.layers)
        self._updates = []
        self.learning_rate = learning_rate

        MAX_DERIV = 1000
        for i, (inputs, f) in enumerate(wiring):
            if not inputs:
                continue
            deriv1 = T.grad(self._cost, self._vweights[i])
            deriv1p = T.switch(T.lt(deriv1, MAX_DERIV), deriv1, MAX_DERIV)
            deriv1pp = T.switch(T.gt(deriv1p, -MAX_DERIV), deriv1p, -MAX_DERIV)
            #deriv1ppp = T.switch(T.isnan(deriv1pp), 0, deriv1pp)
            deriv2 = T.grad(self._cost, self._vbiases[i])
            deriv2p = T.switch(T.lt(deriv2, MAX_DERIV), deriv2, MAX_DERIV)
            deriv2pp = T.switch(T.gt(deriv2p, -MAX_DERIV), deriv2p, -MAX_DERIV)
            #deriv2ppp = T.switch(T.isnan(deriv2pp), 0, deriv2pp)

            self._derivatives[i] = (deriv1pp, deriv2pp)

            self._updates.append((self._vweights[i], self._vweights[i] - self.learning_rate * self._derivatives[i][0]))
            self._updates.append((self._vbiases[i], self._vbiases[i] - self.learning_rate * self._derivatives[i][1]))

        self._train = theano.function(inputs=[self._target]+[self._vlayers[i] for i in self.input_layers],
                                      outputs=self._cost,
                                      updates=self._updates)
                                      #mode=NanGuardMode(nan_is_error=True, inf_is_error=True, big_is_error=True)) # debug NaN
        self._costfun = theano.function(inputs=[self._target]+[self._vlayers[i] for i in self.input_layers],
                                      outputs=self._cost)

    def set_weights(self, weights):
        '''
        set_weights: sets the weights of the neural network

        :param weights: a list of (weight, bias) tuples, the k-th
                        index of which gives the weights of layer k
                        (the tuple should be (None, None) for input layers).
                        Here, weight is an i by j numpy array and bias is a
                        size i numpy array.
        '''
        assert len(weights) == len(self.layers)
        for i, (inputs, _)  in enumerate(self.wiring):
            if i in self.input_layers:
                continue
            size = sum(self.layers[j] for j in inputs)
            assert weights[i][0].shape == (size, self.layers[i])
            assert weights[i][1].shape == (self.layers[i],)
            self._vweights[i].set_value(weights[i][0])
            self._vbiases[i].set_value(weights[i][1])

    def eval(self, inputs):
        '''
        eval: evaluates neural network on inputs

        :param inputs: a list of numpy 1d array representing inputs of the neural network.
                       The number of inputs should equal the number of input layers

        :return: a list of numpy1d array, corresponding to each output layer
        '''

        assert len(inputs) == len(self.input_layers)
        for i in self.input_layers:
            assert self.layers[i] == len(inputs[i])

        return self._prediction(*(inp.reshape(1, len(inp)) for inp in inputs))

    def train(self, target, inputs, max_epochs=1000, batch_size=100):
        '''
        train: trains the neural network using stochastic gradient descent
        
        :param target: a list of n arrays, where n is the number of training examples.
                       The k-th element of the list is the target output for the k-th
                       training example.
        :param inputs: a list of n lists of arrays.
                       The k-th element of inputs is the list of inputs for the k-th
                       training example
        '''
        assert len(inputs) == len(target)
        epoch = 0
        batches = []
        for i in range(int(math.ceil(len(inputs) / float(batch_size)))):
            ls = [[] for _ in range(len(inputs[0]))]
            for inp in inputs[i * batch_size: (i+1)*batch_size]:
                for j, arr in enumerate(inp):
                    ls[j].append(arr)

            batches.append((numpy.array(target[i*batch_size: (i+1)*batch_size]),
                [numpy.array(inp) for inp in ls]))
            assert len(batches[-1][1]) == len(self.input_layers)

        while epoch < max_epochs:
            epoch += 1
            batch_count = 0
            err_sum = 0.0
            for batch in batches:
                batch_count += 1
                err = self._train(batch[0], *batch[1])
                err_sum += err
            print 'Epoch %d: error = %.4f' % (epoch, err_sum/len(inputs))