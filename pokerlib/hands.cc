#include <cassert>
#include <cstdio>
#include "hands.h"
#include <stdint.h>

#include "evalHandTables"


inline static int find_3_of_kind(Card* cards) {
    // Returns position of highest 3 of kind
    if (cards[4].value == cards[5].value && cards[5].value == cards[6].value)
        return 4;
    if (cards[3].value == cards[4].value && cards[4].value == cards[5].value)
        return 3;
    if (cards[2].value == cards[3].value && cards[3].value == cards[4].value)
        return 2;
    if (cards[1].value == cards[2].value && cards[2].value == cards[3].value)
        return 1;
    if (cards[0].value == cards[1].value && cards[1].value == cards[2].value)
        return 0;
    return -1;
}

inline static int find_2_of_kind(Card* cards, int start) {
    // Returns position of highest pair before start
    for (int i = start - 1; i >= 1; i--) {
        if (cards[i].value == cards[i-1].value)
            return i-1;
    }
    return -1;
}

inline static int find_straight(Card* cards) {
    // Finds a straight in 7 sorted cards
    // Returns value of highest card if straight found,
    // -1 otherwise

    int i5;
    for (i5 = 6; i5 >= 3;) {
        int i1, i2, i3, i4;
        for (i4 = i5 - 1; i4 >= 2 && cards[i4].value == cards[i5].value; i4--);
        if (cards[i4].value != cards[i5].value - 1) {
            i5 = i4;
            continue;
        }
        for (i3 = i4 - 1; i3 >= 1 && cards[i3].value == cards[i4].value; i3--);
        if (cards[i3].value != cards[i4].value - 1) {
            i5 = i3;
            continue;
        }
        for (i2 = i3 - 1; i2 >= 0 && cards[i2].value == cards[i3].value; i2--);
        if (i2 < 0 || cards[i2].value != cards[i3].value - 1) {
            i5 = i2;
            continue;
        }
        for (i1 = i2; cards[i1].value == cards[i2].value && i1 >= 0; i1--);
        if (cards[i1].value != cards[i2].value - 1) {
            // Special case of Ace-low straights
            if (cards[i5].value == 5 && cards[6].value == 14)
                return 5;
            i5 = i1;
            continue;
        }

        return cards[i5].value;
    }
    return -1;
}

int score_hand(HoleCards* hole_cards, CommunityCards* community_cards) {
    Cardset c = emptyCardset();
    addCardToCardset(&c, hole_cards->cards[0].suit, hole_cards->cards[0].value-2);
    addCardToCardset(&c, hole_cards->cards[1].suit, hole_cards->cards[1].value-2);
    addCardToCardset(&c, community_cards->cards[0].suit, community_cards->cards[0].value-2);
    addCardToCardset(&c, community_cards->cards[1].suit, community_cards->cards[1].value-2);
    addCardToCardset(&c, community_cards->cards[2].suit, community_cards->cards[2].value-2);
    addCardToCardset(&c, community_cards->cards[3].suit, community_cards->cards[3].value-2);
    addCardToCardset(&c, community_cards->cards[4].suit, community_cards->cards[4].value-2);

    return rankCardset(c);
}

