import Classes.village as village
import random


def _parse_location(location):
    # accepts either string like "[0, '/', 25]" or list [0, '/', 25]
    if isinstance(location, list):
        hold_list = []
        for item in location:
            if isinstance(item, int):
                hold_list.append(item)
        if len(hold_list) == 2:
            return hold_list
    if isinstance(location, str):
        cleaned = location.replace("[", "").replace("]", "").replace(" ", "")
        cleaned = cleaned.replace("'", "").replace('"', "")
        split_list = cleaned.split(",")
        hold_list = []
        for item in split_list:
            if item == "/":
                continue
            try:
                hold_list.append(int(item))
            except:
                pass
        if len(hold_list) == 2:
            return hold_list
    raise ValueError(f"Unable to parse coordinates from {location}")


def _interpret_quadrant(quadrant, rng_holder):
    if quadrant is None:
        return rng_holder.choice([("+", "+"), ("+", "-"), ("-", "+"), ("-", "-")])
    if isinstance(quadrant, str):
        cleaned = quadrant.replace(" ", "")
        if "," in cleaned:
            split_vals = cleaned.split(",")
        else:
            split_vals = [cleaned[0], cleaned[1]]
    else:
        split_vals = list(quadrant)
    if len(split_vals) != 2:
        raise ValueError(f"Quadrant should contain two values, received {quadrant}")
    if split_vals[0] not in ("+", "-") or split_vals[1] not in ("+", "-"):
        raise ValueError(f"Quadrant values must be + or -, received {quadrant}")
    return split_vals[0], split_vals[1]


def create_village(map_dict, owner, quadrant=None, rng_holder=None):
    if rng_holder is None:
        rng_holder = random

    chosen_quadrant = _interpret_quadrant(quadrant, rng_holder)

    inner_tiles = []
    mid_inner_tiles = []
    mid_tiles = []
    mid_outer_tiles = []
    outer_tiles = []
    total_target_tiles = 0

    for key in map_dict:
        tile = map_dict[key]
        if tile.type_square != "habitable":
            continue
        if tile.type_hab != [4, 4, 4, 6]:
            continue
        coords = _parse_location(tile.location)
        x_val = coords[0]
        y_val = coords[1]

        # exclusion zone
        if -20 <= x_val <= 20 or -20 <= y_val <= 20:
            continue

        # quadrant filter
        x_sign = "+" if x_val >= 0 else "-"
        y_sign = "+" if y_val >= 0 else "-"
        if x_sign != chosen_quadrant[0] or y_sign != chosen_quadrant[1]:
            continue

        total_target_tiles += 1
        distance_val = max(abs(x_val), abs(y_val))
        if distance_val <= 60:
            inner_tiles.append(key)
        elif distance_val <= 100:
            mid_inner_tiles.append(key)
        elif distance_val <= 140:
            mid_tiles.append(key)
        elif distance_val <= 180:
            mid_outer_tiles.append(key)
        else:
            outer_tiles.append(key)

    available_tiles = []
    if inner_tiles:
        available_tiles.append(("inner", 46, inner_tiles))
    if mid_inner_tiles:
        available_tiles.append(("mid_inner", 40, mid_inner_tiles))
    if mid_tiles:
        available_tiles.append(("mid", 10, mid_tiles))
    if mid_outer_tiles:
        available_tiles.append(("mid_outer", 5, mid_outer_tiles))
    if outer_tiles:
        available_tiles.append(("outer", 1, outer_tiles))

    if not available_tiles:
        if total_target_tiles == 0:
            print("No available 4,4,4,6 tiles remain outside the exclusion zone.")
        else:
            print("All available tiles in the chosen quadrant have been settled already.")
        print(f"Failed to make a village for player {owner}.")
        raise RuntimeError("Unable to place village - map appears saturated.")

    weight_total = 0
    for option in available_tiles:
        weight_total += option[1]

    roll = rng_holder.randint(1, weight_total)
    chosen_list = available_tiles[-1][2]
    for option in available_tiles:
        label = option[0]
        weight = option[1]
        tile_list = option[2]
        if roll <= weight:
            chosen_list = tile_list
            break
        roll -= weight

    selected_key = rng_holder.choice(chosen_list)
    selected_tile = map_dict[selected_key]

    new_village = village.Village(
        location=selected_key,
        type_hab=selected_tile.type_hab,
        field_list_dict=selected_tile.field_list_dict,
        owner=owner,
    )
    map_dict[selected_key] = new_village

    return selected_key
