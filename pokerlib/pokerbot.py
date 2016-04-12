#!/usr/bin/env python

'''
PokerBot: an abstract class for poker playing robots. It handles all the networking, so all a specific agent needs to do is
to output the action given a game state.

Example:

import pokerlib
from pokerlib.pokerbot import PokerBot

class AlwaysFoldAgent(PokerBot):
    def __init__(self, host, port, gamefile, agent specific parameters):
        # Initialize networking stuff
        super(AlwaysFoldAgent, self).__init__()

        # Do agent specific initialization
        pass

    def what_should_i_do(self, my_id, state):
        board_cards = pokerlib.get_board_cards(self.game, state)
        hole_cards = pokerlib.get_hole_cards(self.game, state)
        # super complicated algorithm
        
        action = Action()
        action = pokerlib.FOLD
        return action

p = AlwaysFoldAgent('localhost', 8080, 'holdem.nolimit.2p.game', other params)
p.run()
'''


import poker 
import socket
import sys

class PokerBot(object):
    def __init__(self, host, port, gamefile):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.f = self.sock.makefile()
        self.line = ''
        sent = self.sock.send("VERSION:2.0.0\n")
        if sent != 14:
            raise Exception('Bad send')
        self.game = poker._readGame(gamefile)

    def what_should_i_do(self, my_id, state):
        '''Return an action object, given the game and current state'''
        raise NotImplementedError

    def read_state(self):
        for line in self.f:
            if not line:
                return None

            if line[0] == '#' or line[0] == ';':
                continue
            state = poker.MatchState()
            self.line = line
            poker.readMatchState(line, self.game, state)
            return state

    def do_action(self, action):
        new_stuff = '0' * 4096
        r = poker.printAction(self.game, action, 4096, new_stuff)
        self.line = '%s:%s\r\n' % (self.line.strip(), new_stuff[:r].strip())
        print self.line
        self.sock.send(self.line)

    def run(self):
        while True:
            state = self.read_state()
            if not state:
                break
            if state.state.finished:
                # Game over message. ignore????
                continue
            if poker.currentPlayer(self.game, state.state) != state.viewingPlayer:
                continue
            
            action = self.what_should_i_do(state.viewingPlayer, state.state)
            self.do_action(action)

if __name__ == '__main__':
    p = PokerBot(sys.argv[2], int(sys.argv[3]), 'holdem.limit.2p.reverse_blinds.game')
    p.run()
