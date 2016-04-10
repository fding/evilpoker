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

uint8_t getHoleCard(const State *state, int pnum, int i) {
    return state->holeCards[pnum][i];
}

uint8_t getCurrentPos(const State *state) {
    return state->numActions[state->round];
}

int getPotSize(const State *state, int nplayers) {
    int sz = 0;
    int i = 0;
    for (i = 0; i < nplayers; i++) {
        sz += state->spent[i];
    }
    return sz;
}

int getSpent(const State *state, int pnum) {
    return state->spent[pnum];
}

int getStack(const Game *game, int pnum) {
    return game->stack[pnum];
}

int getFolded(const State *state, int pnum) {
    return state->playerFolded[pnum];
}

int chipsToCall(const State *state, int pnum) {
    return state->maxSpent - state->spent[pnum];
}

int getRaiseSize(const Game *game, int rnd) {
    return game->raiseSize[rnd];
}

int getNumActions(const State *state, int rnd) {
    return state->numActions[rnd];
}


%}
%include "stdint.i"

%include "typemaps.i"
%apply int32_t *OUTPUT { int32_t *minSize, int32_t *maxSize };

%include "game.h"

