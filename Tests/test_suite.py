import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure project root is on sys.path when executed directly.
if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

import random
import json
from unittest import mock

from master_controller.simulation_constraints import create_simulation_constraints
from master_controller import game_rules
from Specific_Functions.map_creation import map_creation, modify_base_map
from Specific_Functions.populate_players import (
    populate_players,
    populate_players_with_villages,
)
from Classes.village import Village
from Classes.AI_Classes.generic_running_mechanism import base_controller
from Generic_Functions.generic_functions import sec_val
from Base_Data import Fields_Data as f_data
from Base_Data import Building_Data as b_data
from simulation_runner import game_state_progression as progress_state
from simulation_runner import run_logger
from simulation_runner import run_simulation as run_sim


def _summarise_map(world: Dict[str, object]) -> List[Dict[str, object]]:
    """Produce a deterministic summary of the generated map for comparisons."""
    summary: List[Dict[str, object]] = []
    for key in sorted(world.keys()):
        tile = world[key]
        entry = {
            "key": key,
            "class": type(tile).__name__,
            "type_square": getattr(tile, "type_square", None),
        }
        if hasattr(tile, "type_hab"):
            entry["type_hab"] = list(getattr(tile, "type_hab"))
        if hasattr(tile, "resources"):
            entry["resources"] = list(getattr(tile, "resources"))
        summary.append(entry)
    return summary


def _extract_field_counts(field_dict: Dict[str, object]) -> Dict[str, int]:
    """Count fields by resource prefix (e.g., Wood, Clay)."""
    counts = {"Wood": 0, "Clay": 0, "Iron": 0, "Crop": 0}
    for field_name in field_dict:
        prefix = "".join(ch for ch in field_name if ch.isalpha())
        if prefix in counts:
            counts[prefix] += 1
    return counts


def test_map_determinism() -> Tuple[bool, str]:
    """Ensure identical seeds create identical worlds."""
    radius, _ = create_simulation_constraints(rng_seed=123, map_radius=2)
    first_world = modify_base_map(map_creation(radius))
    first_summary = _summarise_map(first_world)

    radius, _ = create_simulation_constraints(rng_seed=123, map_radius=2)
    second_world = modify_base_map(map_creation(radius))
    second_summary = _summarise_map(second_world)

    if first_summary != second_summary:
        return (
            False,
            "Map summaries differ between seeded runs; RNG seeding is not deterministic.",
        )
    return True, "Repeated seeded runs generate identical map summaries."


def test_map_dimensions() -> Tuple[bool, str]:
    """Verify map size matches the configured radius."""
    radius = 3
    radius_out, _ = create_simulation_constraints(rng_seed=999, map_radius=radius)
    world = map_creation(radius_out)
    expected_tiles = (radius * 2 + 1) ** 2
    actual_tiles = len(world)
    if actual_tiles != expected_tiles:
        return (
            False,
            f"Tile count mismatch: expected {expected_tiles}, got {actual_tiles}.",
        )
    return True, "Tile count matches expected grid size."


def test_habitable_fields_match_blueprint() -> Tuple[bool, str]:
    """Check each habitable tile instantiates the expected field composition."""
    radius, _ = create_simulation_constraints(rng_seed=321, map_radius=2)
    world = modify_base_map(map_creation(radius))
    mismatches: List[str] = []
    for key, tile in world.items():
        if getattr(tile, "type_square", None) != "habitable":
            continue
        expected = getattr(tile, "type_hab", [])
        field_dict = getattr(tile, "field_list_dict", {})
        counts = _extract_field_counts(field_dict)
        expected_map = dict(zip(["Wood", "Clay", "Iron", "Crop"], expected))
        for resource, expected_count in expected_map.items():
            if counts[resource] != expected_count:
                mismatches.append(
                    f"{key}:{resource} expected {expected_count}, got {counts[resource]}"
                )
    if mismatches:
        return False, "Field composition mismatches -> " + "; ".join(mismatches)
    return True, "All habitable tiles expose field counts matching their blueprint."


