'''
The evolution agent (EA) runs the evolutionary process
    1. creates a pool of N agents
    2. divides the agents into groups of n players to play poker games (n=2 default)
    3. creates a dealer for each game playing group
        - the dealer and agents play G games, where G is the number of games per epoch
        - for each game, the dealer outputs the result of the game, which is recorded and saved by EA
    4. after each epoch, EA ranks the agents and mutates the top agents (retaining a few top 
        unchanged agents) to generate the next population of agents, and reruns the algorithm
'''

import random
import os 
import uuid
from mutator import Mutator

class EvoAgent(object):

    to_mutate = 50
    to_keep = 5
    agent_dir = "agent_params"
    top_agent_file = "top_agent%d.txt"
    
    def __init__(self, num_agents=100, num_epochs=10, num_games_per_epoch=10, coevolve=False):
        self.num_epochs = num_epochs
        self.num_games_per_epoch = num_games_per_epoch
        self.num_agents = num_agents
        self.coevolve = coevolve
        
        self.num_game_players = 2

        self.benchmark_agents = []
        self.agents = []
        self.epoch_results = []
        
        if not os.path.exists(agent_dir):
            os.makedirs(agent_dir)
        
    '''
    Run by the main function to produce the top agents.
    Function that runs num_epochs epochs and writes the parameter results of the 
    top three evolved agents to file
    '''
    def produce_agents(self, num_agents):
        print "Producing 3 top agents of evolution:\n\
                %d epochs\n \
                %d agents\n\
                %d agents per game group\n\
                coevolution: %b\n" % \
                (self.num_epochs, self.num_agents, self.num_game_players, self.coevolve)
        
        self.run_epochs(self.to_mutate, self.to_keep)
        
        # get the parameters of the top agent
        for i in xrange(num_agents):
            with open(self.top_agent_file % i, 'w') as f:
                parameters = self.agents[self.top_agents[i]]
                for p in parameters:
                   f.write(p + "\n")
            print "Top agent %d parameters written to file %s" % (i, top_agent_file % i)

    '''
    Runs num_epoch epochs, each of which plays num_game games.
    After the end of each epoch, agents are ranked in order of their success in winning games.

    The top to_mutate agents are then mutated/crossed-over to generate the next population of 
    agents for the next epoch. The top to_keep agents from each generation are kept in the next generation
    as benchmarks for the next generation and to ensure that the evolution never loses progress.
    '''
    def run_epochs(self, to_mutate, to_keep):
        for _ in xrange(self.num_epochs):
            # set the gameplaying groups
            self.init_agent_gameplaying_groups(self.coevolve)
           
            # get the results of each epoch for each gameplaying group
            for group in self.game_groups:
                self.epoch_results.append(self.play_epoch(group))

            # sort the agents in order of rank 
            self.agents = self.rank_agents()
            mutate_agents = self.agents[:self.to_mutate]
            # get the top to_keep agents
            top_agents = self.agents[:self.to_keep]
            
            # mutate the agents for the next generation 
            self.mutator = Mutator(self.agents)
            num_agents_in_mutate_groups = len(mutate_agents)/3
            crossovers = self.mutator.crossover(num_agents_in_mutate_groups)
            mutated = self.mutator.mutate(num_agents_in_mutate_groups)
            combinations = self.mutator.combo(len(mutate_agents) - 2*num_agents_in_mutate_groups)

            # set the agents for the next epoch
            self.agents = crossovers + mutated + combinations + top_agents
            self.epoch_results = []

    '''
    Plays one epoch (num_games_per_epoch games) and outputs a list of
    the results, one entry per game
    '''
    def play_epoch(self, agents):    
        game_results = []
        for i in xrange(self.num_games):
            #TODO play game here
            # TODO fork off the dealer + agents here
            game_results.append(self.play_game(agents))
        return game_results

    '''
    Ranks the agents based upon the results from the epoch 
    '''
    def rank_agents(self):
        self.epoch_results
        # TODO 
        # use ids of self.agents, sort them somehow, return list
        return []

    ''' 
    Sets self.agents to be the initial list of agents as a dictionary
    mapping from an agent ID to the agent parameters
    '''
    def init_agents(self):
        self.agents = []
        for i in xrange(self.num_agents):
            # XXX David, is this a function you'd write?
            params = init_agent()
            uuid = uuid.uuid4()
            with open(os.path.join(agent_dir, "%s.txt" % uuid), 'w') as f:
                for p in param:
                    f.write(p + '\n')
            self.agents.append(uuid)

    ''' 
    Sets the list of benchmark agents the agent will
    play each game (only called if coevolve is false)
    '''
    def init_benchmark_agents(self):
        # TODO Serena?
        self.benchmark_agents = []

    '''
    Inits the game_groups list of lists indicating (by agent ID) which agents
    are playing which other agents

    If not coevolving the agents, game_groups indicates (by agent ID) the agent 
    in the population and the benchmark agents it is playing
    '''
    def init_agent_gameplaying_groups(self):
        self.init_agents()
        agent_game_groups = []
       
        if self.coevolve:
            agents_indices = range(len(self.agents))
            random.shuffle(agents_indicies)

            while (i < len(self.agents)):
                group = []
                for _ in xrange(self.num_game_players):
                    agent_game_groups.append(self.agents[i])
                    i += 1
        else:
            self.init_benchmark_agents()
            for agent in self.agents:
                agent_game_groups.append([agent] + self.benchmark_agents)

        return agent_game_groups

def main():
    evoagent = EvoAgent(num_agents=100,num_epochs=1,num_games_per_epoch=10,coevolve=False)
    evoagent.produce_agents(3)

if __name__ == "__main__":
    main()

