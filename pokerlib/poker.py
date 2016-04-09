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

import hands_swig

from hands_swig import Deck, Card

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


def card_value(c):
    return value_dict[c[0]]

def suit(c):
    return c[1]

def highest_nkind(l):
    lp = sorted(l)
    maxcount = 0
    maxval = 0
    oldc = 0
    count = 0
    for c in lp:
        if c == oldc:
            count += 1
            continue
        else:
            if count == maxcount:
                if oldc > maxval:
                    maxval = oldc
            elif count > maxcount:
                maxval = oldc
                maxcount = count
            
            count = 0
            oldc = c

    return (maxcount, maxval)

def calculate_card_features(nplayers, hole_cards, table_cards):
    potential = eval_hand_potential(nplayers, hole_cards, table_cards)
    hole_values = map(card_value, hole_cards)
    max_hole_value = max(hole_values)
    other_hole_value = min(hole_values)

    table_values = map(card_value, table_cards)
    tvsum = sum(table_values)

    highest_pair = 0
    highest_triple = 0

    nkind, val = highest_nkind(hole_values + table_values)
    if nkind >= 2:
        highest_pair = val
    if nkind >= 3:
        highest_triple = val

    flush_potential = max(count(map(suit, hole_cards + table_cards)))
    table_flush_potential = max(count(map(suit, table_cards) + [0]))

    return [nplayers, len(table_cards) + len(hole_cards), potential, max_hole_value, other_hole_value, tvsum, highest_pair, highest_triple,
            flush_potential, table_flush_potential]

def eval_hand_potential(nplayers, hole, board, ntrials=20000):
    hole_s = hands_swig.HoleCards()
    board_s = hands_swig.CommunityCards()
    for i, c in enumerate(hole):
        hole_s.set_card(i, hands_swig.Card(c))
    for i, c in enumerate(board):
        board_s.set_card(i, hands_swig.Card(c))

    return hands_swig.eval_hand(nplayers, hole_s, board_s, ntrials)
