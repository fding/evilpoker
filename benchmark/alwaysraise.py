import evilpoker.poker
from evilpoker.pokerbot import PokerBot
import sys

# Always raises by the min amount allowed, otherwise calls.
class AlwaysRaiseAgent(PokerBot):
    def __init__(self, host, port, gamefile, raise_amount):
        # Initialize networking stuff
        super(AlwaysFoldAgent, self).__init__()

        # Do agent specific initialization
		
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state)
        
		# Do I need to check if there are chips left? or does it fold automatically?
        action = Action()
		action.type = poker.CALL
		action.size = 0
		# Modify action in place by reference?
		min = 0
		max = 0
		if poker.raiseIsValid( game, state.state, min, max ) > 0:
			action.type = poker.RAISE
			action.size = min
		assert(poker.isValidAction( game, state.state, 0, action ) > 0)
        return action

# Take user input host and port
try:
    opts, args = getopt.getopt(argv,["dealer_host=","dealer_port=","--game_file"])
except getopt.GetoptError:
    print 'USAGE: ./benchmark_agent --dealer_host=localhost --dealer_port=8080 --game_file=holdem.limit.2p.reverse_blinds.game'
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
		
p = AlwaysRaiseAgent(host, port, gamefile, raise_amount)
p.run()