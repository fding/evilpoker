all:
	cd hand_eval && make all && cd ..
	cd pokerlib && make all && cd ..

clean:
	cd hand_eval && make clean && cd ..
	cd pokerlib && make clean && cd ..
