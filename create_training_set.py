from pokerlib.poker import Deck, Card, calculate_card_features
import sys
import os
from multiprocessing import Pool

import argparse
import glob
import itertools

hdb = {}
roster = {}
players = {}

def encode(a):
    if a == 'r' or a == 'b':
        return [0, 0, 1]
    if a == 'c' or a == 'k':
        return [0, 1, 0]
    if a == 'f':
        return [1, 0, 0]
    raise Exception('Saw %s' % a)

def print_atomic(line):
    # Prints atomically (single system call) to stdout
    os.write(sys.stdout.fileno(), line + '\n')

def count(l):
    counts = {}
    for i in l:
        if i not in counts:
            counts[i] = 0
        counts[i] += 1

    return counts.values()


def calculate_features(nplayers, hole_cards, table_cards, bets, action):
    card_features = calculate_card_features(nplayers, hole_cards, table_cards)

    return card_features + list(bets[:-1]) + list(bets[-1]) + encode(action)

def calculate_bet_structure(nplayers, pot_at_round_begin, chips_at_round_begin,
                            my_chips_in_pot_at_round_begin, diff, sequence):
    units_per_bet = 0
    nunits = 0
    bet_seq = {}
    last_bet_size = {}
    chips = {}

    bet_structure = {}
    remain = {}
    for p in range(nplayers):
        last_bet_size[p] = 0
        bet_seq[p] = []
        bet_structure[p] = []
        chips[p] = 0
        remain[p] = True

    nremain = nplayers
    for position, (p, a) in enumerate(sequence):
        betsize = units_per_bet - last_bet_size[p]
        tocall = betsize
        if a in {'B', 'r', 'b'}:
            units_per_bet += 1
            betsize = units_per_bet - last_bet_size[p]
            nunits += betsize
            chips[p] -= betsize
        elif a in {'k', 'c'}:
            nunits += betsize
            chips[p] -= betsize
        elif a in {'f', 'Q'}:
            betsize = 0
            nremain -= 1
            remain[p] = False
        else:
            betsize = 0

        bet_seq[p].append((nremain, nunits, betsize, tocall, position,
                           [chips_at_round_begin[p] + chips[i] for i in range(nplayers)],
                           [chips_at_round_begin[p] + chips[i] for i in range(nplayers) if remain[p]]
                          ))
        last_bet_size[p] = units_per_bet

    if nunits > 0:
        unitsize = float(diff)/nunits
    else:
        unitsize = 0

    my_chips_in_pot = {}
    check = {}
    for p in range(nplayers):
        last_bet_size[p] = 0
        my_chips_in_pot[p] = my_chips_in_pot_at_round_begin[p]
        bet_structure[p] = []
        check[p] = (chips_at_round_begin[p] - chips[p]) * unitsize
        for nremain, nunits, betsize, tocall, position, chips_all, chips_remain in bet_seq[p]:
            my_chips_in_pot[p] += unitsize * betsize
            bet_structure[p].append((my_chips_in_pot[p], 
                                     pot_at_round_begin + nunits * unitsize,
                                     tocall * unitsize,
                                     position,
                                     nremain,
                                     # [c * unitsize for c in chips_all],
                                     chips_remain, chips_all))

    return bet_structure

