import sys
from pathlib import Path
if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[1]  # repo root
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
#testing line, left in for functionality
#print(sys.path[0])

from master_controller.simulation_constraints import create_simulation_constraints
from Specific_Functions.map_creation import map_creation, modify_base_map
from Specific_Functions.populate_players import populate_players

map_radius, num_players = create_simulation_constraints()
base_map = map_creation(map_radius)
base_map = modify_base_map(base_map)

#now we add a section to populate the map with villagers
player_dict = populate_players(num_players)