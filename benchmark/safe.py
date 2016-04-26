import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot

import argparse
import numpy as np

class SafeAgent(PokerBot):
    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state, my_id)
        nplayers = self.game.numPlayers
        nremaining = poker.numActingPlayers(self.game, state)

        if nremaining == 1:
            action = poker.Action()
            action.type = poker.CALL
            action.size = 0
            return action
         
        # pot features are chips in pot, chips to call, number of opponents, and position 
        chips_in_pot = poker.getPotSize(state, nplayers)
        p = poker.eval_hand_potential(nremaining, hole_cards, board_cards)
        expected_winning =  p / (1.001-p) * chips_in_pot

        chips_to_call = poker.chipsToCall(state, my_id)
        my_chips_in_pot = poker.getSpent(state, my_id)

        action = poker.Action()
        if chips_to_call <= expected_winning:
            action.type = poker.CALL
        else:
            action.type = poker.FOLD

        if (poker.isValidAction(self.game, state, 0, action ) <= 0):
            action.type = poker.CALL
        print expected_winning, chips_in_pot, chips_to_call
        print action.type, action.size
	
        assert(poker.isValidAction( self.game, state, 0, action ) > 0)
        return action


# Take user input host and port
parser = argparse.ArgumentParser(description="run safe agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
args = parser.parse_args()
		
p = SafeAgent(args.host, args.port, args.gamefile)
p.run()
