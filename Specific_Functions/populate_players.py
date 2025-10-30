import Classes.player as player
from Classes.AI_Classes.generic_running_mechanism import base_controller
import Specific_Functions.village_creation as village_creation
import random
from Classes.AI_Classes.Hardcoded_AI.field_focus import FieldFocus
from Classes.AI_Classes.Hardcoded_AI.field_focus_lowest import FieldFocusLowest
from Classes.AI_Classes.Hardcoded_AI.field_focus_lowest_legacy import FieldFocusLowestLegacy
from Classes.AI_Classes.Hardcoded_AI.building_focus import BuildingFocus
from Classes.AI_Classes.Hardcoded_AI.main_building_bias import MainBuildingBias
from Classes.AI_Classes.Hardcoded_AI.storage_first import StorageFirst
from Classes.AI_Classes.Hardcoded_AI.balanced_lowest_level import BalancedLowestLevel
from Classes.AI_Classes.Hardcoded_AI.storage_support_blend import StorageSupportBlend
from Classes.AI_Classes.Hardcoded_AI.resource_specialists import (
    CropHoarder,
    WoodWorker,
    ClayCrafter,
    IronMiner,
)
from Classes.AI_Classes.Hardcoded_AI.early_field_focus import EarlyFieldFocus

AI_OPTIONS = [
    {'tag': 'RND', 'label': 'Generic Random', 'builder': None},
    {'tag': 'FF', 'label': 'Field Focus', 'builder': FieldFocus},
    {'tag': 'FL', 'label': 'Field Focus - Lowest Level', 'builder': FieldFocusLowest},
    {'tag': 'FLL', 'label': 'Field Focus - Lowest Level (Legacy)', 'builder': FieldFocusLowestLegacy},
    {'tag': 'BF', 'label': 'Building Focus', 'builder': BuildingFocus},
    {'tag': 'MB', 'label': 'Main Building Bias', 'builder': MainBuildingBias},
    {'tag': 'SF', 'label': 'Storage First', 'builder': StorageFirst},
    {'tag': 'BL', 'label': 'Balanced Lowest Level', 'builder': BalancedLowestLevel},
    {'tag': 'SS', 'label': 'Storage & Support Blend', 'builder': StorageSupportBlend},
    {'tag': 'EF', 'label': 'Early Field Focus', 'builder': EarlyFieldFocus},
    {'tag': 'CH', 'label': 'Resource Specialist - Crop', 'builder': CropHoarder},
    {'tag': 'WW', 'label': 'Resource Specialist - Wood', 'builder': WoodWorker},
    {'tag': 'CC', 'label': 'Resource Specialist - Clay', 'builder': ClayCrafter},
    {'tag': 'IM', 'label': 'Resource Specialist - Iron', 'builder': IronMiner},
]


def populate_players(num_players):
    player_dict = {}
    for i in range(num_players):
        name = f'Player{i}'
        hold_player = player.Player(name, None, None, None)
        player_dict[name] = hold_player
    return player_dict


def populate_players_with_villages(map_dict, num_players, rng_holder=None):
    if rng_holder is None:
        rng_holder = random
    player_dict = populate_players(num_players)
    quadrant_options = [('+', '+'), ('+', '-'), ('-', '+'), ('-', '-')]
    failed_players = []
    for key in list(player_dict.keys()):
        active_player = player_dict[key]
        if active_player.quadrant is None:
            active_player.quadrant = rng_holder.choice(quadrant_options)
        chosen_ai = rng_holder.choice(AI_OPTIONS)
        ai_tag = chosen_ai['tag']
        ai_label = chosen_ai['label']
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

            seed_value = rng_holder.randint(0, 10**9) if hasattr(rng_holder, 'randint') else random.randint(0, 10**9)
            local_rng = random.Random(seed_value)

            final_name = f"{active_player.name}_{ai_tag}"

            controller_player = base_controller(
                final_name,
                active_player.quadrant,
                active_player.race,
                None,
                population=active_player.population,
                attack_points=active_player.attack_points,
                defence_points=active_player.defence_points,
                raid_points=active_player.raid_points,
                culture_points=active_player.culture_points,
                villages=active_player.villages,
                rng_holder=local_rng,
            )
            controller_player.villages = active_player.villages
            controller_player.ai_label = ai_label

            builder = chosen_ai['builder']
            if builder is not None:
                controller_player.ai_controller = builder(controller_player)

            player_dict.pop(key, None)
            player_dict[final_name] = controller_player
        except RuntimeError:
            failed_players.append(active_player.name)
    if len(failed_players) > 0:
        raise ValueError(f"Players unable to receive villages: {failed_players}")
    return player_dict
