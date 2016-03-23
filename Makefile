hands.o: hands.cc
	clang -O3 -c hands.cc

test_hands: test_hands.cc hands.o
	clang -O3 -c test_hands.cc
	clang -o test_hands hands.o test_hands.o

test: test_hands
	./test_hands
