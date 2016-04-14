from create_training_set import calculate_bet_structure, encode, print_atomic
from pokerlib.poker import calculate_card_features
import numpy as np
import sys
import itertools

# Good players to use as training data. Only use pairs of good players.
good_players = {"Tartanian7", "HibiscusBiscuit", "Nyx", "Prelude", "Hyperborean_iro", "Slumbot"}
nplayers = 2
# Assume all players start with the same number of chips.
chip_features = [0.5,0.5]

#[nplayers, card features, my chips in pot (not normalized), number of chips in pot (not normalized), chips to call (not normalized), number of turns before current action within round, 
# nplayers, each player's number of chips (normalized)] 
# target: action
def calculate_features(nplayers, hole_cards, table_cards, bets, action, raise_amount):
    card_features = calculate_card_features(nplayers, hole_cards, table_cards)

    return [nplayers] + card_features + list(bets[:-1]) + list(bets[-1]) + encode(action) + [raise_amount]

# splits a string of cards into a list of cards. 
# example: '5sQc' -> [5s, Qc] 
def split_cards(card_string):
	card_list = []
	i = 0
	while i < len(card_string):
		card_list.append(card_string[i:i+2])
		i += 2
	return card_list
	
# round is a string (e.g. 'r300f')
# Returns tuple: ([encoded action type, raise amount (0 if not raise)], string of rest of the round)
def find_next_action(round):
	assert(len(round) > 0)
	actions = {'r','c','f'}
	cur_action = round[0]
	assert(cur_action in actions)
	round = round[1:]
	raise_amount = ''
	for i in range(len(round)):
		if round[i] in actions:
			round = round[i:]
			break
		else:
			raise_amount += round[i]
	return encode(cur_action).append(int(raise_amount)), round
	
# Writes all features from given datafile to output csvfile given by writer
def write_features(datafile, writer):
	f = open(datafile, 'r')
	for line in f:
		parts = line.split(":")
		if linesplit[0] == "STATE":
			# hands[0] is big blind, hands[1] is small blind
			cards = linesplit[3].split("/")
			hands = cards[0].split("|")
			hands = map(split_cards, hands)
			assert(len(hands[0]) == 2)
			board = cards[1:]
			board = map(split_cards, board)
			assert(len(board) < 4) # should only include flop, turn, river
			
			# start the pot after sb and bb
			chips_in_pot = [100, 50]
			
			# Iterate through turns
			rounds = linesplit[2].split("/")
			assert(len(rounds) < 5)
			for i in range(len(rounds)):
				player_index = 0
				if i == 0:
					# First round means sb goes first (i.e. player 1)
					player_index = 1	

				nturns = 0
				board_cards = list(itertools.chain.from_iterable(board[:i]))
				
				# Iterate through turns in the round
				rest_of_round = rounds[i]
				while len(rest_of_round > 0):
					cur_hand = hands[player_index]
					cur_action, rest_of_round = find_next_action(rest_of_round)
					raise_amount = cur_action[3]
					
					chips_to_call = chips_in_pot[player_index] - chips_in_pot[~player_index]
					hole_cards = hands[player_index]
					card_features = calculate_card_features(nplayers, hole_cards, board_cards)
					pot_features = [chips_in_pot[player_index], sum(chips_in_pot), chips_to_call, nplayers, nturns]
					
					all_features = card_features + pot_features + chip_features
					
					# write features to file
					writer.writerow(all_features + cur_action)
					print 'features:', all_features
					print 'action:', cur_action
					
					player_index = ~player_index
					nturns += 1
					# update pot
					# raise
					if cur_action[:3] == [0,0,1]:
						chips_in_pot[player_index] = raise_amount
					# call
					elif cur_action[:3] == [0,1,0]:
						chips_in_pot[player_index] += chips_to_call
						assert(chips_in_pot[player_index] == chips_in_pot[~player_index])
					# fold
					elif cur_action[:3] == [1,0,0]:
						assert(i + 1 == len(rounds)) # shouldn't be any more rounds after this
					else:
						sys.exit("bad action")
	f.close()
	

parser = argparse.ArgumentParser(description='Creates training data for neural network from previous AAAI data.')    
parser.add_argument('--output', dest='output', default='data.txt', help='Output data file')
parser.add_argument('--input', dest='input', help='Input AAAI folder')
args = parser.parse_args()

db_folder = args.input

csvfile = open(args.output, 'w')
writer = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

# Get data from one pair of players
for player1 in players:
	for player2 in players:
		for datafile in glob.glob(os.path.expanduser(os.path.join(db_folder, '2pn.' + player1 + '.' + player2 + '*' ))):
			print "opening file", datafile
			write_features(datafile, writer)
			
csvfile.close()