def test_oasis_storage_matches_resources() -> Tuple[bool, str]:
    """Ensure oasis storage values align with advertised resources."""
    radius, _ = create_simulation_constraints(rng_seed=555, map_radius=2)
    world = modify_base_map(map_creation(radius))
    failures: List[str] = []
    for key, tile in world.items():
        if getattr(tile, "type_square", None) != "oasis":
            continue
        resources = set(getattr(tile, "resources", []))
        storage = getattr(tile, "storage", [])
        if len(storage) != 4:
            failures.append(f"{key}: storage slots {len(storage)} != 4")
            continue
        expected_storage = [
            3600 if res in resources else 1800
            for res in ["wood", "clay", "iron", "crop"]
        ]
        if storage != expected_storage:
            failures.append(f"{key}: {storage} != {expected_storage}")
    if failures:
        return False, "Oasis storage inconsistencies -> " + "; ".join(failures)
    return True, "All oasis tiles report storage aligned with their resources."


def test_populate_players_basic() -> Tuple[bool, str]:
    """Ensure populate_players creates the requested number of players with empty villages."""
    players = populate_players(5)
    if len(players) != 5:
        return False, f"Expected 5 players, received {len(players)}"
    if len(set(players.keys())) != len(players):
        return False, "Player dictionary contains duplicate keys"
    for name, obj in players.items():
        if obj.villages != []:
            return False, f"Player {name} should start without villages, found {obj.villages}"
    return True, "populate_players builds unique players with empty village lists."


def _build_world(map_radius: int, seed: int) -> Dict[str, object]:
    radius, _ = create_simulation_constraints(rng_seed=seed, map_radius=map_radius)
    return modify_base_map(map_creation(radius))


def test_populate_players_with_villages_assigns_tiles() -> Tuple[bool, str]:
    """Check players receive exactly one village and the map updates accordingly."""
    world = _build_world(30, seed=200)
    rng_holder = random.Random(500)
    players = populate_players_with_villages(world, 8, rng_holder=rng_holder)

    if len(players) != 8:
        return False, f"Expected 8 players, received {len(players)}"

    taken_tiles: List[str] = []
    for name, obj in players.items():
        if len(obj.villages) != 1:
            return False, f"Player {name} has villages {obj.villages}; expected exactly one."
        village_obj = obj.villages[0]
        if not isinstance(village_obj, Village):
            return False, f"Player {name} did not receive a Village instance."
        location = village_obj.location
        if location in taken_tiles:
            return False, f"Village {location} assigned to multiple players."
        taken_tiles.append(location)
        tile = world.get(location)
        if tile is not village_obj or getattr(tile, "type_square", None) != "village":
            return False, f"Map entry {location} was not converted into the owning Village object."
    return True, "populate_players_with_villages attaches one unique Village object per player."


def test_populate_players_with_villages_handles_saturation() -> Tuple[bool, str]:
    """Verify the helper reports failure when no eligible tiles exist."""
    world = _build_world(20, seed=123)
    rng_holder = random.Random(250)
    try:
        populate_players_with_villages(world, 1, rng_holder=rng_holder)
    except ValueError as exc:
        message = str(exc)
        if "Players unable to receive villages" not in message:
            return False, f"Raised ValueError but message was unexpected: {message}"
        return True, "populate_players_with_villages surfaces saturation as a ValueError."
    return False, "Expected populate_players_with_villages to raise when the map is saturated."


def test_populate_players_with_villages_returns_controllers() -> Tuple[bool, str]:
    """Ensure controller instances are returned after population."""
    world = _build_world(40, seed=210)
    rng_holder = random.Random(77)
    players = populate_players_with_villages(world, 4, rng_holder=rng_holder)
    for name, obj in players.items():
        if not isinstance(obj, base_controller):
            return False, f"Player {name} is not a base_controller instance: {type(obj).__name__}"
    return True, "populate_players_with_villages returns controller instances."


