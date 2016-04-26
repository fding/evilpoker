import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot
from pokernet_nolimit import PokerNetNoLimit

import argparse
import numpy as np


class NeuralNetNolimitAgent(PokerBot):
    import cProfile
    def __init__(self, host, port, gamefile, paramf):
        # Initialize networking stuff

        # For now, only support 2 player poker
        self.neural_net = PokerNetNoLimit(maxn=2)
        self.neural_net.load_params(paramf)
        self.actions = [poker.FOLD, poker.CALL, poker.RAISE]
        self.prev_action = poker.FOLD

        super(NeuralNetNolimitAgent, self).__init__(host, port, gamefile)

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

        card_features = poker.calculate_card_features(nremaining, hole_cards, board_cards)
         
        # pot features are chips in pot, chips to call, number of opponents, and position 
        chips_in_pot = poker.getPotSize(state, nplayers)

        chips_to_call = poker.chipsToCall(state, my_id)
        my_chips_in_pot = poker.getSpent(state, my_id)
        pos = poker.getNumActions(state, state.round)

        pot_features = [my_chips_in_pot * 0.01, chips_in_pot * 0.01, chips_to_call * 0.01, nremaining, pos]
        chip_features = [poker.getStack(self.game, i) - poker.getSpent(state, i)
                         for i in range(nplayers) if not poker.getFolded(state, i)]
        s = sum(chip_features)
        chip_features = [c/float(s) for c in chip_features]

        action_output = self.neural_net.eval(nremaining, card_features, pot_features, chip_features)[0]
        action_probabilities = action_output[:3]

        # action_probabilities[0] *= 100
        s = sum(action_probabilities)
        action_probabilities = action_probabilities / s
        raise_amount = int(action_output[3])
        
        print card_features
        print action_probabilities
        print 'Raise amount=', raise_amount
        
        action = poker.Action()
        action.type = np.random.choice(self.actions, 1, p=action_probabilities)[0]
        action.size = 0

        raisevalid, minsize, maxsize = poker.raiseIsValid(self.game, state)

        if action.type == poker.RAISE and raisevalid:
            if raise_amount < minsize:
                action.size = minsize
            elif raise_amount > maxsize:
                action.size = maxsize
            else:
                action.size = raise_amount
        elif action.type == poker.RAISE and not raisevalid:
            action.type = poker.CALL
        elif (poker.isValidAction(self.game, state, 0, action ) <= 0):
            action.type = poker.CALL

        if action.type == poker.RAISE and self.prev_action == poker.RAISE:
            action.type = poker.CALL
            action.size = 0
        print action.type, action.size
        self.prev_action = action.type	
        assert(poker.isValidAction( self.game, state, 0, action ) > 0)
        return action

# Take user input host and port
parser = argparse.ArgumentParser(description="run neuralnet agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
parser.add_argument('--param_file', dest='params', type=str)
args = parser.parse_args()
		
p = NeuralNetNolimitAgent(args.host, args.port, args.gamefile, args.params)
p.run()
