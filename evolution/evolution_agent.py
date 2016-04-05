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

class EvoAgent(object):

    evoagent_params_file = "evopoker_agent.txt"
    to_mutate = 50
    to_keep = 10
    
    def __init__(self, num_agents=100, num_epochs=10, num_games_per_epoch=10, coevolve=False):
        self.num_epochs = num_epochs
        self.num_games_per_epoch = num_games_per_epoch
        self.num_agents = num_agents
        self.coevolve = coevolve
        
        self.num_game_players = 2

        self.benchmark_agents = []
        self.agents = []
        self.epoch_results = []
        
        self.produce_agent()
    
    '''
    Main function that runs num_epochs epochs and writes the parameter results of the 
    top three evolved agents to file
    '''
    def produce_agent(self):
        print "Producing 3 top agents of evolution:\n\
                %d epochs\n \
                %d agents\n\
                %d agents per game group\n\
                coevolution: %b\n" % \
                (self.num_epochs, self.num_agents, self.num_game_players, self.coevolve)

        self.run_epochs(self.to_mutate, self.to_keep)
        
        # get the parameters of the top agent
        parameters = self.agents[self.top_agents[0]]
        for i in xrange(3):
            with open(self.evoagent_params_file + str(i), 'w') as f:
                for p in parameters:
                   f.write(p + "\n")
            print "Top agent %d parameters written to file evopoker_agent%d.txt" % (i, i)

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
            # get the top agents (arbitrarilty set to num_agents/2)
            mutate_agents = self.agents[:len(self.agents) - (self.to_mutate)]
            top_agents = self.agents[:len(self.agents) - (self.to_keep)]
            
            # reset the agents to be the next generation of agents
            self.agents = self.evolve(mutate_agents) + top_agents
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
    Returns a list of (num_agents - to_keep) agents with their parameters
    derived from the list of agents to mutate
    Assigns these agents new IDs
    '''
    def evolve(mutate_agents):
        # TODO 
        return []

    ''' 
    Sets self.agents to be the initial list of agents as a dictionary
    mapping from an agent ID to the agent parameters
    '''
    def init_agents(self):
        self.agents = []
        for i in xrange(self.num_agents):
            # TODO assign each agent an ID + parameter values
            pass

    ''' 
    Sets the list of benchmark agents the agent will
    play each game (only called if coevolve is false)
    '''
    def init_benchmark_agents(self):
        # TODO
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