def test_base_controller_countdown_no_action() -> Tuple[bool, str]:
    """Confirm next_action counts down when no work is performed."""
    controller = base_controller("Timer", ("+", "+"), None, None)
    controller.villages = []
    controller.next_action_due_at = 100
    remaining = controller.will_i_act(current_time=10, global_last_active=0)
    if remaining != 90 or controller.next_action_due_at != 100:
        return False, f"Expected countdown to 90, saw {remaining} with due_at {controller.next_action_due_at}"
    return True, "Controller countdown path reduces time remaining by elapsed time."


def test_base_controller_triggers_field_upgrade() -> Tuple[bool, str]:
    """Ensure a controller can trigger a field upgrade via its AI hook."""
    world = _build_world(40, seed=250)
    rng_holder = random.Random(33)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]
    field_id = next(iter(village_obj.fields.keys()))

    field_prefix = field_id[:4]
    current_level = village_obj.fields[field_id].level

    class StubAI:
        def __init__(self, action):
            self.action = action
        def derive_next_action(self):
            return self.action

    stub_action = {
        "type": "field",
        "field_id": field_id,
        "resource": field_prefix,
        "level": current_level,
    }
    controller.ai_controller = StubAI(stub_action)
    controller.next_action_due_at = 10
    initial_stock = village_obj.stored.copy()
    upgrade_cost = f_data.field_dict[field_prefix][current_level][0]
    expected_wait = sec_val(f_data.field_dict[field_prefix][current_level][3])
    pop_before = village_obj.population
    yield_before = village_obj.total_yield
    cp_rate_before = village_obj.culture_points_rate

    wait_time = controller.will_i_act(current_time=10, global_last_active=0)
    if wait_time != expected_wait or controller.next_action_due_at != 10 + expected_wait:
        return False, f"Expected wait {expected_wait}, saw {wait_time} and due_at {controller.next_action_due_at}"
    if len(village_obj.currently_upgrading) != 1:
        return False, f"Upgrade queue unexpected: {village_obj.currently_upgrading}"
    job = next(iter(village_obj.currently_upgrading.values()))
    payload = job.get("payload", {})
    if payload.get("field_id") != field_id:
        return False, f"Queued field mismatch: {payload}"
    if job.get("time_remaining") != expected_wait:
        return False, f"Job timer mismatch: expected {expected_wait}, saw {job.get('time_remaining')}"
    for idx in range(4):
        if village_obj.stored[idx] != initial_stock[idx] - upgrade_cost[idx]:
            return False, "Upgrade cost was not deducted correctly."

    village_obj.field_upgraded(job)
    new_level = current_level + 1
    expected_pop_delta = f_data.field_dict[field_prefix][new_level][2] - f_data.field_dict[field_prefix][current_level][2]
    expected_cp_delta = f_data.field_dict[field_prefix][new_level][1] - f_data.field_dict[field_prefix][current_level][1]
    if village_obj.population != pop_before + expected_pop_delta:
        return False, "Population did not increase as expected."
    if abs(village_obj.culture_points_rate - (cp_rate_before + expected_cp_delta)) > 1e-6:
        return False, "Culture point rate did not update correctly."
    expected_yield_delta = f_data.field_dict[field_prefix][new_level][4] - f_data.field_dict[field_prefix][current_level][4]
    expected_total_yield = yield_before + expected_yield_delta - expected_pop_delta
    if abs(village_obj.total_yield - expected_total_yield) > 1e-6:
        return False, "Total yield did not update to match the new field level."
    if village_obj.currently_upgrading != {}:
        return False, "Upgrade queue was not cleared after completion."
    return True, "Controller triggers field upgrade and schedules next wake correctly."


