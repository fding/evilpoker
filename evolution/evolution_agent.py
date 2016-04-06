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
from parameters import Param

class EvoAgent(object):

    to_mutate = 50
    to_keep = 5

    num_hands = 10
    num_agents= 100
    num_epochs= 10
    num_games_per_epoch = 10
    num_game_players = 2

    agent_dir = "agent_params"
    top_agent_file = "top_agent%d"
    
    def __init__(self, coevolve=False):
        self.coevolve = coevolve

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
    def produce_agents(self, nagents):
        print "Producing 3 top agents of evolution:\n\
                %d epochs\n \
                %d agents\n\
                %d agents per game group\n\
                coevolution: %b\n" % \
                (self.num_epochs, self.num_agents, self.num_game_players, self.coevolve)
        
        self.run_epochs(self.to_mutate, self.to_keep)
        
        # get the parameters of the top agent
        for i in xrange(max(nagents, to_keep)):
            print "Top agent %d ID: %s" % (i, self.top_agents[i])

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

            # maps from player to list player scores in games played during
            # the epoch
            self.epoch_results = {}
           
            # get the results of each epoch for each gameplaying group
            for group in self.game_groups:
                # TODO parallelize
                for player, scores in self.play_epoch(group).iteritems():
                    self.epoch_results[player] = scores

            # sort the agents in order of rank 
            self.agents = self.rank_agents()
            
            # get which agents to mutate
            self.mutate_agents = self.agents[:self.to_mutate]
            # mutate the agents for the next generation 
            self.mutator = Mutator(self.mutate_agents)
            num_agents_in_mutate_groups = (self.num_agents - self.to_keep)/3
            crossovers = self.mutator.crossover(num_agents_in_mutate_groups)
            mutated = self.mutator.mutate(num_agents_in_mutate_groups)
            combinations = self.mutator.combo(self.num-agents - self.to_keep - 2*num_agents_in_mutate_groups)

            # get the top to_keep agents
            self.top_agents = self.agents[:self.to_keep]

            # set the agents for the next epoch
            self.agents = crossovers + mutated + combinations + top_agents
            self.epoch_results = {}

    '''
    Plays one epoch (num_games_per_epoch games) and outputs a dict of results, 
    which maps a player's aid to the player's scores in each game
    '''
    def play_epoch(self, agents):    
        game_results = {}
        
        match_args = ["play_match.pl",
                "match",
                "holdem.nolimit.2p.game",
                1000,
                random.randint()]
       
        # add all agents to the game
        if self.coevolve:
            for aid in agents:
                game_results[aid] = []
                match_args.append(aid)
                match_args.append("./agent.sh")

        else:
            game_results[agents[0]] = []
            match_args.append(agents[0])
            match_args.append("./play_agent.sh")
            match_args.append("benchmark")
            match_args.append("./play_benchmark.sh")

        # play the games and record the output (which is the scores of the agents in the game)
        for i in xrange(self.num_games_per_epoch):
            match = subprocess.Popen(match_args, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
            fcntl.fcntl(p.stdout.fileno(), fcntl.F_SETFL, os.O_NONBLOCK)
            
            while True:
                try:
                    output = dealer.stdout.read()
                except IOError:
                    pass
                # output should be of format SCORE:-530|530:Alice|Bob
                if output.split(':')[0] == "SCORE": 
                    output = re.split(r'[:|]', output)
                    game_results[output[3]].append(output[1])
                    if output[4] != "benchmark":
                        game_results[output[4]].append(output[2])
                    break

                time.sleep(.1)
        return game_results

    '''
    Sorts agents based upon the results from the epoch 
    Top agents are placed first
    '''
    def rank_agents(self):
        sum_scores = []
        for aid, scores in self.epoch_results.iteritems():
            sum_scores.append((aid, sum(scores)))
        sorted_list = [aid for aid, _ in sum_scores.sort(key=itemgetter(1), reverse=True)]
        return sorted_list

    ''' 
    Sets self.agents to be the initial list of agents as a dictionary
    mapping from an agent ID to the agent parameters
    '''
    # XXX David, is this a function you'd write?
    def init_agents(self):
        self.agents = []
        for i in xrange(self.num_agents):
            params = init_agent()
            aid = uuid.uuid4()
            with open(os.path.join(agent_dir, "%s" % aid), 'w') as f:
                for p in param:
                    f.write(p + '\n')
            self.agents.append(aid)

    '''
    Inits the game_groups list of lists indicating (by agent ID) which agents
    are playing which other agents

    If not coevolving the agents, game_groups indicates (by agent ID) the agent 
    in the population that is playing the game
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
            for agent in self.agents:
                agent_game_groups.append([agent])
                # the other agents will be benchmark agent programs
        return agent_game_groups

def main():
    evoagent = EvoAgent(coevolve=False)
    evoagent.produce_agents(3)

if __name__ == "__main__":
    main()

