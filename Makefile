all:
	cd pokerlib && make all && cd ..
	cd project_acpc_server && make && cd ..
	ln -f project_acpc_server/dealer game/dealer

clean:
	cd pokerlib && make clean && cd ..
	cd project_acpc_server && make clean && cd ..