def test_culture_points_accumulate() -> Tuple[bool, str]:
    """Ensure culture points accumulate based on rate and elapsed time."""
    world = _build_world(40, seed=410)
    rng_holder = random.Random(45)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    class IdleAI:
        def derive_next_action(self):
            return None

    controller.ai_controller = IdleAI()
    controller.next_action_due_at = 100
    village_obj.culture_points_rate = 12.0
    village_obj.culture_points_total = 0.0
    village_obj.stored = [0, 0, 0, 0]

    remaining = controller.will_i_act(current_time=100, global_last_active=0)
    expected_total = village_obj.culture_points_rate * (100 / 3600)
    if abs(village_obj.culture_points_total - expected_total) > 1e-6:
        return False, "Culture points did not accumulate as expected."
    if remaining != controller.next_action_due_at - 100:
        return False, "Controller did not schedule the fallback delay correctly."
    return True, "Culture points accumulate according to rate and elapsed time."


def test_game_state_progression_tick_advances() -> Tuple[bool, str]:
    """Validate game_state_progression advances by the minimum scheduled delay."""
    progress_state.game_counter = 0
    progress_state.turn_counter = 0
    progress_state.time_elapsed = 0
    progress_state.time_will_elapse = 3
    progress_state.global_last_active = 0

    class PassiveTile:
        type_square = "habitable"
        def next_update(self):
            return 5

    class StubController:
        def __init__(self):
            self.calls: List[Tuple[int, int]] = []
            self.next_action = 10
        def will_i_act(self, current_time, global_last_active):
            self.calls.append((current_time, global_last_active))
            return 7

    map_dict = {"p": PassiveTile()}
    stub_player = StubController()
    player_dict = {"player": stub_player}

    progress_state.simulate_time(map_dict, player_dict)

    if progress_state.game_counter != 3:
        return False, f"Game counter expected 3, found {progress_state.game_counter}"
    if progress_state.time_will_elapse != 5:
        return False, f"time_will_elapse expected 5, found {progress_state.time_will_elapse}"
    if progress_state.turn_counter != 1:
        return False, f"turn_counter expected 1, found {progress_state.turn_counter}"
    if stub_player.calls != [(3, 0)]:
        return False, f"Player was not called with expected timestamps: {stub_player.calls}"
    return True, "Game state progression advances using the minimum scheduled delay."


def test_logger_records_village_metrics() -> Tuple[bool, str]:
    """Ensure logger attaches population, culture, and yield metrics to events."""
    run_logger.reset()
    run_logger.log_action(
        player="Tester",
        village_location="(0,0)",
        action_type="idle",
        target=None,
        wait_time=None,
        reason="no upgrades",
        population=10,
        culture_rate=3.5,
        culture_total=12.0,
        total_yield=25.0,
    )
    run_logger.log_completion(
        player="Tester",
        village_location="(0,0)",
        job_type="field",
        target="Wood1",
        population=11,
        culture_rate=4.0,
        culture_total=14.0,
        total_yield=28.0,
        resources=[5, 6, 7, 8],
        storage_cap=[800, 800, 800, 800],
    )
    events = run_logger.get_events()
    if len(events) != 2:
        return False, f"Expected 2 events, found {len(events)}"
    action_event, completion_event = events
    for key in ["population", "culture_rate", "culture_total", "total_yield"]:
        if key not in action_event or key not in completion_event:
            return False, f"Logger missing '{key}' in events."
    for key in ["resources", "storage_cap"]:
        if key not in completion_event:
            return False, f"Completion missing '{key}' snapshot."
    if completion_event["population"] != 11 or abs(completion_event["total_yield"] - 28.0) > 1e-6:
        run_logger.reset()
        return False, "Completion payload did not record the supplied metrics."
    if completion_event["resources"] != [5, 6, 7, 8]:
        run_logger.reset()
        return False, "Resource snapshot mismatch on completion."
    if completion_event["storage_cap"] != [800, 800, 800, 800]:
        run_logger.reset()
        return False, "Storage cap snapshot mismatch on completion."
    run_logger.reset()
    return True, "Logger captures population, culture, and yield metrics on events."


