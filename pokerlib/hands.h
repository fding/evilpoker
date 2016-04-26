#ifndef HANDS_H
#define HANDS_H
#include <cassert>
#include <cstdlib>

enum Suit {
    HEARTS = 0,
    SPADES = 1,
    DIAMONDS = 2,
    CLUBS = 3,
};

struct Card {
    unsigned char value:5;
    unsigned char suit:2;
    unsigned char unknown:1;

    Card() {
        value = 0;
        suit = 0;
        unknown = 1;
    }

    Card(const char* name) {
        unknown = 1;
        if (name[0] >= '2' && name[0] <= '9') {
            value = name[0] - '0';
        } else if (name[0] == 'T') {
            value = 10;
        } else if (name[0] == 'J') {
            value = 11;
        } else if (name[0] == 'Q') {
            value = 12;
        } else if (name[0] == 'K') {
            value = 13;
        } else if (name[0] == 'A') {
            value = 14;
        }

        switch (name[1]) {
            case 'H':
            case 'h':
                suit = HEARTS;
                break;
            case 'S':
            case 's':
                suit = SPADES;
                break;
            case 'D':
            case 'd':
                suit = DIAMONDS;
                break;
            case 'C':
            case 'c':
                suit = CLUBS;
                break;
        }
    }

    inline bool operator< (const Card& rhs) const {
        if (value < rhs.value) return true;
        if (rhs.value < value) return false;
        if (suit < rhs.suit) return true;
        return false;
    }
    inline bool operator> (const Card& rhs) const {
        if (value < rhs.value) return false;
        if (rhs.value < value) return true;
        if (suit < rhs.suit) return false;
        return false;
    }
    inline bool operator<=(const Card& rhs) const { return !(*this > rhs); }
    inline bool operator>=(const Card& rhs) const { return !(*this < rhs); }

    unsigned char serialize() const {
        return (value - 2) * 4 + suit;
    }
};

class Deck {
    // Simulates a deck of cards for sampling without replacement

    public:
    Deck() {
        for (int i = 0; i < 52; i++)
            cards[i] = i;
        max = 51;
        seenmax = 51;
    }

    void reset() {
        max = seenmax;
    }

    void seen(unsigned char card) {
        // Mark a card as seen
        int i = card;
        if (cards[i] != card) {
            i = max;
            for (i = 0; i < 52; i++) {
                if (cards[i] == card)
                    break;
            }
        }
        unsigned char temp = cards[max];
        cards[max] = cards[i];
        cards[i] = temp;
        max--;
        seenmax--;
    }

    Card draw() {
        char i = rand() % (max + 1);
        char temp = cards[max];
        cards[max] = cards[i];
        cards[i] = temp;
        max--;
        unsigned char card_i = cards[max + 1];
        Card card;
        card.value = card_i / 4 + 2;
        card.suit = card_i % 4;
        card.unknown = 1;
        return card;
    }

    private:
        unsigned char cards[52];
        char max;
        char seenmax;
};

struct HoleCards {
    Card cards[2];
    void set_card(int i, Card c) {
        cards[i] = c;
    }
};

struct CommunityCards {
    Card cards[5];
    void set_card(int i, Card c) {
        cards[i] = c;
    }
};

typedef int score_t;

#define HIGH_CARD_MIN 0
#define ONE_PAIR_MIN (HIGH_CARD_MIN + 15*15*15*15*15)
#define TWO_PAIR_MIN (ONE_PAIR_MIN + 15*15*15*15)
#define THREE_OF_KIND_MIN (TWO_PAIR_MIN + 15*15*15)
#define STRAIGHT_MIN (THREE_OF_KIND_MIN + 15*15*15)
#define FLUSH_MIN (STRAIGHT_MIN + 15)
#define FULL_HOUSE_MIN (FLUSH_MIN + 15*15*15*15*15)
#define FOUR_OF_KIND_MIN (FULL_HOUSE_MIN + 15*15)
#define STRAIGHT_FLUSH_MIN (FOUR_OF_KIND_MIN + 15*15)


int score_hand(HoleCards* hole_cards, CommunityCards* community_cards);

// 20000 gives accuracy within ~0.003 in 6 ms.
float eval_hand(int nplayers, HoleCards* hole_cards, CommunityCards* community_cards, int ntrials=20000);
#endif
