import os
import sys
sys.path.append(os.getcwd())

import argparse

from pokerlib import poker
from pokerlib.pokerbot import PokerBot


# Always folds when valid, otherwise calls.
class AlwaysFoldAgent(PokerBot):
    def __init__(self, host, port, gamefile):
        # Initialize networking stuff
        super(AlwaysFoldAgent, self).__init__(host, port, gamefile)

        # Do agent specific initialization
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state, my_id)
        
        action = poker.Action()
        action.type = poker.FOLD
        action.size = 0
        if (not poker.isValidAction(self.game, state, 0, action ) > 0):
            action.type = poker.CALL
        return action

# Take user input host and port
parser = argparse.ArgumentParser(description="run benchmark agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
args = parser.parse_args()
		
p = AlwaysFoldAgent(args.host, args.port, args.gamefile)
p.run()
