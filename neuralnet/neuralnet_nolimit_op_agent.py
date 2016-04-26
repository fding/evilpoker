import os
import sys
sys.path.append(os.getcwd())

from pokerlib import poker
from pokerlib.pokerbot import PokerBot
from pokernet_nolimit import PokerNetNoLimit

import argparse
import numpy as np
import math
import time

class State(object):
    def __init__(self):
        self.hands = [[], []]
        self.boardcards = []
        self.hiddenboardcards = []
        self.actions = []
        self.pot = 0
        self.chips_per_player = [0, 0]
        self.betsize = 0
        self.neural_nets = {}
        
    def savestate(self):
        self.oldboardcards = self.boardcards[:]
        self.oldpot = self.pot
        self.oldchips_per_player = self.chips_per_player[:]
        self.oldbetsize = self.betsize

    def restorestate(self):
        self.boardcards = self.oldboardcards[:]
        self.pot = self.oldpot
        self.betsize = self.oldbetsize
        self.chips_per_player = self.oldchips_per_player[:]

    def step(self, curplayer, ncallsinrow, nraiseinrow, pos):
        pot_features = [self.chips_per_player[curplayer] * 0.01, self.pot * 0.01, (self.betsize - self.chips_per_player[curplayer]) * 0.01, 2, pos]
        card_features = poker.calculate_card_features(2, self.hands[curplayer], self.boardcards)

        cur_neural_net = self.neural_nets[curplayer]
        
        # Generate opponent moves
        action_output = cur_neural_net.eval(2, card_features, pot_features, [.5,.5])[0]
        action_probabilities = action_output[:3]
        action_probabilities[0] *= 20

        if nraiseinrow[curplayer] >= 1:
            action_probabilities[2] = 0
        
        s = sum(action_probabilities)
        action_probabilities = action_probabilities / s
        at = np.random.choice([poker.FOLD, poker.CALL, poker.RAISE], 1, p=action_probabilities)[0]
        rs = int(action_output[3])
        
        nremaining = 2
        self.doaction(curplayer, at, rs)
        if at == poker.RAISE:
            ncallsinrow = 0
            nraiseinrow[curplayer] += 1
        elif at == poker.CALL:
            ncallsinrow += 1
            nraiseinrow[curplayer] = 0
        else:
            nremaining -= 1

        return ncallsinrow, nraiseinrow, nremaining

    def run_round_to_finish(self, curplayer, ncallsinrow, pos):
        # First, finish current round
        nremaining = 2
        nraiseinrow = [0, 0]
        while ncallsinrow < 2:
            ncallsinrow, nraiseinrow, nremaining = self.step(curplayer, ncallsinrow, nraiseinrow, pos)
            pos += 1
            curplayer = 1 - curplayer
            if nremaining == 1:
                break
        return curplayer, nremaining

    def score(self, who, whowon):
        if who == whowon:
            return self.pot - self.chips_per_player[who]
        else:
            return -self.chips_per_player[who]

    def doaction(self, curplayer, action_type, raise_size):
        if action_type == poker.RAISE:
            self.pot += raise_size - self.chips_per_player[curplayer]
            self.chips_per_player[curplayer] = raise_size
            self.betsize = raise_size
        elif action_type == poker.CALL:
            self.pot += self.betsize - self.chips_per_player[curplayer]
            self.chips_per_player[curplayer] = self.betsize

def dprint(fmt, *args):
    # To disable debug printing, change this to false
    if True:
        print (('[Opponent Modeling] [ts %s]' % time.time()) + fmt) % args
        sys.stdout.flush()