/*
score_t score_hand(HoleCards* hole_cards, CommunityCards* community_cards) {
    // Assign each hand a score so that a higher scoring hand always beats a lower scoring hand

    Card cards[7];

    // Sort cards in ascending value
    if (hole_cards->cards[1] < hole_cards->cards[0]) {
        cards[0] = hole_cards->cards[1];
        cards[1] = hole_cards->cards[0];
    } else {
        cards[0] = hole_cards->cards[0];
        cards[1] = hole_cards->cards[1];
    }

    cards[2] = community_cards->cards[0];
    cards[3] = community_cards->cards[1];
    cards[4] = community_cards->cards[2];
    cards[5] = community_cards->cards[3];
    cards[6] = community_cards->cards[4];

    for (int i = 0; i < 5; i++) {
        int j;
        Card tmp = cards[2 + i];
        for (j = 2 + i; j > 0 && cards[j - 1] > tmp; j--) {
            cards[j] = cards[j - 1];
        }
        cards[j] = tmp;
    }

    int suit_count[4] = {0, 0, 0, 0};

    // Find flushes
    for (int i = 0; i < 7; i++) {
        suit_count[cards[i].suit]++;
    }

    for (int i = 0; i < 4; i++) {
        if (suit_count[i] >= 5) {
            // Flush. Check if it is straight flush
            Card suit_cards[7];
            int k = 0;
            for (int j = 0; j < 7; j++) {
                if (cards[j].suit == i) {
                    suit_cards[k] = cards[j];
                    k++;
                }
            }

            int straight = find_straight(suit_cards);
            if (straight >= 0 && straight <= suit_cards[k-1].value) {
                return STRAIGHT_FLUSH_MIN + straight;
            }
            return FLUSH_MIN + (((suit_cards[k-1].value * 15 + suit_cards[k-2].value) * 15 + suit_cards[k-3].value) * 15 +
                    suit_cards[k-4].value) * 15 + suit_cards[k-5].value;
        }
    }

    // Check if two pairs
    int pair1 = find_2_of_kind(cards, 7);
    int three_of_kind = -1;

    // Micro-optimization
    if (pair1 >= 0) {
        three_of_kind = find_3_of_kind(cards);

        if (three_of_kind >= 0) {
            // Check if 4 of a kind
            if (cards[4].value == cards[5].value && cards[5].value == cards[6].value && cards[3].value == cards[4].value)
                return FOUR_OF_KIND_MIN + 15 * cards[3].value + cards[2].value;
            if (cards[4].value == cards[5].value && cards[2].value == cards[3].value && cards[3].value == cards[4].value)
                return FOUR_OF_KIND_MIN + 15 * cards[2].value + cards[6].value;
            if (cards[1].value == cards[2].value && cards[2].value == cards[3].value && cards[3].value == cards[4].value)
                return FOUR_OF_KIND_MIN + 15 * cards[1].value + cards[6].value;
            if (cards[0].value == cards[1].value && cards[1].value == cards[2].value && cards[2].value == cards[3].value)
                return FOUR_OF_KIND_MIN + 15 * cards[0].value + cards[6].value;
        }
    }

    // Check if full house
    if (three_of_kind >= 0) {
        int two_of_kind = -1;
        int pos = 7;
        pos = find_2_of_kind(cards, pos);
        if (pos >= three_of_kind && pos <= three_of_kind + 2) {
            pos = find_2_of_kind(cards, three_of_kind);
            if (pos >= 0)
                two_of_kind = pos;
        } else if (pos >= 0) {
            two_of_kind = pos;
        }

        if (two_of_kind >= 0) {
            return FULL_HOUSE_MIN + 15 * cards[three_of_kind].value + cards[two_of_kind].value;
        }
    }

    // Check if straight
    int straight = find_straight(cards);
    if (straight >= 0) {
        return STRAIGHT_MIN + straight;
    }

    // Check if three of kind
    if (three_of_kind >= 0) {
        if (three_of_kind < 3)
            return THREE_OF_KIND_MIN + ((15 * cards[three_of_kind].value) + cards[6].value) * 15 + cards[5].value;
        if (three_of_kind == 3)
            return THREE_OF_KIND_MIN + ((15 * cards[three_of_kind].value) + cards[6].value) * 15 + cards[2].value;
        if (three_of_kind == 4)
            return THREE_OF_KIND_MIN + ((15 * cards[three_of_kind].value) + cards[3].value) * 15 + cards[2].value;
    }

    if (pair1 >= 0) {
        int pair2 = find_2_of_kind(cards, pair1);
        if (pair2 >= 0) {
            if (pair1 < 5)
                return TWO_PAIR_MIN + (15 * cards[pair1].value + cards[pair2].value) * 15 + cards[6].value;
            else {
                if (pair2 < 3)
                    return TWO_PAIR_MIN + (15 * cards[pair1].value + cards[pair2].value) * 15 + cards[4].value;
                else
                    return TWO_PAIR_MIN + (15 * cards[pair1].value + cards[pair2].value) * 15 + cards[2].value;
            }
        } else {
            // This is one pair
            switch (pair1) {
                case 3:
                    return ONE_PAIR_MIN + ((15 * cards[pair1].value + cards[6].value) * 15 + cards[5].value) * 15 + cards[2].value;
                case 4:
                    return ONE_PAIR_MIN + ((15 * cards[pair1].value + cards[6].value) * 15 + cards[3].value) * 15 + cards[2].value;
                case 5:
                    return ONE_PAIR_MIN + ((15 * cards[pair1].value + cards[4].value) * 15 + cards[3].value) * 15 + cards[2].value;
                default:
                    return ONE_PAIR_MIN + ((15 * cards[pair1].value + cards[6].value) * 15 + cards[5].value) * 15 + cards[4].value;
            }
        }
    }

    return HIGH_CARD_MIN + (((15 * cards[6].value + cards[5].value) * 15 + cards[4].value) * 15 + cards[3].value) * 15 + cards[2].value;
}
*/

