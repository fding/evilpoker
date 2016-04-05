import hands_swig

from hands_swig import Deck, Card

def eval_hand_potential(nplayers, hole, board, ntrials=20000):
    hole_s = hands_swig.HoleCards()
    board_s = hands_swig.CommunityCards()
    for i, c in enumerate(hole):
        hole_s.set_card(i, hands_swig.Card(c))
    for i, c in enumerate(board):
        board_s.set_card(i, hands_swig.Card(c))

    return hands_swig.eval_hand(nplayers, hole_s, board_s, ntrials)