def simulate(my_id, game, state, nets, action_probabilities, raise_size, chips_to_call, minraise):
    t_start = time.time()
    dprint('Started at %s', t_start)
    deck = poker.Deck()
    for card in poker.get_board_cards(game, state):
        deck.seen(poker.card_to_int(card))
    for card in poker.get_hole_cards(game, state, my_id):
        deck.seen(poker.card_to_int(card))

    raise_sizes = [raise_size * 0.5, raise_size * 0.75, raise_size, raise_size * 1.25, raise_size * 1.5, raise_size * 2, raise_size * 3, raise_size * 5, raise_size * 10, raise_size * 100]
    raise_sizes = [int(r) for r in raise_sizes if r > minraise]
    raise_num = [1.0 for _ in raise_sizes]
    raise_num[-1] = 0.05
    raise_num[-2] = 0.2
    raise_denom = sum(raise_num)

    action_num = [int(a * 16) + 1 for a in action_probabilities]
    # Folding is invalid in this case
    if chips_to_call == 0:
        action_num[0] = 0
    action_denom = sum(action_num)

    for i in range(100):
        dprint('Round %d. My id=%d', i, my_id)
        # Assign random cards
        s = State()
        logpval = 0
        deck.reset()
        s.neural_nets = nets
        s.boardcards = poker.get_board_cards(game, state)
        s.hands[my_id] = poker.get_hole_cards(game, state, my_id)
        s.hands[1 - my_id].append(poker.int_to_card(deck.draw().serialize()))
        s.hands[1 - my_id].append(poker.int_to_card(deck.draw().serialize()))

        s.hiddenboardcards = s.boardcards + [poker.int_to_card(deck.draw().serialize()) for _ in range(5 - len(s.boardcards))]

        dprint('Round %d. Hole cards: [%s] [%s]. Board cards: [%s]. Hidden cards: [%s]',
               i, ';'.join(s.hands[0]), ';'.join(s.hands[1]), ';'.join(s.boardcards), ';'.join(s.hiddenboardcards))

        # Replay game up to current state
        # First, add the blinds
        s.pot += poker.getBlind(game, 0)
        s.pot += poker.getBlind(game, 1)
        s.chips_per_player[0] = poker.getBlind(game, 0)
        s.chips_per_player[1] = poker.getBlind(game, 1)

        s.betsize = max(poker.getBlind(game, 0), poker.getBlind(game, 1))

        dprint('Round %d. After blinds, pot=%d, chips[0]=%d, chips[1]=%d, betsize=%d',
               i, s.pot, s.chips_per_player[0], s.chips_per_player[1], s.betsize)

        pos = 0
        for r in range(state.round + 1):
            s.actions.append([])
            pos = 0
            for a in range(poker.getNumActions(state, r)):
                act = poker.getAction(state, r, a)
                s.actions[-1].append(act)
                curplayer = poker.getActingPlayer(state, r, a)
                pot_features = [s.chips_per_player[curplayer], s.pot, (s.betsize - s.chips_per_player[curplayer]), 2, pos]
                card_features = poker.calculate_card_features(2, s.hands[curplayer], s.boardcards)
                dprint('Round %d. Action=(%d,%d). curplayer=%d', i, act.type, act.size, curplayer)
                pos += 1
                s.doaction(curplayer, act.type, act.size)
                logpval += math.log(nets[curplayer].eval(2, card_features, pot_features, [])[0][act.type]) - math.log(0.34)

        s.savestate()

        # Current and future actions
        for j in range(10):
            s.restorestate()

            # Choose an action at random
            probabilities = [a / float(action_denom) for a in action_num]
            action_type = np.random.choice([poker.FOLD, poker.CALL, poker.RAISE], 1, p=probabilities)[0]
            raise_dist = [r / float(raise_denom) for r in raise_num]
            dprint('raise_dist = [%s]', ';'.join(map(str, raise_dist)))
            raise_size = np.random.choice(raise_sizes, 1, p=raise_dist)[0]

            dprint('Round %d, hand %d. Action=(%d, %d), probabilities=[%s]', i, j, action_type, raise_size, ';'.join(map(str, probabilities)))
            # TODO: check move validity

            # evaluate move
            score = 0

            # fold: automatic loss
            if action_type == poker.FOLD:
                score = s.score(my_id, 1 - my_id)
                score = - s.chips_per_player[my_id]
            else:
                at = action_type
                rs = raise_size
                curplayer = my_id
                pos += 1
                s.doaction(curplayer, at, rs)
                curplayer = 1 - curplayer

                ncallsinrow = 0
                nremaining = 2
                if at == poker.CALL:
                    ncallsinrow += 1
                    if len(s.actions) > 0 and len(s.actions[-1]) > 0 and s.actions[-1][-1].type == poker.CALL:
                        ncallsinrow += 1

                # First, finish current round
                curplayer, nremaining = s.run_round_to_finish(curplayer, ncallsinrow, pos)

                if nremaining == 1:
                    score = s.score(my_id, 1 - curplayer)
                else:
                    # Play out the other rounds
                    for r in range(state.round + 1, game.numRounds):
                        s.boardcards = s.hiddenboardcards[0: len(s.boardcards) + poker.getNumBoardCards(game, r)]
                        pos = 0
                        curplayer = poker.getFirstPlayer(game, r)
                        ncallsinrow = 0

                        curplayer, nremaining = s.run_round_to_finish(curplayer, ncallsinrow, pos)
                        if nremaining == 1:
                            score = s.score(my_id, 1 - curplayer)
                    
                    # Showdown
                    if nremaining == 2:
                        scores = [poker.score_hand(s.hands[0], s.boardcards), 
                                  poker.score_hand(s.hands[1], s.boardcards)]
                        dprint('Round %d, hand %d. Showdown! hands[0]=%s, hands1[0]=%s, board=%s, scores=[%d, %d]', i, j, s.hands[0], s.hands[1], s.boardcards, scores[0], scores[1])
                        score = s.score(my_id, my_id if scores[my_id] >= scores[1 - my_id] else 1 - my_id)
            
            # Update probabilities

            inc = abs(score) * math.exp(logpval) * 0.01
            action_denom += inc
            if score < 0:
                dprint('Round %d, hand %d. inc = %s, logpval = %.4f, pot=%s, score=%s, chips=%s', i, j, inc, logpval, s.pot, score, s.chips_per_player[my_id])
                if action_type == poker.RAISE:
                    raise_denom += inc
                    for ind, size in enumerate(raise_sizes):
                        if size != raise_size:
                            raise_num[ind] += inc / float(len(raise_sizes) - 1)
                for ind in range(len(action_num)):
                    if ind != action_type:
                        action_num[ind] += inc / 2.0
            else:
                dprint('Round %d, hand %d. inc = %s, logpval = %.4f, pot=%s, score=%s, chips=%s', i, j, inc, logpval, s.pot, score, s.chips_per_player[my_id])
                action_num[action_type] += inc
                if action_type == poker.RAISE:
                    raise_denom += inc
                    raise_num[raise_sizes.index(raise_size)] += inc

    probabilities = [a / float(action_denom) for a in action_num]
    dprint('Round %d. Hole cards: [%s]. Board cards: [%s]', i, ';'.join(s.hands[my_id]), ';'.join(s.boardcards))
    dprint('Finished. Initial probabilities=[%s]. Final denom=%d, Final probabilities=[%s]', ';'.join(map(str,action_probabilities)), action_denom, ';'.join(map(str, probabilities)))
    dprint('Ended. Took %s seconds.', time.time() - t_start)

    return probabilities, raise_sizes[raise_num.index(max(raise_num))]

            
