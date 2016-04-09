import os
import sys
sys.path.append(os.getcwd())

import pokerlib
from pokerlib.pokerbot import PokerBot
from neuralnet.pokernet import PokerNet

import numpy as np
import sys

class NeuralNet_Agent(PokerBot):
    def __init__(self, host, port, gamefile):
        # Initialize networking stuff
        super(AlwaysFoldAgent, self).__init__()

        self.neural_net = PokerNet()
        self.actions = [pokerlib.FOLD, pokerlib.CALL, pokerlib.RAISE]

    def what_should_i_do(self, my_id, state):
        board_cards = pokerlib.get_board_cards(self.game, state)
        hole_cards = pokerlib.get_hole_cards(self.game, state)
        nplayers = self.game.numPlayers

        card_features = calculate_card_features(nplayers, hole_cards, board_cards)
         
        # pot features are chips in pot, chips to call, number of opponents, and position 
        chips_in_pot = sum(state.spent)
        chips_to_call = self.game.stack[my_id]
        pos = pokerlib. get_current_pos(state)

        pot_features = [chips_in_pot, chips_to_call, nplayers, pos]
        chip_features = self.game.stack

        action_probabilities = self.neural_net.eval(self.nplayers, card_features, pot_features, chip_features)

        action = Action()
        action.type = np.random.choice(self.actions, 1, p=action_probabilities)
        action.size = 0
        raise_amount = 0 # TODO what is this? we need to set this somehow?

        if action.type == poker.Raise and poker.raiseIsValid( game, state.state. min, max) > 0:
            action.size = raise_amount
        # XXX when is a fold not valid?
        elif action.type == poker.Fold and not poker.isValidAction( game, state.state, 0, action):
            action.type = poker.CALL
	
        assert(pokerlib.isValidAction( game, state.state, 0, action ) > 0)
        return action

# Take user input host and port
try:
    opts, args = getopt.getopt(argv,["dealer_host=","dealer_port=","--game_file"])
except getopt.GetoptError:
    print 'USAGE: python neuralnet_agent.py --dealer_host=localhost --dealer_port=8080 --game_file=holdem.nolimit.2p.game'
    sys.exit(2)

host = 'localhost'
port = 8080
gamefile = ''
for opt, arg in opts:
	if opt == "--dealer_host":
		host = arg
	elif opt == "--dealer_port":
		port = arg
	elif opt == "--game_file":
		gamefile = arg
		
p = NeuralNet_Agent(host, port, gamefile)
p.run()