def process_hand(hand_id):
    try:
        last_pot = 0
        last_nplayers = int(hdb[hand_id][2])
        chips_in_pot = {}
        chips = {}
        player_list = roster[hand_id][1]
        for p in player_list:
            chips_in_pot[p] = 0
            chips[p] = int(players[p][hand_id][6])

        for roundi, round in enumerate(hdb[hand_id][3:7]):
            if round == '0/0':
                return
            nplayers = int(round.split('/')[0])
            pot = int(round.split('/')[1])
            diff = pot - last_pot
            last_pot, pot = pot, last_pot
            last_nplayers, nplayers = nplayers, last_nplayers
            chips_in_pot_round = {}
            chips_round = {}
            counter = 0
            name_to_id = {}
            id_to_name = {}
            actions = []
            for player_name in player_list:
                p = players[player_name][hand_id]
                if p[2 + roundi] != '-':
                    name_to_id[player_name] = counter
                    id_to_name[counter] = player_name
                    chips_in_pot_round[counter] = chips_in_pot[player_name]
                    chips_round[counter] = chips[player_name]
                    actions.append((int(p[1]), counter, p[2 + roundi]))
                    counter += 1
            actions.sort()

            sequence = []
            for t in itertools.izip_longest(*[a[2] for a in actions], fillvalue='-'):
                for i, a in enumerate(t):
                    sequence.append((actions[i][1], a))

            bet_structure= calculate_bet_structure(nplayers, pot, chips_round, chips_in_pot_round, diff, sequence)

            for p in range(nplayers):
                chips_in_pot[id_to_name[p]] = bet_structure[p][-1][0]
                chips[id_to_name[p]] = bet_structure[p][-1][-1][p]


            for player_name in player_list:
                p = players[player_name][hand_id]
                if player_name in name_to_id:
                    for bet, a in itertools.izip_longest(bet_structure[name_to_id[player_name]], p[2+roundi], fillvalue='-'):
                        bet = bet[:-1]
                        if a not in {'b', 'c', 'k', 'r', 'f'}:
                            continue
                        if roundi == 0:
                            print_atomic(' '.join(map(str, calculate_features(nplayers, p[-1], [], bet, a))))
                        elif roundi == 1:
                            print_atomic(' '.join(map(str, calculate_features(nplayers, p[-1], hdb[hand_id][-1][:3], bet, a))))
                        elif roundi == 2:
                            print_atomic(' '.join(map(str, calculate_features(nplayers, p[-1], hdb[hand_id][-1][:4], bet, a))))
                        elif roundi == 3:
                            print_atomic(' '.join(map(str, calculate_features(nplayers, p[-1], hdb[hand_id][-1][:5], bet, a))))
    except Exception as e:
        print >>sys.stderr, e


value_to_name = {
    0: '2',
    1: '3',
    2: '4',
    3: '5',
    4: '6',
    5: '7',
    6: '8',
    7: '9',
    8: 'T',
    9: 'J',
    10: 'Q',
    11: 'K',
    12: 'A',
}

suit_to_name = {
    0: 'h',
    1: 's',
    2: 'd',
    3: 'c'
}

def int_to_name(i):
    suit = i.suit
    value = i.value - 2
    return value_to_name[value] + suit_to_name[suit]

def assign_cards():
    global players
    global hdb
    ks = hdb.keys()
    for ts in ks:
        d = Deck()
        bad = False
        for c in hdb[ts][-1]:
            d.seen(Card(c).serialize())
        for p in roster[ts][-1]:
            try:
                for c in players[p][ts][-1]:
                    d.seen(Card(c).serialize())
            except:
                del hdb[ts]
                bad = True
                break

        if bad:
            continue

        while len(hdb[ts][-1]) < 5:
            hdb[ts][-1].append(int_to_name(d.draw()))

        for p in roster[ts][-1]:
            while len(players[p][ts][-1]) < 2:
                players[p][ts][-1].append(int_to_name(d.draw()))


def main():
    global hdb
    global players
    global roster
    parser = argparse.ArgumentParser(description='Creates training data for neural network.')
    parser.add_argument('--threads', dest='threads', type=int, default=1, help='Number of threads')
    parser.add_argument('--output', dest='output', default='data.txt', help='Output data file')
    parser.add_argument('--input', dest='input', help='Input db directory')
    args = parser.parse_args()
    db_folder = args.input

    hdb_file = open(os.path.expanduser(os.path.join(db_folder, 'hdb')))

    hdb = {}
    for line in hdb_file:
        parts = line.strip().split()
        if parts:
            hdb[int(parts[0])] = parts[1:8] + [parts[8:]]

    hdb_file.close()

    roster_file = open(os.path.expanduser(os.path.join(db_folder, 'hroster')))
    roster = {}
    for line in roster_file:
        parts = line.strip().split()
        if parts:
            roster[int(parts[0])] = parts[1:2] + [parts[2:]]

    roster_file.close()

    players = {}
    for fname in glob.glob(os.path.expanduser(os.path.join(db_folder, 'pdb/pdb.*'))):
        f = open(fname)
        player_dict = {}
        name = ''
        for line in f:
            parts = line.strip().split()
            if parts:
                name = parts[0]
                player_dict[int(parts[1])] = parts[2:11] + [parts[11:]]
        f.close()
        players[name] = player_dict

    assign_cards()
    pool = Pool(args.threads)
    pool.map(process_hand, hdb.keys())

if __name__ == '__main__':
    main()