class NeuralNetNolimitOpAgent(PokerBot):
    import cProfile
    def __init__(self, host, port, gamefile, paramf):
        # Initialize networking stuff

        # Initialize both self and op neural net with initial params
        self.neural_net = PokerNetNoLimit(maxn=2)
        self.neural_net.load_params(paramf)
        self.neural_net_op = PokerNetNoLimit(maxn=2)
        self.neural_net_op.load_params(paramf)
        
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

        action_probabilities[0] *= 20
        s = sum(action_probabilities)
        action_probabilities = action_probabilities / s
        raise_amount = int(action_output[3])
        raisevalid, minsize, maxsize = poker.raiseIsValid(self.game, state)
        
        simulated_agents = {}
        simulated_agents[my_id] = self.neural_net
        simulated_agents[1 - my_id] = self.neural_net_op
        
        action_probabilities, raise_amount = simulate(my_id, self.game, state, simulated_agents, action_probabilities, raise_amount, chips_to_call, minsize)
        
        #print card_features
        #print action_output[:3]
        #print 'Raise amount=', action_output[3] 
        
        action = poker.Action()
        action.type = np.random.choice(self.actions, 1, p=action_probabilities)[0]
        action.size = 0

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
                err = self.neural_net_op.cost_array(op_data)
                print 'Validation error for opponent neural net: %s' % (str(err))
                # Backpropogation: update opponent NN params
                self.neural_net_op.backprop(op_data)
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
