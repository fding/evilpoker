import os
from parameters import Param
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
    params_to_combine = 5
    parents_to_combine = 5

    def __init__(self, parent_agents=[], agent_dir="agent_params"):
        self.agent_dir = agent_dir
        self.parent_agents = parent_agents
        
        # insert in order of top-ranked parent agent to bottom agent
        for p in parent_agents:
            self.parent_agents.append(Params(aid=p, agent_dir=agent_dir, create=False))
        # calculate the parent probability of being chosen
        self.num_parents = len(parent_agents)
        self.parent_weights = [float(self.num_parents - i) / self.num_parents for i in range(self.num_parents)]
      
    '''
    Randomly choose two parent agents, prioritizing the top agents, 
    and exchange (params_to_cross) parameters chosen at random
    
    Writes the new agents to file, and returns the aids
    '''
    def crossover(num_agents_to_produce):
        agents = []
        for n in num_agents_to_produce:
            parents = get_parents(2)

            # create a new agent and its parameters
            new_aid = uuid.uuid4()
            agents.append(new_aid)
            new_agent_params = Param(aid=new_aid, agent_dir=agent_dir, create=True)
           
            # randomize which parameters to take from which parents
            random.shuffle(Param.param_names)
            for i, param in enumerate(Param.param_names):
                if i < params_to_cross:
                    new_agent_params.param_dict[param] = parents[0].param_dict[param]
                else:
                    new_agent_params.param_dict[param] = parents[1].param_dict[param]
            new_agent_params.write_params()
        return agents

    def mutate(num_agents_to_produce):
        agents = []
        for n in num_agents_to_produce:
            parent = get_parents(1)[0]

            # create a new agent and its parameters
            new_aid = uuid.uuid4()
            agents.append(new_aid)
            new_agent_params = Param(aid=new_aid, agent_dir=agent_dir, create=True)
            
            # randomly add noise to weights
            for param in enumerate(Param.param_names):
                new_agent_params.param_dict[param] = np.random.normal(parent.param_dict[param], 1, 1)[0]

            new_agent_params.write_params()
        return agents
    
    def combo(num_agents_to_produce):
        agents = []
        for n in num_agents_to_produce:
            parents = get_parents(parents_to_combine)

            # create a new agent and its parameters
            new_aid = uuid.uuid4()
            agents.append(new_aid)
            new_agent_params = Param(aid=new_aid, agent_dir=agent_dir, create=True)
            
            # randomly assign each parent weights
            parent_weights = [random.random() for _ in xrange(len(parents))]

            for param in enumerate(Param.param_names):
                new_param = 0
                for i, p in enumerate(parents):
                    new_param += parent_weights[i] * p.param_dict[param]
                new_param /= sum(parent_weights)
                new_agent_params.param_dict[param] = new_param

            new_agent_params.write_params()
        return agents

    def get_parents(nparents):
        parents = []
        for i in weighted_values(np.array(range(self.num_parents)), np.array(self.parent_weights), nparents):
            parents.append(self.parent_agents[i])
        return parents
