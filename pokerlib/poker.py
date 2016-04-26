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
    printAction,
    sumBoardCards,
    getPotSize,
    chipsToCall,
    getSpent,
    getNumActions,
    getStack,
    getFolded,
    getRaiseSize,
    getNumActions,
    getAction,
    getActingPlayer,
    getBlind,
    getNumBoardCards,
    getFirstPlayer,
)

import hands_swig

from hands_swig import Deck, Card

FOLD = 0
CALL = 1
RAISE = 2

value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

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

def card_to_int(c):
    suits = "cdhs"
    ranks = "23456789TJQKA"
    return ranks.index(c[0]) * 4 + suits.index(c[1])

def get_board_cards(game, state):
    '''Return all board cards at given state'''
    n = sumBoardCards(game, state.round)
    return [int_to_card(poker_swig.getBoardCard(state, i)) for i in range(0, n)]

def get_hole_cards(game, state, pid):
    '''Return all hole cards'''
    return [int_to_card(poker_swig.getHoleCard(state, pid, i)) for i in range(0, game.numHoleCards)]

def get_current_pos(state):
    '''Get the current position of the player in the round'''
    return poker_swig.getCurrentPos(state)

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

    return [len(table_cards) + len(hole_cards), potential, max_hole_value, other_hole_value, tvsum, highest_pair, highest_triple,
            flush_potential, table_flush_potential]

def count(l):
    counts = {}
    for i in l:
        if i not in counts:
            counts[i] = 0
        counts[i] += 1

    return counts.values()


hands_hash = {}

def eval_hand_potential(nplayers, hole, board, ntrials=8000):
    if (nplayers, tuple(hole), tuple(board)) in hands_hash:
        return hands_hash[(nplayers, tuple(hole), tuple(board))]
    hole_s = hands_swig.HoleCards()
    board_s = hands_swig.CommunityCards()
    for i, c in enumerate(hole):
        card = hands_swig.Card(c)
        card.unknown = 0
        hole_s.set_card(i, card)
    for i, c in enumerate(board):
        card = hands_swig.Card(c)
        card.unknown = 0
        board_s.set_card(i, card)

    hands_hash[(nplayers, tuple(hole), tuple(board))] = hands_swig.eval_hand(nplayers, hole_s, board_s, ntrials)
    return hands_hash[(nplayers, tuple(hole), tuple(board))]

def score_hand(hole, board):
    hole_s = hands_swig.HoleCards()
    board_s = hands_swig.CommunityCards()
    for i, c in enumerate(hole):
        card = hands_swig.Card(c)
        card.unknown = 0
        hole_s.set_card(i, card)
    for i, c in enumerate(board):
        card = hands_swig.Card(c)
        card.unknown = 0
        board_s.set_card(i, card)

    return hands_swig.score_hand(hole_s, board_s)
