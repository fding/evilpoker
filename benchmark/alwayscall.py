import os
import sys
sys.path.append(os.getcwd())

import argparse
import pokerlib
from neuralnet import neuralnet
from pokerlib import poker
from pokerlib.pokerbot import PokerBot

class AlwaysCallAgent(PokerBot):
    def __init__(self, host, port, gamefile):
        # Initialize networking stuff
        super(AlwaysCallAgent, self).__init__()

        # Do agent specific initialization
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state)
        
		# Do I need to check if there are chips left? or does it fold automatically?
        action = Action()
        action.type = poker.CALL
        action.size = 0
        # How do we deal with passing by reference using swig??
        assert(poker.isValidAction( game, state.state, 0, action ) > 0)
        return action

# Take user input host and port
parser = argparse.ArgumentParser(description="run always call agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
args = parser.parse_args()
		
p = AlwaysCallAgent(args.host, args.port, args.gamefile)
p.run()
