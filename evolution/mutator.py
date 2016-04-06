import os
from parameters import Param

'''
Mutates the agents using three methods:
    - Crossover (divides weights for features into different groups and 
        exchanges groups of weights between agents)
    - Mutation: introduces random noise (Gaussian) to alter parent weights
    - Weighted Combination: takes a weight average of several parent agents'
        weights

    Each function returns a list of (num_agents_to_produce) agent IDs
    These agents have been assigned new IDs, and their parameters written to the 
    corresponding agent file.
'''
class Mutator(object):
    def __init__(self, parent_agents=[], agent_dir="agent_params"):
        self.parent_agents = []
        self.agent_dir = agent_dir
        # insert in order of top-ranked parent agent to bottom agent
        for p in parent_agents:
            with open(os.path.join(agent_dir, p), 'r') as f:
                feature_params = [line.split(':') for line in f.read().splitlines()]
                params = {}
                for feature, param in feature_params:
                    params[feature] = int(param)
                self.parent_agents.append(Params(p, agent_dir))
       
    def crossover(num_agents_to_produce):
        agents = {}
        for n in num_agents_to_produce:
            pass

    def mutate(num_agents_to_produce):
        pass
    
    def combo(num_agents_to_produce):
        pass