float eval_hand(int nplayers, HoleCards* hole_cards, CommunityCards* community_cards, int ntrials) {
    // Evaluates a hand
    HoleCards otherplayer;
    assert(nplayers < 16);
    int score = 0;

    Deck deck;
    deck.seen(hole_cards->cards[0].serialize());
    deck.seen(hole_cards->cards[1].serialize());

    int start = 0, j;
    for (j = 0; j < 5; j++) {
        if (!community_cards->cards[j].unknown) {
            deck.seen(community_cards->cards[j].serialize());
            start++;
        }
    }

    for (int i = 0; i < ntrials; i++) {
        deck.reset();

        for (int j = start; j < 5; j++) {
            community_cards->cards[j] = deck.draw();
        }

        score_t myscore = score_hand(hole_cards, community_cards);
        int best = 1;

        for (int j = 0; j < nplayers - 1; j++) {
            otherplayer.cards[0] = deck.draw();
            otherplayer.cards[1] = deck.draw();

            score_t otherscore = score_hand(&otherplayer, community_cards);
            if (otherscore >= myscore) {
                best = 0;
                break;
            }
        }
        if (best)
            score += 1;
    }

    return ((float) score)/ntrials;
}

/* Precomputed values of hands
 * Pre flop:
 * 16 * (13 + 13*12)
 * Total: 16 * 169 = 2704 entries for pre-flop lookup table
 *
 * Post river:
 * 16 * (1716 [all different] + 10296 [one pair] + 6435 [one 3 of kind] + 22464 [one 4 of kind, remaining three cards could be same]
 *      + 171366 [highest two pirs, pairs different but could be same as remaining card]) * 2
 * Total: 16 * 212277 * 2 = 6792864 entries
 *
 * 1287 [all different]
 * 2860 [one pair]
 * 858 [one 3 of kind]
 * 156 [one 4 of kind]
 * 1014 [two pairs, pairs different but could be same as remaining card]
 * 16 * 
 *   1. 5 of same suit. 1287 possibilities
 *   2. 4 of same suit. 1287*5 + 2860 possibilities = 9295 possibilities
 *   3. 3 of same suit. 1287 * 10 + 2860 * 
 *
 *
 *
 * (1287 [all different] + 2860 [one pair] + 858 [one 3 of kind] + 156 [one 4 of kind] +
 *      1014 [two pairs, pairs different but could be same as remaining card])  * 4 (<3, 3 of same suit, 4 of same, 5 of same)
 * Total: 16*6175*4 = 395200 entries
 *
 * 16 * (1716 [all different] + 6435 [one pair] + 2860 [one 3 of kind] + 1872 [one 4 of kind, remaining two cards could be the same]
 *       + 13182 [highest two pairs, pairs have to be different but could be same as remaining card]) * 3
 * Total: 16*26065*3 = 1251120 entries
 *
 * 16 * (1716 [all different] + 10296 [one pair] + 6435 [one 3 of kind] + 22464 [one 4 of kind, remaining three cards could be same]
 *      + 171366 [highest two pirs, pairs different but could be same as remaining card]) * 2
 * Total: 16 * 212277 * 2 = 6792864 entries
 *
 * Grand total: 8441888 entries = 34 MB of lookup tables
 */

