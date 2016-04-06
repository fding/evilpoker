class Params(object):
    def __init__(self, aid="", agent_dir="agent_params"):
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
        self.aid = aid 
        self.agent_dir = agent_dir
        self.param_dict = read_params(self.aid, self.agent_dir)
      

    ''' 
    writes this param object's parameters to file
    '''
    def write_params(self):
        with open(os.path.join(agent_dir, self.aid), 'w') as f:
            for name, param in params:
                f.write("%s:%f\n" % name, param)

    '''
    returns a params dict
    '''
    def read_params(self, aid, agent_dir):
        with open(os.path.join(agent_dir, self.aid), 'r') as f:
            feature_params = [line.split(':') for line in f.read().splitlines()]
            params = {}
            for feature, param in feature_params:
                params[feature] = int(param)
            return params

