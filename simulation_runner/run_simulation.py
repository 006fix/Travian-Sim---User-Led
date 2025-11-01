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
from simulation_runner import periodic_monitor


def _reset_progress_state():
    """Zero the global counters so consecutive runs start clean."""
    progress_state.game_counter = 0
    progress_state.turn_counter = 0
    progress_state.time_elapsed = 0
    progress_state.time_will_elapse = 0
    progress_state.global_last_active = 0


def _execute_simulation(num_ticks, num_players, base_random_seed, map_radius, label):
    """Run a single simulation instance with the provided configuration."""
    # Derive constraints (seed may override map/player defaults downstream).
    radius, players = create_simulation_constraints(
        rng_seed=base_random_seed,
        map_radius=map_radius,
        num_players=num_players,
    )

    base_map = map_creation(radius)
    base_map = modify_base_map(base_map)
    player_dict = populate_players_with_villages(base_map, players)

    _reset_progress_state()
    periodic_monitor.reset(
        interval=900,
        variant=label,
        metadata={
            "rng_seed": base_random_seed,
            "map_radius": radius,
            "num_players": players,
        },
    )
    periodic_monitor.capture_initial(progress_state.game_counter, player_dict)
    run_logger.start_run(
        {
            "map_radius": radius,
            "num_players": players,
            "rng_seed": base_random_seed,
            "planned_ticks": num_ticks,
            "run_variant": label,
        }
    )

    for _ in range(num_ticks):
        progress_state.simulate_time(base_map, player_dict)

    final_ticks = progress_state.turn_counter
    final_time = progress_state.game_counter
    periodic_monitor.final_capture(final_time, player_dict)
    log_output = run_logger.finalise_run(
        {
            "ticks": final_ticks,
            "final_game_time": final_time,
            "run_variant": label,
        }
    )
    run_id = log_output.get("metadata", {}).get("run_id", "unknown")
    try:
        periodic_monitor.export_results(run_id, label)
    except RuntimeError as exc:
        print(f"[{label}] Monitoring export skipped: {exc}")
    print(
        f"[{label}] Completed with {len(log_output['events'])} events "
        f"across {final_ticks} ticks."
    )
    return log_output


def run_simulation(num_ticks, num_players, base_random_seed, map_radius):
    """Run the requested configuration, then a fixed comparison pass."""
    primary_log = _execute_simulation(
        num_ticks=num_ticks,
        num_players=num_players,
        base_random_seed=base_random_seed,
        map_radius=map_radius,
        label="primary",
    )
    comparison_log = _execute_simulation(
        num_ticks=2000,
        num_players=3,
        base_random_seed=0,
        map_radius=map_radius,
        label="comparison",
    )
    return primary_log, comparison_log


if __name__ == "__main__":
    run_simulation(
        num_ticks=2000,
        num_players=40,
        base_random_seed=42,
        map_radius=50,
    )
