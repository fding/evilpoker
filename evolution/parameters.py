import os
import numpy as np

class Params(object):

    def __init__(self, aid="", agent_dir="evolution/agent_params", params_list=None):
        self.aid = aid 
        self.agent_dir = agent_dir

        self.params = params_list
        if self.params is not None:
            self.params = params_list
            self.write_params()
        else:
            self.params = []

    ''' 
    writes this param object's parameters to file
    '''
    def write_params(self):
        np.savez(os.path.join(self.agent_dir,self.aid+".npz"), *self.params)

    '''
    returns a params dict
    '''
    def read_params(self):
        self.params = []
        with np.load(os.path.join(self.agent_dir,self.aid+".npz")) as data:
            for i in range(len(data.keys())):
                self.params.append(data["arr_%d" % i])