def test_run_logger_generates_scoreboard() -> Tuple[bool, str]:
    """Ensure scoreboard data is written as a separate artefact."""
    run_logger.reset()
    run_logger.start_run({"map_radius": 1, "num_players": 1})
    run_logger.log_action(
        player="Alpha",
        village_location=(0, 0),
        action_type="idle",
        target=None,
        wait_time=None,
        population=5,
        culture_rate=2.0,
        culture_total=1.0,
        total_yield=10.0,
    )
    run_logger.log_completion(
        player="Alpha",
        village_location=(0, 0),
        job_type="field",
        target="Wood1",
        population=6,
        culture_rate=2.5,
        culture_total=2.0,
        total_yield=12.0,
        resources=[1, 2, 3, 4],
        storage_cap=[800, 800, 800, 800],
    )
    run_logger.log_action(
        player="Beta",
        village_location=(1, 1),
        action_type="idle",
        target=None,
        wait_time=None,
        population=4,
        culture_rate=1.5,
        culture_total=0.5,
        total_yield=9.0,
    )
    payload = run_logger.finalise_run({"ticks": 1, "final_game_time": 10})
    scoreboard_path = Path(payload["metadata"]["scoreboard_path"])
    if not scoreboard_path.exists():
        return False, "Scoreboard file was not created."
    scoreboard_data = json.loads(scoreboard_path.read_text(encoding="utf-8"))
    players = {entry["player"]: entry for entry in scoreboard_data.get("players", [])}
    alpha_entry = players.get("Alpha")
    beta_entry = players.get("Beta")
    scoreboard_path.unlink(missing_ok=True)
    if alpha_entry is None or beta_entry is None:
        return False, "Scoreboard is missing expected player entries."
    if alpha_entry["actions"] != 1 or alpha_entry["completions"] != 1:
        return False, "Scoreboard counters do not match Alpha activity."
    if alpha_entry["population"] != 6 or alpha_entry["total_yield"] != 12.0:
        return False, "Scoreboard did not capture Alpha's final stats."
    if beta_entry["actions"] != 1 or beta_entry["population"] != 4:
        return False, "Scoreboard did not capture Beta's action."
    if alpha_entry.get("settle_points", 0) != 0 or beta_entry.get("settle_points", 0) != 0:
        return False, "Scoreboard should expose settle_points with zero default for players without settlements."
    return True, "Scoreboard file summarises per-player metrics."


def test_settler_training_increments_counter() -> Tuple[bool, str]:
    """Settler training should consume resources and increment the owner's settler count."""
    run_logger.reset()
    world = _build_world(40, seed=801)
    rng_holder = random.Random(31)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]
    village_obj.owner = controller
    village_obj.buildings[3] = ["residence", 10, True]
    village_obj.available_buildings.discard("residence")
    village_obj.stored = game_rules.SETTLER_COST.copy()
    for field in village_obj.fields.values():
        field.field_yield = 0
    controller.settlers_built = 0
    controller.Last_Active = 0

    duration = village_obj.start_train_settler()
    if duration is None or duration <= 0:
        return False, "Failed to queue settler training job."
    if len(village_obj.currently_upgrading) != 1:
        return False, "Settler training job not enqueued correctly."

    controller.will_i_act(current_time=duration, global_last_active=0)

    if controller.settlers_built != 1:
        return False, "Settler completion did not increment settlers_built."
    if village_obj.currently_upgrading:
        return False, "Settler job still present after completion."
    if any(value != 0 for value in village_obj.stored):
        return False, "Settler training did not consume the provided resources."
    return True, "Settler training consumes resources and increments settlers_built."


