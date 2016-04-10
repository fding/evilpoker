import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot
from neuralnet.pokernet import PokerNet

import numpy as np
import sys

class NeuralNetAgent(PokerBot):
    def __init__(self, host, port, gamefile, paramf):
        # Initialize networking stuff
        super(NeuralNetAgent, self).__init__()

        self.neural_net = PokerNet()
        self.neural_net.load_params(paramf)
        self.actions = [pokerlib.FOLD, pokerlib.CALL, pokerlib.RAISE]

    def what_should_i_do(self, my_id, state):
        board_cards = pokerlib.get_board_cards(self.game, state)
        hole_cards = pokerlib.get_hole_cards(self.game, state)
        nplayers = self.game.numPlayers
        nremaining = poker.numActingPlayers(self.game, state)

        card_features = calculate_card_features(nremaining, hole_cards, board_cards)
         
        # pot features are chips in pot, chips to call, number of opponents, and position 
        chips_in_pot = poker.getPotSize(state.spent, nplayers)

        chips_to_call = poker.chipsToCall(state, my_id)
        my_chips_in_pot = poker.getSpent(state, my_id)
        pos = poker.getNumActions(state, state.round)

        pot_features = [my_chips_in_pot, chips_in_pot, chips_to_call, nremaining, pos]
        chip_features = [poker.getStack(self.game, i) - poker.getSpent(state, i)
                         for i in range(nplayers) if not poker.getFolded(state, i)]

        action_probabilities = self.neural_net.eval(self.nplayers, card_features, pot_features, chip_features)

        action = Action()
        action.type = np.random.choice(self.actions, 1, p=action_probabilities)
        action.size = 0

        raisevalid, minsize, maxsize = poker.raiseIsValid(game, state.state)
        if action.type == poker.Raise and raisevalid:
            action.size = 0 # for no limit, size can be anything
        elif action.type == poker.Raise and not raisevalid:
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
		
p = NeuralNetAgent(host, port, gamefile)
p.run()
