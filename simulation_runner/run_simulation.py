import sys
from pathlib import Path
from typing import Optional
if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[1]  # repo root
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))
#testing line, left in for functionality
#print(sys.path[0])

from master_controller.simulation_constraints import create_simulation_constraints
from master_controller import game_rules
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


def _execute_simulation(num_ticks, num_players, base_random_seed, map_radius, label, log_settlement_events=False):
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
    previous_settle_points = {player.name: player.settle_points for player in player_dict.values()}
    run_context = {
        "global_settles_completed": 0,
        "settle_goal": game_rules.target_settles(players),
    }

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
            "settle_goal": run_context["settle_goal"],
            "settler_cost": game_rules.SETTLER_COST,
            "settler_time": game_rules.SETTLER_TIME,
            "settle_cost": game_rules.SETTLE_COST,
            "settle_time": game_rules.SETTLE_TIME,
            "cp_settlement_threshold": game_rules.CP_THRESHOLD,
        }
    )

    goal_reached_at: Optional[int] = None
    for _ in range(num_ticks):
        progress_state.simulate_time(base_map, player_dict)
        total_settlements = sum(player.settle_points for player in player_dict.values())
        run_context["global_settles_completed"] = total_settlements
        if log_settlement_events:
            for player in player_dict.values():
                current_points = player.settle_points
                prev_points = previous_settle_points.get(player.name, 0)
                if current_points > prev_points:
                    print(
                        f"[{label}] t={progress_state.game_counter}s tick={progress_state.turn_counter} "
                        f"{player.name} completed settlement #{current_points}"
                    )
                previous_settle_points[player.name] = current_points
        if total_settlements >= run_context["settle_goal"]:
            goal_reached_at = progress_state.game_counter
            break

    final_ticks = progress_state.turn_counter
    final_time = progress_state.game_counter
    periodic_monitor.final_capture(final_time, player_dict)
    log_output = run_logger.finalise_run(
        {
            "ticks": final_ticks,
            "final_game_time": final_time,
            "run_variant": label,
            "settle_points": {player.name: player.settle_points for player in player_dict.values()},
            "global_settles_completed": run_context["global_settles_completed"],
            "settle_goal": run_context["settle_goal"],
            "settle_goal_reached_time": goal_reached_at,
            "settle_threshold_met": goal_reached_at is not None,
        }
    )
    run_id = log_output.get("metadata", {}).get("run_id", "unknown")
    try:
        periodic_monitor.export_results(run_id, label)
    except RuntimeError as exc:
        print(f"[{label}] Monitoring export skipped: {exc}")
    if goal_reached_at is not None:
        print(
            f"[{label}] Settlement goal reached at t={goal_reached_at}s; "
            f"completed after {final_ticks} ticks with {len(log_output['events'])} events."
        )
    else:
        print(
            f"[{label}] Completed with {len(log_output['events'])} events "
            f"across {final_ticks} ticks."
        )
    return log_output


def run_simulation(num_ticks, num_players, base_random_seed, map_radius, log_settlement_events=False):
    """Run the requested configuration, then a fixed comparison pass."""
    primary_log = _execute_simulation(
        num_ticks=num_ticks,
        num_players=num_players,
        base_random_seed=base_random_seed,
        map_radius=map_radius,
        label="primary",
        log_settlement_events=log_settlement_events,
    )
    comparison_log = _execute_simulation(
        num_ticks=2000,
        num_players=3,
        base_random_seed=0,
        map_radius=map_radius,
        label="comparison",
        log_settlement_events=log_settlement_events,
    )
    return primary_log, comparison_log


if __name__ == "__main__":
    run_simulation(
        num_ticks=40000,
        num_players=80,
        base_random_seed=42,
        map_radius=50,
        log_settlement_events=True,
    )