def test_settle_job_consumes_settlers_and_awards_points() -> Tuple[bool, str]:
    """Settling should spend three settlers and award settlement points to the owner."""
    run_logger.reset()
    world = _build_world(40, seed=802)
    rng_holder = random.Random(17)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]
    village_obj.owner = controller
    village_obj.buildings[3] = ["residence", 10, True]
    village_obj.available_buildings.discard("residence")
    for field in village_obj.fields.values():
        field.field_yield = 0
    controller.settlers_built = 3
    controller.settle_points = 0
    controller.culture_points = game_rules.CP_THRESHOLD
    controller.Last_Active = 0
    village_obj.stored = game_rules.SETTLE_COST.copy()

    duration = village_obj.start_settle()
    if duration is None or duration <= 0:
        return False, "Failed to queue settle job."
    if len(village_obj.currently_upgrading) != 1:
        return False, "Settle job not enqueued correctly."

    controller.will_i_act(current_time=duration, global_last_active=0)

    if controller.settlers_built != 0:
        return False, "Settlers were not deducted upon settlement completion."
    if controller.settle_points != 1:
        return False, "Settlement completion did not award a settlement point."
    if village_obj.currently_upgrading:
        return False, "Settle job remained in the queue after completion."
    if any(value != 0 for value in village_obj.stored):
        return False, "Settlement job did not consume the provided resources."
    return True, "Settlement completion spends settlers and awards settlement points."


def test_simulation_stops_when_settlement_goal_met() -> Tuple[bool, str]:
    """The simulation runner should terminate once the settlement goal is met."""
    run_logger.reset()
    call_count = {"value": 0}

    def fake_simulate(map_dict, player_dict):
        call_count["value"] += 1
        progress_state.turn_counter += 1
        progress_state.game_counter += 60
        progress_state.time_elapsed = 60
        progress_state.time_will_elapse = 0
        progress_state.global_last_active = progress_state.game_counter
        players_list = list(player_dict.values())
        if not players_list:
            return
        goal = game_rules.target_settles(len(players_list))
        players_list[0].settle_points = goal
        for other in players_list[1:]:
            other.settle_points = 0

    with mock.patch("simulation_runner.run_simulation.progress_state.simulate_time", side_effect=fake_simulate):
        log_output = run_sim._execute_simulation(
            num_ticks=10,
            num_players=1,
            base_random_seed=0,
            map_radius=80,
            label="test",
        )

    if call_count["value"] != 1:
        return False, f"Simulation did not stop after reaching the settlement goal (iterations={call_count['value']})."

    summary_event = next((event for event in log_output["events"] if event.get("event") == "run_summary"), None)
    if summary_event is None:
        return False, "Run summary event missing from log output."
    if not summary_event.get("settle_threshold_met"):
        return False, "Settlement threshold was not flagged as met."
    if summary_event.get("settle_goal_reached_time") is None:
        return False, "No timestamp recorded for when the settlement goal was reached."

    settle_points_map = summary_event.get("settle_points", {})
    if not settle_points_map:
        return False, "Settlement points summary missing from run summary."

    settle_goal = summary_event.get("settle_goal")
    winner_list = summary_event.get("settle_winners", [])
    if len(winner_list) != 1:
        return False, f"Expected a single settlement winner, found {winner_list}."
    winner = winner_list[0]
    if settle_points_map.get(winner, 0) < max(1, settle_goal or 0):
        return False, "Winner did not record settlement points equal to the goal."

    scoreboard_players = log_output.get("scoreboard", {}).get("players", [])
    if scoreboard_players:
        top_entry = scoreboard_players[0]
        if top_entry.get("player") != winner:
            return False, "Scoreboard leader does not match the settlement winner."
        if top_entry.get("settle_points", 0) < max(1, settle_goal or 0):
            return False, "Scoreboard did not persist settlement points for the winner."

    return True, "Simulation terminates once the settlement goal is met and records the winner."


