%module poker_swig
%include "cpointer.i"

%pointer_functions(uint8_t, uint8);

%{
#include <stdint.h>
#include "game.h"
%}

%inline %{
Game *_readGame(const char * fname) {
    FILE *f = fopen(fname, "r");
    Game * ret = readGame(f);
    fclose(f);
    return ret;
}

void _printGame(const char * fname, const Game *game) {
    FILE *f = fopen(fname, "w");
    printGame(f, game);
    fclose(f);
}

uint8_t getBoardCard(const State *state, int i) {
    return state->boardCards[i];
}

uint8_t getHoleCard(const State *state, int i) {
    return state->holeCards[i];
}
%}

%include "stdint.i"
%include "game.h"
