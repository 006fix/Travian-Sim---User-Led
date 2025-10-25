import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Ensure project root is on sys.path when executed directly.
if __package__ in (None, ""):
    ROOT = Path(__file__).resolve().parents[1]
    if str(ROOT) not in sys.path:
        sys.path.insert(0, str(ROOT))

import random

from master_controller.simulation_constraints import create_simulation_constraints
from Specific_Functions.map_creation import map_creation, modify_base_map
from Specific_Functions.populate_players import (
    populate_players,
    populate_players_with_villages,
)


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
        tile_key = obj.villages[0]
        if tile_key in taken_tiles:
            return False, f"Village {tile_key} assigned to multiple players."
        taken_tiles.append(tile_key)
        tile = world.get(tile_key)
        if tile is None or getattr(tile, "type_square", None) != "village":
            return False, f"Map entry {tile_key} was not converted into a village."
    return True, "populate_players_with_villages attaches one unique village per player."


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


TESTS = [
    ("Map determinism with seeded RNG", test_map_determinism),
    ("Map dimensions respect radius", test_map_dimensions),
    ("Habitable field composition", test_habitable_fields_match_blueprint),
    ("Oasis storage consistency", test_oasis_storage_matches_resources),
    ("populate_players basic behaviour", test_populate_players_basic),
    ("populate_players_with_villages assignment", test_populate_players_with_villages_assigns_tiles),
    ("populate_players_with_villages saturation handling", test_populate_players_with_villages_handles_saturation),
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
