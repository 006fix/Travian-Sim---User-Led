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
from Specific_Functions.populate_players import populate_players_with_villages
from simulation_runner import game_state_progression as progress_state
from simulation_runner import run_logger

map_radius, num_players = create_simulation_constraints()
base_map = map_creation(map_radius)
base_map = modify_base_map(base_map)

#now we add a section to populate the map with villagers
player_dict = populate_players_with_villages(base_map, num_players)

run_logger.start_run(
    {
        "map_radius": map_radius,
        "num_players": num_players,
    }
)

#now trigger the loop
for i in range(30):
    progress_state.simulate_time(base_map, player_dict) 

log_output = run_logger.finalise_run(
    {
        "ticks": progress_state.turn_counter,
        "final_game_time": progress_state.game_counter,
    }
)

#placeholder: dump summary length for now
print(f"Run completed with {len(log_output['events'])} logged events.")
