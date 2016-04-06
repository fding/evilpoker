class Params(object):
    def __init__(self, aid="", params=params, agent_dir="agent_params"):
        self.param_names = [
            "hand_strength"
            "hand_potential"
            "sum_agent_cards"
            "sum_table_cards"
            "highest_pair "
            "highest_triple"
            "flush_potential"
            "table_flush_potential"
            "agent_pot_chips"
            "pot_chips"
            "call_chips "
            "num_opponents"
            "round_pos"
            "chips_per_opponent"
        ]
        self.param_dict = params
        self.aid = aid 

    def write_params(self):
        with open(os.path.join(agent_dir, self.aid), 'w') as f:
            for name, param in params:
                f.write("%s:%f\n" % name, param)