def test_crop_yield_uses_population_consumption() -> Tuple[bool, str]:
    """Confirm crop output subtracts population usage once."""
    world = _build_world(40, seed=512)
    rng_holder = random.Random(77)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    crop_per_hour = sum(
        field.field_yield for field_name, field in village_obj.fields.items() if "Crop" in field_name
    )
    expected_crop_per_second = (crop_per_hour - village_obj.population) / 3600
    wood, clay, iron, crop = village_obj.yield_calc()
    if abs(crop - expected_crop_per_second) > 1e-6:
        return False, f"Expected crop/sec {expected_crop_per_second}, got {crop}"
    if any(val < 0 for val in (wood, clay, iron)):
        return False, "Non-crop resource yields should not be negative."
    return True, "Crop yield subtracts population usage exactly once."


def test_crop_storage_clamped_at_zero() -> Tuple[bool, str]:
    """Ensure storage never dips below zero even if crop income is negative."""
    world = _build_world(40, seed=612)
    rng_holder = random.Random(19)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    class IdleAI:
        def derive_next_action(self):
            return None

    controller.ai_controller = IdleAI()
    controller.next_action_due_at = 100
    controller.Last_Active = 0
    village_obj.stored = [0, 0, 0, 0]
    for field_name, field in village_obj.fields.items():
        if "Crop" in field_name:
            field.field_yield = 0
    # ensure population still positive so crop becomes negative
    if village_obj.population == 0:
        village_obj.population = 2

    controller.will_i_act(current_time=100, global_last_active=0)
    if village_obj.stored[3] < 0:
        return False, f"Crop storage dropped below zero: {village_obj.stored[3]}"
    return True, "Negative crop flow is clamped at zero storage."


def test_main_building_speed_modifier_applies() -> Tuple[bool, str]:
    """Verify upgrade durations scale with the main building speed modifier."""
    world = _build_world(40, seed=712)
    rng_holder = random.Random(91)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    field_id = next(iter(village_obj.fields.keys()))
    prefix = field_id[:4]
    current_level = village_obj.fields[field_id].level
    base_seconds = sec_val(f_data.field_dict[prefix][current_level][3])

    # bump the main building level to 4 to get a clear multiplier (0.9)
    village_obj.buildings[0][1] = 4
    village_obj.buildings[0][2] = True

    expected_modifier = b_data.building_dict['main_building'][4][4]
    wait_time = village_obj.upgrade_field(field_id)
    expected_time = max(1, int(round(base_seconds * expected_modifier)))
    if wait_time != expected_time:
        return False, f"Expected wait {expected_time}, got {wait_time}"
    return True, "Upgrade durations respect the main building speed modifier."


def test_building_upgrade_handles_max_level() -> Tuple[bool, str]:
    """Ensure building upgrades handle terminal levels without crashing."""
    world = _build_world(40, seed=913)
    rng_holder = random.Random(12)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    job_spec = [0, "main_building"]
    village_obj.buildings[0][1] = 19
    village_obj.buildings[0][2] = True
    village_obj.stored = [1_000_000, 1_000_000, 1_000_000, 1_000_000]

    wait_time = village_obj.upgrade_building(job_spec)
    if wait_time <= 0:
        return False, "Expected positive wait time for main building upgrade."

    if len(village_obj.currently_upgrading) != 1:
        return False, "Building upgrade did not enter the queue."
    job = next(iter(village_obj.currently_upgrading.values()))
    payload = job.get("payload", {})
    if payload.get("slot") != 0 or payload.get("building") != "main_building":
        return False, f"Unexpected job payload recorded: {payload}"

    village_obj.building_upgraded(job)

    if village_obj.buildings[0][1] != 20:
        return False, "Main building level did not increment to the terminal level."
    if village_obj.buildings[0][2] is not False:
        return False, "Main building should no longer be upgradeable at max level."
    available = village_obj.possible_buildings()["buildings"]
    if any(item["name"] == "main_building" for item in available):
        return False, "Main building remained in the upgrade list after reaching max level."
    return True, "Terminal building upgrades complete cleanly and mark the job finished."


