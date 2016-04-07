import poker_swig

from poker_swig import (
    Action,
    Game,
    State,
    MatchState,
    _readGame,
    _printGame,
    raiseIsValid,
    isValidAction,
    doAction,
    currentPlayer,
    numRaises,
    numFolded,
    numCalled,
    numAllIn,
    numActingPlayers,
    readMatchState,
    printAction
)

FOLD = 0
CALL = 1
RAISE = 2


'''
Included functions:

def readGame(fname):
    return Game described in file with name fname

def printGame(fname, Game):
    return Game described in file with name fname

Other functions as in game.h
'''

def int_to_card(i):
    suits = "cdhs"
    ranks = "23456789TJQKA"
    return ranks[i / 4] + suits[i % 4]

def get_board_cards(game, state):
    '''Return all board cards at given state'''
    n = sumBoardCards(game, state.round)
    return [int_to_card(poker_swig.getBoardCard(state, i)) for i in range(0, n)]

def get_hole_cards(game, state):
    '''Return all hole cards'''
    return [int_to_card(poker_swig.getHoleCard(state, i)) for i in range(0, game.numHoleCards)]
