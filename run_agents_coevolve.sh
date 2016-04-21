#!/bin/bash
coevolve=("9851394a-0919-40b1-a9a8-2882322c191d" "ca83b026-5e1b-4b57-afad-9afd240fb0c3" "7cf43402-a38f-43f7-9d6c-1528008ca403" "b7e8d74b-7b35-411c-aedf-4b5bc2802dc1" "defdf3c4-85aa-4ad0-b933-3fcbb8e2b184" "a18efbac-b96f-4437-b9da-355e96b22757" "0125c723-43e1-4a60-9b9a-a120676623ab" "2e162a8c-cfc0-4e3c-8472-d5aecceb53f8" "5741519b-a74f-4555-bae9-633c8027db9d" "21690196-5a01-4727-8d09-060b35287800")

benchmarks=("9e727835-7701-4014-a2c0-31c471b81908" "efc7890c-78b2-469b-8eda-1bd049761f4b" "4b16fd47-93fa-4578-93dd-e7eb56998603" "1d09413b-85f0-4ab9-8a98-ce39a180041f" "82fa18f5-8aa3-4985-afe7-c40c2ed8dfaa" "39c74d3b-f5d2-4529-b0f0-d65e652d3e62" "2fcba191-8d9b-4beb-b534-0589ae95fbe0" "cb1fc19f-39d2-400b-98d5-e1d2c8c60a36" "ffc4f092-8afc-437b-aa64-a817ba3a7ded" "f5d18c84-3394-4bf5-8377-3f604c0a3f92")


for i1 in `seq 0 4`; 
do
    for i2 in `seq 5 9` 
    do
	echo coevolve A $i1 vs coevolve A $i2
	game/play_match.pl game game/holdem.nolimit.2p.game 3000 0 ${coevolve[i1]} neuralnet/play_nolimit_agent.sh ${coevolve[i2]} neuralnet/play_nolimit_agent.sh
    done
done
