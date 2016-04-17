UNAME=$(shell uname -s)
ifeq ($(UNAME), Linux)
INCLUDE=-I/usr/include/python2.7
LIB=-L/usr/lib/python2.7
else
ifeq ($(UNAME), Darwin)
INCLUDE=-I/System/Library/Frameworks/Python.framework/Versions/2.6/include/python2.6/
LIB=-L/System/Library/Frameworks/Python.framework/Versions/2.6/lib/
endif
endif

all: poker_swig.py hands_swig.py

hands.o: hands.cc hands.h
	c++ -O3 -c hands.cc -fPIC

test_hands: test_hands.cc hands.o
	c++ -O3 -c test_hands.cc -fPIC
	c++ -o test_hands hands.o test_hands.o -fPIC

test: test_hands
	./test_hands

hands_swig.py: hands.o hands.i
	swig -python -c++ hands.i
	c++ $(INCLUDE) -c hands_wrap.cxx -fPIC
	c++ $(LIB) -shared hands.o hands_wrap.o -o _hands_swig.so -lpython2.7

game.o: game.c
	cc -O3 -c game.c -fPIC

rng.o: rng.c
	cc -O3 -c rng.c -fPIC

net.o: net.c
	cc -O3 -c net.c -fPIC

poker_swig.py: poker.i game.o rng.o net.o
	swig -python poker.i
	cc $(INCLUDE) -c poker_wrap.c -fPIC
	cc $(LIB) -shared game.o rng.o net.o poker_wrap.o -o _poker_swig.so -lpython2.7

clean:
	rm -f game.o rng.o net.o poker_swig.py poker_wrap.c poker_wrap.o _poker_swig.so
	rm -f hands.o hands_swig.py hands_wrap.cxx hands.o test_hands test_hands.o hands_wrap.o _hands_swig.so
