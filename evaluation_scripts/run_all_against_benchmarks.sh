#!/bin/bash
agents=("9851394a-0919-40b1-a9a8-2882322c191d" "ca83b026-5e1b-4b57-afad-9afd240fb0c3" "7cf43402-a38f-43f7-9d6c-1528008ca403" "b7e8d74b-7b35-411c-aedf-4b5bc2802dc1" "defdf3c4-85aa-4ad0-b933-3fcbb8e2b184" "a18efbac-b96f-4437-b9da-355e96b22757" "0125c723-43e1-4a60-9b9a-a120676623ab" "2e162a8c-cfc0-4e3c-8472-d5aecceb53f8" "5741519b-a74f-4555-bae9-633c8027db9d" "21690196-5a01-4727-8d09-060b35287800")

a_i=0
for a in "${agents[@]}"
do
    for b in benchmarks/play_*
    do
        echo benchmark B $b vs agent $a
        game/play_match.pl game game/holdem.nolimit.2p.game 3000 0 $b $b $a neuralnet/play_nolimit_agent.sh
    done
    a_i=$((a_i+1))
done
