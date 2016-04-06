import os
import numpy as np

class Params(object):

    def __init__(self, aid="", agent_dir="agent_params", params_list=None):
        self.aid = aid 
        self.agent_dir = agent_dir

        self.params = params_list
        if self.params is not None:
            self.params = params_list
        else:
            self.params = []

    ''' 
    writes this param object's parameters to file
    '''
    def write_params(self):
        np.savez(os.path.join(agent_dir,self.aid), *self.params)

    '''
    returns a params dict
    '''
    def read_params(self, aid, agent_dir):
        self.params = np.load(os.path.join(agent_dir,self.aid))
