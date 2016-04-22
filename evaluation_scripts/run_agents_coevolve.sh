#!/bin/bash
coevolve=("797ead4d-bdee-4aa5-9143-3aec9900a976" "c51dafff-3da3-43ff-b56b-195ce2f87e86" "3dd46949-9199-4d59-acc1-d57c4217417b" "d5d256f3-5228-448c-9b28-ec3842562200" "ecef7f69-6a8b-4aaa-9026-799649a514d1" "6921212e-8066-4acb-90ba-95aedff82ef2" "adc371e2-0239-45a1-b109-51bc1cfd4227" "ba450ca7-26be-4b1d-99a0-0914d8992297" "b5dbc384-392a-4c54-9dc9-155794d90103" "98c3044e-54b6-4c29-a86f-118c80c472c1")

benchmarks=("e45556ee-1928-4385-a828-bd3d454378e0" "0093233f-fe90-4002-8af8-4cb3cbd84d9c" "66ec13c6-e5d2-4171-9773-fa28f02cc649" "69a8c022-d2ba-4aa2-b1e6-112b67476121" "5ac588db-e34c-464f-8a58-d70b6eb1bdae" "75662f2c-dc4f-448a-a5b1-887bf498f54f" "3a617f08-e08e-452a-b5d4-94241fdfb723" "764c4e3c-d54b-46e2-8018-13f0f0edab5f" "a588fef6-7582-46a6-99ed-ee8fa19b885e" "4dd97199-47c5-446e-bfef-c57591ec8e8e")

cd ../
for i1 in `seq 0 4`; 
do
    for i2 in `seq 5 9` 
    do
	echo coevolve A $i1 vs coevolve A $i2
	game/play_match.pl game game/holdem.nolimit.2p.game 3000 0 ${coevolve[i1]} neuralnet/play_nolimit_agent.sh ${coevolve[i2]} neuralnet/play_nolimit_agent.sh
    done
done
