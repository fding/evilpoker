# Evopoker: Evolutionary Opponent-Modeling Poker Playing Agent

David Ding, Lily Tsai, Serena Wang

##Evaluation
- Agents vs. Benchmarks:
    - Top agent-trained agents A0-A4
    - Benchmark-trained agents B0-B4
    - Initial agents in the agent-training population A5-A9
    - Initial agents in the benchmark-training population against B5-B9
```
./evaluation_scripts/run_all_against_benchmarks.sh
```

- Top Agents in Agent-Trained Population vs. Top Agents in Benchmark-Trained Population:
```
./evaluation_scripts/agent_vs_benchmark_training_full_population.sh
```

- Top Agent-Trained (Coevolved) Agents vs. Top Benchmark-Trained Agents:
```
./evaluation_scripts/coevolution_vs_evolution.sh
```

- Top Initial Agents in Agent-Training Population vs. Top Agent-Trained Agents:
```
./evaluation_scripts/initial_agent_trained_vs_trained.sh
```

- Top Initial Agents in Benchmark-Training Population vs. Top Benchmark-Trained Agents:
```
./evaluation_scripts/initial_agent_trained_vs_trained.sh
```

##Evolution
```
Usage: python evolution/evolution_agent.py 
                          [-h] [--bmfile BMFILE]
                          [--nn_agent_file NN_AGENT_FILE]
                          [--agent_param_dir AGENT_DIR] [--gamefile GAMEFILE]
                          [--ntopagents NTOPAGENTS] [--epochs EPOCHS]
                          [--nagents NAGENTS]
                          [--nagents_to_mutate NAGENTS_TO_MUTATE]
                          [--nagents_to_keep NAGENTS_TO_KEEP] [--coevolve]
                          [--nthreads NTHREADS] [--nhands NHANDS]
```
