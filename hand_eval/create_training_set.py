from hands import eval_hand_potential, Deck, Card
import sys
import os
from multiprocessing import Pool

import argparse
import glob

hdb = {}
roster = {}
players = {}
value_dict = {'2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14}

def card_value(c):
    return value_dict[c[0]]

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

def suit(c):
    return c[1]

def count(l):
    counts = {}
    for i in l:
        if i not in counts:
            counts[i] = 0
        counts[i] += 1

    return counts.values()


def calculate_features(nplayers, hole_cards, table_cards):
    potential = eval_hand_potential(nplayers), hole_cards, table_cards)
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
    table_flush_potential = max(count(map(suit, table_cards)))

    return [potential, max_hole_value, other_hole_value, tvsum, highest_pair, highest_triple,
            flush_potential, table_flush_potential]


def process_hand(hand_id):
    player_list = roster[hand_id][1]
    for player_name in player_list:
        p = players[player_name][hand_id]
        if p[-1]:
            print calculate_features(hdb[hand_id], p)

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
