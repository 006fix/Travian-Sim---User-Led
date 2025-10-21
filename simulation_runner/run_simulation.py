from master_controller.simulation_constraints import create_simulation_contraints
from Specific_Functions.map_creation import map_creation, modify_base_map

map_radius = create_simulation_contraints()
base_map = map_creation(map_radius)
base_map = modify_base_map(base_map)

