import random

def create_simulation_constraints(rng_seed=42, map_radius = 40, num_players = 20):
    random.seed(rng_seed)
    return map_radius, num_players