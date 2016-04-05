
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
    def __init__(self, parent_agents=[], ):
        self.parent_agents = parent_agents
       
    def crossover(num_agents_to_produce):
        pass

    def mutate(num_agents_to_produce):
        pass
    
    def combo(num_agents_to_produce):
        pass
