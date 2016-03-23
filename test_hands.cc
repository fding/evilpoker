#include "hands.h"

#include <cassert>
#include <cstdio>

void init_hole_cards(HoleCards* hole_cards, const char* card1, const char* card2) {
    hole_cards->cards[0] = Card(card1);
    hole_cards->cards[0].unknown = 0;
    hole_cards->cards[1] = Card(card2);
    hole_cards->cards[0].unknown = 0;
}

void init_community_cards(CommunityCards* community_cards,
        const char* card1, const char* card2, const char* card3,
        const char* card4, const char* card5) {
    community_cards->cards[0] = Card(card1);
    community_cards->cards[0].unknown = 0;
    community_cards->cards[1] = Card(card2);
    community_cards->cards[1].unknown = 0;
    community_cards->cards[2] = Card(card3);
    community_cards->cards[2].unknown = 0;
    community_cards->cards[3] = Card(card4);
    community_cards->cards[3].unknown = 0;
    community_cards->cards[4] = Card(card5);
    community_cards->cards[4].unknown = 0;
}

void test_score() {
    HoleCards hole_cards;
    CommunityCards community_cards;
    score_t score, score1, score2;

    // Test case 1. Nothing
    init_hole_cards(&hole_cards, "KH", "JS");
    init_community_cards(&community_cards, "TC", "6H", "3D", "2D", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= HIGH_CARD_MIN && score < ONE_PAIR_MIN);

    // Test case 2. One pair
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "TC", "6H", "3D", "2D", "AC");
    score1 = score_hand(&hole_cards, &community_cards);
    assert(score1 >= ONE_PAIR_MIN && score1 < TWO_PAIR_MIN);

    init_hole_cards(&hole_cards, "AH", "JS");
    init_community_cards(&community_cards, "TC", "6H", "3D", "2D", "AC");
    score2 = score_hand(&hole_cards, &community_cards);
    assert(score2 >= ONE_PAIR_MIN && score2 < TWO_PAIR_MIN);
    assert(score1 < score2);

    // Test case 3. Two pairs
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "TC", "TH", "3D", "2D", "AC");
    score1 = score_hand(&hole_cards, &community_cards);
    assert(score1 >= TWO_PAIR_MIN && score1 < THREE_OF_KIND_MIN);

    init_hole_cards(&hole_cards, "AH", "JS");
    init_community_cards(&community_cards, "TC", "6H", "3D", "3H", "AC");
    score2 = score_hand(&hole_cards, &community_cards);
    assert(score2 >= TWO_PAIR_MIN && score2 < THREE_OF_KIND_MIN);
    assert(score1 < score2);

    // Test case 4. One 3 of kind
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "KC", "6H", "3D", "2D", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= THREE_OF_KIND_MIN && score < STRAIGHT_MIN);

    // Test case 5. Straight
    init_hole_cards(&hole_cards, "KH", "JS");
    init_community_cards(&community_cards, "QC", "TH", "TD", "2D", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= STRAIGHT_MIN && score < FLUSH_MIN);

    init_hole_cards(&hole_cards, "KH", "JS");
    init_community_cards(&community_cards, "QC", "TH", "JD", "2D", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= STRAIGHT_MIN && score < FLUSH_MIN);

    init_hole_cards(&hole_cards, "KH", "JS");
    init_community_cards(&community_cards, "QC", "TH", "AD", "AS", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= STRAIGHT_MIN && score < FLUSH_MIN);

    init_hole_cards(&hole_cards, "5H", "4S");
    init_community_cards(&community_cards, "3C", "2H", "AD", "AS", "AC");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= STRAIGHT_MIN && score < FLUSH_MIN);

    // Test case 6. Flush
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "TC", "TH", "3H", "2H", "AH");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= FLUSH_MIN && score < FULL_HOUSE_MIN);

    // Test case 7. Full House
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "TC", "TH", "TD", "KD", "AH");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= FULL_HOUSE_MIN && score < FOUR_OF_KIND_MIN);

    // Test case 8. 4 of a kind
    init_hole_cards(&hole_cards, "KH", "KS");
    init_community_cards(&community_cards, "TC", "TH", "TD", "TS", "AH");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= FOUR_OF_KIND_MIN && score < STRAIGHT_FLUSH_MIN);

    // Test case 9. Straight Flush
    init_hole_cards(&hole_cards, "KH", "JH");
    init_community_cards(&community_cards, "QH", "TH", "AS", "AD", "AH");
    score = score_hand(&hole_cards, &community_cards);
    assert(score >= STRAIGHT_FLUSH_MIN);
}

#define NTRIALS 20000
void test_eval() {
    // Using
    // http://www.pokernews.com/poker-tools/poker-odds-calculator.htm
    HoleCards hole_cards;
    CommunityCards community_cards;
    float prob;

    // Pre flop
    community_cards.cards[0].unknown=1;
    community_cards.cards[1].unknown=1;
    community_cards.cards[2].unknown=1;
    community_cards.cards[3].unknown=1;
    community_cards.cards[4].unknown=1;

    init_hole_cards(&hole_cards, "2C", "2D");
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .1754\n", prob);

    init_hole_cards(&hole_cards, "AC", "KD");
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .3137\n", prob);

    init_hole_cards(&hole_cards, "AC", "KC");
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .3451\n", prob);

    init_hole_cards(&hole_cards, "AC", "AS");
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .5563\n", prob);

    // flop
    init_hole_cards(&hole_cards, "AC", "9D");
    init_community_cards(&community_cards,
            "7D", "5D", "2D", "3D", "4D");
    community_cards.cards[3].unknown=1;
    community_cards.cards[4].unknown=1;
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .2133\n", prob);



    init_hole_cards(&hole_cards, "AC", "9D");
    init_community_cards(&community_cards,
            "7D", "5D", "2D", "TD", "4D");
    community_cards.cards[4].unknown=1;
    prob = eval_hand(5, &hole_cards, &community_cards, NTRIALS);
    printf("%.4f; Expected: .4371\n", prob);
}


int main() {
//    test_score();
    test_eval();
}