def test_storage_building_updates_capacity() -> Tuple[bool, str]:
    """Warehouse/granary upgrades should refresh the village storage caps."""
    world = _build_world(40, seed=110)
    rng_holder = random.Random(5)
    players = populate_players_with_villages(world, 1, rng_holder=rng_holder)
    controller = next(iter(players.values()))
    village_obj = controller.villages[0]

    village_obj.stored = [1_000_000, 1_000_000, 1_000_000, 1_000_000]
    initial_cap = village_obj.storage_cap.copy()

    wait_time = village_obj.upgrade_building([1, "warehouse"])
    if wait_time <= 0:
        return False, "Expected warehouse upgrade to require positive time."
    job = next(iter(village_obj.currently_upgrading.values()))
    village_obj.building_upgraded(job)

    if village_obj.storage_cap[0] <= initial_cap[0]:
        return False, "Warehouse upgrade did not increase storage capacity."

    wait_time = village_obj.upgrade_building([2, "granary"])
    job = next(iter(village_obj.currently_upgrading.values()))
    village_obj.building_upgraded(job)
    if village_obj.storage_cap[3] <= initial_cap[3]:
        return False, "Granary upgrade did not increase crop storage capacity."

    return True, "Storage buildings refresh capacity after upgrades."


TESTS = [
    ("Map determinism with seeded RNG", test_map_determinism),
    ("Map dimensions respect radius", test_map_dimensions),
    ("Habitable field composition", test_habitable_fields_match_blueprint),
    ("Oasis storage consistency", test_oasis_storage_matches_resources),
    ("populate_players basic behaviour", test_populate_players_basic),
    ("populate_players_with_villages assignment", test_populate_players_with_villages_assigns_tiles),
    ("populate_players_with_villages saturation handling", test_populate_players_with_villages_handles_saturation),
    ("populate_players_with_villages returns controllers", test_populate_players_with_villages_returns_controllers),
    ("base_controller countdown without action", test_base_controller_countdown_no_action),
    ("base_controller triggers field upgrade", test_base_controller_triggers_field_upgrade),
    ("culture points accumulate", test_culture_points_accumulate),
    ("game_state_progression tick advances", test_game_state_progression_tick_advances),
    ("run_logger captures village metrics", test_logger_records_village_metrics),
    ("run_logger generates scoreboard", test_run_logger_generates_scoreboard),
    ("Settler training increments counter", test_settler_training_increments_counter),
    ("Settlement completion awards points", test_settle_job_consumes_settlers_and_awards_points),
    ("Simulation stops when settlement goal met", test_simulation_stops_when_settlement_goal_met),
    ("crop yield subtracts population usage", test_crop_yield_uses_population_consumption),
    ("crop storage never negative", test_crop_storage_clamped_at_zero),
    ("main building speed modifier applies", test_main_building_speed_modifier_applies),
    ("building upgrade handles max level", test_building_upgrade_handles_max_level),
    ("storage building updates capacity", test_storage_building_updates_capacity),
]


def run_all_tests() -> bool:
    """Execute all tests and print human-readable feedback."""
    outcomes: List[bool] = []
    for name, test in TESTS:
        try:
            success, message = test()
        except Exception as exc:  # pylint: disable=broad-except
            success = False
            message = f"Raised unexpected exception: {exc!r}"
        label = "PASS" if success else "FAIL"
        print(f"[{label}] {name} - {message}")
        outcomes.append(success)
    passed = sum(outcomes)
    total = len(TESTS)
    print(f"\nSummary: {passed}/{total} tests passed.")
    return all(outcomes)


if __name__ == "__main__":
    run_all_tests()

