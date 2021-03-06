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
import sys
from multiprocessing import Pool
from collections import defaultdict
from mutator import Mutator
from parameters import Params
import numpy as np
    
NUM_GAMES_PER_EPOCH = 1
NUM_GAME_PLAYERS = 2

parser = argparse.ArgumentParser(description="evolve agent against other agents or benchmarks")
parser.add_argument('--bmfile', dest='bmfile', type=str, default='benchmark/play_callorraise.sh')
parser.add_argument('--nn_agent_file', dest='nn_agent_file', type=str, default='neuralnet/play_limit_agent.sh')
parser.add_argument('--agent_param_dir', type=str, dest='agent_dir', default="agent_params_limit")
parser.add_argument('--gamefile', dest='gamefile', type=str, default='game/holdem.limit.2p.game')
parser.add_argument('--ntopagents', type=int, dest='ntopagents', default=3)
parser.add_argument('--epochs', type=int, dest='epochs', default=50)
parser.add_argument('--nagents', type=int, dest='nagents', default=100)
parser.add_argument('--nagents_to_mutate', type=int, dest='nagents_to_mutate', default=25)
parser.add_argument('--nagents_to_keep', type=int, dest='nagents_to_keep', default=10)
parser.add_argument('--coevolve', dest='coevolve', action='store_true')
parser.add_argument('--nthreads', type=int, dest='nthreads', default=32)
parser.add_argument('--nhands', type=int, dest='nhands', default=500)
args = parser.parse_args()
NN_AGENT_FILE = args.nn_agent_file
NUM_AGENTS = args.nagents
NUM_EPOCHS = args.epochs
COEVOLVE = args.coevolve
TO_MUTATE = args.nagents_to_mutate
TO_KEEP = args.nagents_to_keep
GAME = args.gamefile
AGENT_DIR = args.agent_dir 
NUM_HANDS = args.nhands
benchmarks = ["benchmark/play_callorraise.sh", "benchmark/play_alwayscall.sh", "benchmark/play_alwaysfold.sh", "benchmark/play_alwaysraise.sh"]
'''
Plays one epoch (NUM_GAMES_PER_EPOCH games) and outputs a dict of results, 
which maps a player's aid to the player's scores in each game
'''
def play_epoch(agents):    
    game_results = defaultdict(list)

    btes = map(ord, os.urandom(2))
    match_args = (GAME, NUM_HANDS, btes[0] * 256 + btes[1],)
    
    # add all agents and the appropriate scripts to the game
    if COEVOLVE:
        for aid in agents:
            game_results[aid] = []
            match_args += (str(aid), NN_AGENT_FILE,)
    else:
        game_results[agents[0]] = []
    
    # play the games and record the output (which is the scores of the agents in the game)
    for i in xrange(NUM_GAMES_PER_EPOCH):
        play_game_strs = []
        if COEVOLVE:
            play_game_strs.append("game/play_match.pl game %s %d %d %s %s %s %s" % match_args)
            print >> sys.stderr, "Playing: %s" % play_game_strs[0] 
            sys.stderr.flush()

        else:
            for i, bm in enumerate(benchmarks):
                play_game_strs.append("game/play_match.pl game %s %d %d %s %s %s %s" % (match_args + ("benchmark", bm, str(agents[0]), NN_AGENT_FILE,)))
                print >> sys.stderr, "Playing: %s" % play_game_strs[i]
            sys.stderr.flush()

        for game in play_game_strs:
            try:
                output = subprocess.check_output(game, shell=True)
            except subprocess.CalledProcessError as e:
                raise Exception(str(e))

            if output.split(':')[0] == "SCORE": 
                # output should be of format SCORE:-530|530:Alice|Bob
                output = re.split(r'[:|]', output)
                game_results[output[3].strip()].append(int(output[1]))
                if output[4] != "benchmark":
                    game_results[output[4].strip()].append(int(output[2]))
    return game_results


class EvoAgent(object):
    def __init__(self):

        self.benchmark_agents = []
        self.agents = []
        self.epoch_results = []
        
        if not os.path.exists(AGENT_DIR):
            os.makedirs(AGENT_DIR)

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
	sys.stdout.flush()
        
        self.run_epochs(TO_MUTATE, TO_KEEP)
        
        # get the parameters of the top agent
        for i in xrange(min(nagents, TO_KEEP)):
            print "Top agent %d ID: %s" % (i, self.top_agents[i])
	sys.stdout.flush()

    '''
    Runs num_epoch epochs, each of which plays num_game games.
    After the end of each epoch, agents are ranked in order of their success in winning games.

    The top to_mutate agents are then mutated/crossed-over to generate the next population of 
    agents for the next epoch. The top to_keep agents from each generation are kept in the next generation
    as benchmarks for the next generation and to ensure that the evolution never loses progress.
    '''
    def run_epochs(self, to_mutate, to_keep):
        self.init_agents()
        for i in xrange(NUM_EPOCHS):
            # set the gameplaying groups
            self.init_agent_gameplaying_groups()

            # maps from player to list player scores in games played during
            # the epoch
            self.epoch_results = {}
           
            p = Pool(args.nthreads)
            all_game_scores = p.map(play_epoch, self.game_groups)
            
            # get the results of each epoch for each gameplaying group
            # don't record scores for benchmark
            for game_scores in all_game_scores: 
                for player, scores in game_scores.iteritems():
                    if player != "benchmark":
                        self.epoch_results[player] = self.epoch_results.get(player, []) + scores

            # sort the agents in order of rank 
            self.agents = self.rank_agents()
            
            # get which agents to mutate
            self.mutate_agents = self.agents[:TO_MUTATE]
            # mutate the agents for the next generation 
            self.mutator = Mutator(self.mutate_agents, AGENT_DIR)
            NUM_AGENTS_in_mutate_groups = (NUM_AGENTS - TO_KEEP)/3
            crossovers = self.mutator.crossover(NUM_AGENTS_in_mutate_groups)
            mutated = self.mutator.mutate(NUM_AGENTS_in_mutate_groups)
            combinations = self.mutator.combo(NUM_AGENTS - TO_KEEP - 2*NUM_AGENTS_in_mutate_groups)

            # get the top to_keep agents
            self.top_agents = self.agents[:TO_KEEP]

	    for aid in self.top_agents:
                print "---------------------------------------\n"
                print "Evaluating top agent %s from epoch %d: " % (aid, i)
                print "\tTotal Winnings: %d" % sum(self.epoch_results[aid])
                print "\tGames Won: %d/%d" % (len(filter(lambda x: x >= 0, self.epoch_results[aid])), 
                    len(self.epoch_results[aid]))
		sys.stdout.flush()

            # set the agents for the next epoch
            self.agents = crossovers + mutated + combinations + self.top_agents
            self.epoch_results = {}

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
            with np.load(os.path.join(AGENT_DIR,"initial-poker-params.npz")) as data:
                for i in range(len(data.keys())):
                    initial_params.append(data["arr_%d" % i] + np.random.normal(0, noise, 1)[0])
            agent_params = Params(aid=aid, agent_dir=AGENT_DIR, params_list=initial_params)
            self.agents.append(aid)

    '''
    Inits the game_groups list of lists indicating (by agent ID) which agents
    are playing which other agents

    If not coevolving the agents, game_groups indicates (by agent ID) the agent 
    in the population that is playing the game
    '''
    def init_agent_gameplaying_groups(self):
        agent_game_groups = []
       
        if COEVOLVE:
            agents_indices = range(len(self.agents))

            for _ in range(4):
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


if __name__ == "__main__":
    evoagent = EvoAgent()
    evoagent.produce_agents(args.ntopagents)

