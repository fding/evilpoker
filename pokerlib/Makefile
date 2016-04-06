UNAME=$(shell uname -s)
ifeq ($(UNAME), Linux)
INCLUDE=-I/usr/local/include/python2.7
LIB=-L/usr/local/lib/python2.7
else
ifeq ($(UNAME), Darwin)
INCLUDE=-I/System/Library/Frameworks/Python.framework/Versions/2.7/include/python2.7/
LIB=-L/System/Library/Frameworks/Python.framework/Versions/2.7/lib/
endif
endif

all: poker.py

game.o: game.c
	cc -O3 -c game.c

rng.o: rng.c
	cc -O3 -c rng.c

net.o: net.c
	cc -O3 -c net.c

poker.py: poker.i game.o rng.o net.o
	swig -python poker.i
	cc $(INCLUDE) -c poker_wrap.c
	cc $(LIB) -shared game.o rng.o net.o poker_wrap.o -o _poker.so -lpython2.7

clean:
	rm -f game.o rng.o net.o poker.py poker_wrap.c poker_wrap.o _poker.so
