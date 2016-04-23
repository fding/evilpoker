import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot
from pokernet_nolimit import PokerNetNoLimit

import argparse
import numpy as np

class NeuralNetNolimitOpAgent(PokerBot):
    import cProfile
    def __init__(self, host, port, gamefile, paramf):
        # Initialize networking stuff

        # Initialize both self and op neural net with initial params
        self.neural_net = PokerNetNoLimit(maxn=2)
        self.neural_net.load_params(paramf)
        
        self.actions = [poker.FOLD, poker.CALL, poker.RAISE]
        self.prev_action = poker.FOLD

        super(NeuralNetNolimitOpAgent, self).__init__(host, port, gamefile)

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

        pot_features = [my_chips_in_pot, chips_in_pot, chips_to_call, nremaining, pos]
        chip_features = [poker.getStack(self.game, i) - poker.getSpent(state, i)
                         for i in range(nplayers) if not poker.getFolded(state, i)]
        s = sum(chip_features)
        chip_features = [c/float(s) for c in chip_features]

        action_output = self.neural_net.eval(nremaining, card_features, pot_features, chip_features)[0]
        action_probabilities = action_output[:3]
        raise_amount = int(action_output[3])
        
        #print card_features
        #print action_output[:3]
        #print 'Raise amount=', action_output[3] 
        
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
        #print action.type, action.size
        self.prev_action = action.type	
        assert(poker.isValidAction( self.game, state, 0, action ) > 0)
        return action

    def encode_action(self, action):
        if action.type == poker.RAISE:
            return [0,0,1,action.size]
        elif action.type == poker.CALL:
            return [0,1,0,200]
        elif action.type == poker.FOLD:
            return [1,0,0,200]
    
    # Turns finished state into a data array of features and targets.
    # Data array features match format in input files to neural network training
    # ONLY WORKS FOR 2 PLAYER
    def get_data_array(self, state):
        nplayers = 2
        # Assume everyone starts with the same number of chips
        chip_features = [0.5,0.5]
        viewing_player = state.viewingPlayer
        data = []
        # Pot starts with sb and bb
        # ** which player index is sb and which is bb? Assuming 0 is sb.
        chips_in_pot = [0,0]
        my_chips_in_pot = 0
        all_board_cards = poker.get_board_cards(self.game, state.state)
        for r in range(state.state.round + 1):
            num_actions = poker.getNumActions(state.state, r)
            for i in range(num_actions + 1):
                acting_player = poker.getActingPlayer(state.state, r, i)
                # Figure out which player is sb
                if r == 0 and i == 0:
                    chips_in_pot[acting_player] = 50
                    chips_in_pot[~acting_player] = 100
                chips_to_call = chips_in_pot[~acting_player] - chips_in_pot[acting_player]
                action = poker.getAction(state.state, r, i)
                # Only record opponent's actions
                if acting_player != viewing_player:
                    # *** Assuming that we can see cards even when the
                    # opponent folds for now.
                    hole_cards = poker.get_hole_cards(self.game, state.state, acting_player)
                    board_cards = all_board_cards[:0 if r == 0 else 3 + (r-1)]
                    card_features = poker.calculate_card_features(nplayers, hole_cards, board_cards)
                    pos = i
                    # Executive decision: not normalizing these
                    pot_features = [chips_in_pot[acting_player], sum(chips_in_pot), chips_to_call, nplayers, pos]
                    all_features = [nplayers] + card_features + pot_features + chip_features
                    action_vector = self.encode_action(action)
                    data.append(all_features + action_vector)
                    
                # Update total number of chips in pot whether acting player
                # is self or opponent
                if action.type == poker.RAISE:
                    chips_in_pot[acting_player] += action.size
                elif action.type == poker.CALL:
                    chips_in_pot[acting_player] += chips_to_call
		    assert(chips_in_pot[acting_player] == chips_in_pot[~acting_player])
        return data
    
    def run(self):
        while True:
            state = self.read_state()
            if not state:
                break
            if state.state.finished:
                print "Finished match:", self.line
                # Set up training input from state
                op_data = self.get_data_array(state)
                #print op_data
                
                # Calculate prediction accuracy of previous opponent
                # NN on new data
                err = self.neural_net.cost_array(op_data)
                print 'Validation error for opponent neural net: %s' % (str(err))
                # Backpropogation: update opponent NN params
                self.neural_net.backprop(op_data)
                continue

            if poker.currentPlayer(self.game, state.state) != state.viewingPlayer:
                continue
            
            action = self.what_should_i_do(state.viewingPlayer, state.state)
            self.do_action(action)
    
# Take user input host and port
parser = argparse.ArgumentParser(description="run neuralnet agent")
parser.add_argument('--dealer_host', dest='host', type=str)
parser.add_argument('--dealer_port', dest='port', type=int)
parser.add_argument('--game_file', dest='gamefile', type=str, default='holdem.nolimit.2p.game')
parser.add_argument('--param_file', dest='params', type=str)
args = parser.parse_args()
		
p = NeuralNetNolimitOpAgent(args.host, args.port, args.gamefile, args.params)
p.run()
