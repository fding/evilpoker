all:
	cd hand_eval && make all && cd ..
	cd pokerlib && make all && cd ..
	cd project_acpc_server && make && cd ..
	ln -f project_acpc_server/dealer evolution/dealer

clean:
	cd hand_eval && make clean && cd ..
	cd pokerlib && make clean && cd ..
