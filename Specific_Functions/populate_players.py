import Classes.player as player
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
    for key in player_dict:
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
            active_player.villages.append(village_key)
        except RuntimeError:
            failed_players.append(active_player.name)
    if len(failed_players) > 0:
        raise ValueError(f"Players unable to receive villages: {failed_players}")
    return player_dict
