import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot

import argparse

# Always raises by the min amount allowed, otherwise calls.
class AlwaysRaiseAgent(PokerBot):
    def __init__(self, host, port, gamefile):
        # Initialize networking stuff
        super(AlwaysRaiseAgent, self).__init__(host, port, gamefile)

        # Do agent specific initialization
		
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state, my_id)
        
        action = poker.Action()
	action.type = poker.CALL
       	action.size = 0
        raisevalid, minsize, maxsize = poker.raiseIsValid(self.game, state)
	if raisevalid:
	    action.type = poker.RAISE
	    action.size = minsize
            
	assert(poker.isValidAction( self.game, state, 0, action ) > 0)
        return action

# Take user input host and port
parser = argparse.ArgumentParser(description="run benchmark agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
args = parser.parse_args()

p = AlwaysRaiseAgent(args.host, args.port, args.gamefile)
p.run()
