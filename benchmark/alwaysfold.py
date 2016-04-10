import evilpoker.poker
from evilpoker.pokerbot import PokerBot
import sys

# Always folds when valid, otherwise calls.
class AlwaysFoldAgent(PokerBot):
    def __init__(self, host, port, gamefile):
        # Initialize networking stuff
        super(AlwaysFoldAgent, self).__init__()

        # Do agent specific initialization
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = poker.get_board_cards(self.game, state)
        hole_cards = poker.get_hole_cards(self.game, state)
        # super complicated algorithm
        
        action = Action()
        action.type = poker.FOLD
        action.size = 0
        if (not poker.isValidAction( game, state.state, 0, action ) > 0):
            action.type = poker.CALL
        return action

# Take user input host and port
try:
    opts, args = getopt.getopt(argv,["dealer_host=","dealer_port=","--game_file"])
except getopt.GetoptError:
    print 'USAGE: ./benchmark_agent --dealer_host=localhost --dealer_port=8080 --game_file=evolution/holdem.nolimit.2p.game'
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
		
p = AlwaysFoldAgent(host, port, gamefile)
p.run()
