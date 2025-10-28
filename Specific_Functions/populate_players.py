import Classes.player as player
from Classes.AI_Classes.generic_running_mechanism import base_controller
import Specific_Functions.village_creation as village_creation
import random


def populate_players(num_players):
    player_dict = {}
    for i in range(num_players):
        name = f'Player{i}'
        #key for below = name, quadrant, race
        hold_player = player.Player(name, None, None, None)
        player_dict[name] = hold_player
    return player_dict


def populate_players_with_villages(map_dict, num_players, rng_holder=None):
    if rng_holder is None:
        rng_holder = random
    player_dict = populate_players(num_players)
    quadrant_options = [("+", "+"), ("+", "-"), ("-", "+"), ("-", "-")]
    failed_players = []
    for key in list(player_dict.keys()):
        active_player = player_dict[key]
        if active_player.quadrant is None:
            active_player.quadrant = rng_holder.choice(quadrant_options)
        try:
            village_key = village_creation.create_village(
                map_dict,
                active_player.name,
                active_player.quadrant,
                rng_holder,
            )
            created_village = map_dict[village_key]
            created_village.location = village_key
            map_dict[village_key] = created_village
            active_player.villages.append(created_village)

            seed_value = rng_holder.randint(0, 10**9) if hasattr(rng_holder, "randint") else random.randint(0, 10**9)
            local_rng = random.Random(seed_value)

            controller_player = base_controller(
                active_player.name,
                active_player.quadrant,
                active_player.race,
                active_player.ai_controller,
                population=active_player.population,
                attack_points=active_player.attack_points,
                defence_points=active_player.defence_points,
                raid_points=active_player.raid_points,
                culture_points=active_player.culture_points,
                rng_holder=local_rng,
            )
            controller_player.villages = active_player.villages
            player_dict[key] = controller_player
        except RuntimeError:
            failed_players.append(active_player.name)
    if len(failed_players) > 0:
        raise ValueError(f"Players unable to receive villages: {failed_players}")
    return player_dict
