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
import fcntl
import time
import subprocess
import re
import operator
import argparse
from multiprocessing import Pool
from collections import defaultdict
from mutator import Mutator
from parameters import Params
import numpy as np
    
NUM_GAMES_PER_EPOCH = 1
NUM_AGENTS= 2
NUM_EPOCHS= 5
NUM_GAME_PLAYERS = 2
GAME = "game/holdem.nolimit.2p.game"
COEVOLVE = False

parser = argparse.ArgumentParser(description="evolve agent against other agents or benchmarks")
parser.add_argument('--bmfile', dest='bmfile', type=str)
args = parser.parse_args()
BMFILE = args.bmfile 

'''
Plays one epoch (NUM_GAMES_PER_EPOCH games) and outputs a dict of results, 
which maps a player's aid to the player's scores in each game
'''
def play_epoch(agents):    
    game_results = defaultdict(list)

    btes = map(ord, os.urandom(2))
    match_args = (GAME, btes[0] * 256 + btes[1],)
    
    # add all agents and the appropriate scripts to the game
    if COEVOLVE:
        for aid in agents:
            game_results[aid] = []
            match_args += (str(aid), "neuralnet/play_agent.sh",)
    else:
        game_results[agents[0]] = []
        match_args += ("benchmark", BMFILE, str(agents[0]), "neuralnet/play_agent.sh",)
    
    # play the games and record the output (which is the scores of the agents in the game)
    for i in xrange(NUM_GAMES_PER_EPOCH):
        play_game_str = "game/play_match.pl game %s 1000 %d %s %s %s %s" % match_args
        print "Playing: %s" % play_game_str

        output = subprocess.check_output(play_game_str, shell=True)
        if output.split(':')[0] == "SCORE": 
            # output should be of format SCORE:-530|530:Alice|Bob
            output = re.split(r'[:|]', output)
            game_results[output[3].strip()].append(int(output[1]))
            if output[4] != "benchmark":
                game_results[output[4].strip()].append(int(output[2]))
    return game_results


class EvoAgent(object):
    to_mutate = 50
    to_keep = 3
    agent_dir = "agent_params"
    top_agent_file = "top_agent%d"
    
    def __init__(self):

        self.benchmark_agents = []
        self.agents = []
        self.epoch_results = []
        
        if not os.path.exists(self.agent_dir):
            os.makedirs(self.agent_dir)
        
    '''
    Run by the main function to produce the top agents.
    Function that runs NUM_EPOCHS epochs and writes the parameter results of the 
    top three evolved agents to file
    '''
    def produce_agents(self, nagents):
        print "Producing %d top agents of evolution:\n\
                %d epochs\n\
                %d agents\n\
                %d players per game group\n\
                coevolution: %d\n" % \
                (nagents, NUM_EPOCHS, NUM_AGENTS, NUM_GAME_PLAYERS, COEVOLVE)
        
        self.run_epochs(self.to_mutate, self.to_keep)
        
        # get the parameters of the top agent
        for i in xrange(min(nagents, self.to_keep)):
            print "Top agent %d ID: %s" % (i, self.top_agents[i])

    '''
    Runs num_epoch epochs, each of which plays num_game games.
    After the end of each epoch, agents are ranked in order of their success in winning games.

    The top to_mutate agents are then mutated/crossed-over to generate the next population of 
    agents for the next epoch. The top to_keep agents from each generation are kept in the next generation
    as benchmarks for the next generation and to ensure that the evolution never loses progress.
    '''
    def run_epochs(self, to_mutate, to_keep):
        for i in xrange(NUM_EPOCHS):
            # set the gameplaying groups
            self.init_agent_gameplaying_groups()

            # maps from player to list player scores in games played during
            # the epoch
            self.epoch_results = {}
           
            p = Pool(8)
            all_game_scores = p.map(play_epoch, self.game_groups)
            
            # get the results of each epoch for each gameplaying group
            # don't record scores for benchmark
            for game_scores in all_game_scores: 
                for player, scores in game_scores.iteritems():
                    if player != "benchmark":
                        self.epoch_results[player] = scores

            # sort the agents in order of rank 
            self.agents = self.rank_agents()
            
            # get which agents to mutate
            self.mutate_agents = self.agents[:self.to_mutate]
            # mutate the agents for the next generation 
            self.mutator = Mutator(self.mutate_agents, self.agent_dir)
            NUM_AGENTS_in_mutate_groups = (NUM_AGENTS - self.to_keep)/3
            crossovers = self.mutator.crossover(NUM_AGENTS_in_mutate_groups)
            mutated = self.mutator.mutate(NUM_AGENTS_in_mutate_groups)
            combinations = self.mutator.combo(NUM_AGENTS - self.to_keep - 2*NUM_AGENTS_in_mutate_groups)

            # get the top to_keep agents
            self.top_agents = self.agents[:self.to_keep]

            # set the agents for the next epoch
            self.agents = crossovers + mutated + combinations + self.top_agents
            self.epoch_results = {}

            for aid in self.top_agents:
                print "---------------------------------------\n"
                print "Evaluating top agent %s from epoch %d: " % (aid, i)
                eval_string = "python evaluate_agent.py --benchmarkfile %s --game_file %s --num_games %d --aid %s" % (BMFILE, GAME, NUM_GAMES_PER_EPOCH, aid)
                print subprocess.check_output(eval_string, shell=True)
                print "---------------------------------------\n"

    '''
    Sorts agents based upon the results from the epoch 
    Top agents are placed first
    '''
    def rank_agents(self):
        sum_scores = []
        for aid, scores in self.epoch_results.iteritems():
            sum_scores.append((sum(scores), aid))
            sum_scores.sort(reverse=True)
        sorted_list = [aid for (_, aid) in sum_scores]
        return sorted_list

    ''' 
    Sets self.agents to be the initial list of agents as a dictionary
    mapping from an agent ID to the agent parameters
    '''
    def init_agents(self):
        self.agents = []
        noise = 0.001
        for i in xrange(NUM_AGENTS):
            aid = str(uuid.uuid4())
            initial_params = []
            with np.load(os.path.join(self.agent_dir,"initial-poker-params.npz")) as data:
                for i in range(len(data.keys())):
                    initial_params.append(data["arr_%d" % i] + np.random.normal(0, noise, 1)[0])
            agent_params = Params(aid=aid, agent_dir=self.agent_dir, params_list=initial_params)
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
       
        if COEVOLVE:
            agents_indices = range(len(self.agents))
            random.shuffle(agents_indices)

            i = 0
            while (i < len(self.agents)):
                group = []
                for _ in xrange(NUM_GAME_PLAYERS):
                    group.append(self.agents[i])
                    i += 1
                agent_game_groups.append(group)
        else:
            for agent in self.agents:
                agent_game_groups.append([agent])
                # the other agents will be benchmark agent programs
        self.game_groups = agent_game_groups

def main():
    evoagent = EvoAgent()
    evoagent.produce_agents(3)

if __name__ == "__main__":
    main()
