import os
from parameters import Params
import numpy as np
from numpy.random import random_sample
import random
import uuid

def weighted_values(values, probabilities, size):
    bins = np.add.accumulate(probabilities)
    return values[np.digitize(random_sample(size), bins)]

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

    A higher-ranked parent agent is weighted more heavily when choosing which parents
    to mutate to create children.
'''
class Mutator(object):

    params_to_cross = 5
    params_to_mutate = 5
    std_mutation = 1
    parents_to_combine = 5

    def __init__(self, parent_agents=[], agent_dir="agent_params"):
        self.agent_dir = agent_dir
        self.parent_agents = [] 
        
        # insert in order of top-ranked parent agent to bottom agent
        for p in parent_agents:
            p_param = Params(aid=p, agent_dir=self.agent_dir)
            p_param.read_params()
            self.parent_agents.append(p_param)
        # calculate the parent probability of being chosen
        self.num_parents = len(parent_agents)
        self.parent_weights = [float(self.num_parents - i) / self.num_parents for i in range(self.num_parents)]
      
    '''
    Randomly choose two parent agents, prioritizing the top agents, 
    and exchange (params_to_cross) parameters chosen at random
    
    Writes the new agents to file, and returns the aids
    '''
    def crossover(self, num_agents_to_produce):
        agents = []
        for _ in xrange(num_agents_to_produce):
            parents = self.get_parents(2)

            # create a new agent and its parameters
            new_aid = str(uuid.uuid4())
            agents.append(new_aid)
            new_agent_params = Params(aid=new_aid, agent_dir=self.agent_dir)
           
            # randomize which parameters to take from which parents
            indices = range(len(parents[0].params))
            for i, j in enumerate(indices):
                if i < self.params_to_cross:
                    new_agent_params.params.append(parents[0].params[j])
                else:
                    new_agent_params.params.append(parents[1].params[j])
            print new_agent_params.params
            new_agent_params.write_params()
        return agents

    def mutate(self, num_agents_to_produce):
        agents = []
        for _ in xrange(num_agents_to_produce):
            parent = self.get_parents(1)[0]

            # create a new agent and its parameters
            new_aid = str(uuid.uuid4())
            agents.append(new_aid)
            new_agent_params = Params(aid=new_aid, agent_dir=self.agent_dir)
            
            # randomly add noise to weights
            for param in parent.params:
                new_agent_params.params.append(param + np.random.normal(0, 1, 1))
            print new_agent_params.params
            new_agent_params.write_params()
        return agents
    
    def combo(self, num_agents_to_produce):
        agents = []
        for _ in xrange(num_agents_to_produce):
            parents = self.get_parents(self.parents_to_combine)

            # create a new agent and its parameters
            new_aid = str(uuid.uuid4())
            agents.append(new_aid)
            new_agent_params = Params(aid=new_aid, agent_dir=self.agent_dir)
            
            # randomly assign each parent weights
            parent_weights = [random.random() for _ in xrange(len(parents))]

            # iterate through all parent parameters, calculating a weighted average
            # as the new agent's parameter
            for param_index in xrange(len(parents[0].params)):
                new_param = np.zeros((parents[0].params[param_index].shape))
                for i, p in enumerate(parents):
                    new_param += parent_weights[i] * p.params[param_index]
                new_param /= sum(parent_weights)
                new_agent_params.params.append(new_param)

            print new_agent_params.params
            new_agent_params.write_params()
        return agents

    def get_parents(self, nparents):
        parents = []
        for i in weighted_values(np.array(range(self.num_parents)), np.array(self.parent_weights), nparents):
            parents.append(self.parent_agents[i])
        return parents
