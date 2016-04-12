from collections import defaultdict
import argparse
import re
import os
import subprocess

def play_game(aid, benchmarkfile, gamefile, ngames):    
    game_results = defaultdict(list)

    btes = map(ord, os.urandom(2))
    match_args = (gamefile, btes[0] * 256 + btes[1], "benchmark", benchmarkfile, aid)

    print match_args
    # play the games and record the output (which is the scores of the agents in the game)
    for _ in xrange(ngames):
        output = subprocess.check_output("game/play_match.pl game %s 1000 %d %s %s %s neuralnet/play_agent.sh" % match_args, shell=True)
        
        if output.split(':')[0] == "SCORE": 
            # output should be of format SCORE:-530|530:Alice|Bob
            print output
            output = re.split(r'[:|]', output)
            game_results[output[3].strip()].append(int(output[1]))
            game_results[output[4].strip()].append(int(output[2]))
    
    print "Agent %s overall score: %d (won %d/%d games)" % (aid, 
            sum(game_results[aid], ngames), len(filter(lambda x: x >0, game_results[aid])), ngames)
    print "Benchmark %s overall score: %d" % (benchmarkfile, sum(game_results['benchmark']))

    for k, v in game_results.iteritems():
        print "%s game scores: " % k, v

# Take user input host and port
parser = argparse.ArgumentParser(description="run evaluation of NN agent against a benchmark")
parser.add_argument('--num_games', dest='ngames', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='game/holdem.limit.2p.game')
parser.add_argument('--benchmarkfile', dest='bmfile', type=str, default='game/example_player.nolimit.2p.sh')
parser.add_argument('--aid', dest='aid', type=str, default='initial-poker-params')
args = parser.parse_args()

play_game(args.aid, args.bmfile, args.gamefile, args.ngames)
